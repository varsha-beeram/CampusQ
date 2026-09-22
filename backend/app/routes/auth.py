from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from ..extensions import db
from ..models import User

bp = Blueprint("auth", __name__)

@bp.post("/register")
def register():
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    if not name or not email or len(password) < 8:
        return jsonify(success=False, message="Name, email and an 8+ character password are required"), 400
    if User.query.filter_by(email=email).first():
        return jsonify(success=False, message="Email is already registered"), 409
    u = User(name=name, email=email, phone=data.get("phone"), role="STUDENT")
    u.set_password(password)
    db.session.add(u); db.session.commit()
    token = create_access_token(identity=str(u.id), additional_claims={"role": u.role})
    return jsonify(success=True, data={"token": token, "user": u.to_dict()}), 201

@bp.post("/login")
def login():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    u = User.query.filter_by(email=email).first()
    if not u or not u.is_active or not u.check_password(data.get("password") or ""):
        return jsonify(success=False, message="Invalid email or password"), 401
    token = create_access_token(identity=str(u.id), additional_claims={"role": u.role})
    return jsonify(success=True, data={"token": token, "user": u.to_dict()})

@bp.get("/me")
@jwt_required()
def me():
    u = User.query.get(int(get_jwt_identity()))
    if not u:
        return jsonify(success=False, message="User not found"), 404
    return jsonify(success=True, data=u.to_dict())
