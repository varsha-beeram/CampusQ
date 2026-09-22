from flask import Blueprint, jsonify
from ..models import Department, SubDepartment, Service

bp = Blueprint("catalog", __name__)

@bp.get("/departments")
def departments():
    return jsonify(success=True, data=[d.to_dict() for d in Department.query.filter_by(is_active=True).all()])

@bp.get("/departments/<int:department_id>/sub-departments")
def sub_departments(department_id):
    return jsonify(success=True, data=[s.to_dict() for s in SubDepartment.query.filter_by(
        department_id=department_id, is_active=True).all()])

@bp.get("/sub-departments/<int:sub_department_id>/services")
def services(sub_department_id):
    return jsonify(success=True, data=[s.to_dict() for s in Service.query.filter_by(
        sub_department_id=sub_department_id, is_active=True).all()])

@bp.get("/services/<int:service_id>")
def service(service_id):
    s = Service.query.get_or_404(service_id)
    return jsonify(success=True, data=s.to_dict())
