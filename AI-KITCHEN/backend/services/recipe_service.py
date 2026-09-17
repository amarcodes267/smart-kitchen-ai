import json
import logging
import re
from backend.models.inventory import Inventory
from backend.utils.config import Config

logger = logging.getLogger(__name__)

# =====================================================
# CURATED CULINARY KNOWLEDGE BASE (DOMAIN FALLBACK)
# =====================================================

RECIPE_KNOWLEDGE_BASE = {
    "samosa": {
        "food_item_name": "Samosa",
        "category": "Snacks",
        "cooking_method": "Deep Frying",
        "prep_time_minutes": 30,
        "cook_time_minutes": 20,
        "yield_quantity": 4,
        "yield_unit": "pieces",
        "storage_instructions": "Store in an airtight container for up to 2 days; reheat in oven/air fryer.",
        "ingredients": [
            {"name": "Potatoes", "quantity": 350.0, "unit": "g", "notes": "Boiled, peeled, and diced"},
            {"name": "Green Peas", "quantity": 80.0, "unit": "g", "notes": "Steamed or thawed"},
            {"name": "All Purpose Flour (Maida)", "quantity": 250.0, "unit": "g", "notes": "Sifted for pastry crust"},
            {"name": "Cooking Oil", "quantity": 500.0, "unit": "ml", "notes": "For deep frying + 2 tbsp for dough"},
            {"name": "Cumin Seeds", "quantity": 5.0, "unit": "g", "notes": "Whole spice for tempering"},
            {"name": "Garam Masala", "quantity": 5.0, "unit": "g", "notes": "Ground spice mix"},
            {"name": "Green Chillies", "quantity": 10.0, "unit": "g", "notes": "Finely chopped"},
            {"name": "Ginger", "quantity": 15.0, "unit": "g", "notes": "Freshly grated"},
            {"name": "Salt", "quantity": 8.0, "unit": "g", "notes": "To taste"}
        ],
        "preparation_steps": [
            "Knead all-purpose flour, oil, carom seeds (ajwain), salt, and cold water into a stiff dough. Rest covered for 20 minutes.",
            "Heat 1 tbsp oil in a pan, add cumin seeds, grated ginger, and chopped green chillies until aromatic.",
            "Add boiled diced potatoes, green peas, garam masala, chili powder, and salt. Sauté for 4-5 minutes, then cool completely.",
            "Divide dough into smooth balls, roll into ovals, cut into halves, form cones, and stuff with spiced potato filling.",
            "Seal edges with a touch of water, pressing firmly into a pyramid shape.",
            "Deep fry in medium-hot oil until crisp and golden brown on all sides (approx 12-15 minutes). Drain and serve hot with chutney."
        ]
    },
    "biryani": {
        "food_item_name": "Chicken Biryani",
        "category": "Main Course",
        "cooking_method": "Dum Cooking (Slow Steam)",
        "prep_time_minutes": 35,
        "cook_time_minutes": 45,
        "yield_quantity": 4,
        "yield_unit": "servings",
        "storage_instructions": "Refrigerate in a sealed container up to 3 days; steam or microwave with a splash of water.",
        "ingredients": [
            {"name": "Basmati Rice", "quantity": 500.0, "unit": "g", "notes": "Long-grain, soaked for 30 minutes"},
            {"name": "Chicken", "quantity": 700.0, "unit": "g", "notes": "Bone-in curry cut pieces"},
            {"name": "Onions", "quantity": 300.0, "unit": "g", "notes": "Thinly sliced and browned (Birista)"},
            {"name": "Yogurt (Curd)", "quantity": 200.0, "unit": "g", "notes": "Whisked smooth for marinade"},
            {"name": "Ginger Garlic Paste", "quantity": 30.0, "unit": "g", "notes": "Freshly blended"},
            {"name": "Biryani Masala", "quantity": 15.0, "unit": "g", "notes": "Aromatic whole spice blend"},
            {"name": "Mint Leaves", "quantity": 25.0, "unit": "g", "notes": "Freshly torn"},
            {"name": "Coriander Leaves", "quantity": 25.0, "unit": "g", "notes": "Chopped"},
            {"name": "Ghee", "quantity": 60.0, "unit": "g", "notes": "Clarified butter for layering"},
            {"name": "Cooking Oil", "quantity": 50.0, "unit": "ml", "notes": "For frying onions and chicken"},
            {"name": "Saffron Milk", "quantity": 50.0, "unit": "ml", "notes": "Saffron strands steeped in warm milk"},
            {"name": "Salt", "quantity": 15.0, "unit": "g", "notes": "For rice water and marinade"}
        ],
        "preparation_steps": [
            "Marinate chicken pieces with yogurt, ginger-garlic paste, red chili powder, turmeric, biryani masala, half the fried onions, and salt for 1 hour.",
            "Boil water with whole spices (cardamom, cinnamon, cloves, bay leaf) and generous salt. Cook soaked basmati rice until 70% done, then drain.",
            "Sear the marinated chicken in a heavy-bottomed handi until partially cooked (about 10 minutes).",
            "Layer 70% parboiled rice evenly over the chicken base.",
            "Top with remaining browned onions, fresh mint, coriander, saffron milk, and generous spoonfuls of melted ghee.",
            "Seal the handi with foil or dough and a tight lid. Cook on high for 5 minutes, then transfer to low heat (dum) on a tawa for 25 minutes.",
            "Let rest for 10 minutes before gently fluffing and serving with raita."
        ]
    },
    "paneer butter masala": {
        "food_item_name": "Paneer Butter Masala",
        "category": "Main Course",
        "cooking_method": "Simmering",
        "prep_time_minutes": 20,
        "cook_time_minutes": 25,
        "yield_quantity": 4,
        "yield_unit": "servings",
        "storage_instructions": "Refrigerate up to 3 days in an airtight container.",
        "ingredients": [
            {"name": "Paneer", "quantity": 400.0, "unit": "g", "notes": "Fresh cottage cheese cut into cubes"},
            {"name": "Tomatoes", "quantity": 400.0, "unit": "g", "notes": "Ripe red, pureed smooth"},
            {"name": "Onions", "quantity": 150.0, "unit": "g", "notes": "Finely chopped"},
            {"name": "Butter", "quantity": 50.0, "unit": "g", "notes": "Unsalted dairy butter"},
            {"name": "Fresh Cream", "quantity": 60.0, "unit": "ml", "notes": "Heavy cooking cream"},
            {"name": "Cashews", "quantity": 30.0, "unit": "g", "notes": "Soaked and ground to a fine paste"},
            {"name": "Ginger Garlic Paste", "quantity": 20.0, "unit": "g", "notes": "Freshly ground"},
            {"name": "Kasuri Methi", "quantity": 5.0, "unit": "g", "notes": "Dried fenugreek leaves, crushed"},
            {"name": "Garam Masala", "quantity": 5.0, "unit": "g", "notes": "Kitchen blend"},
            {"name": "Kashmiri Red Chili Powder", "quantity": 10.0, "unit": "g", "notes": "For vibrant color"},
            {"name": "Salt", "quantity": 8.0, "unit": "g", "notes": "To taste"}
        ],
        "preparation_steps": [
            "Melt 2 tbsp butter with 1 tsp oil in a pan. Sauté chopped onions until golden translucent.",
            "Add ginger-garlic paste and sauté for 1 minute until raw aroma dissipates.",
            "Pour in smooth tomato puree, Kashmiri red chili powder, turmeric, and salt. Cook until butter separates from masala (approx 10 minutes).",
            "Stir in smooth cashew paste and 1/2 cup water. Simmer on low heat for 5 minutes into a silky makhani gravy.",
            "Gently fold in fresh paneer cubes and simmer for 3 minutes without overcooking.",
            "Finish with fresh cream, crushed kasuri methi, and remaining dollop of butter. Serve piping hot with naan or rice."
        ]
    },
    "margherita pizza": {
        "food_item_name": "Margherita Pizza",
        "category": "Main Course",
        "cooking_method": "Baking",
        "prep_time_minutes": 25,
        "cook_time_minutes": 15,
        "yield_quantity": 2,
        "yield_unit": "pizzas",
        "storage_instructions": "Store leftover slices wrapped in foil in the fridge up to 3 days; reheat on a hot skillet.",
        "ingredients": [
            {"name": "Pizza Dough", "quantity": 400.0, "unit": "g", "notes": "Fermented yeast dough"},
            {"name": "Mozzarella Cheese", "quantity": 250.0, "unit": "g", "notes": "Fresh shredded or torn"},
            {"name": "Pizza Sauce (Crushed Tomatoes)", "quantity": 180.0, "unit": "g", "notes": "Seasoned San Marzano tomato sauce"},
            {"name": "Fresh Basil Leaves", "quantity": 15.0, "unit": "g", "notes": "Whole fresh sweet basil"},
            {"name": "Extra Virgin Olive Oil", "quantity": 25.0, "unit": "ml", "notes": "For drizzling"},
            {"name": "Garlic", "quantity": 10.0, "unit": "g", "notes": "Minced into sauce"},
            {"name": "Salt & Black Pepper", "quantity": 5.0, "unit": "g", "notes": "Seasoning"}
        ],
        "preparation_steps": [
            "Preheat oven or pizza stone to maximum temperature (240°C - 260°C / 475°F - 500°F).",
            "Stretch out fermented dough ball on a semolina-dusted counter into a 10-12 inch round with a raised rim (cornicione).",
            "Spread crushed tomato sauce evenly, leaving 1/2 inch border around edges.",
            "Distribute mozzarella cheese evenly across the sauce base.",
            "Bake on preheated stone or tray for 10-14 minutes until crust is charred and cheese is bubbling golden.",
            "Remove from oven, immediately scatter fresh basil leaves, drizzle with extra virgin olive oil, slice and serve immediately."
        ]
    },
    "burger": {
        "food_item_name": "Classic Cheeseburger",
        "category": "Main Course",
        "cooking_method": "Grilling",
        "prep_time_minutes": 15,
        "cook_time_minutes": 10,
        "yield_quantity": 2,
        "yield_unit": "burgers",
        "storage_instructions": "Best served fresh; assemble immediately before consumption.",
        "ingredients": [
            {"name": "Burger Buns", "quantity": 2.0, "unit": "pcs", "notes": "Brioche buns, halved"},
            {"name": "Burger Patty", "quantity": 300.0, "unit": "g", "notes": "Beef or vegetable patty (150g each)"},
            {"name": "Cheddar Cheese Slices", "quantity": 2.0, "unit": "pcs", "notes": "Melted over patties"},
            {"name": "Lettuce Leaves", "quantity": 40.0, "unit": "g", "notes": "Crisp iceberg or romaine"},
            {"name": "Tomatoes", "quantity": 80.0, "unit": "g", "notes": "Thickly sliced"},
            {"name": "Red Onion", "quantity": 40.0, "unit": "g", "notes": "Thinly sliced rings"},
            {"name": "Burger Sauce / Mayo", "quantity": 40.0, "unit": "g", "notes": "Special house spread"},
            {"name": "Butter", "quantity": 15.0, "unit": "g", "notes": "For toasting buns"}
        ],
        "preparation_steps": [
            "Lightly butter cut sides of brioche buns and toast on a hot flat-top skillet until golden brown.",
            "Season patties generously with salt and pepper. Sear on high-heat grill or cast-iron griddle for 3-4 minutes per side.",
            "Place cheddar cheese slice on top of each patty during the last minute of cooking; cover with lid to melt.",
            "Spread sauce on bottom bun, layer with crisp lettuce and tomato slices.",
            "Place hot cheesy patty on top, crown with red onion rings, spread sauce on top bun, and close."
        ]
    },
    "pasta": {
        "food_item_name": "Fettuccine Alfredo",
        "category": "Main Course",
        "cooking_method": "Boiling & Sautéing",
        "prep_time_minutes": 10,
        "cook_time_minutes": 15,
        "yield_quantity": 3,
        "yield_unit": "servings",
        "storage_instructions": "Refrigerate up to 2 days; loosen with a splash of milk when reheating.",
        "ingredients": [
            {"name": "Fettuccine Pasta", "quantity": 350.0, "unit": "g", "notes": "Durum wheat semolina pasta"},
            {"name": "Heavy Cream", "quantity": 250.0, "unit": "ml", "notes": "Whipping or cooking cream"},
            {"name": "Butter", "quantity": 50.0, "unit": "g", "notes": "Unsalted high-fat butter"},
            {"name": "Parmesan Cheese", "quantity": 80.0, "unit": "g", "notes": "Freshly grated Parmigiano-Reggiano"},
            {"name": "Garlic", "quantity": 15.0, "unit": "g", "notes": "Minced"},
            {"name": "Black Pepper", "quantity": 4.0, "unit": "g", "notes": "Freshly cracked"},
            {"name": "Salt", "quantity": 10.0, "unit": "g", "notes": "For pasta boiling water"}
        ],
        "preparation_steps": [
            "Boil pasta in salted rolling water until al dente (approx 8-10 minutes). Reserve 1/2 cup pasta water, then drain.",
            "In a large deep skillet, melt butter over medium heat, add minced garlic, and cook for 1 minute until fragrant.",
            "Pour in heavy cream and gently simmer for 3 minutes until slightly reduced.",
            "Turn heat to lowest, stir in freshly grated parmesan cheese until silky smooth and emulsified.",
            "Toss cooked fettuccine into the sauce, adding a splash of pasta water to achieve glossy consistency.",
            "Season with cracked black pepper and serve immediately with extra parmesan."
        ]
    }
}


