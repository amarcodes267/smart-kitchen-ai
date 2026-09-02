from backend.utils.database import db


class Prediction(db.Model):
    __tablename__ = "predictions"

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

    prediction_date = db.Column(
        db.Date,
        nullable=False
    )

    predicted_demand = db.Column(
        db.Float,
        nullable=False
    )

    recommended_preparation = db.Column(
        db.Float,
        nullable=True
    )

    model_name = db.Column(
        db.String(100),
        nullable=True,
        default="XGBoost"
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
            "prediction_date": self.prediction_date.isoformat(),
            "predicted_demand": self.predicted_demand,
            "recommended_preparation": self.recommended_preparation,
            "model_name": self.model_name,
            "created_at": (
                self.created_at.isoformat()
                if self.created_at else None
            )
        }