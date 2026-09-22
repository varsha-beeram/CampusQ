from datetime import datetime, timezone
from ..extensions import db

class Notification(db.Model):
    __tablename__ = "notifications"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(160), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(30), nullable=False, default="INFO")
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
