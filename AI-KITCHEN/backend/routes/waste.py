from datetime import datetime
from flask import Blueprint, request, jsonify

from backend.utils.database import db
from backend.models.waste import Waste
from backend.models.kitchen import Kitchen
from backend.models.menu import MenuItem
from backend.services.waste_service import (
    get_waste_summary,
    get_waste_by_item,
    get_high_waste_items
)
from backend.services.waste_analytics_service import WasteAnalytics, CostOptimizer


waste_bp = Blueprint(
    "waste",
    __name__,
    url_prefix="/api/waste"
)


# -------------------------
# Add Waste Record
# -------------------------

@waste_bp.route("/", methods=["POST"])
def add_waste():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "No data provided."
        }), 400

    kitchen_id = data.get("kitchen_id")
    menu_item_id = data.get("menu_item_id")
    waste_date = data.get("waste_date")
    quantity_wasted = data.get("quantity_wasted")

    if not all([
        kitchen_id,
        waste_date,
        quantity_wasted is not None
    ]):
        return jsonify({
            "success": False,
            "message": (
                "kitchen_id, waste_date and "
                "quantity_wasted are required."
            )
        }), 400

    kitchen = db.session.get(Kitchen, kitchen_id)

    if not kitchen:
        return jsonify({
            "success": False,
            "message": "Kitchen not found."
        }), 404

    menu_item = None

    if menu_item_id:

        menu_item = db.session.get(
            MenuItem,
            menu_item_id
        )

        if not menu_item:
            return jsonify({
                "success": False,
                "message": "Menu item not found."
            }), 404

        if menu_item.kitchen_id != kitchen_id:
            return jsonify({
                "success": False,
                "message": (
                    "Menu item does not belong "
                    "to this kitchen."
                )
            }), 400

    try:

        waste_date = datetime.strptime(
            waste_date,
            "%Y-%m-%d"
        ).date()

    except ValueError:

        return jsonify({
            "success": False,
            "message": "waste_date must be YYYY-MM-DD."
        }), 400

    try:

        quantity_wasted = float(
            quantity_wasted
        )

    except (TypeError, ValueError):

        return jsonify({
            "success": False,
            "message": (
                "quantity_wasted must be a number."
            )
        }), 400

    if quantity_wasted < 0:

        return jsonify({
            "success": False,
            "message": (
                "quantity_wasted cannot be negative."
            )
        }), 400

    estimated_cost = data.get(
        "estimated_cost"
    )

    if (
        estimated_cost is None
        and menu_item
        and menu_item.cost_per_serving
    ):

        estimated_cost = (
            quantity_wasted
            * menu_item.cost_per_serving
        )

    if estimated_cost is not None:
        try:
            estimated_cost = float(estimated_cost)
        except (TypeError, ValueError):
            return jsonify({
                "success": False,
                "message": "Estimated cost must be a number."
            }), 400

        if estimated_cost < 0:
            return jsonify({
                "success": False,
                "message": "Estimated cost cannot be negative."
            }), 400

    waste = Waste(

        kitchen_id=kitchen_id,

        menu_item_id=menu_item_id,

        waste_date=waste_date,

        quantity_wasted=quantity_wasted,

        unit=data.get(
            "unit",
            "servings"
        ),

        reason=data.get(
            "reason"
        ),

        estimated_cost=(
            estimated_cost
            if estimated_cost is not None
            else 0
        )
    )

    db.session.add(waste)

    db.session.commit()

    return jsonify({

        "success": True,

        "message": (
            "Waste record added successfully."
        ),

        "waste": waste.to_dict()
    }), 201


# -------------------------
# Get Waste Records
# -------------------------

