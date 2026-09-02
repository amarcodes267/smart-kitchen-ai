from flask import Blueprint, request, jsonify

from ml.predict import predict_demand


prediction_bp = Blueprint(
    "prediction",
    __name__,
    url_prefix="/api/prediction"
)


@prediction_bp.route("/", methods=["POST"])
def prediction():

    try:

        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "message": "No prediction data received."
            }), 400


        # -----------------------------------------
        # Read input
        # -----------------------------------------

        week = int(
            data.get("week", 1)
        )

        center_id = int(
            data.get("center_id")
        )

        meal_id = int(
            data.get("meal_id")
        )

        checkout_price = float(
            data.get("checkout_price")
        )

        base_price = float(
            data.get("base_price")
        )

        emailer_for_promotion = int(
            data.get(
                "emailer_for_promotion",
                0
            )
        )

        homepage_featured = int(
            data.get(
                "homepage_featured",
                0
            )
        )


        # -----------------------------------------
        # Validate
        # -----------------------------------------

        if week <= 0:

            return jsonify({
                "success": False,
                "message": "Week must be greater than 0."
            }), 400


        if center_id <= 0:

            return jsonify({
                "success": False,
                "message": "Invalid center ID."
            }), 400


        if meal_id <= 0:

            return jsonify({
                "success": False,
                "message": "Invalid meal ID."
            }), 400


        if checkout_price <= 0:

            return jsonify({
                "success": False,
                "message": "Checkout price must be greater than 0."
            }), 400


        if base_price <= 0:

            return jsonify({
                "success": False,
                "message": "Base price must be greater than 0."
            }), 400


        # -----------------------------------------
        # XGBoost Prediction
        # -----------------------------------------

        predicted_demand = predict_demand(

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


        # -----------------------------------------
        # Response
        # -----------------------------------------

        return jsonify({

            "success": True,

            "prediction": {

                "predicted_demand":
                    predicted_demand,

                "model":
                    "XGBoost",

                "week":
                    week,

                "meal_id":
                    meal_id,

                "center_id":
                    center_id

            }

        })


    except ValueError as error:

        return jsonify({

            "success": False,

            "message":
                f"Invalid input: {error}"

        }), 400


    except Exception as error:

        print(
            "Prediction error:",
            error
        )

        return jsonify({

            "success": False,

            "message":
                str(error)

        }), 500