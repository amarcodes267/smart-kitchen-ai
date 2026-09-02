from backend.utils.database import db


class MenuItem(db.Model):
    __tablename__ = "menu_items"

    id = db.Column(db.Integer, primary_key=True)

    kitchen_id = db.Column(
        db.Integer,
        db.ForeignKey("kitchens.id"),
        nullable=False
    )

    name = db.Column(db.String(150), nullable=False)

    category = db.Column(db.String(100), nullable=True)

    price = db.Column(db.Float, nullable=True)

    serving_unit = db.Column(
        db.String(50),
        nullable=False,
        default="servings"
    )

    cost_per_serving = db.Column(
        db.Float,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    def to_dict(self):
        return {
            "id": self.id,
            "kitchen_id": self.kitchen_id,
            "name": self.name,
            "category": self.category,
            "price": self.price,
            "serving_unit": self.serving_unit,
            "cost_per_serving": self.cost_per_serving,
            "created_at": (
                self.created_at.isoformat()
                if self.created_at else None
            )
        }
