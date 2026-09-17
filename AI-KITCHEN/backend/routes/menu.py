import os
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify

from backend.utils.database import db
from backend.models.menu import MenuItem
from backend.models.kitchen import Kitchen
from backend.models.sales import Sales
from backend.models.prediction import Prediction
from backend.models.waste import Waste


menu_bp = Blueprint(
    "menu",
    __name__,
    url_prefix="/api/menu"
)

UPLOAD_FOLDER = os.path.join(
    os.path.dirname(__file__),
    "..",
    "..",
    "static",
    "uploads",
    "menu"
)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# -------------------------
# Add Menu Item
# -------------------------

@menu_bp.route("/", methods=["POST"])
def add_menu_item():
    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "No data provided."
        }), 400

    kitchen_id = data.get("kitchen_id")
    name = data.get("name")

    if not kitchen_id or not name:
        return jsonify({
            "success": False,
            "message": "kitchen_id and name are required."
        }), 400

    # Check whether kitchen exists
    kitchen = db.session.get(Kitchen, kitchen_id)

    if not kitchen:
        return jsonify({
            "success": False,
            "message": "Kitchen not found."
        }), 404

    try:
        price = (
            float(data["price"])
            if data.get("price") is not None
            else None
        )
        cost_per_serving = (
            float(data["cost_per_serving"])
            if data.get("cost_per_serving") is not None
            else None
        )
    except (TypeError, ValueError):
        return jsonify({
            "success": False,
            "message": "Price and cost_per_serving must be numbers."
        }), 400

    if (
        (price is not None and price < 0)
        or (
            cost_per_serving is not None
            and cost_per_serving < 0
        )
    ):
        return jsonify({
            "success": False,
            "message": "Price and cost_per_serving cannot be negative."
        }), 400

    menu_item = MenuItem(
        kitchen_id=kitchen_id,
        name=name,
        category=data.get("category"),
        price=price,
        serving_unit=data.get("serving_unit", "servings"),
        cost_per_serving=cost_per_serving,
        image_url=data.get("image_url")
    )

    db.session.add(menu_item)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Menu item added successfully.",
        "menu_item": menu_item.to_dict()
    }), 201


# -------------------------
# Upload Menu Item Image
# -------------------------

@menu_bp.route("/<int:item_id>/image", methods=["POST"])
def upload_menu_image(item_id):

    menu_item = db.session.get(MenuItem, item_id)

    if not menu_item:
        return jsonify({
            "success": False,
            "message": "Menu item not found."
        }), 404

    if "image" not in request.files:
        return jsonify({
            "success": False,
            "message": "No image file provided."
        }), 400

    file = request.files["image"]

    if file.filename == "":
        return jsonify({
            "success": False,
            "message": "No file selected."
        }), 400

    allowed_extensions = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
    _, ext = os.path.splitext(file.filename)

    if ext.lower() not in allowed_extensions:
        return jsonify({
            "success": False,
            "message": "Unsupported file type."
        }), 400

    # Validate file size (max 5 MB)
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    if file_size > 5 * 1024 * 1024:
        return jsonify({
            "success": False,
            "message": "File exceeds maximum size limit of 5 MB."
        }), 400

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    filename = f"menu_{item_id}_{timestamp}{ext.lower()}"
    save_path = os.path.join(UPLOAD_FOLDER, filename)

    file.save(save_path)

    menu_item.image_url = f"/static/uploads/menu/{filename}"
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Image uploaded successfully.",
        "image_url": menu_item.image_url,
        "menu_item": menu_item.to_dict()
    })


# -------------------------
# Get Menu Items
# -------------------------

@menu_bp.route("/<int:kitchen_id>", methods=["GET"])
def get_menu_items(kitchen_id):

    kitchen = db.session.get(Kitchen, kitchen_id)

    if not kitchen:
        return jsonify({
            "success": False,
            "message": "Kitchen not found."
        }), 404

    menu_items = MenuItem.query.filter_by(
        kitchen_id=kitchen_id
    ).order_by(
        MenuItem.id.desc()
    ).all()

    return jsonify({
        "success": True,
        "menu_items": [
            item.to_dict()
            for item in menu_items
        ]
    })


# -------------------------
# Delete Menu Item
# -------------------------

@menu_bp.route("/<int:item_id>", methods=["DELETE"])
def delete_menu_item(item_id):

    menu_item = db.session.get(MenuItem, item_id)

    if not menu_item:
        return jsonify({
            "success": False,
            "message": "Menu item not found."
        }), 404

    try:
        Prediction.query.filter_by(menu_item_id=item_id).delete()
        Sales.query.filter_by(menu_item_id=item_id).delete()
        Waste.query.filter_by(menu_item_id=item_id).update({"menu_item_id": None})

        db.session.delete(menu_item)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Menu item deleted successfully."
        })
    except Exception as error:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Failed to delete menu item: {str(error)}"
        }), 500
