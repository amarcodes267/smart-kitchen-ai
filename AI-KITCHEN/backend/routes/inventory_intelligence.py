from flask import Blueprint, jsonify, request

from backend.services.inventory_intelligence_service import InventoryIntelligence


inventory_intelligence_bp = Blueprint(
    "inventory_intelligence",
    __name__,
    url_prefix="/api/inventory-intelligence",
)


intelligence = InventoryIntelligence()


@inventory_intelligence_bp.route("/kitchen/<int:kitchen_id>", methods=["GET"])
def get_inventory_analysis(kitchen_id):
    try:
        result = intelligence.analyze_kitchen_inventory(kitchen_id)
        return jsonify({"success": True, "analysis": result})
    except ValueError as error:
        return jsonify({"success": False, "message": str(error)}), 404
    except Exception as error:
        return jsonify({"success": False, "message": str(error)}), 500
