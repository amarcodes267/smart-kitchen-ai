from datetime import date, timedelta

import numpy as np
import pandas as pd
from sqlalchemy import func

from backend.models.sales import Sales
from backend.models.prediction import Prediction
from backend.models.menu import MenuItem
from backend.models.kitchen import Kitchen
from backend.utils.database import db


class DemandAnalyzer:
    def analyze_kitchen_demand(self, kitchen_id, days=30):
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

        if not sales:
            return {
                "kitchen_id": kitchen_id,
                "kitchen_name": kitchen.name,
                "generated_at": date.today().isoformat(),
                "summary": {"total_orders": 0, "days_analyzed": days},
                "items": [],
                "trends": {"increasing": [], "stable": [], "decreasing": []},
                "alerts": [],
            }

        rows = [
            {
                "menu_item_id": s.menu_item_id,
                "date": s.sale_date,
                "quantity_sold": s.quantity_sold,
                "revenue": s.revenue or 0,
            }
            for s in sales
        ]

        df = pd.DataFrame(rows)
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")

        menu_map = {
            mi.id: mi.name
            for mi in MenuItem.query.filter_by(kitchen_id=kitchen_id).all()
        }

        today = date.today()
        tomorrow = today + timedelta(days=1)

        items = []
        trends = {"increasing": [], "stable": [], "decreasing": []}
        alerts = []

        for menu_item_id, group in df.groupby("menu_item_id"):
            group = group.sort_values("date")
            item_name = menu_map.get(menu_item_id, f"Item {menu_item_id}")

            recent = group[group["date"] >= (pd.Timestamp(today) - pd.Timedelta(days=14))]
            previous = group[(group["date"] < (pd.Timestamp(today) - pd.Timedelta(days=14))) & (group["date"] >= (pd.Timestamp(today) - pd.Timedelta(days=28)))]

            recent_avg = float(recent["quantity_sold"].mean()) if not recent.empty else 0
            previous_avg = float(previous["quantity_sold"].mean()) if not previous.empty else 0

            if previous_avg > 0:
                change_pct = ((recent_avg - previous_avg) / previous_avg) * 100
            else:
                change_pct = 100 if recent_avg > 0 else 0

            if change_pct > 15:
                trend = "increasing"
                trend_symbol = "↗️"
            elif change_pct < -15:
                trend = "decreasing"
                trend_symbol = "↘️"
            else:
                trend = "stable"
                trend_symbol = "→"

            trends[trend].append({
                "menu_item_id": menu_item_id,
                "name": item_name,
                "change_pct": round(change_pct, 1),
                "recent_avg": round(recent_avg, 2),
                "previous_avg": round(previous_avg, 2),
            })

            hist = group.copy()
            prev_sales = float(hist["quantity_sold"].iloc[-1])
            rolling_avg = float(hist["quantity_sold"].tail(7).mean())

            features = pd.DataFrame([{
                "day_of_week": tomorrow.weekday(),
                "month": tomorrow.month,
                "previous_sales": prev_sales,
                "rolling_7_day_avg": rolling_avg,
            }])

            try:
                from ml.predict import load_model
                model, feature_cols = load_model()
                features = features[[c for c in feature_cols if c in features.columns]]
                predicted = float(model.predict(features)[0])
            except Exception:
                try:
                    from backend.services.prediction_service import FallbackModel
                    predicted = float(FallbackModel().predict(features)[0])
                except Exception:
                    predicted = max(0, round(recent_avg * 1.05, 2))

            predicted_demand = max(0.0, round(predicted, 1))

            pred_record = Prediction(
                kitchen_id=kitchen_id,
                menu_item_id=menu_item_id,
                prediction_date=tomorrow,
                predicted_demand=predicted_demand,
                model_name="XGBoost",
            )
            db.session.add(pred_record)

            total_sold = float(group["quantity_sold"].sum())
            total_revenue = float(group["revenue"].sum())
            avg_daily = float(group.groupby("date")["quantity_sold"].sum().mean()) if not group.empty else 0
            max_daily = float(group.groupby("date")["quantity_sold"].sum().max()) if not group.empty else 0
            min_daily = float(group.groupby("date")["quantity_sold"].sum().min()) if not group.empty else 0

            items.append({
                "menu_item_id": menu_item_id,
                "name": item_name,
                "total_orders": round(total_sold, 2),
                "total_revenue": round(total_revenue, 2),
                "avg_daily_demand": round(avg_daily, 2),
                "max_daily_demand": round(max_daily, 2),
                "min_daily_demand": round(min_daily, 2),
                "predicted_demand_tomorrow": predicted_demand,
                "trend": trend,
                "trend_symbol": trend_symbol,
                "change_pct": round(change_pct, 2),
                "previous_avg": round(previous_avg, 2),
                "recent_avg": round(recent_avg, 2),
            })

            if predicted_demand > 0 and recent_avg > 0 and change_pct > 30:
                alerts.append({
                    "level": "warning",
                    "type": "unusual_demand_increase",
                    "message": f"{item_name} demand increased by {round(change_pct, 1)}% recently.",
                    "menu_item_id": menu_item_id,
                })

            if predicted_demand > 0 and recent_avg > 0 and change_pct < -30:
                alerts.append({
                    "level": "info",
                    "type": "unusual_demand_decrease",
                    "message": f"{item_name} demand dropped by {round(abs(change_pct), 1)}% recently.",
                    "menu_item_id": menu_item_id,
                })

        items.sort(key=lambda x: x["predicted_demand_tomorrow"], reverse=True)

        db.session.commit()

        return {
            "kitchen_id": kitchen_id,
            "kitchen_name": kitchen.name,
            "generated_at": today.isoformat(),
            "analysis_period_days": days,
            "summary": {
                "total_orders": round(float(df["quantity_sold"].sum()), 2),
                "total_revenue": round(float(df["revenue"].sum()), 2),
                "days_with_sales": int(df["date"].dt.date.nunique()),
                "avg_daily_orders": round(float(df.groupby("date")["quantity_sold"].sum().mean()), 2),
            },
            "items": items,
            "high_demand_items": [i for i in items if i["predicted_demand_tomorrow"] > 0 and i["predicted_demand_tomorrow"] >= (items[0]["predicted_demand_tomorrow"] * 0.8 if items else 0)][:5],
            "low_demand_items": [i for i in items if i["predicted_demand_tomorrow"] > 0 and i["predicted_demand_tomorrow"] <= (items[-1]["predicted_demand_tomorrow"] * 1.2 if items else 0)][:5],
            "trends": trends,
            "alerts": alerts,
        }


