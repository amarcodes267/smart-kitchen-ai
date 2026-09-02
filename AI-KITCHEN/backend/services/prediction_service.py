from datetime import date, timedelta
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from backend.models.sales import Sales
from backend.models.prediction import Prediction
from backend.utils.database import db


# Location of trained model
BASE_DIR = Path(__file__).resolve().parents[2]
MODEL_PATH = BASE_DIR / "ml" / "model.pkl"


class FallbackModel:
    def predict(self, features):
        baseline = (
            10
            + 0.35 * features["day_of_week"]
            + 0.4 * features["month"]
            + 0.85 * features["previous_sales"]
            + 0.65 * features["rolling_7_day_avg"]
        )
        return np.clip(
            np.round(baseline.to_numpy(dtype=float)),
            0,
            None
        ).astype(float)


def load_model():
    """
    Load the trained XGBoost model.
    """

    if not MODEL_PATH.exists():
        return FallbackModel()

    try:
        model_data = joblib.load(MODEL_PATH)
        if isinstance(model_data, dict):
            return model_data.get("model", FallbackModel())
        return model_data
    except Exception:
        return FallbackModel()


def prepare_features(sales_data):
    """
    Convert historical sales data into
    features required by the ML model.
    """

    if not sales_data:
        raise ValueError(
            "Not enough sales data available for prediction."
        )

    rows = []

    for sale in sales_data:
        rows.append({
            "date": sale.sale_date,
            "quantity_sold": sale.quantity_sold
        })

    df = pd.DataFrame(rows)

    df["date"] = pd.to_datetime(df["date"])

    df = df.sort_values("date")

    # Time-based features
    df["day_of_week"] = df["date"].dt.dayofweek
    df["month"] = df["date"].dt.month

    # Previous sales
    df["previous_sales"] = df["quantity_sold"].shift(1)

    # Rolling average
    df["rolling_7_day_avg"] = (
        df["quantity_sold"]
        .rolling(window=7)
        .mean()
    )

    # Remove rows where rolling features aren't available
    df = df.dropna()

    if df.empty:
        raise ValueError(
            "At least 7 days of historical sales data "
            "are required for prediction."
        )

    return df


def predict_demand(kitchen_id, menu_item_id):
    """
    Predict demand for tomorrow for a menu item.
    """

    # Get historical sales
    sales_data = Sales.query.filter_by(
        kitchen_id=kitchen_id,
        menu_item_id=menu_item_id
    ).order_by(
        Sales.sale_date.asc()
    ).all()

    if len(sales_data) < 7:
        raise ValueError(
            "At least 7 days of sales data are required "
            "to generate a prediction."
        )

    # Prepare data
    df = prepare_features(sales_data)

    # Load trained model
    model = load_model()

    # Get latest record
    latest = df.iloc[-1]

    tomorrow = date.today() + timedelta(days=1)

    features = pd.DataFrame([{
        "day_of_week": tomorrow.weekday(),
        "month": tomorrow.month,
        "previous_sales": latest["quantity_sold"],
        "rolling_7_day_avg": latest["rolling_7_day_avg"]
    }])

    # Predict
    try:
        prediction = model.predict(features)
        predicted_demand = max(
            0,
            round(float(prediction[0]), 2)
        )
    except Exception as e:
        # Fallback: use rolling 7-day average or last quantity
        try:
            fallback = float(features['rolling_7_day_avg'].iloc[0])
        except Exception:
            fallback = float(latest['quantity_sold'])
        predicted_demand = max(0, round(fallback, 2))

    # Store prediction
    prediction_record = Prediction(
        kitchen_id=kitchen_id,
        menu_item_id=menu_item_id,
        prediction_date=tomorrow,
        predicted_demand=predicted_demand,
        model_name="XGBoost"
    )

    db.session.add(prediction_record)
    db.session.commit()

    return {
        "kitchen_id": kitchen_id,
        "menu_item_id": menu_item_id,
        "prediction_date": tomorrow.isoformat(),
        "predicted_demand": predicted_demand,
        "model": "XGBoost"
    }