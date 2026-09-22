from ..extensions import db

class Department(db.Model):
    __tablename__ = "departments"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140), unique=True, nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    sub_departments = db.relationship("SubDepartment", backref="department", cascade="all, delete-orphan")

    def to_dict(self):
        return {"id": self.id, "name": self.name, "description": self.description, "is_active": self.is_active}

class SubDepartment(db.Model):
    __tablename__ = "sub_departments"
    id = db.Column(db.Integer, primary_key=True)
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=False)
    name = db.Column(db.String(140), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    def to_dict(self):
        return {"id": self.id, "department_id": self.department_id, "name": self.name,
                "description": self.description, "is_active": self.is_active}

class Service(db.Model):
    __tablename__ = "services"
    id = db.Column(db.Integer, primary_key=True)
    sub_department_id = db.Column(db.Integer, db.ForeignKey("sub_departments.id"), nullable=False)
    name = db.Column(db.String(160), nullable=False)
    description = db.Column(db.Text)
    code = db.Column(db.String(20), nullable=False)
    average_service_time = db.Column(db.Integer, default=10, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    sub_department = db.relationship("SubDepartment", backref=db.backref("services", cascade="all, delete-orphan"))

    def to_dict(self):
        return {"id": self.id, "sub_department_id": self.sub_department_id, "name": self.name,
                "description": self.description, "code": self.code,
                "average_service_time": self.average_service_time, "is_active": self.is_active}

class Counter(db.Model):
    __tablename__ = "counters"
    id = db.Column(db.Integer, primary_key=True)
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    counter_number = db.Column(db.String(30), nullable=False)
    location = db.Column(db.String(160))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    department = db.relationship("Department", backref="counters")

class StaffAssignment(db.Model):
    __tablename__ = "staff_assignments"
    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    counter_id = db.Column(db.Integer, db.ForeignKey("counters.id"), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey("services.id"), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    staff = db.relationship("User", backref="assignments")
    counter = db.relationship("Counter", backref="assignments")
    service = db.relationship("Service", backref="staff_assignments")
