from sqlalchemy import func

from backend.models.waste import Waste
from backend.models.sales import Sales
from backend.models.menu import MenuItem


def get_waste_summary(kitchen_id):
    """
    Calculate overall food-waste statistics
    for a kitchen.
    """

    total_waste = (
        Waste.query
        .filter_by(kitchen_id=kitchen_id)
        .with_entities(
            func.coalesce(
                func.sum(Waste.quantity_wasted), 0
            )
        )
        .scalar()
    )

    total_waste_cost = (
        Waste.query
        .filter_by(kitchen_id=kitchen_id)
        .with_entities(
            func.coalesce(
                func.sum(Waste.estimated_cost), 0
            )
        )
        .scalar()
    )

    total_sales = (
        Sales.query
        .filter_by(kitchen_id=kitchen_id)
        .with_entities(
            func.coalesce(
                func.sum(Sales.quantity_sold), 0
            )
        )
        .scalar()
    )

    # Waste percentage compared with consumed quantity
    if total_sales > 0:
        waste_percentage = (
            total_waste / (total_sales + total_waste)
        ) * 100
    else:
        waste_percentage = 0

    return {
        "total_waste": round(float(total_waste), 2),
        "total_waste_cost": round(float(total_waste_cost), 2),
        "total_sales": round(float(total_sales), 2),
        "waste_percentage": round(
            float(waste_percentage), 2
        )
    }


def get_waste_by_item(kitchen_id):
    """
    Find how much waste has been recorded
    for each menu item.
    """

    results = (
        Waste.query
        .filter_by(kitchen_id=kitchen_id)
        .with_entities(
            Waste.menu_item_id,
            func.sum(Waste.quantity_wasted).label(
                "total_waste"
            ),
            func.sum(Waste.estimated_cost).label(
                "total_cost"
            )
        )
        .group_by(Waste.menu_item_id)
        .all()
    )

    waste_items = []

    for item_id, total_waste, total_cost in results:

        menu_item = MenuItem.query.get(item_id)

        waste_items.append({
            "menu_item_id": item_id,
            "menu_item": (
                menu_item.name
                if menu_item
                else "Unknown"
            ),
            "total_waste": round(
                float(total_waste or 0), 2
            ),
            "total_cost": round(
                float(total_cost or 0), 2
            )
        })

    # Highest waste first
    waste_items.sort(
        key=lambda x: x["total_waste"],
        reverse=True
    )

    return waste_items


def get_high_waste_items(kitchen_id, limit=5):
    """
    Return the food items with the highest
    recorded waste.
    """

    waste_items = get_waste_by_item(kitchen_id)

    return waste_items[:limit]