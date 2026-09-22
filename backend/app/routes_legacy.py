from datetime import date,datetime,timezone
from flask import Blueprint,request,jsonify
from flask_jwt_extended import create_access_token,jwt_required,get_jwt_identity,get_jwt
from werkzeug.security import generate_password_hash,check_password_hash
from . import db
bp=Blueprint('api',__name__)

class User(db.Model):
    id=db.Column(db.Integer,primary_key=True); name=db.Column(db.String(120),nullable=False); email=db.Column(db.String(160),unique=True,nullable=False); phone=db.Column(db.String(30)); password_hash=db.Column(db.String(255),nullable=False); role=db.Column(db.String(20),default='STUDENT'); is_active=db.Column(db.Boolean,default=True)
class Department(db.Model):
    id=db.Column(db.Integer,primary_key=True); name=db.Column(db.String(120),unique=True,nullable=False); description=db.Column(db.Text); is_active=db.Column(db.Boolean,default=True)
class SubDepartment(db.Model):
    id=db.Column(db.Integer,primary_key=True); department_id=db.Column(db.Integer,db.ForeignKey('department.id'),nullable=False); name=db.Column(db.String(120),nullable=False); description=db.Column(db.Text); is_active=db.Column(db.Boolean,default=True)
class Service(db.Model):
    id=db.Column(db.Integer,primary_key=True); sub_department_id=db.Column(db.Integer,db.ForeignKey('sub_department.id'),nullable=False); name=db.Column(db.String(160),nullable=False); description=db.Column(db.Text); average_service_time=db.Column(db.Integer,default=10); is_active=db.Column(db.Boolean,default=True)
class Queue(db.Model):
    id=db.Column(db.Integer,primary_key=True); service_id=db.Column(db.Integer,db.ForeignKey('service.id'),nullable=False); queue_date=db.Column(db.Date,default=date.today); current_number=db.Column(db.Integer,default=0); status=db.Column(db.String(20),default='OPEN'); __table_args__=(db.UniqueConstraint('service_id','queue_date'),)
class Token(db.Model):
    id=db.Column(db.Integer,primary_key=True); queue_id=db.Column(db.Integer,db.ForeignKey('queue.id'),nullable=False); student_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False); token_number=db.Column(db.Integer,nullable=False); status=db.Column(db.String(20),default='WAITING'); joined_at=db.Column(db.DateTime,default=lambda:datetime.now(timezone.utc)); estimated_wait=db.Column(db.Integer,default=0)


def ud(u): return {'id':u.id,'name':u.name,'email':u.email,'phone':u.phone,'role':u.role}
def role(r): return get_jwt().get('role')==r

@bp.post('/auth/register')
def register():
    d=request.get_json() or {}; email=d.get('email','').strip().lower(); password=d.get('password','')
    if not d.get('name') or not email or len(password)<8:return jsonify(success=False,message='Name, email and 8+ character password required'),400
    if User.query.filter_by(email=email).first():return jsonify(success=False,message='Email already registered'),409
    u=User(name=d['name'].strip(),email=email,phone=d.get('phone'),password_hash=generate_password_hash(password));db.session.add(u);db.session.commit()
    t=create_access_token(identity=str(u.id),additional_claims={'role':u.role});return jsonify(success=True,data={'token':t,'user':ud(u)}),201
@bp.post('/auth/login')
def login():
    d=request.get_json() or {};u=User.query.filter_by(email=d.get('email','').lower()).first()
    if not u or not check_password_hash(u.password_hash,d.get('password','')):return jsonify(success=False,message='Invalid email or password'),401
    return jsonify(success=True,data={'token':create_access_token(identity=str(u.id),additional_claims={'role':u.role}),'user':ud(u)})