def _get_curated_fallback(dish_name: str, category: str = None, target_servings: float = 4.0) -> dict:
    """Find closest match in curated recipes or dynamically construct a culinary recipe."""
    normalized = dish_name.strip().lower()

    # Direct match or substring match in curated library
    for key, recipe_data in RECIPE_KNOWLEDGE_BASE.items():
        if key in normalized or normalized in key:
            recipe_copy = json.loads(json.dumps(recipe_data))
            # Scale yield if different
            orig_yield = recipe_copy["yield_quantity"]
            if target_servings and target_servings > 0 and orig_yield > 0:
                scale = float(target_servings) / float(orig_yield)
                recipe_copy["yield_quantity"] = float(target_servings)
                for ing in recipe_copy["ingredients"]:
                    ing["quantity"] = round(float(ing["quantity"]) * scale, 2)
            if category:
                recipe_copy["category"] = category
            return recipe_copy

    # Algorithmic procedural generator for any custom dish name
    title_case_name = dish_name.strip().title()
    assigned_cat = category or "Main Course"
    
    return {
        "food_item_name": title_case_name,
        "category": assigned_cat,
        "cooking_method": "Sautéing & Simmering",
        "prep_time_minutes": 20,
        "cook_time_minutes": 25,
        "yield_quantity": float(target_servings or 4),
        "yield_unit": "servings",
        "storage_instructions": "Store in an airtight container in refrigerator up to 3 days.",
        "ingredients": [
            {"name": f"Main Protein/Vegetable for {title_case_name}", "quantity": round(150.0 * (target_servings or 4), 1), "unit": "g", "notes": "Freshly prepped and cut"},
            {"name": "Onions", "quantity": round(60.0 * (target_servings or 4), 1), "unit": "g", "notes": "Finely diced"},
            {"name": "Tomatoes", "quantity": round(50.0 * (target_servings or 4), 1), "unit": "g", "notes": "Chopped or pureed"},
            {"name": "Cooking Oil / Butter", "quantity": round(15.0 * (target_servings or 4), 1), "unit": "ml", "notes": "For cooking base"},
            {"name": "Garlic & Ginger", "quantity": round(8.0 * (target_servings or 4), 1), "unit": "g", "notes": "Minced aromatics"},
            {"name": "House Spice Blend", "quantity": round(5.0 * (target_servings or 4), 1), "unit": "g", "notes": "Seasoning to profile"},
            {"name": "Salt", "quantity": round(3.0 * (target_servings or 4), 1), "unit": "g", "notes": "To taste"}
        ],
        "preparation_steps": [
            f"Prep and wash all ingredients for {title_case_name}.",
            "Heat cooking fat in pan; sauté aromatics (garlic, ginger, onions) until golden and fragrant.",
            "Add spice seasonings and tomatoes; cook until sauce base thickens and oil releases.",
            f"Fold in prepped main ingredients for {title_case_name} and cook thoroughly until tender.",
            "Adjust seasoning with salt and herbs, garnish, and serve hot."
        ]
    }


