from flask import Blueprint, request, jsonify

from backend.utils.database import db
from backend.models.kitchen import Kitchen


kitchen_bp = Blueprint("kitchen", __name__, url_prefix="/api/kitchen")


# -------------------------
# Create Kitchen
# -------------------------

@kitchen_bp.route("/", methods=["POST"])
def create_kitchen():
    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "No data provided."
        }), 400

    name = data.get("name")

    if not name:
        return jsonify({
            "success": False,
            "message": "Kitchen name is required."
        }), 400

    kitchen = Kitchen(
        name=name,
        cuisine_type=data.get("cuisine_type"),
        seats=data.get("seats"),
        meals_per_day=data.get("meals_per_day")
    )

    db.session.add(kitchen)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Kitchen created successfully.",
        "kitchen": kitchen.to_dict()
    }), 201


# -------------------------
# Get All Kitchens
# -------------------------

@kitchen_bp.route("/", methods=["GET"])
def get_kitchens():
    kitchens = Kitchen.query.order_by(
        Kitchen.id.desc()
    ).all()

    return jsonify({
        "success": True,
        "kitchens": [
            kitchen.to_dict()
            for kitchen in kitchens
        ]
    })


# -------------------------
# Get Single Kitchen
# -------------------------

@kitchen_bp.route("/<int:kitchen_id>", methods=["GET"])
def get_kitchen(kitchen_id):
    kitchen = db.session.get(Kitchen, kitchen_id)

    if not kitchen:
        return jsonify({
            "success": False,
            "message": "Kitchen not found."
        }), 404

    return jsonify({
        "success": True,
        "kitchen": kitchen.to_dict()
    })