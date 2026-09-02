from backend.models.inventory import Inventory
from backend.models.waste import Waste
from backend.models.menu import MenuItem


def get_recommended_preparation(
    kitchen_id,
    menu_item_id,
    predicted_demand
):
    """
    Calculate the recommended preparation quantity
    using predicted demand, inventory, and waste history.
    """

    # -------------------------------------------------
    # 1. Validate predicted demand
    # -------------------------------------------------

    try:
        predicted_demand = float(predicted_demand)
    except (TypeError, ValueError):
        raise ValueError(
            "Predicted demand must be a number."
        )

    if predicted_demand < 0:
        raise ValueError(
            "Predicted demand cannot be negative."
        )

    # -------------------------------------------------
    # 2. Check menu item
    # -------------------------------------------------

    menu_item = MenuItem.query.filter_by(
        id=menu_item_id,
        kitchen_id=kitchen_id
    ).first()

    if not menu_item:
        raise ValueError(
            "Menu item not found for this kitchen."
        )

    # -------------------------------------------------
    # 3. Get current inventory
    # -------------------------------------------------

    inventory_items = Inventory.query.filter_by(
        kitchen_id=kitchen_id
    ).all()

    # NOTE:
    # At this stage inventory is stored as ingredients.
    # We don't yet have a recipe-to-ingredient mapping.
    #
    # Therefore, for the MVP, we use the available
    # inventory quantity as an approximate available
    # quantity.
    #
    # Later we can add a Recipe/Ingredient mapping.

    total_inventory = sum(
        float(item.quantity or 0)
        for item in inventory_items
    )

    # -------------------------------------------------
    # 4. Get historical waste
    # -------------------------------------------------

    waste_records = Waste.query.filter_by(
        kitchen_id=kitchen_id,
        menu_item_id=menu_item_id
    ).all()

    total_waste = sum(
        float(record.quantity_wasted or 0)
        for record in waste_records
    )

    # -------------------------------------------------
    # 5. Calculate average waste
    # -------------------------------------------------

    if waste_records:

        average_waste = (
            total_waste / len(waste_records)
        )

    else:

        average_waste = 0

    # -------------------------------------------------
    # 6. Calculate waste rate
    # -------------------------------------------------

    if predicted_demand > 0:

        waste_rate = (
            average_waste / predicted_demand
        )

    else:

        waste_rate = 0

    # Keep waste rate within reasonable limits
    waste_rate = min(
        max(waste_rate, 0),
        0.30
    )

    # -------------------------------------------------
    # 7. Safety stock
    # -------------------------------------------------

    safety_stock = predicted_demand * 0.05

    # -------------------------------------------------
    # 8. Adjust preparation according to waste
    # -------------------------------------------------

    waste_adjustment = (
        predicted_demand * waste_rate
    )

    recommended_preparation = (
        predicted_demand
        + safety_stock
        - waste_adjustment
    )

    # -------------------------------------------------
    # 9. Prevent negative preparation
    # -------------------------------------------------

    recommended_preparation = max(
        0,
        recommended_preparation
    )

    # -------------------------------------------------
    # 10. Round result
    # -------------------------------------------------

    recommended_preparation = round(
        recommended_preparation,
        2
    )

    return {
        "kitchen_id": kitchen_id,
        "menu_item_id": menu_item_id,
        "menu_item": menu_item.name,
        "predicted_demand": round(
            predicted_demand,
            2
        ),
        "current_inventory": round(
            total_inventory,
            2
        ),
        "average_waste": round(
            average_waste,
            2
        ),
        "waste_rate": round(
            waste_rate * 100,
            2
        ),
        "safety_stock": round(
            safety_stock,
            2
        ),
        "recommended_preparation": (
            recommended_preparation
        )
    }