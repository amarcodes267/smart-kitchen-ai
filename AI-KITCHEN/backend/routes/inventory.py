from datetime import datetime

from flask import Blueprint, request, jsonify

from backend.utils.database import db
from backend.models.inventory import Inventory
from backend.models.kitchen import Kitchen


inventory_bp = Blueprint(
    "inventory",
    __name__,
    url_prefix="/api/inventory"
)


# -------------------------
# Add Inventory Item
# -------------------------

@inventory_bp.route("/", methods=["POST"])
def add_inventory():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "No data provided."
        }), 400

    kitchen_id = data.get("kitchen_id")
    ingredient_name = data.get("ingredient_name")
    quantity = data.get("quantity")

    if not kitchen_id or not ingredient_name or quantity is None:
        return jsonify({
            "success": False,
            "message": "kitchen_id, ingredient_name and quantity are required."
        }), 400

    # Check kitchen
    kitchen = db.session.get(Kitchen, kitchen_id)

    if not kitchen:
        return jsonify({
            "success": False,
            "message": "Kitchen not found."
        }), 404

    try:
        quantity = float(quantity)
    except (TypeError, ValueError):
        return jsonify({
            "success": False,
            "message": "Quantity must be a number."
        }), 400

    if quantity < 0:
        return jsonify({
            "success": False,
            "message": "Quantity cannot be negative."
        }), 400

    try:
        minimum_stock = float(data.get("minimum_stock", 0))
    except (TypeError, ValueError):
        return jsonify({
            "success": False,
            "message": "Minimum stock must be a number."
        }), 400

    if minimum_stock < 0:
        return jsonify({
            "success": False,
            "message": "Minimum stock cannot be negative."
        }), 400

    expiry_date = None

    if data.get("expiry_date"):
        try:
            expiry_date = datetime.strptime(
                data["expiry_date"],
                "%Y-%m-%d"
            ).date()
        except ValueError:
            return jsonify({
                "success": False,
                "message": "Expiry date must be YYYY-MM-DD."
            }), 400

    inventory = Inventory(
        kitchen_id=kitchen_id,
        ingredient_name=ingredient_name,
        quantity=quantity,
        unit=data.get("unit", "kg"),
        minimum_stock=minimum_stock,
        expiry_date=expiry_date
    )

    db.session.add(inventory)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Inventory item added successfully.",
        "inventory": inventory.to_dict()
    }), 201


# -------------------------
# Get Kitchen Inventory
# -------------------------

@inventory_bp.route("/<int:kitchen_id>", methods=["GET"])
def get_inventory(kitchen_id):

    kitchen = db.session.get(Kitchen, kitchen_id)

    if not kitchen:
        return jsonify({
            "success": False,
            "message": "Kitchen not found."
        }), 404

    inventory = Inventory.query.filter_by(
        kitchen_id=kitchen_id
    ).order_by(
        Inventory.ingredient_name.asc()
    ).all()

    return jsonify({
        "success": True,
        "inventory": [
            item.to_dict()
            for item in inventory
        ]
    })


# -------------------------
# Update Inventory
# -------------------------

@inventory_bp.route("/<int:item_id>", methods=["PUT"])
def update_inventory(item_id):

    inventory = db.session.get(Inventory, item_id)

    if not inventory:
        return jsonify({
            "success": False,
            "message": "Inventory item not found."
        }), 404

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "No data provided."
        }), 400

    if "quantity" in data:
        try:
            quantity = float(data["quantity"])

            if quantity < 0:
                return jsonify({
                    "success": False,
                    "message": "Quantity cannot be negative."
                }), 400

            inventory.quantity = quantity

        except (TypeError, ValueError):
            return jsonify({
                "success": False,
                "message": "Quantity must be a number."
            }), 400

    if "ingredient_name" in data:
        ingredient_name = str(data["ingredient_name"]).strip()
        if not ingredient_name:
            return jsonify({
                "success": False,
                "message": "Ingredient name cannot be empty."
            }), 400
        inventory.ingredient_name = ingredient_name

    if "minimum_stock" in data:
        try:
            minimum_stock = float(data["minimum_stock"])
        except (TypeError, ValueError):
            return jsonify({
                "success": False,
                "message": "Minimum stock must be a number."
            }), 400

        if minimum_stock < 0:
            return jsonify({
                "success": False,
                "message": "Minimum stock cannot be negative."
            }), 400

        inventory.minimum_stock = minimum_stock

    if "unit" in data:
        inventory.unit = data["unit"]

    if "expiry_date" in data:
        if data["expiry_date"]:
            try:
                inventory.expiry_date = datetime.strptime(
                    data["expiry_date"],
                    "%Y-%m-%d"
                ).date()
            except ValueError:
                return jsonify({
                    "success": False,
                    "message": "Expiry date must be YYYY-MM-DD."
                }), 400
        else:
            inventory.expiry_date = None

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Inventory updated successfully.",
        "inventory": inventory.to_dict()
    })


# -------------------------
# Delete Inventory Item
# -------------------------

@inventory_bp.route("/<int:item_id>", methods=["DELETE"])
def delete_inventory(item_id):

    inventory = db.session.get(Inventory, item_id)

    if not inventory:
        return jsonify({
            "success": False,
            "message": "Inventory item not found."
        }), 404

    db.session.delete(inventory)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Inventory item deleted successfully."
    })
