from flask import Blueprint, jsonify, request

from backend.services.health_score_service import HealthScoreCalculator
from backend.services.whatif_service import WhatIfAnalyzer


health_score_bp = Blueprint(
    "health_score",
    __name__,
    url_prefix="/api/health-score",
)


calculator = HealthScoreCalculator()


@health_score_bp.route("/kitchen/<int:kitchen_id>", methods=["GET"])
def get_health_score(kitchen_id):
    try:
        result = calculator.calculate(kitchen_id)
        return jsonify({"success": True, "health_score": result})
    except ValueError as error:
        return jsonify({"success": False, "message": str(error)}), 404
    except Exception as error:
        return jsonify({"success": False, "message": str(error)}), 500
