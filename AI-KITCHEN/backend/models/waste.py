from backend.utils.database import db


class Waste(db.Model):
    __tablename__ = "waste"

    id = db.Column(db.Integer, primary_key=True)

    kitchen_id = db.Column(
        db.Integer,
        db.ForeignKey("kitchens.id"),
        nullable=False
    )

    menu_item_id = db.Column(
        db.Integer,
        db.ForeignKey("menu_items.id"),
        nullable=True
    )

    waste_date = db.Column(
        db.Date,
        nullable=False
    )

    quantity_wasted = db.Column(
        db.Float,
        nullable=False,
        default=0
    )

    unit = db.Column(
        db.String(50),
        nullable=False,
        default="servings"
    )

    reason = db.Column(
        db.String(255),
        nullable=True
    )

    estimated_cost = db.Column(
        db.Float,
        nullable=True,
        default=0
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    def to_dict(self):
        return {
            "id": self.id,
            "kitchen_id": self.kitchen_id,
            "menu_item_id": self.menu_item_id,
            "waste_date": self.waste_date.isoformat(),
            "quantity_wasted": self.quantity_wasted,
            "unit": self.unit,
            "reason": self.reason,
            "estimated_cost": self.estimated_cost,
            "created_at": (
                self.created_at.isoformat()
                if self.created_at else None
            )
        }