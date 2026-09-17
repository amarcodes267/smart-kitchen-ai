from backend.services.demand_service import DemandAnalyzer
from backend.services.inventory_intelligence_service import InventoryIntelligence
from backend.services.waste_analytics_service import WasteAnalytics
from backend.services.health_score_service import HealthScoreCalculator
from backend.models.alert import Alert
from backend.utils.database import db


class RecommendationEngine:
    def generate_dashboard_recommendations(self, kitchen_id):
        analyzer = DemandAnalyzer()
        demand = analyzer.analyze_kitchen_demand(kitchen_id, days=30)

        intelligence = InventoryIntelligence()
        inv_analysis = intelligence.analyze_kitchen_inventory(kitchen_id)

        waste_analytics = WasteAnalytics()
        waste_analysis = waste_analytics.analyze_kitchen_waste(kitchen_id, days=30)

        health = HealthScoreCalculator()
        health_data = health.calculate(kitchen_id)

        recommendations = []

        for item in demand["items"]:
            if item["trend"] == "increasing" and item["predicted_demand_tomorrow"] > 0:
                recommendations.append({
                    "priority": "high",
                    "type": "prepare_more",
                    "category": "demand",
                    "title": f"Prepare More: {item['name']}",
                    "message": f"Demand is rising by {item['change_pct']}%. Increase preparation to {item['predicted_demand_tomorrow']} portions.",
                    "menu_item_id": item["menu_item_id"],
                })
            elif item["trend"] == "decreasing" and item["predicted_demand_tomorrow"] > 0:
                recommendations.append({
                    "priority": "medium",
                    "type": "prepare_less",
                    "category": "demand",
                    "title": f"Reduce Preparation: {item['name']}",
                    "message": f"Demand dropped by {abs(item['change_pct'])}%. Reduce preparation to {item['predicted_demand_tomorrow']} portions.",
                    "menu_item_id": item["menu_item_id"],
                })

        for item in inv_analysis["items"]:
            if item["status"] == "critical":
                recommendations.append({
                    "priority": "high",
                    "type": "restock",
                    "category": "inventory",
                    "title": f"Urgent Restock: {item['ingredient_name']}",
                    "message": f"{item['ingredient_name']} is at {item['current_qty']} {item['unit']}. Buy {item['restock_qty']} {item['unit']} immediately.",
                })
            elif item["status"] == "low":
                recommendations.append({
                    "priority": "medium",
                    "type": "restock",
                    "category": "inventory",
                    "title": f"Restock: {item['ingredient_name']}",
                    "message": f"{item['ingredient_name']} will run out soon. Purchase {item['restock_qty']} {item['unit']}.",
                })

        for item in waste_analysis["high_waste_items"][:3]:
            if item["waste_percentage"] > 10:
                recommendations.append({
                    "priority": "high",
                    "type": "waste_alert",
                    "category": "waste",
                    "title": f"Waste Alert: {item['name']}",
                    "message": f"{item['name']} has {item['waste_percentage']}% waste. {item['reduction_strategy']}",
                })

        if waste_analysis["summary"]["waste_percentage"] > 15:
            recommendations.append({
                "priority": "high",
                "type": "cost_saving",
                "category": "cost",
                "title": "High Waste Cost",
                "message": f"Monthly avoidable waste cost: ₹{waste_analysis['summary']['total_waste_cost']}. Potential savings: ₹{waste_analysis['summary']['total_waste_cost'] * 0.6:.0f}.",
            })

        recommendations.sort(key=lambda x: 0 if x["priority"] == "high" else 1 if x["priority"] == "medium" else 2)

        self._persist_recommendations(kitchen_id, recommendations)

        return {
            "kitchen_id": kitchen_id,
            "kitchen_name": demand["kitchen_name"],
            "generated_at": demand["generated_at"],
            "health_score": health_data["overall_score"],
            "health_status": health_data["status"],
            "health_emoji": health_data["emoji"],
            "recommendations": recommendations,
            "summary": {
                "total": len(recommendations),
                "high": len([r for r in recommendations if r["priority"] == "high"]),
                "medium": len([r for r in recommendations if r["priority"] == "medium"]),
                "low": len([r for r in recommendations if r["priority"] == "low"]),
            },
        }

    def _persist_recommendations(self, kitchen_id, recommendations):
        Alert.query.filter_by(kitchen_id=kitchen_id, category="recommendation").delete()
        for rec in recommendations:
            alert = Alert(
                kitchen_id=kitchen_id,
                level=rec["priority"],
                category="recommendation",
                title=rec["title"],
                message=rec["message"],
                meta=rec.get("menu_item_id") and str(rec.get("menu_item_id")) or None,
            )
            db.session.add(alert)
        db.session.commit()
