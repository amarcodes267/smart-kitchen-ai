from pathlib import Path

import pandas as pd

from flask import Blueprint, jsonify


data_bp = Blueprint(
    "data",
    __name__,
    url_prefix="/api/data"
)


# =========================================================
# DATASET PATH
# =========================================================

BASE_DIR = Path(__file__).resolve().parents[2]

TRAIN_PATH = (
    BASE_DIR
    / "data"
    / "raw"
    / "kitchen_data.csv"
)


# =========================================================
# LOAD DATA
# =========================================================

def load_dataset():

    if not TRAIN_PATH.exists():

        raise FileNotFoundError(
            f"kitchen_data.csv not found at {TRAIN_PATH}"
        )

    return pd.read_csv(
        TRAIN_PATH
    )


# =========================================================
# GET MEALS
# =========================================================

@data_bp.route(
    "/meals",
    methods=["GET"]
)
def get_meals():

    try:

        df = load_dataset()


        meals = (
            df[
                [
                    "meal_id",
                    "checkout_price",
                    "base_price"
                ]
            ]
            .drop_duplicates(
                subset=["meal_id"]
            )
            .sort_values(
                "meal_id"
            )
        )


        result = []


        for _, row in meals.iterrows():

            result.append({

                "meal_id":
                    int(row["meal_id"]),

                "checkout_price":
                    float(
                        row["checkout_price"]
                    ),

                "base_price":
                    float(
                        row["base_price"]
                    )

            })


        return jsonify({

            "success": True,

            "meals": result

        })


    except Exception as error:

        print(
            "Meal data error:",
            error
        )


        return jsonify({

            "success": False,

            "message":
                str(error)

        }), 500


# =========================================================
# GET CENTERS
# =========================================================

@data_bp.route(
    "/centers",
    methods=["GET"]
)
def get_centers():

    try:

        df = load_dataset()


        centers = (
            df["center_id"]
            .drop_duplicates()
            .sort_values()
        )


        result = [

            int(center)

            for center in centers

        ]


        return jsonify({

            "success": True,

            "centers": result

        })


    except Exception as error:

        print(
            "Center data error:",
            error
        )


        return jsonify({

            "success": False,

            "message":
                str(error)

        }), 500
