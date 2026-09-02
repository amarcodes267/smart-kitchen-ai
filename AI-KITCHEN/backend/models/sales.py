from backend.utils.database import db


class Sales(db.Model):
    __tablename__ = "sales"

    id = db.Column(db.Integer, primary_key=True)

    kitchen_id = db.Column(
        db.Integer,
        db.ForeignKey("kitchens.id"),
        nullable=False
    )

    menu_item_id = db.Column(
        db.Integer,
        db.ForeignKey("menu_items.id"),
        nullable=False
    )

    sale_date = db.Column(
        db.Date,
        nullable=False
    )

    quantity_sold = db.Column(
        db.Float,
        nullable=False,
        default=0
    )

    revenue = db.Column(
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
            "sale_date": self.sale_date.isoformat(),
            "quantity_sold": self.quantity_sold,
            "revenue": self.revenue,
            "created_at": (
                self.created_at.isoformat()
                if self.created_at else None
            )
        }