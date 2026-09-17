from backend.utils.database import db


class Alert(db.Model):
    __tablename__ = "alerts"

    id = db.Column(db.Integer, primary_key=True)

    kitchen_id = db.Column(
        db.Integer,
        db.ForeignKey("kitchens.id"),
        nullable=False
    )

    level = db.Column(
        db.String(20),
        nullable=False,
        default="info"
    )

    category = db.Column(
        db.String(50),
        nullable=False
    )

    title = db.Column(
        db.String(200),
        nullable=False
    )

    message = db.Column(
        db.String(500),
        nullable=False
    )

    meta = db.Column(
        db.String(500),
        nullable=True
    )

    is_read = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    def to_dict(self):
        return {
            "id": self.id,
            "kitchen_id": self.kitchen_id,
            "level": self.level,
            "category": self.category,
            "title": self.title,
            "message": self.message,
            "meta": self.meta,
            "is_read": self.is_read,
            "created_at": (
                self.created_at.isoformat()
                if self.created_at else None
            )
        }
