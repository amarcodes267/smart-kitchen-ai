from flask import Blueprint, request, jsonify
from datetime import date, timedelta

from backend.utils.database import db
from backend.models.kitchen import Kitchen
from backend.models.menu import MenuItem
from backend.models.inventory import Inventory
from backend.models.sales import Sales
from backend.models.waste import Waste


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

    if data.get("seed_demo", False):
        _seed_demo_data(kitchen.id)

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


# -------------------------
# Delete Kitchen
# -------------------------

@kitchen_bp.route("/<int:kitchen_id>", methods=["DELETE"])
def delete_kitchen(kitchen_id):
    kitchen = db.session.get(Kitchen, kitchen_id)

    if not kitchen:
        return jsonify({
            "success": False,
            "message": "Kitchen not found."
        }), 404

    try:
        # Cascade delete all child items
        Sales.query.filter_by(kitchen_id=kitchen_id).delete()
        Waste.query.filter_by(kitchen_id=kitchen_id).delete()
        Inventory.query.filter_by(kitchen_id=kitchen_id).delete()
        MenuItem.query.filter_by(kitchen_id=kitchen_id).delete()

        db.session.delete(kitchen)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Kitchen deleted successfully."
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Failed to delete kitchen: {str(e)}"
        }), 500


# -------------------------
# Demo Data Seeding
# -------------------------

def _seed_demo_data(kitchen_id):

    menu_items = [
        {
            "name": "Chicken Biryani",
            "category": "Main Course",
            "price": 250,
            "serving_unit": "servings",
            "cost_per_serving": 120,
        },
        {
            "name": "Veg Pulao",
            "category": "Main Course",
            "price": 180,
            "serving_unit": "servings",
            "cost_per_serving": 80,
        },
        {
            "name": "Paneer Butter Masala",
            "category": "Main Course",
            "price": 220,
            "serving_unit": "servings",
            "cost_per_serving": 100,
        },
        {
            "name": "Dal Tadka",
            "category": "Main Course",
            "price": 140,
            "serving_unit": "servings",
            "cost_per_serving": 55,
        },
        {
            "name": "Garlic Naan",
            "category": "Bread",
            "price": 40,
            "serving_unit": "pieces",
            "cost_per_serving": 15,
        },
    ]

    created_items = []

    for item in menu_items:
        mi = MenuItem(
            kitchen_id=kitchen_id,
            name=item["name"],
            category=item["category"],
            price=item["price"],
            serving_unit=item["serving_unit"],
            cost_per_serving=item["cost_per_serving"],
        )
        db.session.add(mi)
        db.session.flush()
        created_items.append(mi)

    inventory_items = [
        {"name": "Rice", "quantity": 50, "unit": "kg", "minimum_stock": 20},
        {"name": "Chicken", "quantity": 15, "unit": "kg", "minimum_stock": 10},
        {"name": "Paneer", "quantity": 8, "unit": "kg", "minimum_stock": 5},
        {"name": "Dal", "quantity": 12, "unit": "kg", "minimum_stock": 5},
        {"name": "Flour", "quantity": 25, "unit": "kg", "minimum_stock": 10},
        {"name": "Oil", "quantity": 20, "unit": "L", "minimum_stock": 10},
        {"name": "Vegetables", "quantity": 30, "unit": "kg", "minimum_stock": 15},
        {"name": "Spices", "quantity": 5, "unit": "kg", "minimum_stock": 2},
    ]

    for item in inventory_items:
        inv = Inventory(
            kitchen_id=kitchen_id,
            ingredient_name=item["name"],
            quantity=item["quantity"],
            unit=item["unit"],
            minimum_stock=item["minimum_stock"],
        )
        db.session.add(inv)

    today = date.today()

    for i in range(30):
        sale_date = today - timedelta(days=30 - i)

        for mi in created_items:
            base = {
                "Chicken Biryani": 35,
                "Veg Pulao": 25,
                "Paneer Butter Masala": 20,
                "Dal Tadka": 30,
                "Garlic Naan": 50,
            }.get(mi.name, 20)

            qty = base + (i % 5) + (mi.id % 3)

            sale = Sales(
                kitchen_id=kitchen_id,
                menu_item_id=mi.id,
                sale_date=sale_date,
                quantity_sold=qty,
                revenue=qty * mi.price,
            )
            db.session.add(sale)

    waste_samples = [
        {"menu_item_id": created_items[1].id, "days_ago": 1, "qty": 8, "reason": "Over-preparation", "cost": 640},
        {"menu_item_id": created_items[2].id, "days_ago": 3, "qty": 4, "reason": "Spoilage", "cost": 400},
        {"menu_item_id": created_items[0].id, "days_ago": 5, "qty": 3, "reason": "Low demand", "cost": 360},
    ]

    for w in waste_samples:
        waste = Waste(
            kitchen_id=kitchen_id,
            menu_item_id=w["menu_item_id"],
            waste_date=today - timedelta(days=w["days_ago"]),
            quantity_wasted=w["qty"],
            unit="servings",
            reason=w["reason"],
            estimated_cost=w["cost"],
        )
        db.session.add(waste)

    db.session.commit()