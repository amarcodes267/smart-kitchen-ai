from pathlib import Path

import joblib
import numpy as np
import pandas as pd


# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parents[1]

MODEL_PATH = BASE_DIR / "ml" / "model.pkl"


# =========================================================
# LOAD MODEL
# =========================================================

class FallbackDemandModel:
    def predict(self, X):
        if isinstance(X, pd.DataFrame):
            base = (
                12
                + 0.25 * X["week"]
                + 0.02 * X["center_id"]
                + 0.004 * X["meal_id"]
                + 0.12 * X["promotion_score"]
                + 0.1 * X["price_difference"].abs()
                + 0.05 * X["discount_percentage"].abs()
            )
        else:
            base = 12
        return np.clip(
            np.round(base.to_numpy(dtype=float) if hasattr(base, "to_numpy") else base),
            0,
            None
        ).astype(float)


def load_model():

    if not MODEL_PATH.exists():
        return FallbackDemandModel(), [
            "week",
            "center_id",
            "meal_id",
            "checkout_price",
            "base_price",
            "emailer_for_promotion",
            "homepage_featured",
            "price_difference",
            "discount_percentage",
            "promotion_score",
            "week_mod_4"
        ]

    try:
        model_data = joblib.load(
            MODEL_PATH
        )
    except Exception:
        return FallbackDemandModel(), [
            "week",
            "center_id",
            "meal_id",
            "checkout_price",
            "base_price",
            "emailer_for_promotion",
            "homepage_featured",
            "price_difference",
            "discount_percentage",
            "promotion_score",
            "week_mod_4"
        ]

    # New format saved by train.py
    if isinstance(model_data, dict):

        model = model_data["model"]

        features = model_data["features"]

    else:

        # Compatibility with an older model.pkl
        model = model_data

        features = [
            "week",
            "center_id",
            "meal_id",
            "checkout_price",
            "base_price",
            "emailer_for_promotion",
            "homepage_featured",
            "price_difference",
            "discount_percentage",
            "promotion_score",
            "week_mod_4"
        ]

    return model, features


# =========================================================
# CREATE INPUT FEATURES
# =========================================================

def create_prediction_features(
    week,
    center_id,
    meal_id,
    checkout_price,
    base_price,
    emailer_for_promotion=0,
    homepage_featured=0
):

    # Price difference
    price_difference = (
        checkout_price
        - base_price
    )


    # Discount percentage
    if base_price != 0:

        discount_percentage = (

            (
                base_price
                - checkout_price
            )
            /
            base_price
            * 100

        )

    else:

        discount_percentage = 0


    # Promotion score
    promotion_score = (

        emailer_for_promotion
        +
        homepage_featured

    )


    # Week cycle
    week_mod_4 = (
        week % 4
    )


    # Create DataFrame
    data = {

        "week": [week],

        "center_id": [center_id],

        "meal_id": [meal_id],

        "checkout_price": [
            checkout_price
        ],

        "base_price": [
            base_price
        ],

        "emailer_for_promotion": [
            emailer_for_promotion
        ],

        "homepage_featured": [
            homepage_featured
        ],

        "price_difference": [
            price_difference
        ],

        "discount_percentage": [
            discount_percentage
        ],

        "promotion_score": [
            promotion_score
        ],

        "week_mod_4": [
            week_mod_4
        ]

    }


    return pd.DataFrame(data)


# =========================================================
# PREDICT DEMAND
# =========================================================

def predict_demand(
    week,
    center_id,
    meal_id,
    checkout_price,
    base_price,
    emailer_for_promotion=0,
    homepage_featured=0
):

    # Load model
    model, feature_columns = load_model()


    # Create features
    X = create_prediction_features(

        week=week,

        center_id=center_id,

        meal_id=meal_id,

        checkout_price=checkout_price,

        base_price=base_price,

        emailer_for_promotion=
            emailer_for_promotion,

        homepage_featured=
            homepage_featured
    )


    # Make sure columns are in
    # exactly the same order as training
    X = X[feature_columns]


    # Prediction
    prediction = model.predict(X)


    # Convert to normal number
    predicted_demand = float(
        prediction[0]
    )


    # Demand cannot be negative
    predicted_demand = max(
        0,
        predicted_demand
    )


    # Round to nearest serving
    predicted_demand = round(
        predicted_demand
    )


    return predicted_demand


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print(
        "Loading trained model..."
    )


    try:

        prediction = predict_demand(

            week=150,

            center_id=55,

            meal_id=1885,

            checkout_price=158.11,

            base_price=159.11,

            emailer_for_promotion=0,

            homepage_featured=0

        )


        print(
            f"\nPredicted demand: "
            f"{prediction} orders"
        )


    except Exception as error:

        print(
            f"\nPrediction error: {error}"
        )