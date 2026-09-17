from datetime import date, timedelta

from sqlalchemy import func

from backend.models.waste import Waste
from backend.models.menu import MenuItem
from backend.models.sales import Sales
from backend.models.kitchen import Kitchen
from backend.utils.database import db


class WasteAnalytics:
    def analyze_kitchen_waste(self, kitchen_id, days=30):
        kitchen = db.session.get(Kitchen, kitchen_id)
        if not kitchen:
            raise ValueError("Kitchen not found.")

        cutoff = date.today() - timedelta(days=days)
        waste_records = (
            Waste.query
            .filter(Waste.kitchen_id == kitchen_id, Waste.waste_date >= cutoff)
            .order_by(Waste.waste_date.desc())
            .all()
        )

        sales_records = (
            Sales.query
            .filter(Sales.kitchen_id == kitchen_id, Sales.sale_date >= cutoff)
            .all()
        )

        menu_items = MenuItem.query.filter_by(kitchen_id=kitchen_id).all()
        menu_map = {mi.id: mi.name for mi in menu_items}

        total_waste = sum(float(w.quantity_wasted or 0) for w in waste_records)
        total_waste_cost = sum(float(w.estimated_cost or 0) for w in waste_records)
        total_sales = sum(float(s.quantity_sold or 0) for s in sales_records)

        if total_sales + total_waste > 0:
            waste_percentage = (total_waste / (total_sales + total_waste)) * 100
        else:
            waste_percentage = 0

        by_item = {}
        for w in waste_records:
            item_id = w.menu_item_id or 0
            name = menu_map.get(item_id, "General Waste") if item_id else "General Waste"
            if item_id not in by_item:
                by_item[item_id] = {"menu_item_id": item_id, "name": name, "total_waste": 0, "total_cost": 0, "count": 0, "reasons": {}}
            by_item[item_id]["total_waste"] += float(w.quantity_wasted or 0)
            by_item[item_id]["total_cost"] += float(w.estimated_cost or 0)
            by_item[item_id]["count"] += 1
            reason = w.reason or "Unknown"
            by_item[item_id]["reasons"][reason] = by_item[item_id]["reasons"].get(reason, 0) + 1

        waste_by_item = sorted(by_item.values(), key=lambda x: x["total_waste"], reverse=True)

        high_waste_items = []
        for item in waste_by_item[:5]:
            if total_sales > 0:
                item_waste_pct = (item["total_waste"] / (total_sales + item["total_waste"])) * 100
            else:
                item_waste_pct = 0

            top_reason = max(item["reasons"], key=item["reasons"].get) if item["reasons"] else "Unknown"

            high_waste_items.append({
                "menu_item_id": item["menu_item_id"],
                "name": item["name"],
                "total_waste": round(item["total_waste"], 2),
                "total_cost": round(item["total_cost"], 2),
                "waste_percentage": round(item_waste_pct, 2),
                "count": item["count"],
                "top_reason": top_reason,
                "reduction_strategy": self._suggest_reduction_strategy(top_reason, item["name"]),
            })

        trends = self._calculate_waste_trends(waste_records, days)

        return {
            "kitchen_id": kitchen_id,
            "kitchen_name": kitchen.name,
            "generated_at": date.today().isoformat(),
            "period_days": days,
            "summary": {
                "total_waste": round(total_waste, 2),
                "total_waste_cost": round(total_waste_cost, 2),
                "total_sales": round(total_sales, 2),
                "waste_percentage": round(waste_percentage, 2),
                "waste_records_count": len(waste_records),
            },
            "high_waste_items": high_waste_items,
            "trends": trends,
            "reduction_suggestions": self._generate_reduction_suggestions(high_waste_items, waste_percentage),
        }

    def _calculate_waste_trends(self, waste_records, days):
        if not waste_records:
            return {"direction": "stable", "message": "No waste data available."}

        recent = [w for w in waste_records if w.waste_date >= date.today() - timedelta(days=days // 2)]
        previous = [w for w in waste_records if w.waste_date < date.today() - timedelta(days=days // 2)]

        recent_total = sum(float(w.quantity_wasted or 0) for w in recent)
        previous_total = sum(float(w.quantity_wasted or 0) for w in previous)

        if previous_total > 0:
            change = ((recent_total - previous_total) / previous_total) * 100
        else:
            change = 0 if recent_total == 0 else 100

        if change > 15:
            direction = "increasing"
            message = f"Waste increased by {round(change, 1)}% recently."
        elif change < -15:
            direction = "decreasing"
            message = f"Waste decreased by {round(abs(change), 1)}% recently."
        else:
            direction = "stable"
            message = "Waste levels are stable."

        return {
            "direction": direction,
            "change_pct": round(change, 2),
            "message": message,
            "recent_period_waste": round(recent_total, 2),
            "previous_period_waste": round(previous_total, 2),
        }

    def _suggest_reduction_strategy(self, reason, item_name):
        strategies = {
            "Over-preparation": f"Reduce {item_name} preparation by 10-15% and monitor sales closely.",
            "Low demand": f"Consider reducing portion size or promoting {item_name} differently.",
            "Spoilage": f"Improve storage conditions and check expiry dates for {item_name}.",
            "Expired": f"Use FIFO (First In First Out) for {item_name} and reduce bulk orders.",
            "Cooking error": f"Standardize cooking process for {item_name} to reduce preparation errors.",
        }
        return strategies.get(reason, f"Review preparation process for {item_name}.")

    def _generate_reduction_suggestions(self, high_waste_items, waste_percentage):
        suggestions = []

        if waste_percentage > 20:
            suggestions.append({
                "priority": "high",
                "title": "High Overall Waste",
                "message": f"Waste is at {round(waste_percentage, 1)}%. Focus on reducing preparation of high-waste items.",
            })
        elif waste_percentage > 10:
            suggestions.append({
                "priority": "medium",
                "title": "Moderate Waste",
                "message": f"Waste is at {round(waste_percentage, 1)}%. Small adjustments can save costs.",
            })

        for item in high_waste_items[:3]:
            suggestions.append({
                "priority": "high" if item["waste_percentage"] > 15 else "medium",
                "title": f"Reduce {item['name']}",
                "message": item["reduction_strategy"],
            })

        return suggestions


class CostOptimizer:
    def analyze_costs(self, kitchen_id, days=30):
        kitchen = db.session.get(Kitchen, kitchen_id)
        if not kitchen:
            raise ValueError("Kitchen not found.")

        cutoff = date.today() - timedelta(days=days)
        waste_records = (
            Waste.query
            .filter(Waste.kitchen_id == kitchen_id, Waste.waste_date >= cutoff)
            .all()
        )

        total_waste_cost = sum(float(w.estimated_cost or 0) for w in waste_records)
        total_waste_qty = sum(float(w.quantity_wasted or 0) for w in waste_records)

        high_cost_waste = sorted(
            [{"reason": w.reason or "Unknown", "cost": float(w.estimated_cost or 0), "qty": float(w.quantity_wasted or 0)} for w in waste_records],
            key=lambda x: x["cost"],
            reverse=True,
        )[:5]

        potential_savings = round(total_waste_cost * 0.6, 2)

        return {
            "kitchen_id": kitchen_id,
            "kitchen_name": kitchen.name,
            "period_days": days,
            "generated_at": date.today().isoformat(),
            "total_waste_cost": round(total_waste_cost, 2),
            "total_waste_qty": round(total_waste_qty, 2),
            "potential_savings": potential_savings,
            "high_cost_waste": high_cost_waste,
            "suggestions": [
                {
                    "title": "Reduce Overproduction",
                    "message": f"Avoiding overproduction could save up to ₹{round(total_waste_cost * 0.4, 2)}.",
                },
                {
                    "title": "Track Expiry Dates",
                    "message": "Better expiry tracking could prevent spoilage-related waste.",
                },
            ],
        }
