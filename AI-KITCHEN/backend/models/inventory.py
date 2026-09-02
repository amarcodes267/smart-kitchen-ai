from backend.utils.database import db


class Inventory(db.Model):
    __tablename__ = "inventory"

    id = db.Column(db.Integer, primary_key=True)

    kitchen_id = db.Column(
        db.Integer,
        db.ForeignKey("kitchens.id"),
        nullable=False
    )

    ingredient_name = db.Column(
        db.String(150),
        nullable=False
    )

    quantity = db.Column(
        db.Float,
        nullable=False,
        default=0
    )

    unit = db.Column(
        db.String(50),
        nullable=False,
        default="kg"
    )

    minimum_stock = db.Column(
        db.Float,
        nullable=True,
        default=0
    )

    expiry_date = db.Column(
        db.Date,
        nullable=True
    )

    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        onupdate=db.func.now()
    )

    def to_dict(self):
        return {
            "id": self.id,
            "kitchen_id": self.kitchen_id,
            "ingredient_name": self.ingredient_name,
            "quantity": self.quantity,
            "unit": self.unit,
            "minimum_stock": self.minimum_stock,
            "expiry_date": (
                self.expiry_date.isoformat()
                if self.expiry_date else None
            ),
            "updated_at": (
                self.updated_at.isoformat()
                if self.updated_at else None
            )
        }