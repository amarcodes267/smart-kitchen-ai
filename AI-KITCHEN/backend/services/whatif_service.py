from backend.services.demand_service import DemandAnalyzer
from backend.services.inventory_intelligence_service import InventoryIntelligence
from backend.services.optimization_service import get_recommended_preparation


class WhatIfAnalyzer:
    def demand_increase(self, kitchen_id, menu_item_id, increase_pct):
        kitchen_id = int(kitchen_id)
        menu_item_id = int(menu_item_id)
        analyzer = DemandAnalyzer()
        demand = analyzer.analyze_kitchen_demand(kitchen_id, days=30)

        item = next((i for i in demand["items"] if i["menu_item_id"] == menu_item_id), None)
        if not item:
            raise ValueError("Menu item not found or insufficient data.")

        base = item["predicted_demand_tomorrow"]
        new_demand = round(base * (1 + increase_pct / 100), 2)

        recommendation = get_recommended_preparation(
            kitchen_id=kitchen_id,
            menu_item_id=menu_item_id,
            predicted_demand=new_demand,
        )

        return {
            "scenario": "demand_increase",
            "parameters": {"increase_pct": increase_pct},
            "base_demand": base,
            "new_demand": new_demand,
            "additional_portions": round(new_demand - base, 2),
            "recommendation": recommendation,
        }

    def preparation_reduction(self, kitchen_id, menu_item_id, reduction_pct):
        kitchen_id = int(kitchen_id)
        menu_item_id = int(menu_item_id)
        analyzer = DemandAnalyzer()
        demand = analyzer.analyze_kitchen_demand(kitchen_id, days=30)

        item = next((i for i in demand["items"] if i["menu_item_id"] == menu_item_id), None)
        if not item:
            raise ValueError("Menu item not found or insufficient data.")

        base = item["predicted_demand_tomorrow"]
        new_demand = round(base * (1 - reduction_pct / 100), 2)

        recommendation = get_recommended_preparation(
            kitchen_id=kitchen_id,
            menu_item_id=menu_item_id,
            predicted_demand=new_demand,
        )

        return {
            "scenario": "preparation_reduction",
            "parameters": {"reduction_pct": reduction_pct},
            "base_demand": base,
            "new_demand": new_demand,
            "reduced_portions": round(base - new_demand, 2),
            "recommendation": recommendation,
        }