@bp.get('/auth/me')
@jwt_required()
def me():return jsonify(success=True,data=ud(User.query.get(int(get_jwt_identity()))))
@bp.get('/departments')
def deps():return jsonify(success=True,data=[{'id':d.id,'name':d.name,'description':d.description} for d in Department.query.filter_by(is_active=True)])
@bp.get('/departments/<int:id>/sub-departments')
def subs(id):return jsonify(success=True,data=[{'id':s.id,'name':s.name,'description':s.description} for s in SubDepartment.query.filter_by(department_id=id,is_active=True)])
@bp.get('/sub-departments/<int:id>/services')
def services(id):return jsonify(success=True,data=[{'id':s.id,'name':s.name,'description':s.description,'average_service_time':s.average_service_time} for s in Service.query.filter_by(sub_department_id=id,is_active=True)])
@bp.post('/tokens/join')
@jwt_required()
def join():
    sid=int(get_jwt_identity());d=request.get_json() or {};s=Service.query.get(d.get('service_id'))
    if not s:return jsonify(success=False,message='Service not found'),404
    q=Queue.query.filter_by(service_id=s.id,queue_date=date.today()).first()
    if not q:q=Queue(service_id=s.id);db.session.add(q);db.session.flush()
    dup=Token.query.filter_by(queue_id=q.id,student_id=sid).filter(Token.status.in_(['WAITING','CALLED','SERVING'])).first()
    if dup:return jsonify(success=False,message='You already have an active token for this service today'),409
    last=Token.query.filter_by(queue_id=q.id).order_by(Token.token_number.desc()).first();num=(last.token_number if last else 0)+1
    ahead=Token.query.filter_by(queue_id=q.id,status='WAITING').count();t=Token(queue_id=q.id,student_id=sid,token_number=num,estimated_wait=ahead*s.average_service_time);db.session.add(t);q.current_number=num;db.session.commit()
    return jsonify(success=True,data={'id':t.id,'token_number':num,'status':t.status,'people_ahead':ahead,'estimated_wait':t.estimated_wait}),201
@bp.get('/tokens/my-active')
@jwt_required()
def active():
    sid=int(get_jwt_identity());ts=Token.query.filter_by(student_id=sid).filter(Token.status.in_(['WAITING','CALLED','SERVING'])).all();return jsonify(success=True,data=[{'id':t.id,'token_number':t.token_number,'status':t.status,'estimated_wait':t.estimated_wait} for t in ts])
@bp.post('/tokens/<int:id>/cancel')
@jwt_required()
def cancel(id):
    t=Token.query.get_or_404(id)
    if t.student_id!=int(get_jwt_identity()):return jsonify(success=False,message='Access denied'),403
    t.status='CANCELLED';db.session.commit();return jsonify(success=True,message='Token cancelled')
@bp.get('/staff/queue')
@jwt_required()
def staff_queue():
    if not role('STAFF'):return jsonify(success=False,message='Staff access required'),403
    return jsonify(success=True,data=[{'id':t.id,'token_number':t.token_number,'status':t.status} for t in Token.query.filter(Token.status.in_(['WAITING','CALLED','SERVING'])).order_by(Token.joined_at)])
@bp.post('/staff/queue/call-next')
@jwt_required()
def call_next():
    if not role('STAFF'):return jsonify(success=False,message='Staff access required'),403
    t=Token.query.filter_by(status='WAITING').order_by(Token.joined_at).first()
    if not t:return jsonify(success=False,message='No waiting tokens'),404
    t.status='CALLED';db.session.commit();return jsonify(success=True,data={'id':t.id,'token_number':t.token_number})
@bp.post('/staff/tokens/<int:id>/<action>')
@jwt_required()
def staff_action(id,action):
    if not role('STAFF'):return jsonify(success=False,message='Staff access required'),403
    t=Token.query.get_or_404(id);m={'start':'SERVING','complete':'COMPLETED','skip':'SKIPPED'}
    if action not in m:return jsonify(success=False,message='Invalid action'),400
    t.status=m[action];db.session.commit();return jsonify(success=True,data={'id':t.id,'status':t.status})
@bp.get('/admin/dashboard')
@jwt_required()
def admin_dash():
    if not role('ADMIN'):return jsonify(success=False,message='Admin access required'),403
    return jsonify(success=True,data={'students':User.query.filter_by(role='STUDENT').count(),'staff':User.query.filter_by(role='STAFF').count(),'departments':Department.query.count(),'services':Service.query.count(),'waiting_tokens':Token.query.filter_by(status='WAITING').count()})
