from flask import Blueprint, jsonify

from backend.models.alert import Alert
from backend.models.kitchen import Kitchen
from backend.utils.database import db
from backend.services.recommendation_engine_service import RecommendationEngine


alerts_bp = Blueprint(
    "alerts",
    __name__,
    url_prefix="/api/alerts",
)


@alerts_bp.route("/kitchen/<int:kitchen_id>", methods=["GET"])
def get_alerts(kitchen_id):
    kitchen = db.session.get(Kitchen, kitchen_id)
    if not kitchen:
        return jsonify({"success": False, "message": "Kitchen not found."}), 404

    # Automatically generate alerts if none exist yet
    alert_count = Alert.query.filter_by(kitchen_id=kitchen_id).count()
    if alert_count == 0:
        try:
            re = RecommendationEngine()
            re.generate_dashboard_recommendations(kitchen_id)
        except Exception as e:
            print(f"[WARN] Failed to auto-generate alerts: {e}")

    alerts = (
        Alert.query
        .filter_by(kitchen_id=kitchen_id)
        .order_by(Alert.created_at.desc())
        .limit(50)
        .all()
    )

    return jsonify({
        "success": True,
        "alerts": [a.to_dict() for a in alerts],
    })


@alerts_bp.route("/kitchen/<int:kitchen_id>/refresh", methods=["POST"])
def refresh_alerts(kitchen_id):
    kitchen = db.session.get(Kitchen, kitchen_id)
    if not kitchen:
        return jsonify({"success": False, "message": "Kitchen not found."}), 404

    try:
        re = RecommendationEngine()
        re.generate_dashboard_recommendations(kitchen_id)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    alerts = (
        Alert.query
        .filter_by(kitchen_id=kitchen_id)
        .order_by(Alert.created_at.desc())
        .limit(50)
        .all()
    )

    return jsonify({
        "success": True,
        "message": "Alerts refreshed successfully.",
        "alerts": [a.to_dict() for a in alerts],
    })


@alerts_bp.route("/kitchen/<int:kitchen_id>/read", methods=["POST"])
def mark_alerts_read(kitchen_id):
    kitchen = db.session.get(Kitchen, kitchen_id)
    if not kitchen:
        return jsonify({"success": False, "message": "Kitchen not found."}), 404

    Alert.query.filter_by(kitchen_id=kitchen_id, is_read=False).update({"is_read": True})
    db.session.commit()

    return jsonify({"success": True, "message": "Alerts marked as read."})
