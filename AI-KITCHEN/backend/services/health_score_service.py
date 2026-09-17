from datetime import date, timedelta

from backend.models.inventory import Inventory
from backend.models.waste import Waste
from backend.models.sales import Sales
from backend.models.kitchen import Kitchen
from backend.utils.database import db


class HealthScoreCalculator:
    def calculate(self, kitchen_id):
        kitchen = db.session.get(Kitchen, kitchen_id)
        if not kitchen:
            raise ValueError("Kitchen not found.")

        cutoff = date.today() - timedelta(days=30)
        sales = Sales.query.filter(Sales.kitchen_id == kitchen_id, Sales.sale_date >= cutoff).all()
        waste = Waste.query.filter(Waste.kitchen_id == kitchen_id, Waste.waste_date >= cutoff).all()
        inventory = Inventory.query.filter_by(kitchen_id=kitchen_id).all()

        total_orders = sum(float(s.quantity_sold or 0) for s in sales)
        total_revenue = sum(float(s.revenue or 0) for s in sales)
        total_waste = sum(float(w.quantity_wasted or 0) for w in waste)
        total_waste_cost = sum(float(w.estimated_cost or 0) for w in waste)

        if total_orders + total_waste > 0:
            waste_rate = (total_waste / (total_orders + total_waste)) * 100
        else:
            waste_rate = 0

        low_stock = len([i for i in inventory if float(i.quantity or 0) <= float(i.minimum_stock or 0)])
        total_inventory = len(inventory)
        stock_health = max(0, 100 - (low_stock / max(total_inventory, 1) * 100)) if total_inventory > 0 else 50

        waste_score = max(0, 100 - waste_rate * 2)

        demand_score = min(100, total_orders * 2)

        if total_revenue > 0 and total_waste_cost > 0:
            cost_efficiency = max(0, 100 - (total_waste_cost / total_revenue * 100))
        elif total_revenue > 0 and total_waste_cost == 0:
            cost_efficiency = 100.0
        else:
            cost_efficiency = 80
            cost_efficiency = 80.0

        stock_availability = min(100, total_orders * 1.5) if total_orders > 0 else 30

        weights = {
            "waste_efficiency": 0.25,
            "inventory_management": 0.2,
            "demand_fulfillment": 0.2,
            "cost_efficiency": 0.2,
            "stock_availability": 0.15,
        }

        overall = (
            waste_score * weights["waste_efficiency"]
            + stock_health * weights["inventory_management"]
            + demand_score * weights["demand_fulfillment"]
            + cost_efficiency * weights["cost_efficiency"]
            + stock_availability * weights["stock_availability"]
        )

        overall = round(max(0, min(100, overall)), 1)

        if overall >= 80:
            status = "GOOD"
            emoji = "🟢"
        elif overall >= 60:
            status = "NEEDS IMPROVEMENT"
            emoji = "🟡"
        else:
            status = "CRITICAL"
            emoji = "🔴"

        return {
            "kitchen_id": kitchen_id,
            "kitchen_name": kitchen.name,
            "generated_at": date.today().isoformat(),
            "overall_score": overall,
            "status": status,
            "emoji": emoji,
            "health_emoji": emoji,
            "components": {
                "waste_efficiency": round(waste_score, 1),
                "inventory_management": round(stock_health, 1),
                "demand_fulfillment": round(demand_score, 1),
                "cost_efficiency": round(cost_efficiency, 1),
                "stock_availability": round(stock_availability, 1),
            },
            "weights": weights,
            "summary": {
                "total_orders": round(total_orders, 2),
                "total_revenue": round(total_revenue, 2),
                "total_waste": round(total_waste, 2),
                "waste_cost": round(total_waste_cost, 2),
                "waste_percentage": round(waste_rate, 2),
                "low_stock_items": low_stock,
                "inventory_items": total_inventory,
            },
        }
