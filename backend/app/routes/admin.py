from datetime import date
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from ..models import User, Department, Service, Queue, QueueToken

bp=Blueprint("admin",__name__)

def allowed(): return get_jwt().get("role")=="ADMIN"

@bp.get("/dashboard")
@jwt_required()
def dashboard():
    if not allowed(): return jsonify(success=False,message="Admin access required"),403
    return jsonify(success=True,data={
        "students":User.query.filter_by(role="STUDENT").count(),
        "staff":User.query.filter_by(role="STAFF").count(),
        "departments":Department.query.count(),
        "services":Service.query.count(),
        "active_queues":Queue.query.filter_by(queue_date=date.today(),status="OPEN").count(),
        "waiting_tokens":QueueToken.query.filter_by(status="WAITING").count(),
        "completed_tokens":QueueToken.query.filter_by(status="COMPLETED").count()
    })

@bp.get("/users")
@jwt_required()
def users():
    if not allowed(): return jsonify(success=False,message="Admin access required"),403
    return jsonify(success=True,data=[u.to_dict() for u in User.query.order_by(User.id.desc()).all()])
