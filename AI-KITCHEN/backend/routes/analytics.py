from flask import Blueprint, jsonify, request

from backend.services.sales_analytics_service import SalesAnalytics, MenuIntelligence


analytics_bp = Blueprint(
    "analytics",
    __name__,
    url_prefix="/api/analytics",
)


sales_analyzer = SalesAnalytics()
menu_intel = MenuIntelligence()


@analytics_bp.route("/sales/kitchen/<int:kitchen_id>", methods=["GET"])
def get_sales_analytics(kitchen_id):
    try:
        days = int(request.args.get("days", 30))
        days = max(1, min(days, 365))
    except (TypeError, ValueError):
        days = 30

    try:
        result = sales_analyzer.analyze_kitchen_sales(kitchen_id, days)
        return jsonify({"success": True, "analytics": result})
    except ValueError as error:
        return jsonify({"success": False, "message": str(error)}), 404
    except Exception as error:
        return jsonify({"success": False, "message": str(error)}), 500


@analytics_bp.route("/menu/kitchen/<int:kitchen_id>", methods=["GET"])
def get_menu_analytics(kitchen_id):
    try:
        result = menu_intel.analyze_menu(kitchen_id)
        return jsonify({"success": True, "analytics": result})
    except ValueError as error:
        return jsonify({"success": False, "message": str(error)}), 404
    except Exception as error:
        return jsonify({"success": False, "message": str(error)}), 500
