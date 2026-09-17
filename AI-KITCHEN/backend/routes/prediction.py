from flask import Blueprint, request, jsonify

from backend.services.demand_service import DemandAnalyzer
from backend.services.gemini_service import generate_prediction_explanation


prediction_bp = Blueprint(
    "prediction",
    __name__,
    url_prefix="/api/prediction"
)


analyzer = DemandAnalyzer()


@prediction_bp.route("/", methods=["POST"])
def prediction():

    try:

        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "message": "No prediction data received."
            }), 400

        kitchen_id = int(data.get("kitchen_id") or data.get("center_id", 0))
        menu_item_id = int(data.get("menu_item_id") or data.get("meal_id", 0))

        if kitchen_id <= 0 or menu_item_id <= 0:
            return jsonify({
                "success": False,
                "message": "kitchen_id and menu_item_id are required."
            }), 400

        item = None
        try:
            demand = analyzer.analyze_kitchen_demand(kitchen_id, days=30)
            item = next(
                (i for i in demand["items"] if i["menu_item_id"] == menu_item_id),
                None,
            )
        except Exception:
            item = None

        if not item:
            if "checkout_price" in data:
                try:
                    from ml.predict import predict_demand
                    legacy_pred = predict_demand(
                        week=int(data.get("week", 1)),
                        center_id=kitchen_id,
                        meal_id=menu_item_id,
                        checkout_price=float(data.get("checkout_price", 100)),
                        base_price=float(data.get("base_price", data.get("checkout_price", 100))),
                        emailer_for_promotion=int(data.get("emailer_for_promotion", 0)),
                        homepage_featured=int(data.get("homepage_featured", 0))
                    )
                    explanation_data = generate_prediction_explanation(
                        item_name=f"Meal #{menu_item_id}",
                        predicted_demand=legacy_pred,
                        trend="stable",
                        trend_symbol="→",
                        change_pct=0.0,
                        previous_avg=legacy_pred,
                        recent_avg=legacy_pred,
                    )
                    return jsonify({
                        "success": True,
                        "prediction": {
                            "predicted_demand": legacy_pred,
                            "model": "XGBoost",
                            "kitchen_id": kitchen_id,
                            "menu_item_id": menu_item_id,
                            "item_name": f"Meal #{menu_item_id}",
                            "trend": "stable",
                            "trend_symbol": "→",
                            "change_pct": 0.0,
                            "previous_avg": legacy_pred,
                            "recent_avg": legacy_pred,
                            "ai_explanation": explanation_data["explanation"],
                            "kitchen_recommendation": explanation_data["kitchen_recommendation"],
                            "recommended_prep": explanation_data["recommended_prep"],
                            "safety_buffer": explanation_data["safety_buffer_units"],
                        }
                    })
                except Exception:
                    pass

            from backend.models.menu import MenuItem
            from backend.models.sales import Sales
            from backend.models.prediction import Prediction
            from backend.utils.database import db
            from ml.predict import load_model
            from datetime import date, timedelta
            import numpy as np
            import pandas as pd

            menu_item = db.session.get(MenuItem, menu_item_id)
            if not menu_item:
                return jsonify({
                    "success": False,
                    "message": "Menu item not found."
                }), 404

            # Check if there are any all-time sales for this item
            all_sales = (
                Sales.query
                .filter(Sales.kitchen_id == kitchen_id, Sales.menu_item_id == menu_item_id)
                .order_by(Sales.sale_date.asc())
                .all()
            )

            tomorrow = date.today() + timedelta(days=1)

            if all_sales:
                prev_sales = float(all_sales[-1].quantity_sold)
                rolling_avg = float(np.mean([s.quantity_sold for s in all_sales[-7:]]))
            else:
                kitchen_sales = Sales.query.filter_by(kitchen_id=kitchen_id).all()
                if kitchen_sales:
                    prev_sales = float(np.mean([s.quantity_sold for s in kitchen_sales[-14:]]))
                    rolling_avg = prev_sales
                else:
                    prev_sales = 20.0
                    rolling_avg = 20.0

            features = pd.DataFrame([{
                "day_of_week": tomorrow.weekday(),
                "month": tomorrow.month,
                "previous_sales": prev_sales,
                "rolling_7_day_avg": rolling_avg,
            }])

            model, feature_cols = load_model()
            features = features[[c for c in feature_cols if c in features.columns]]
            predicted_demand = round(max(0.0, float(model.predict(features)[0])), 1)

            pred_record = Prediction(
                kitchen_id=kitchen_id,
                menu_item_id=menu_item_id,
                prediction_date=tomorrow,
                predicted_demand=predicted_demand,
                model_name="XGBoost",
            )
            db.session.add(pred_record)
            db.session.commit()

            item_name = menu_item.name if menu_item else f"Item {menu_item_id}"
            explanation_data = generate_prediction_explanation(
                item_name=item_name,
                predicted_demand=predicted_demand,
                trend="stable",
                trend_symbol="→",
                change_pct=0.0,
                previous_avg=round(prev_sales, 1),
                recent_avg=round(rolling_avg, 1),
            )

            return jsonify({
                "success": True,
                "prediction": {
                    "predicted_demand": predicted_demand,
                    "model": "XGBoost",
                    "kitchen_id": kitchen_id,
                    "menu_item_id": menu_item_id,
                    "item_name": item_name,
                    "trend": "stable",
                    "trend_symbol": "→",
                    "change_pct": 0.0,
                    "previous_avg": round(prev_sales, 1),
                    "recent_avg": round(rolling_avg, 1),
                    "ai_explanation": explanation_data["explanation"],
                    "kitchen_recommendation": explanation_data["kitchen_recommendation"],
                    "recommended_prep": explanation_data["recommended_prep"],
                    "safety_buffer": explanation_data["safety_buffer_units"],
                }
            })

        explanation_data = generate_prediction_explanation(
            item_name=item["name"],
            predicted_demand=item["predicted_demand_tomorrow"],
            trend=item["trend"],
            trend_symbol=item["trend_symbol"],
            change_pct=item["change_pct"],
            previous_avg=item["previous_avg"],
            recent_avg=item["recent_avg"],
        )

        return jsonify({

            "success": True,

            "prediction": {

                "predicted_demand":
                    item["predicted_demand_tomorrow"],

                "model":
                    "XGBoost",

                "kitchen_id":
                    kitchen_id,

                "menu_item_id":
                    menu_item_id,

                "item_name":
                    item["name"],

                "trend":
                    item["trend"],

                "trend_symbol":
                    item["trend_symbol"],

                "change_pct":
                    item["change_pct"],

                "previous_avg":
                    item["previous_avg"],

                "recent_avg":
                    item["recent_avg"],

                "ai_explanation":
                    explanation_data["explanation"],

                "kitchen_recommendation":
                    explanation_data["kitchen_recommendation"],

                "recommended_prep":
                    explanation_data["recommended_prep"],

                "safety_buffer":
                    explanation_data["safety_buffer_units"],

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