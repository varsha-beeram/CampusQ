from app import create_app
from app.extensions import db
from app.models import User, Department, SubDepartment, Service, Counter, StaffAssignment
from app.models import Queue, QueueToken
from datetime import date, datetime, timedelta, timezone

app=create_app()
with app.app_context():
    db.drop_all(); db.create_all()

    admin=User(name="CampusQ Admin",email="admin@campusq.com",role="ADMIN"); admin.set_password("Admin@123")
    staff1=User(name="Priya Staff",email="staff@campusq.com",role="STAFF"); staff1.set_password("Staff@123")
    staff2=User(name="Rahul Staff",email="staff2@campusq.com",role="STAFF"); staff2.set_password("Staff@123")
    student=User(name="Demo Student",email="student@campusq.com",role="STUDENT"); student.set_password("Student@123")
    db.session.add_all([admin,staff1,staff2,student]); db.session.flush()

    catalog=[
        ("Academic Services","Academic records, certificates and student documents.",
         [("Academic Records","Transcript, bonafide and certificates.")]),
        ("Examination Cell","Examination forms, hall tickets and results.",
         [("Exam Support","Examination-related student services.")]),
        ("Library","Library access, issue, return and clearance.",
         [("Library Desk","Books and clearance services.")]),
        ("Student Welfare","Student support and campus welfare services.",
         [("Student Support","General student support.")]),
        ("Administration","General administrative campus services.",
         [("Admin Helpdesk","Administrative support.")])
    ]
    service_refs=[]
    for idx,(dn,dd,subs) in enumerate(catalog,1):
        d=Department(name=dn,description=dd); db.session.add(d); db.session.flush()
        for sn,sd in subs:
            s=SubDepartment(department_id=d.id,name=sn,description=sd); db.session.add(s); db.session.flush()
            svc=Service(sub_department_id=s.id,name=f"{sn} Helpdesk",description=sd,
                        code=f"{'A' if idx==1 else 'E' if idx==2 else 'L' if idx==3 else 'S' if idx==4 else 'AD'}{idx}",
                        average_service_time=8 if idx==3 else 10)
            db.session.add(svc); db.session.flush()
            c=Counter(department_id=d.id,name=f"{dn} Counter",counter_number=str(idx),location="Main Campus")
            db.session.add(c); db.session.flush()
            db.session.add(StaffAssignment(staff_id=staff1.id if idx%2 else staff2.id,counter_id=c.id,service_id=svc.id))
            service_refs.append(svc)

    db.session.commit()

    # Seed a realistic live queue for the first service. Demo student receives the next token.
    service=service_refs[0]
    q=Queue(service_id=service.id,queue_date=date.today(),status="OPEN",last_token_number=5)
    db.session.add(q); db.session.flush()
    for n in range(1,6):
        owner=student if n==5 else User.query.filter_by(role="STUDENT").first()
        # Create additional students so each token has a distinct owner.
        if n != 5:
            owner=User(name=f"Demo Student {n}",email=f"student{n}@campusq.com",role="STUDENT")
            owner.set_password("Student@123"); db.session.add(owner); db.session.flush()
        status="COMPLETED" if n==1 else "SERVING" if n==2 else "WAITING"
        t=QueueToken(queue_id=q.id,student_id=owner.id,token_number=n,status=status,
                     joined_at=datetime.now(timezone.utc)-timedelta(minutes=(6-n)*10))
        if status=="SERVING":
            t.called_at=datetime.now(timezone.utc)-timedelta(minutes=4)
            t.service_started_at=datetime.now(timezone.utc)-timedelta(minutes=3)
        if status=="COMPLETED":
            t.called_at=datetime.now(timezone.utc)-timedelta(minutes=15)
            t.service_started_at=datetime.now(timezone.utc)-timedelta(minutes=14)
            t.completed_at=datetime.now(timezone.utc)-timedelta(minutes=5)
        db.session.add(t)
    db.session.commit()

    print("CampusQ database seeded.")
    print("Admin   : admin@campusq.com / Admin@123")
    print("Staff   : staff@campusq.com / Staff@123")
    print("Staff 2 : staff2@campusq.com / Staff@123")
    print("Student : student@campusq.com / Student@123")
    print("Student demo starts with a live queue token for the Academic Services queue.")
