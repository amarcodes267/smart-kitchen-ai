from backend.services.inventory_intelligence_service import InventoryIntelligence


class ShoppingListGenerator:
    def generate(self, kitchen_id):
        intelligence = InventoryIntelligence()
        analysis = intelligence.analyze_kitchen_inventory(kitchen_id)

        shopping_items = []

        for item in analysis["items"]:
            if item["status"] in ("critical", "low"):
                shopping_items.append({
                    "ingredient": item["ingredient_name"],
                    "current": item["current_qty"],
                    "unit": item["unit"],
                    "required": round(item["current_qty"] + item["restock_qty"], 2),
                    "action": f"Buy {item['restock_qty']} {item['unit']}",
                    "priority": "high" if item["status"] == "critical" else "medium",
                })
            elif item["status"] == "excess":
                shopping_items.append({
                    "ingredient": item["ingredient_name"],
                    "current": item["current_qty"],
                    "unit": item["unit"],
                    "required": round(item["current_qty"] - item["excess"], 2),
                    "action": "No purchase — reduce usage",
                    "priority": "low",
                })
            else:
                shopping_items.append({
                    "ingredient": item["ingredient_name"],
                    "current": item["current_qty"],
                    "unit": item["unit"],
                    "required": item["current_qty"],
                    "action": "No purchase needed",
                    "priority": "none",
                })

        return {
            "kitchen_id": kitchen_id,
            "generated_at": analysis["generated_at"],
            "items": shopping_items,
            "summary": {
                "to_buy": len([i for i in shopping_items if i["priority"] in ("high", "medium")]),
                "no_purchase": len([i for i in shopping_items if i["priority"] == "none"]),
                "reduce_usage": len([i for i in shopping_items if i["priority"] == "low"]),
            },
        }
