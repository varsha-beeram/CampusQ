from datetime import datetime, timezone
from ..extensions import db

class Queue(db.Model):
    __tablename__ = "queues"
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey("services.id"), nullable=False)
    queue_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="OPEN")
    last_token_number = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    __table_args__ = (db.UniqueConstraint("service_id", "queue_date", name="uq_queue_service_date"),)
    service = db.relationship("Service", backref="queues")

class QueueToken(db.Model):
    __tablename__ = "queue_tokens"
    id = db.Column(db.Integer, primary_key=True)
    queue_id = db.Column(db.Integer, db.ForeignKey("queues.id"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    token_number = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="WAITING")
    joined_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    called_at = db.Column(db.DateTime)
    service_started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    cancelled_at = db.Column(db.DateTime)
    skipped_at = db.Column(db.DateTime)
    estimated_wait_minutes = db.Column(db.Integer, nullable=False, default=0)
    student = db.relationship("User", backref="queue_tokens")
    queue = db.relationship("Queue", backref="tokens")

class QueueEvent(db.Model):
    __tablename__ = "queue_events"
    id = db.Column(db.Integer, primary_key=True)
    token_id = db.Column(db.Integer, db.ForeignKey("queue_tokens.id"), nullable=False)
    actor_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    event_type = db.Column(db.String(30), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