# =====================================================
# AI RECIPE GENERATOR
# =====================================================

def generate_ai_recipe(dish_name: str, category: str = None, target_servings: float = 4.0) -> dict:
    """Generate a structured culinary recipe using Gemini LLM with culinary fallback.

    Args:
        dish_name: Name of the food item or dish.
        category: Optional category hint (e.g. Snacks, Curry, Main Course).
        target_servings: Number of portions/yield desired (default 4).

    Returns:
        dict: Standardized recipe structure with ingredients and preparation steps.
    """
    dish_clean = dish_name.strip()
    servings = float(target_servings or 4)

    api_key = getattr(Config, "GEMINI_API_KEY", "").strip()

    if api_key and api_key.startswith("AIzaSy"):
        try:
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.0-flash")

            prompt = f"""You are a master executive chef and professional commercial kitchen recipe developer.
Create a detailed, precise, commercial-grade culinary recipe for: "{dish_clean}".
Optional Category Hint: "{category or 'General'}"
Target Yield: {servings} servings/portions.

You MUST respond strictly with a valid JSON object. Do not include markdown ticks, explanation text, or conversational intro.
The JSON must adhere exactly to this schema:
{{
  "food_item_name": "{dish_clean}",
  "category": "Main Course | Snacks | Bakery | Beverage | Dessert | Appetizer",
  "cooking_method": "e.g. Deep Frying | Baking | Simmering | Grilling | Sautéing | Steaming",
  "prep_time_minutes": 25,
  "cook_time_minutes": 20,
  "yield_quantity": {servings},
  "yield_unit": "servings | pieces | portions | bowls",
  "storage_instructions": "Clear storage temperature and shelf life instructions.",
  "ingredients": [
    {{
      "name": "Standard Ingredient Name",
      "quantity": 100.0,
      "unit": "g | kg | ml | L | pcs | tbsp | tsp",
      "notes": "prep note (e.g. chopped, boiled, finely diced)"
    }}
  ],
  "preparation_steps": [
    "Step 1: clear actionable instruction...",
    "Step 2: next instruction..."
  ]
}}

Guidelines:
- Quantities must be numeric floats or ints (e.g. 250, not '1 cup').
- Units must be standard commercial units (g, kg, ml, L, pcs, tbsp, tsp).
- Every ingredient must be realistic for commercial kitchen inventory tracking.
- Return ONLY the JSON object.
"""
            response = model.generate_content(
                prompt,
                generation_config={"max_output_tokens": 1200, "temperature": 0.3},
                request_options={"timeout": 15},
            )
            raw_text = getattr(response, "text", "").strip()
            
            # Extract JSON block
            match = re.search(r"\{.*\}", raw_text, re.DOTALL)
            if match:
                parsed = json.loads(match.group(0))
                validated = _validate_and_sanitize_recipe(parsed, dish_clean, servings)
                if validated:
                    return validated

        except Exception as e:
            logger.warning(f"Live Gemini call failed for recipe '{dish_clean}': {e}. Using culinary fallback.")

    # Fallback when no API key or upon failure
    return _get_curated_fallback(dish_clean, category, servings)


