from datetime import datetime

from flask import Blueprint, request, jsonify

from backend.utils.database import db
from backend.models.sales import Sales
from backend.models.kitchen import Kitchen
from backend.models.menu import MenuItem


sales_bp = Blueprint(
    "sales",
    __name__,
    url_prefix="/api/sales"
)


# -------------------------
# Add Daily Sales
# -------------------------

@sales_bp.route("/", methods=["POST"])
def add_sales():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "No data provided."
        }), 400

    kitchen_id = data.get("kitchen_id")
    menu_item_id = data.get("menu_item_id")
    sale_date = data.get("sale_date")
    quantity_sold = data.get("quantity_sold")

    if not all([
        kitchen_id,
        menu_item_id,
        sale_date,
        quantity_sold is not None
    ]):
        return jsonify({
            "success": False,
            "message": (
                "kitchen_id, menu_item_id, sale_date "
                "and quantity_sold are required."
            )
        }), 400

    # Check kitchen
    kitchen = db.session.get(Kitchen, kitchen_id)

    if not kitchen:
        return jsonify({
            "success": False,
            "message": "Kitchen not found."
        }), 404

    # Check menu item
    menu_item = db.session.get(MenuItem, menu_item_id)

    if not menu_item:
        return jsonify({
            "success": False,
            "message": "Menu item not found."
        }), 404

    # Make sure menu item belongs to this kitchen
    if menu_item.kitchen_id != kitchen_id:
        return jsonify({
            "success": False,
            "message": "Menu item does not belong to this kitchen."
        }), 400

    # Validate date
    try:
        sale_date = datetime.strptime(
            sale_date,
            "%Y-%m-%d"
        ).date()
    except ValueError:
        return jsonify({
            "success": False,
            "message": "sale_date must be YYYY-MM-DD."
        }), 400

    # Validate quantity
    try:
        quantity_sold = float(quantity_sold)
    except (TypeError, ValueError):
        return jsonify({
            "success": False,
            "message": "quantity_sold must be a number."
        }), 400

    if quantity_sold < 0:
        return jsonify({
            "success": False,
            "message": "quantity_sold cannot be negative."
        }), 400

    # Calculate revenue from the menu item's selling price when available.
    revenue = data.get("revenue")

    if revenue is None and menu_item.price is not None:
        revenue = quantity_sold * menu_item.price

    if revenue is not None:
        try:
            revenue = float(revenue)
        except (TypeError, ValueError):
            return jsonify({
                "success": False,
                "message": "Revenue must be a number."
            }), 400

        if revenue < 0:
            return jsonify({
                "success": False,
                "message": "Revenue cannot be negative."
            }), 400

    sale = Sales(
        kitchen_id=kitchen_id,
        menu_item_id=menu_item_id,
        sale_date=sale_date,
        quantity_sold=quantity_sold,
        revenue=revenue if revenue is not None else 0
    )

    db.session.add(sale)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Sales record added successfully.",
        "sale": sale.to_dict()
    }), 201


# -------------------------
# Get Sales for Kitchen
# -------------------------

@sales_bp.route("/<int:kitchen_id>", methods=["GET"])
def get_sales(kitchen_id):

    kitchen = db.session.get(Kitchen, kitchen_id)

    if not kitchen:
        return jsonify({
            "success": False,
            "message": "Kitchen not found."
        }), 404

    sales = Sales.query.filter_by(
        kitchen_id=kitchen_id
    ).order_by(
        Sales.sale_date.desc()
    ).all()

    return jsonify({
        "success": True,
        "sales": [
            sale.to_dict()
            for sale in sales
        ]
    })


# -------------------------
# Get Sales for Menu Item
# -------------------------

@sales_bp.route(
    "/<int:kitchen_id>/item/<int:menu_item_id>",
    methods=["GET"]
)
def get_item_sales(kitchen_id, menu_item_id):

    sales = Sales.query.filter_by(
        kitchen_id=kitchen_id,
        menu_item_id=menu_item_id
    ).order_by(
        Sales.sale_date.asc()
    ).all()

    return jsonify({
        "success": True,
        "sales": [
            sale.to_dict()
            for sale in sales
        ]
    })


# -------------------------
# Delete Sales Record
# -------------------------

@sales_bp.route("/<int:sale_id>", methods=["DELETE"])
def delete_sales(sale_id):

    sale = db.session.get(Sales, sale_id)

    if not sale:
        return jsonify({
            "success": False,
            "message": "Sales record not found."
        }), 404

    db.session.delete(sale)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Sales record deleted successfully."
    })
