from backend.utils.database import db


class Kitchen(db.Model):
    __tablename__ = "kitchens"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(150), nullable=False)

    cuisine_type = db.Column(db.String(100), nullable=True)

    seats = db.Column(db.Integer, nullable=True)

    meals_per_day = db.Column(db.Integer, nullable=True)

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "cuisine_type": self.cuisine_type,
            "seats": self.seats,
            "meals_per_day": self.meals_per_day,
            "created_at": self.created_at.isoformat()
            if self.created_at else None
        }