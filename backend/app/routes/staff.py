from datetime import date, datetime, timezone
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from ..extensions import db
from ..models import QueueToken, StaffAssignment, Notification, QueueEvent

bp = Blueprint("staff", __name__)

def authorized():
    return get_jwt().get("role") == "STAFF"

def assignments(staff_id):
    return StaffAssignment.query.filter_by(staff_id=staff_id, is_active=True).all()

def owns(staff_id, token):
    return StaffAssignment.query.filter_by(staff_id=staff_id, service_id=token.queue.service_id, is_active=True).first()

def notify(token, title, message, kind="QUEUE"):
    db.session.add(Notification(user_id=token.student_id, title=title, message=message, type=kind, is_read=False))

@bp.get("/dashboard")
@jwt_required()
def dashboard():
    if not authorized(): return jsonify(success=False, message="Staff access required"), 403
    sid = int(get_jwt_identity()); ids = [a.service_id for a in assignments(sid)]
    waiting = QueueToken.query.filter(QueueToken.status=="WAITING", QueueToken.queue.has(
        QueueToken.queue_date == date.today())).filter(QueueToken.queue.has(
        QueueToken.service_id.in_(ids))).count() if ids else 0
    completed = QueueToken.query.filter(QueueToken.status=="COMPLETED",
        QueueToken.completed_at >= datetime.combine(date.today(), datetime.min.time())).count()
    return jsonify(success=True, data={"waiting":waiting,"completed_today":completed,"assigned_services":ids})

@bp.get("/queue")
@jwt_required()
def queue():
    if not authorized(): return jsonify(success=False, message="Staff access required"), 403
    sid = int(get_jwt_identity()); ids = [a.service_id for a in assignments(sid)]
    if not ids: return jsonify(success=True, data=[])
    rows = QueueToken.query.filter(QueueToken.status.in_(("WAITING","CALLED","SERVING")),
        QueueToken.queue.has(QueueToken.queue_date==date.today()),
        QueueToken.queue.has(QueueToken.service_id.in_(ids))).order_by(QueueToken.token_number).all()
    return jsonify(success=True, data=[{"id":t.id,"token_number":t.token_number,
        "display_token":f"{t.queue.service.code}-{t.token_number:03d}","status":t.status,
        "service_id":t.queue.service_id,"service":t.queue.service.name,
        "student_name":t.student.name} for t in rows])

@bp.post("/queue/call-next")
@jwt_required()
def call_next():
    if not authorized(): return jsonify(success=False, message="Staff access required"), 403
    sid=int(get_jwt_identity()); ids=[a.service_id for a in assignments(sid)]
    if not ids: return jsonify(success=False,message="No assigned service"),400
    t=QueueToken.query.filter_by(status="WAITING").filter(
        QueueToken.queue.has(QueueToken.queue_date==date.today()),
        QueueToken.queue.has(QueueToken.service_id.in_(ids))
    ).order_by(QueueToken.joined_at).first()
    if not t: return jsonify(success=False,message="No waiting tokens"),404
    # Complete any stale serving token for this service before calling the next one.
    serving=QueueToken.query.filter_by(queue_id=t.queue_id,status="SERVING").first()
    if serving: return jsonify(success=False,message="Complete the current serving token first"),409
    t.status="CALLED"; t.called_at=datetime.now(timezone.utc)
    db.session.add(QueueEvent(token_id=t.id,actor_id=sid,event_type="CALLED"))
    notify(t,"Your turn is next",f"Token {t.queue.service.code}-{t.token_number:03d} has been called. Please proceed to your assigned counter.")
    db.session.commit()
    return jsonify(success=True,message="Next token called",data={"id":t.id,"display_token":f"{t.queue.service.code}-{t.token_number:03d}"})

def change(token_id, status):
    if not authorized(): return jsonify(success=False,message="Staff access required"),403
    sid=int(get_jwt_identity()); t=QueueToken.query.get_or_404(token_id)
    if not owns(sid,t): return jsonify(success=False,message="You are not assigned to this service"),403
    now=datetime.now(timezone.utc)
    if status=="SERVING":
        t.status="SERVING"; t.service_started_at=now
        notify(t,"Service started",f"Token {t.queue.service.code}-{t.token_number:03d} is now being served.")
        event="STARTED"
    elif status=="COMPLETED":
        t.status="COMPLETED"; t.completed_at=now
        notify(t,"Service completed",f"Token {t.queue.service.code}-{t.token_number:03d} has been completed.")
        event="COMPLETED"
    else:
        t.status="SKIPPED"; t.skipped_at=now
        notify(t,"Token skipped",f"Token {t.queue.service.code}-{t.token_number:03d} was skipped. Contact the service desk if this was unexpected.")
        event="SKIPPED"
    db.session.add(QueueEvent(token_id=t.id,actor_id=sid,event_type=event))
    db.session.commit()
    return jsonify(success=True,data={"id":t.id,"status":t.status})

@bp.post("/tokens/<int:token_id>/start")
@jwt_required()
def start(token_id): return change(token_id,"SERVING")

@bp.post("/tokens/<int:token_id>/complete")
@jwt_required()
def complete(token_id): return change(token_id,"COMPLETED")

@bp.post("/tokens/<int:token_id>/skip")
@jwt_required()
def skip(token_id): return change(token_id,"SKIPPED")