def _validate_and_sanitize_recipe(raw_dict: dict, fallback_name: str, fallback_yield: float) -> dict:
    """Validate structure and data types of raw recipe dictionary."""
    if not isinstance(raw_dict, dict):
        return None

    food_item_name = str(raw_dict.get("food_item_name") or fallback_name).strip()
    category = str(raw_dict.get("category") or "Main Course").strip()
    cooking_method = str(raw_dict.get("cooking_method") or "Cooked").strip()
    
    try:
        prep_time = int(raw_dict.get("prep_time_minutes") or 15)
    except (ValueError, TypeError):
        prep_time = 15

    try:
        cook_time = int(raw_dict.get("cook_time_minutes") or 20)
    except (ValueError, TypeError):
        cook_time = 20

    try:
        yield_qty = float(raw_dict.get("yield_quantity") or fallback_yield or 4.0)
    except (ValueError, TypeError):
        yield_qty = 4.0

    yield_unit = str(raw_dict.get("yield_unit") or "servings").strip()
    storage_inst = str(raw_dict.get("storage_instructions") or "Keep refrigerated in airtight container.").strip()

    raw_ingredients = raw_dict.get("ingredients")
    if not isinstance(raw_ingredients, list) or len(raw_ingredients) == 0:
        return None

    sanitized_ingredients = []
    for item in raw_ingredients:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name") or "").strip()
        if not name:
            continue
        try:
            qty = float(item.get("quantity") or 0.0)
        except (ValueError, TypeError):
            qty = 1.0
        unit = str(item.get("unit") or "g").strip()
        notes = str(item.get("notes") or "").strip()
        sanitized_ingredients.append({
            "name": name,
            "quantity": qty,
            "unit": unit,
            "notes": notes
        })

    if not sanitized_ingredients:
        return None

    raw_steps = raw_dict.get("preparation_steps")
    sanitized_steps = []
    if isinstance(raw_steps, list):
        for s in raw_steps:
            cleaned = str(s).strip().lstrip("0123456789.-) ")
            if cleaned:
                sanitized_steps.append(cleaned)
    elif isinstance(raw_steps, str):
        sanitized_steps = [
            l.strip().lstrip("0123456789.-) ")
            for l in raw_steps.splitlines()
            if l.strip()
        ]

    if not sanitized_steps:
        sanitized_steps = [f"Prepare {food_item_name} following standard culinary procedure."]

    return {
        "food_item_name": food_item_name,
        "category": category,
        "cooking_method": cooking_method,
        "prep_time_minutes": prep_time,
        "cook_time_minutes": cook_time,
        "yield_quantity": yield_qty,
        "yield_unit": yield_unit,
        "storage_instructions": storage_inst,
        "ingredients": sanitized_ingredients,
        "preparation_steps": sanitized_steps
    }


