from datetime import date, timedelta

from sqlalchemy import func

from backend.models.sales import Sales
from backend.models.menu import MenuItem
from backend.models.kitchen import Kitchen
from backend.utils.database import db


class SalesAnalytics:
    def analyze_kitchen_sales(self, kitchen_id, days=30):
        kitchen = db.session.get(Kitchen, kitchen_id)
        if not kitchen:
            raise ValueError("Kitchen not found.")

        cutoff = date.today() - timedelta(days=days)
        sales = (
            Sales.query
            .filter(Sales.kitchen_id == kitchen_id, Sales.sale_date >= cutoff)
            .order_by(Sales.sale_date.asc())
            .all()
        )

        menu_items = MenuItem.query.filter_by(kitchen_id=kitchen_id).all()
        menu_map = {mi.id: mi.name for mi in menu_items}

        total_orders = sum(float(s.quantity_sold or 0) for s in sales)
        total_revenue = sum(float(s.revenue or 0) for s in sales)

        daily = {}
        for s in sales:
            d = s.sale_date.isoformat()
            if d not in daily:
                daily[d] = {
                    "date": d,
                    "orders": 0.0,
                    "revenue": 0.0,
                }
            daily[d]["orders"] += float(s.quantity_sold or 0)
            daily[d]["revenue"] += float(s.revenue or 0)

        by_item = {}
        for s in sales:
            item_id = s.menu_item_id
            if item_id not in by_item:
                by_item[item_id] = {"menu_item_id": item_id, "name": menu_map.get(item_id, "Unknown"), "orders": 0, "revenue": 0, "days_sold": set()}
            by_item[item_id]["orders"] += float(s.quantity_sold or 0)
            by_item[item_id]["revenue"] += float(s.revenue or 0)
            by_item[item_id]["days_sold"].add(s.sale_date.isoformat())

        item_performance = []
        for item_id, data in by_item.items():
            item_performance.append({
                "menu_item_id": item_id,
                "name": data["name"],
                "total_orders": round(data["orders"], 2),
                "total_revenue": round(data["revenue"], 2),
                "days_sold": len(data["days_sold"]),
                "avg_daily_orders": round(data["orders"] / max(len(data["days_sold"]), 1), 2),
            })

        item_performance.sort(key=lambda x: x["total_orders"], reverse=True)

        best_sellers = item_performance[:5]
        worst_sellers = [i for i in item_performance if i["total_orders"] > 0][-5:] if item_performance else []

        peak_days = sorted(daily.values(), key=lambda x: x["orders"], reverse=True)[:5]

        return {
            "kitchen_id": kitchen_id,
            "kitchen_name": kitchen.name,
            "period_days": days,
            "generated_at": date.today().isoformat(),
            "summary": {
                "total_orders": round(total_orders, 2),
                "total_revenue": round(total_revenue, 2),
                "avg_daily_orders": round(total_orders / max(days, 1), 2),
                "days_with_sales": len(daily),
            },
            "daily_breakdown": sorted(daily.values(), key=lambda x: x["date"])[-30:],
            "item_performance": item_performance,
            "best_sellers": best_sellers,
            "worst_sellers": worst_sellers,
            "peak_days": peak_days,
        }


class MenuIntelligence:
    def analyze_menu(self, kitchen_id):
        kitchen = db.session.get(Kitchen, kitchen_id)
        if not kitchen:
            raise ValueError("Kitchen not found.")

        menu_items = MenuItem.query.filter_by(kitchen_id=kitchen_id).all()

        items = []
        for mi in menu_items:
            sales = Sales.query.filter_by(kitchen_id=kitchen_id, menu_item_id=mi.id).all()
            total_orders = sum(float(s.quantity_sold or 0) for s in sales)
            total_revenue = sum(float(s.revenue or 0) for s in sales)

            if total_orders > 0:
                status = "popular" if total_orders > 50 else "moderate" if total_orders > 10 else "low"
            else:
                status = "no_sales"

            items.append({
                "menu_item_id": mi.id,
                "name": mi.name,
                "category": mi.category,
                "price": mi.price,
                "cost_per_serving": mi.cost_per_serving,
                "total_orders": round(total_orders, 2),
                "total_revenue": round(total_revenue, 2),
                "status": status,
                "recommendation": self._menu_recommendation(status, mi.name, total_orders),
            })

        return {
            "kitchen_id": kitchen_id,
            "kitchen_name": kitchen.name,
            "generated_at": date.today().isoformat(),
            "items": items,
            "summary": {
                "total_items": len(items),
                "popular": len([i for i in items if i["status"] == "popular"]),
                "moderate": len([i for i in items if i["status"] == "moderate"]),
                "low": len([i for i in items if i["status"] == "low"]),
                "no_sales": len([i for i in items if i["status"] == "no_sales"]),
            },
        }

    def _menu_recommendation(self, status, name, orders):
        if status == "popular":
            return f"{name} is a top performer. Ensure adequate stock and consider promoting it."
        elif status == "moderate":
            return f"{name} has steady demand. Maintain current preparation levels."
        elif status == "low":
            return f"{name} has low demand. Consider reducing preparation or running promotions."
        return f"{name} has no sales yet. Consider removing or promoting it."
