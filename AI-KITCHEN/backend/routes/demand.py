from flask import Blueprint, jsonify, request

from backend.services.demand_service import DemandAnalyzer, WeeklyForecast
from backend.services.trend_analysis_service import TrendAnalyzer


demand_bp = Blueprint(
    "demand",
    __name__,
    url_prefix="/api/demand",
)


analyzer = DemandAnalyzer()
forecaster = WeeklyForecast()
trend_analyzer = TrendAnalyzer()


@demand_bp.route("/kitchen/<int:kitchen_id>", methods=["GET"])
def get_kitchen_demand(kitchen_id):
    try:
        days = int(request.args.get("days", 30))
        days = max(1, min(days, 365))
    except (TypeError, ValueError):
        days = 30

    try:
        result = analyzer.analyze_kitchen_demand(kitchen_id, days)
        return jsonify({"success": True, "demand": result})
    except ValueError as error:
        return jsonify({"success": False, "message": str(error)}), 404
    except Exception as error:
        return jsonify({"success": False, "message": str(error)}), 500


@demand_bp.route("/kitchen/<int:kitchen_id>/weekly", methods=["GET"])
@demand_bp.route("/kitchen/<int:kitchen_id>/forecast", methods=["GET"])
def get_weekly_forecast(kitchen_id):
    try:
        days = int(request.args.get("days", 7))
        days = max(1, min(days, 30))
    except (TypeError, ValueError):
        days = 7

    try:
        result = forecaster.forecast_kitchen(kitchen_id, days)
        return jsonify({"success": True, "forecast": result})
    except ValueError as error:
        return jsonify({"success": False, "message": str(error)}), 404
    except Exception as error:
        return jsonify({"success": False, "message": str(error)}), 500


@demand_bp.route("/kitchen/<int:kitchen_id>/trends", methods=["GET"])
def get_kitchen_trends(kitchen_id):
    try:
        window = int(request.args.get("window", 28))
        window = max(7, min(window, 365))
    except (TypeError, ValueError):
        window = 28

    try:
        result = trend_analyzer.analyze_kitchen_trends(kitchen_id, window)
        return jsonify({"success": True, "trends": result})
    except ValueError as error:
        return jsonify({"success": False, "message": str(error)}), 404
    except Exception as error:
        return jsonify({"success": False, "message": str(error)}), 500


@demand_bp.route("/kitchen/<int:kitchen_id>/item/<int:menu_item_id>/trend", methods=["GET"])
def get_item_trend(kitchen_id, menu_item_id):
    try:
        window = int(request.args.get("window", 28))
        window = max(7, min(window, 365))
    except (TypeError, ValueError):
        window = 28

    try:
        result = trend_analyzer.analyze_item_trend(kitchen_id, menu_item_id, window)
        return jsonify({"success": True, "trend": result})
    except ValueError as error:
        return jsonify({"success": False, "message": str(error)}), 404
    except Exception as error:
        return jsonify({"success": False, "message": str(error)}), 500