# =====================================================
# INVENTORY MATCHING & ENRICHMENT
# =====================================================

def match_recipe_ingredients_with_inventory(kitchen_id: int, ingredients: list) -> list:
    """Enrich an ingredient list with live inventory stock and matching status."""
    if not kitchen_id or not ingredients:
        return ingredients

    # Load all inventory items for this kitchen
    inventory_items = Inventory.query.filter_by(kitchen_id=kitchen_id).all()
    
    # Build lookup maps for exact and normalized token matching
    inv_map = {}
    for inv in inventory_items:
        clean_name = inv.ingredient_name.strip().lower()
        inv_map[clean_name] = inv

    enriched = []
    for ing in ingredients:
        ing_copy = dict(ing)
        ing_name = str(ing.get("name") or "").strip().lower()
        matched_inv = None

        # 1. Exact match
        if ing_name in inv_map:
            matched_inv = inv_map[ing_name]
        else:
            # 2. Singular / Plural / Token overlap
            ing_tokens = set(re.findall(r"\w+", ing_name))
            for inv_key, inv_obj in inv_map.items():
                inv_tokens = set(re.findall(r"\w+", inv_key))
                # Check for significant token overlap (e.g. 'potato' in 'potatoes')
                if ing_name in inv_key or inv_key in ing_name:
                    matched_inv = inv_obj
                    break
                # Plural/singular checks (e.g. onion vs onions, tomato vs tomatoes)
                if ing_name.rstrip('s') == inv_key.rstrip('s') or ing_name.rstrip('es') == inv_key.rstrip('es'):
                    matched_inv = inv_obj
                    break
                if len(ing_tokens.intersection(inv_tokens)) >= 1 and len(inv_tokens) <= 2:
                    matched_inv = inv_obj
                    break

        if matched_inv:
            ing_copy["is_linked"] = True
            ing_copy["matched_inventory_id"] = matched_inv.id
            ing_copy["matched_inventory_name"] = matched_inv.ingredient_name
            ing_copy["current_stock"] = float(matched_inv.quantity or 0.0)
            ing_copy["stock_unit"] = matched_inv.unit
        else:
            ing_copy["is_linked"] = False
            ing_copy["matched_inventory_id"] = None
            ing_copy["matched_inventory_name"] = None
            ing_copy["current_stock"] = None
            ing_copy["stock_unit"] = None

        enriched.append(ing_copy)

    return enriched

