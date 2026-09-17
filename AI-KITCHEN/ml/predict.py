from pathlib import Path
from datetime import date

import joblib
import numpy as np
import pandas as pd

from .feature_config import get_feature_columns


# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = BASE_DIR / "ml" / "model.pkl"
NATIVE_MODEL_PATH = BASE_DIR / "ml" / "model.json"


# =========================================================
# FALLBACK MODEL
# =========================================================

class FallbackDemandModel:
    """Robust heuristic model used if no trained weights exist."""
    def predict(self, X):
        if isinstance(X, pd.DataFrame):
            if "previous_sales" in X.columns and "rolling_7_day_avg" in X.columns:
                base = (
                    0.2 * X.get("day_of_week", 2)
                    + 0.1 * X.get("month", 6)
                    + 0.5 * X["previous_sales"]
                    + 0.5 * X["rolling_7_day_avg"]
                )
            elif "week" in X.columns:
                base = (
                    12.0
                    + 0.25 * X["week"]
                    + 0.02 * X.get("center_id", 1)
                    + 0.004 * X.get("meal_id", 1)
                )
            else:
                base = 20.0
        else:
            base = 20.0

        arr = base.to_numpy(dtype=float) if hasattr(base, "to_numpy") else np.array([float(base)])
        return np.clip(np.round(arr), 0, None).astype(float)


# =========================================================
# LOAD MODEL
# =========================================================

def load_model():
    """Load the trained XGBoost model and canonical feature columns."""
    if not MODEL_PATH.exists():
        return FallbackDemandModel(), get_feature_columns()

    try:
        model_data = joblib.load(MODEL_PATH)
        if isinstance(model_data, dict):
            model = model_data.get("model", FallbackDemandModel())
            features = model_data.get("features", get_feature_columns())
        else:
            model = model_data
            features = get_feature_columns()
        return model, features
    except Exception as e:
        print(f"[WARN] Failed to load model from {MODEL_PATH}: {e}. Using fallback.")
        return FallbackDemandModel(), get_feature_columns()


# =========================================================
# CREATE PREDICTION FEATURES
# =========================================================

def create_prediction_features(
    day_of_week=None,
    month=None,
    previous_sales=None,
    rolling_7_day_avg=None,
    **kwargs
):
    """
    Construct a validated DataFrame matching the trained feature columns.
    Accepts both time-series features (primary) and legacy arguments (fallback).
    """
    today = date.today()

    # If time-series features provided directly
    if previous_sales is not None or rolling_7_day_avg is not None:
        try:
            dow = int(day_of_week) if day_of_week is not None else today.weekday()
            m = int(month) if month is not None else today.month
            prev = max(0.0, float(previous_sales if previous_sales is not None else (rolling_7_day_avg or 10.0)))
            roll = max(0.0, float(rolling_7_day_avg if rolling_7_day_avg is not None else prev))
        except (TypeError, ValueError) as err:
            raise ValueError(f"Invalid input values for demand prediction: {err}")

        return pd.DataFrame([{
            "day_of_week": dow,
            "month": m,
            "previous_sales": prev,
            "rolling_7_day_avg": roll
        }])

    # Legacy argument mapping for backwards compatibility
    week = kwargs.get("week", 1)
    checkout_price = kwargs.get("checkout_price", 100.0)
    try:
        week = int(week)
        checkout_price = float(checkout_price)
    except (TypeError, ValueError) as err:
        raise ValueError(f"Invalid input values for legacy demand prediction: {err}")

    mapped_dow = (week * 7) % 7
    mapped_month = ((week // 4) % 12) + 1
    mapped_prev = max(5.0, checkout_price * 0.25)
    mapped_roll = mapped_prev

    return pd.DataFrame([{
        "day_of_week": mapped_dow,
        "month": mapped_month,
        "previous_sales": mapped_prev,
        "rolling_7_day_avg": mapped_roll
    }])


# =========================================================
# PREDICT DEMAND
# =========================================================

def predict_demand(
    day_of_week=None,
    month=None,
    previous_sales=None,
    rolling_7_day_avg=None,
    **kwargs
):
    """
    Execute inference using the trained XGBoost model.
    Returns integer predicted demand rounded to the nearest serving.
    """
    model, feature_columns = load_model()

    X = create_prediction_features(
        day_of_week=day_of_week,
        month=month,
        previous_sales=previous_sales,
        rolling_7_day_avg=rolling_7_day_avg,
        **kwargs
    )

    # Ensure exact column ordering
    X = X[[c for c in feature_columns if c in X.columns]]

    try:
        prediction = model.predict(X)
        predicted_demand = float(prediction[0])
    except Exception as err:
        print(f"[WARN] Prediction failed on model: {err}. Using heuristic fallback.")
        fallback = FallbackDemandModel()
        predicted_demand = float(fallback.predict(X)[0])

    # Demand cannot be negative
    predicted_demand = max(0.0, predicted_demand)

    return int(round(predicted_demand))


if __name__ == "__main__":
    print("Testing inference with trained model...")
    res = predict_demand(day_of_week=4, month=9, previous_sales=28.0, rolling_7_day_avg=27.5)
    print(f"Predicted demand for Friday: {res} servings.")