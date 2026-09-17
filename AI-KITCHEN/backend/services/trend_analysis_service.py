from datetime import date, timedelta

import numpy as np
import pandas as pd

from backend.models.sales import Sales
from backend.models.menu import MenuItem
from backend.models.kitchen import Kitchen
from backend.utils.database import db


class TrendAnalyzer:
    def analyze_item_trend(self, kitchen_id, menu_item_id, window=28):
        kitchen = db.session.get(Kitchen, kitchen_id)
        if not kitchen:
            raise ValueError("Kitchen not found.")

        cutoff = date.today() - timedelta(days=window)
        sales = (
            Sales.query
            .filter(
                Sales.kitchen_id == kitchen_id,
                Sales.menu_item_id == menu_item_id,
                Sales.sale_date >= cutoff,
            )
            .order_by(Sales.sale_date.asc())
            .all()
        )

        menu_item = db.session.get(MenuItem, menu_item_id)
        item_name = menu_item.name if menu_item else f"Item {menu_item_id}"

        if not sales:
            return {
                "kitchen_id": kitchen_id,
                "menu_item_id": menu_item_id,
                "name": item_name,
                "trend": "stable",
                "trend_symbol": "→",
                "confidence": "low",
                "message": "Insufficient data for trend analysis.",
                "data_points": 0,
                "change_pct": 0.0,
            }

        rows = [{"date": s.sale_date, "quantity_sold": s.quantity_sold} for s in sales]
        df = pd.DataFrame(rows)
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")

        daily = df.groupby("date")["quantity_sold"].sum().reset_index()
        daily = daily.sort_values("date")

        if len(daily) < 3:
            trend = "stable"
            trend_symbol = "→"
            confidence = "low"
            change_pct = 0.0
        else:
            x = np.arange(len(daily))
            y = daily["quantity_sold"].values

            slope, intercept = np.polyfit(x, y, 1)

            mean_y = np.mean(y)
            if mean_y > 0:
                change_pct = (slope * len(daily) / mean_y) * 100
            else:
                change_pct = 0 if slope == 0 else (100 if slope > 0 else -100)

            if change_pct > 10:
                trend = "increasing"
                trend_symbol = "↗️"
            elif change_pct < -10:
                trend = "decreasing"
                trend_symbol = "↘️"
            else:
                trend = "stable"
                trend_symbol = "→"

            confidence = "high" if len(daily) >= 14 else "medium" if len(daily) >= 7 else "low"

        return {
            "kitchen_id": kitchen_id,
            "menu_item_id": menu_item_id,
            "name": item_name,
            "trend": trend,
            "trend_symbol": trend_symbol,
            "change_pct": round(float(change_pct), 2),
            "confidence": confidence,
            "data_points": len(daily),
            "window_days": window,
            "message": self._trend_message(trend, change_pct, item_name),
        }

    def analyze_kitchen_trends(self, kitchen_id, window=28):
        kitchen = db.session.get(Kitchen, kitchen_id)
        if not kitchen:
            raise ValueError("Kitchen not found.")

        cutoff = date.today() - timedelta(days=window)
        sales = (
            Sales.query
            .filter(Sales.kitchen_id == kitchen_id, Sales.sale_date >= cutoff)
            .order_by(Sales.sale_date.asc())
            .all()
        )

        if not sales:
            return {
                "kitchen_id": kitchen_id,
                "kitchen_name": kitchen.name,
                "overall_trend": "stable",
                "overall_trend_symbol": "→",
                "items": [],
                "summary": {"total_items": 0, "increasing": 0, "stable": 0, "decreasing": 0},
            }

        menu_items = MenuItem.query.filter_by(kitchen_id=kitchen_id).all()
        menu_ids = [mi.id for mi in menu_items]
        menu_map = {mi.id: mi.name for mi in menu_items}

        items = []
        summary = {"total_items": 0, "increasing": 0, "stable": 0, "decreasing": 0}

        for menu_item_id in menu_ids:
            trend_data = self.analyze_item_trend(kitchen_id, menu_item_id, window)
            items.append(trend_data)
            summary[trend_data["trend"]] += 1
            summary["total_items"] += 1

        items.sort(key=lambda x: x["change_pct"], reverse=True)

        if summary["increasing"] > summary["decreasing"]:
            overall = "increasing"
            overall_symbol = "↗️"
        elif summary["decreasing"] > summary["increasing"]:
            overall = "decreasing"
            overall_symbol = "↘️"
        else:
            overall = "stable"
            overall_symbol = "→"

        return {
            "kitchen_id": kitchen_id,
            "kitchen_name": kitchen.name,
            "overall_trend": overall,
            "overall_trend_symbol": overall_symbol,
            "window_days": window,
            "items": items,
            "summary": summary,
        }

    def _trend_message(self, trend, change_pct, item_name):
        if trend == "increasing":
            return f"{item_name} demand is rising by {round(change_pct, 1)}%. Consider increasing preparation."
        elif trend == "decreasing":
            return f"{item_name} demand is falling by {round(abs(change_pct), 1)}%. Consider reducing preparation."
        return f"{item_name} demand is stable. Maintain current preparation levels."
