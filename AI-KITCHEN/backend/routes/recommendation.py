from flask import Blueprint, request, jsonify

from backend.services.prediction_service import predict_demand
from backend.services.optimization_service import (
    get_recommended_preparation
)


recommendation_bp = Blueprint(
    "recommendation",
    __name__,
    url_prefix="/api/recommendation"
)


# -------------------------
# Generate Recommendation
# -------------------------

@recommendation_bp.route("/", methods=["POST"])
def generate_recommendation():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "No data provided."
        }), 400

    kitchen_id = data.get("kitchen_id")
    menu_item_id = data.get("menu_item_id")

    if not kitchen_id or not menu_item_id:
        return jsonify({
            "success": False,
            "message": (
                "kitchen_id and menu_item_id "
                "are required."
            )
        }), 400

    try:

        # --------------------------------
        # Step 1: Predict future demand
        # --------------------------------

        prediction = predict_demand(
            kitchen_id=kitchen_id,
            menu_item_id=menu_item_id
        )

        predicted_demand = prediction[
            "predicted_demand"
        ]

        # --------------------------------
        # Step 2: Optimize preparation
        # --------------------------------

        recommendation = (
            get_recommended_preparation(
                kitchen_id=kitchen_id,
                menu_item_id=menu_item_id,
                predicted_demand=predicted_demand
            )
        )

        return jsonify({
            "success": True,
            "recommendation": recommendation
        })

    except ValueError as error:

        return jsonify({
            "success": False,
            "message": str(error)
        }), 400

    except FileNotFoundError as error:

        return jsonify({
            "success": False,
            "message": str(error)
        }), 500

    except Exception as error:

        return jsonify({
            "success": False,
            "message": (
                "Unable to generate recommendation."
            ),
            "error": str(error)
        }), 500