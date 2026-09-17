from flask import Blueprint, jsonify, request

from backend.services.whatif_service import WhatIfAnalyzer
from backend.services.recommendation_engine_service import RecommendationEngine


whatif_bp = Blueprint(
    "whatif",
    __name__,
    url_prefix="/api/whatif",
)


whatif = WhatIfAnalyzer()
engine = RecommendationEngine()


@whatif_bp.route("/demand-increase", methods=["POST"])
def demand_increase():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "No data provided."}), 400

    kitchen_id = data.get("kitchen_id")
    menu_item_id = data.get("menu_item_id")
    increase_pct = data.get("increase_pct", 20)
    try:
        kitchen_id = int(data.get("kitchen_id"))
        menu_item_id = int(data.get("menu_item_id"))
    except (TypeError, ValueError):
        return jsonify({"success": False, "message": "kitchen_id and menu_item_id must be valid integers."}), 400

    if not kitchen_id or not menu_item_id:
        return jsonify({"success": False, "message": "kitchen_id and menu_item_id are required."}), 400
    try:
        increase_pct = float(data.get("increase_pct", 20))
    except (TypeError, ValueError):
        return jsonify({"success": False, "message": "increase_pct must be a number."}), 400

    try:
        result = whatif.demand_increase(kitchen_id, menu_item_id, float(increase_pct))
        result = whatif.demand_increase(kitchen_id, menu_item_id, increase_pct)
        return jsonify({"success": True, "analysis": result})
    except ValueError as error:
        return jsonify({"success": False, "message": str(error)}), 400
    except Exception as error:
        return jsonify({"success": False, "message": str(error)}), 500


@whatif_bp.route("/preparation-reduction", methods=["POST"])
def preparation_reduction():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "No data provided."}), 400

    kitchen_id = data.get("kitchen_id")
    menu_item_id = data.get("menu_item_id")
    reduction_pct = data.get("reduction_pct", 10)
    try:
        kitchen_id = int(data.get("kitchen_id"))
        menu_item_id = int(data.get("menu_item_id"))
    except (TypeError, ValueError):
        return jsonify({"success": False, "message": "kitchen_id and menu_item_id must be valid integers."}), 400

    if not kitchen_id or not menu_item_id:
        return jsonify({"success": False, "message": "kitchen_id and menu_item_id are required."}), 400
    try:
        reduction_pct = float(data.get("reduction_pct", 10))
    except (TypeError, ValueError):
        return jsonify({"success": False, "message": "reduction_pct must be a number."}), 400

    try:
        result = whatif.preparation_reduction(kitchen_id, menu_item_id, float(reduction_pct))
        result = whatif.preparation_reduction(kitchen_id, menu_item_id, reduction_pct)
        return jsonify({"success": True, "analysis": result})
    except ValueError as error:
        return jsonify({"success": False, "message": str(error)}), 400
    except Exception as error:
        return jsonify({"success": False, "message": str(error)}), 500


@whatif_bp.route("/dashboard-recommendations/kitchen/<int:kitchen_id>", methods=["GET"])
def get_dashboard_recommendations(kitchen_id):
    try:
        result = engine.generate_dashboard_recommendations(kitchen_id)
        return jsonify({"success": True, "recommendations": result})
    except ValueError as error:
        return jsonify({"success": False, "message": str(error)}), 404
    except Exception as error:
        return jsonify({"success": False, "message": str(error)}), 500
