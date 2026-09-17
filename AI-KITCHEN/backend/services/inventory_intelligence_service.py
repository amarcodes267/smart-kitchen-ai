from datetime import date, timedelta

from sqlalchemy import func

from backend.models.inventory import Inventory
from backend.models.menu import MenuItem
from backend.models.kitchen import Kitchen
from backend.models.alert import Alert
from backend.utils.database import db


class InventoryIntelligence:
    def analyze_kitchen_inventory(self, kitchen_id):
        kitchen = db.session.get(Kitchen, kitchen_id)
        if not kitchen:
            raise ValueError("Kitchen not found.")

        inventory_items = (
            Inventory.query
            .filter_by(kitchen_id=kitchen_id)
            .order_by(Inventory.ingredient_name.asc())
            .all()
        )

        menu_items = MenuItem.query.filter_by(kitchen_id=kitchen_id).all()

        from backend.services.demand_service import DemandAnalyzer
        analyzer = DemandAnalyzer()
        demand = analyzer.analyze_kitchen_demand(kitchen_id, days=30)
        items_count = len(demand.get("items", []))
        total_predicted = sum(i["predicted_demand_tomorrow"] for i in demand.get("items", []))

        items = []
        low_stock_alerts = []
        excess_alerts = []

        for inv in inventory_items:
            current_qty = float(inv.quantity or 0)
            min_stock = float(inv.minimum_stock or 0)
            unit = inv.unit or "kg"

            expected_consumption = self._estimate_consumption(kitchen_id, inv.ingredient_name, days=7)
            expected_consumption = self._estimate_consumption_cached(total_predicted, items_count, days=7)
            shortage = max(0, round(expected_consumption - current_qty, 2))
            excess = max(0, round(current_qty - (expected_consumption * 2), 2)) if expected_consumption > 0 else 0

            restock_qty = round(shortage + min_stock, 2) if shortage > 0 else 0

            status = "ok"
            if current_qty <= min_stock:
                status = "critical"
            elif shortage > 0:
                status = "low"
            elif excess > 0:
                status = "excess"

            item_data = {
                "id": inv.id,
                "ingredient_name": inv.ingredient_name,
                "current_qty": current_qty,
                "unit": unit,
                "minimum_stock": min_stock,
                "expected_consumption_7d": round(expected_consumption, 2),
                "shortage": shortage,
                "excess": excess,
                "restock_qty": restock_qty,
                "status": status,
                "expiry_date": inv.expiry_date.isoformat() if inv.expiry_date else None,
                "days_to_expiry": (inv.expiry_date - date.today()).days if inv.expiry_date else None,
            }
            items.append(item_data)

            if status == "critical":
                low_stock_alerts.append({
                    "level": "critical",
                    "type": "low_inventory",
                    "title": f"Critical: {inv.ingredient_name}",
                    "message": f"{inv.ingredient_name} is at {current_qty} {unit}, below minimum stock of {min_stock} {unit}.",
                    "meta": f'{{"ingredient": "{inv.ingredient_name}", "current": {current_qty}, "minimum": {min_stock}}}',
                })
            elif status == "low":
                low_stock_alerts.append({
                    "level": "warning",
                    "type": "low_inventory",
                    "title": f"Low Stock: {inv.ingredient_name}",
                    "message": f"{inv.ingredient_name} will run out in ~{round(current_qty / max(expected_consumption / 7, 0.01), 1)} days. Restock {restock_qty} {unit}.",
                    "meta": f'{{"ingredient": "{inv.ingredient_name}", "current": {current_qty}, "restock": {restock_qty}}}',
                })
            elif status == "excess":
                excess_alerts.append({
                    "level": "info",
                    "type": "excess_inventory",
                    "title": f"Excess Stock: {inv.ingredient_name}",
                    "message": f"{inv.ingredient_name} has {excess} {unit} excess stock. Consider reducing orders.",
                    "meta": f'{{"ingredient": "{inv.ingredient_name}", "excess": {excess}}}',
                })

        alerts = low_stock_alerts + excess_alerts
        self._persist_alerts(kitchen_id, alerts)

        return {
            "kitchen_id": kitchen_id,
            "kitchen_name": kitchen.name,
            "generated_at": date.today().isoformat(),
            "summary": {
                "total_items": len(items),
                "ok": len([i for i in items if i["status"] == "ok"]),
                "low": len([i for i in items if i["status"] == "low"]),
                "critical": len([i for i in items if i["status"] == "critical"]),
                "excess": len([i for i in items if i["status"] == "excess"]),
            },
            "items": items,
            "alerts": alerts,
        }

    def _estimate_consumption_cached(self, total_predicted, items_count, days=7):
        if total_predicted == 0 or items_count == 0:
            return 0
        ingredient_share = items_count / max(items_count, 1)
        return round(total_predicted * ingredient_share * (days / 1) * 0.3, 2)

    def _estimate_consumption(self, kitchen_id, ingredient_name, days=7):
        from backend.services.demand_service import DemandAnalyzer
        analyzer = DemandAnalyzer()
        demand = analyzer.analyze_kitchen_demand(kitchen_id, days=30)
        total_predicted = sum(i["predicted_demand_tomorrow"] for i in demand["items"])
        total_predicted = sum(i["predicted_demand_tomorrow"] for i in demand.get("items", []))
        return self._estimate_consumption_cached(total_predicted, len(demand.get("items", [])), days)

        if total_predicted == 0 or not demand["items"]:
            return 0

        ingredient_share = len(demand["items"]) / max(len(demand["items"]), 1)
        return round(total_predicted * ingredient_share * (days / 1) * 0.3, 2)

    def _persist_alerts(self, kitchen_id, alerts):
        db.session.query(Alert).filter_by(kitchen_id=kitchen_id, is_read=False).delete()
        db.session.query(Alert).filter(
            Alert.kitchen_id == kitchen_id,
            Alert.category.in_(["low_inventory", "excess_inventory"]),
            Alert.is_read == False
        ).delete(synchronize_session=False)
        for alert_data in alerts:
            alert = Alert(
                kitchen_id=kitchen_id,
                level=alert_data["level"],
                category=alert_data["type"],
                title=alert_data["title"],
                message=alert_data["message"],
                meta=alert_data.get("meta"),
            )
            db.session.add(alert)
        db.session.commit()