class WeeklyForecast:
    def forecast_kitchen(self, kitchen_id, days=7):
        kitchen = db.session.get(Kitchen, kitchen_id)
        if not kitchen:
            raise ValueError("Kitchen not found.")

        today = date.today()
        forecasts = []

        menu_items = MenuItem.query.filter_by(kitchen_id=kitchen_id).all()

        for menu_item in menu_items:
            sales = (
                Sales.query
                .filter(Sales.kitchen_id == kitchen_id, Sales.menu_item_id == menu_item.id)
                .order_by(Sales.sale_date.asc())
                .all()
            )

            if len(sales) < 1:
                continue

            rows = [{"date": s.sale_date, "quantity_sold": s.quantity_sold} for s in sales]
            df = pd.DataFrame(rows)
            df["date"] = pd.to_datetime(df["date"])
            df = df.sort_values("date")

            prev_sales = float(df["quantity_sold"].iloc[-1])
            rolling_avg = float(df["quantity_sold"].tail(7).mean())

            from ml.predict import load_model
            model, feature_cols = load_model()

            weekly = []
            for i in range(days):
                forecast_date = today + timedelta(days=i + 1)
                features = pd.DataFrame([{
                    "day_of_week": forecast_date.weekday(),
                    "month": forecast_date.month,
                    "previous_sales": prev_sales,
                    "rolling_7_day_avg": rolling_avg,
                }])
                features = features[[c for c in feature_cols if c in features.columns]]

                try:
                    predicted = float(model.predict(features)[0])
                except Exception:
                    try:
                        from backend.services.prediction_service import FallbackModel
                        predicted = float(FallbackModel().predict(features)[0])
                    except Exception:
                        predicted = max(0, round(rolling_avg, 2))

                predicted_val = round(max(0.0, predicted), 1)

                pred_record = Prediction(
                    kitchen_id=kitchen_id,
                    menu_item_id=menu_item.id,
                    prediction_date=forecast_date,
                    predicted_demand=predicted_val,
                    model_name="XGBoost",
                )
                db.session.add(pred_record)

                weekly.append({
                    "date": forecast_date.isoformat(),
                    "predicted_demand": predicted_val,
                })

            forecasts.append({
                "menu_item_id": menu_item.id,
                "name": menu_item.name,
                "daily_forecast": weekly,
                "weekly_total": round(max(0, sum(d["predicted_demand"] for d in weekly)), 2),
            })

        db.session.commit()
        return {
            "kitchen_id": kitchen_id,
            "kitchen_name": kitchen.name,
            "forecast_start": (today + timedelta(days=1)).isoformat(),
            "forecast_end": (today + timedelta(days=days)).isoformat(),
            "forecasts": forecasts,
        }
