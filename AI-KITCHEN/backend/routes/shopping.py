from flask import Blueprint, jsonify

from backend.services.shopping_service import ShoppingListGenerator


shopping_bp = Blueprint(
    "shopping",
    __name__,
    url_prefix="/api/shopping",
)


generator = ShoppingListGenerator()


@shopping_bp.route("/kitchen/<int:kitchen_id>", methods=["GET"])
def get_shopping_list(kitchen_id):
    try:
        result = generator.generate(kitchen_id)
        return jsonify({"success": True, "shopping_list": result})
    except ValueError as error:
        return jsonify({"success": False, "message": str(error)}), 404
    except Exception as error:
        return jsonify({"success": False, "message": str(error)}), 500