@waste_bp.route(
    "/<int:kitchen_id>",
    methods=["GET"]
)
def get_waste(kitchen_id):

    kitchen = db.session.get(
        Kitchen,
        kitchen_id
    )

    if not kitchen:

        return jsonify({
            "success": False,
            "message": "Kitchen not found."
        }), 404

    waste_records = (
        Waste.query
        .filter_by(
            kitchen_id=kitchen_id
        )
        .order_by(
            Waste.waste_date.desc()
        )
        .all()
    )

    return jsonify({

        "success": True,

        "waste": [
            record.to_dict()
            for record in waste_records
        ]
    })


# -------------------------
# Waste Summary
# -------------------------

@waste_bp.route(
    "/<int:kitchen_id>/summary",
    methods=["GET"]
)
def waste_summary(kitchen_id):

    kitchen = db.session.get(
        Kitchen,
        kitchen_id
    )

    if not kitchen:

        return jsonify({
            "success": False,
            "message": "Kitchen not found."
        }), 404

    summary = get_waste_summary(
        kitchen_id
    )

    return jsonify({

        "success": True,

        "summary": summary
    })


# -------------------------
# Waste By Food Item
# -------------------------

@waste_bp.route(
    "/<int:kitchen_id>/by-item",
    methods=["GET"]
)
def waste_by_item(kitchen_id):

    kitchen = db.session.get(
        Kitchen,
        kitchen_id
    )

    if not kitchen:

        return jsonify({
            "success": False,
            "message": "Kitchen not found."
        }), 404

    waste_items = get_waste_by_item(
        kitchen_id
    )

    return jsonify({

        "success": True,

        "waste_by_item": waste_items
    })


# -------------------------
# Highest Waste Items
# -------------------------

@waste_bp.route(
    "/<int:kitchen_id>/high-waste",
    methods=["GET"]
)
def high_waste_items(kitchen_id):

    kitchen = db.session.get(
        Kitchen,
        kitchen_id
    )

    if not kitchen:

        return jsonify({
            "success": False,
            "message": "Kitchen not found."
        }), 404

    limit = request.args.get(
        "limit",
        5,
        type=int
    )

    items = get_high_waste_items(
        kitchen_id,
        limit
    )

    return jsonify({

        "success": True,

        "high_waste_items": items
    })


# -------------------------
# Delete Waste Record
# -------------------------

@waste_bp.route(
    "/<int:waste_id>",
    methods=["DELETE"]
)
def delete_waste(waste_id):

    waste = db.session.get(
        Waste,
        waste_id
    )

    if not waste:

        return jsonify({
            "success": False,
            "message": (
                "Waste record not found."
            )
        }), 404

    try:
        db.session.delete(waste)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": (
                "Waste record deleted successfully."
            )
        })
    except Exception as error:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Failed to delete waste record: {str(error)}"
        }), 500


# -------------------------
# Waste Analytics
# -------------------------

@waste_bp.route(
    "/<int:kitchen_id>/analytics",
    methods=["GET"]
)
def waste_analytics(kitchen_id):
    try:
        days = int(request.args.get("days", 30))
        days = max(1, min(days, 365))
    except (TypeError, ValueError):
        days = 30

    try:
        analytics = WasteAnalytics()
        result = analytics.analyze_kitchen_waste(kitchen_id, days)
        return jsonify({"success": True, "analytics": result})
    except ValueError as error:
        return jsonify({"success": False, "message": str(error)}), 404
    except Exception as error:
        return jsonify({"success": False, "message": str(error)}), 500


# -------------------------
# Cost Optimization
# -------------------------

@waste_bp.route(
    "/<int:kitchen_id>/costs",
    methods=["GET"]
)
def cost_optimization(kitchen_id):
    try:
        days = int(request.args.get("days", 30))
        days = max(1, min(days, 365))
    except (TypeError, ValueError):
        days = 30

    try:
        optimizer = CostOptimizer()
        result = optimizer.analyze_costs(kitchen_id, days)
        return jsonify({"success": True, "costs": result})
    except ValueError as error:
        return jsonify({"success": False, "message": str(error)}), 404
    except Exception as error:
        return jsonify({"success": False, "message": str(error)}), 500
