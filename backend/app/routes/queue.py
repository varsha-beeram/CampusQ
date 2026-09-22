from datetime import date, datetime, timezone, timedelta
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_
from ..extensions import db
from ..models import Queue, QueueToken, Service, Counter, Notification, QueueEvent

bp = Blueprint("queue", __name__)
ACTIVE = ("WAITING", "CALLED", "SERVING")

def today_queue(service_id):
    q = Queue.query.filter_by(service_id=service_id, queue_date=date.today()).first()
    if not q:
        q = Queue(service_id=service_id, queue_date=date.today())
        db.session.add(q); db.session.flush()
    return q

def live_position(t):
    waiting_before = QueueToken.query.filter_by(queue_id=t.queue_id, status="WAITING").filter(
        QueueToken.token_number < t.token_number).count()
    called_or_serving = QueueToken.query.filter_by(queue_id=t.queue_id).filter(
        QueueToken.status.in_(("CALLED", "SERVING")),
        QueueToken.token_number < t.token_number
    ).count()
    return waiting_before + called_or_serving

def current_serving(q):
    return QueueToken.query.filter_by(queue_id=q.id).filter(
        QueueToken.status.in_(("CALLED", "SERVING"))
    ).order_by(QueueToken.token_number).first()

def token_payload(t):
    q = t.queue
    service = q.service
    current = current_serving(q)
    position = live_position(t) if t.status == "WAITING" else 0
    ahead = position
    # Include the currently serving token in the wait estimate only when it exists.
    estimate = 0
    if t.status == "WAITING":
        estimate = max(0, ahead * service.average_service_time)
        t.estimated_wait_minutes = estimate
    # Resolve the first active counter assigned to this service.
    assignment = next((a for a in service.staff_assignments if a.is_active and a.counter and a.counter.is_active), None)
    counter = assignment.counter if assignment else None
    expected = None
    if t.status == "WAITING":
        expected = datetime.now() + timedelta(minutes=estimate)
    return {
        "id": t.id, "token_number": t.token_number, "display_token": f"{service.code}-{t.token_number:03d}",
        "status": t.status, "queue_id": q.id, "service_id": service.id,
        "service_name": service.name, "service_code": service.code,
        "people_ahead": ahead, "queue_position": ahead + 1 if t.status == "WAITING" else 0,
        "estimated_wait_minutes": estimate,
        "expected_turn": expected.isoformat(timespec="minutes") if expected else None,
        "current_serving": f"{service.code}-{current.token_number:03d}" if current else None,
        "counter": {"id": counter.id, "name": counter.name, "number": counter.counter_number, "location": counter.location} if counter else None,
        "joined_at": t.joined_at.isoformat() if t.joined_at else None
    }

@bp.get("/queues/service/<int:service_id>")
def queue_summary(service_id):
    service = Service.query.get_or_404(service_id)
    q = today_queue(service_id)
    current = current_serving(q)
    waiting = QueueToken.query.filter_by(queue_id=q.id, status="WAITING").order_by(QueueToken.token_number).all()
    return jsonify(success=True, data={
        "queue_id": q.id, "service": service.to_dict(),
        "status": q.status, "current_serving": f"{service.code}-{current.token_number:03d}" if current else None,
        "waiting_count": len(waiting),
        "waiting_tokens": [f"{service.code}-{t.token_number:03d}" for t in waiting]
    })

@bp.post("/tokens/join")
@jwt_required()
def join():
    student_id = int(get_jwt_identity())
    data = request.get_json() or {}
    service = Service.query.get(data.get("service_id"))
    if not service or not service.is_active:
        return jsonify(success=False, message="Service not found"), 404
    q = today_queue(service.id)
    duplicate = QueueToken.query.filter_by(queue_id=q.id, student_id=student_id).filter(
        QueueToken.status.in_(ACTIVE)).first()
    if duplicate:
        return jsonify(success=False, message="You already have an active token for this service today",
                       data=token_payload(duplicate)), 409
    q.last_token_number += 1
    token = QueueToken(queue_id=q.id, student_id=student_id, token_number=q.last_token_number)
    db.session.add(token); db.session.flush()
    db.session.add(QueueEvent(token_id=token.id, actor_id=student_id, event_type="JOINED"))
    db.session.commit()
    return jsonify(success=True, message="Queue joined successfully", data=token_payload(token)), 201

@bp.get("/tokens/my-active")
@jwt_required()
def my_active():
    sid = int(get_jwt_identity())
    tokens = QueueToken.query.filter_by(student_id=sid).filter(
        QueueToken.status.in_(ACTIVE)).order_by(QueueToken.joined_at.desc()).all()
    return jsonify(success=True, data=[token_payload(t) for t in tokens])

@bp.get("/tokens/my-history")
@jwt_required()
def my_history():
    sid = int(get_jwt_identity())
    tokens = QueueToken.query.filter_by(student_id=sid).filter(
        ~QueueToken.status.in_(ACTIVE)).order_by(QueueToken.joined_at.desc()).all()
    return jsonify(success=True, data=[token_payload(t) for t in tokens])

@bp.get("/tokens/<int:token_id>")
@jwt_required()
def get_token(token_id):
    t = QueueToken.query.get_or_404(token_id)
    if t.student_id != int(get_jwt_identity()):
        return jsonify(success=False, message="Access denied"), 403
    return jsonify(success=True, data=token_payload(t))

@bp.post("/tokens/<int:token_id>/cancel")
@jwt_required()
def cancel(token_id):
    t = QueueToken.query.get_or_404(token_id)
    if t.student_id != int(get_jwt_identity()):
        return jsonify(success=False, message="Access denied"), 403
    if t.status not in ACTIVE:
        return jsonify(success=False, message="Token cannot be cancelled"), 400
    t.status = "CANCELLED"; t.cancelled_at = datetime.now(timezone.utc)
    db.session.add(QueueEvent(token_id=t.id, actor_id=t.student_id, event_type="CANCELLED"))
    db.session.commit()
    return jsonify(success=True, message="Token cancelled", data=token_payload(t))

@bp.get("/notifications")
@jwt_required()
def notifications():
    sid = int(get_jwt_identity())
    rows = Notification.query.filter_by(user_id=sid).order_by(Notification.created_at.desc()).limit(30).all()
    return jsonify(success=True, data=[{"id":n.id,"title":n.title,"message":n.message,"type":n.type,"is_read":n.is_read,
                                       "created_at":n.created_at.isoformat()} for n in rows])
