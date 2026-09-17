import json
from flask import Blueprint, request, jsonify

from backend.utils.database import db
from backend.models.recipe import Recipe, RecipeIngredient
from backend.models.kitchen import Kitchen
from backend.models.menu import MenuItem
from backend.models.inventory import Inventory
from backend.services.recipe_service import (
    generate_ai_recipe,
    match_recipe_ingredients_with_inventory
)

recipe_bp = Blueprint(
    "recipe",
    __name__,
    url_prefix="/api/recipe"
)


# =====================================================
# 1. GENERATE AI RECIPE (NON-DESTRUCTIVE REVIEW)
# =====================================================

@recipe_bp.route("/generate", methods=["POST"])
def generate_recipe_endpoint():
    """Generate a structured recipe from LLM without saving to database.

    Allows kitchen owner to review, edit, and inspect inventory linkage
    before committing to DB.
    """
    data = request.get_json() or {}

    dish_name = data.get("dish_name") or data.get("food_item_name")
    if not dish_name or not str(dish_name).strip():
        return jsonify({
            "success": False,
            "message": "Dish name is required to generate a recipe."
        }), 400

    kitchen_id = data.get("kitchen_id")
    category = data.get("category")
    target_servings = data.get("target_servings") or data.get("yield_quantity") or 4.0

    try:
        target_servings = float(target_servings)
    except (ValueError, TypeError):
        target_servings = 4.0

    # 1. Generate structured recipe
    recipe_data = generate_ai_recipe(
        dish_name=str(dish_name).strip(),
        category=category,
        target_servings=target_servings
    )

    # 2. If kitchen_id provided, enrich ingredients with live inventory matches
    if kitchen_id:
        try:
            k_id = int(kitchen_id)
            recipe_data["ingredients"] = match_recipe_ingredients_with_inventory(
                k_id,
                recipe_data.get("ingredients", [])
            )
        except (ValueError, TypeError):
            pass

    return jsonify({
        "success": True,
        "recipe": recipe_data
    }), 200


# =====================================================
# 2. SAVE RECIPE (COMMIT TO DATABASE)
# =====================================================

@recipe_bp.route("/", methods=["POST"])
def save_recipe():
    """Save reviewed and edited recipe into database with inventory links."""
    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "No data provided."
        }), 400

    kitchen_id = data.get("kitchen_id")
    food_item_name = data.get("food_item_name") or data.get("dish_name")

    if not kitchen_id or not food_item_name:
        return jsonify({
            "success": False,
            "message": "kitchen_id and food_item_name are required."
        }), 400

    # Verify kitchen
    kitchen = db.session.get(Kitchen, kitchen_id)
    if not kitchen:
        return jsonify({
            "success": False,
            "message": "Kitchen not found."
        }), 404

    # Resolve menu_item_id if provided or auto-detect by name
    menu_item_id = data.get("menu_item_id")
    if not menu_item_id:
        menu_item = MenuItem.query.filter(
            MenuItem.kitchen_id == kitchen_id,
            db.func.lower(MenuItem.name) == food_item_name.strip().lower()
        ).first()
        if menu_item:
            menu_item_id = menu_item.id

    # Parse yield quantity
    try:
        yield_quantity = float(data.get("yield_quantity") or 1.0)
    except (ValueError, TypeError):
        yield_quantity = 1.0

    # Parse prep & cook times
    try:
        prep_time = int(data.get("prep_time_minutes") or 0)
    except (ValueError, TypeError):
        prep_time = 0

    try:
        cook_time = int(data.get("cook_time_minutes") or 0)
    except (ValueError, TypeError):
        cook_time = 0

    # Create recipe instance
    recipe = Recipe(
        kitchen_id=kitchen_id,
        menu_item_id=menu_item_id,
        food_item_name=food_item_name.strip(),
        category=data.get("category"),
        cooking_method=data.get("cooking_method"),
        prep_time_minutes=prep_time,
        cook_time_minutes=cook_time,
        yield_quantity=yield_quantity,
        yield_unit=data.get("yield_unit") or "servings",
        storage_instructions=data.get("storage_instructions") or ""
    )

    # Set preparation steps
    steps = data.get("preparation_steps") or []
    recipe.set_steps_list(steps)

    db.session.add(recipe)
    db.session.flush()  # assign recipe.id

    # Add ingredients
    ingredients_input = data.get("ingredients") or []
    
    # Preload kitchen inventory for auto-linking if inventory_id not provided
    kitchen_inventory = Inventory.query.filter_by(kitchen_id=kitchen_id).all()
    inv_lookup = {inv.ingredient_name.strip().lower(): inv.id for inv in kitchen_inventory}

    for item in ingredients_input:
        if not isinstance(item, dict):
            continue
        ing_name = str(item.get("name") or "").strip()
        if not ing_name:
            continue

        try:
            qty = float(item.get("quantity") or 0.0)
        except (ValueError, TypeError):
            qty = 0.0

        unit = str(item.get("unit") or "g").strip()
        notes = str(item.get("notes") or "").strip()

        # Check explicit inventory_id or matched_inventory_id
        inv_id = item.get("inventory_id") or item.get("matched_inventory_id")
        if not inv_id and ing_name.lower() in inv_lookup:
            inv_id = inv_lookup[ing_name.lower()]

        # Validate that referenced inventory belongs to this kitchen
        if inv_id:
            inv_obj = db.session.get(Inventory, inv_id)
            if not inv_obj or inv_obj.kitchen_id != kitchen_id:
                inv_id = None

        recipe_ing = RecipeIngredient(
            recipe_id=recipe.id,
            inventory_id=inv_id,
            name=ing_name,
            quantity=qty,
            unit=unit,
            notes=notes
        )
        db.session.add(recipe_ing)

    db.session.commit()

    return jsonify({
        "success": True,
        "message": f"Recipe for '{recipe.food_item_name}' saved successfully.",
        "recipe": recipe.to_dict()
    }), 201


# =====================================================
# 3. LIST RECIPES FOR KITCHEN
# =====================================================

@recipe_bp.route("/kitchen/<int:kitchen_id>", methods=["GET"])
def list_kitchen_recipes(kitchen_id):
    """Retrieve all saved recipes for a specific kitchen."""
    kitchen = db.session.get(Kitchen, kitchen_id)
    if not kitchen:
        return jsonify({
            "success": False,
            "message": "Kitchen not found."
        }), 404

    recipes = Recipe.query.filter_by(kitchen_id=kitchen_id).order_by(Recipe.updated_at.desc()).all()

    return jsonify({
        "success": True,
        "count": len(recipes),
        "recipes": [r.to_dict(include_ingredients=True) for r in recipes]
    }), 200


# =====================================================
# 4. GET SINGLE RECIPE DETAILS
# =====================================================

@recipe_bp.route("/<int:recipe_id>", methods=["GET"])
def get_recipe(recipe_id):
    """Retrieve single recipe with ingredients and live inventory statuses."""
    recipe = db.session.get(Recipe, recipe_id)
    if not recipe:
        return jsonify({
            "success": False,
            "message": "Recipe not found."
        }), 404

    return jsonify({
        "success": True,
        "recipe": recipe.to_dict(include_ingredients=True)
    }), 200


# =====================================================
# 5. UPDATE RECIPE
# =====================================================

@recipe_bp.route("/<int:recipe_id>", methods=["PUT"])
def update_recipe(recipe_id):
    """Update an existing recipe and its ingredients."""
    recipe = db.session.get(Recipe, recipe_id)
    if not recipe:
        return jsonify({
            "success": False,
            "message": "Recipe not found."
        }), 404

    data = request.get_json() or {}

    if "food_item_name" in data:
        recipe.food_item_name = str(data["food_item_name"]).strip()
    if "category" in data:
        recipe.category = data["category"]
    if "cooking_method" in data:
        recipe.cooking_method = data["cooking_method"]
    if "prep_time_minutes" in data:
        try:
            recipe.prep_time_minutes = int(data["prep_time_minutes"])
        except (ValueError, TypeError):
            pass
    if "cook_time_minutes" in data:
        try:
            recipe.cook_time_minutes = int(data["cook_time_minutes"])
        except (ValueError, TypeError):
            pass
    if "yield_quantity" in data:
        try:
            recipe.yield_quantity = float(data["yield_quantity"])
        except (ValueError, TypeError):
            pass
    if "yield_unit" in data:
        recipe.yield_unit = data["yield_unit"]
    if "storage_instructions" in data:
        recipe.storage_instructions = data["storage_instructions"]
    if "preparation_steps" in data:
        recipe.set_steps_list(data["preparation_steps"])

    # Update ingredients if passed
    if "ingredients" in data and isinstance(data["ingredients"], list):
        # Remove existing ingredients
        RecipeIngredient.query.filter_by(recipe_id=recipe.id).delete()
        
        kitchen_inventory = Inventory.query.filter_by(kitchen_id=recipe.kitchen_id).all()
        inv_lookup = {inv.ingredient_name.strip().lower(): inv.id for inv in kitchen_inventory}

        for item in data["ingredients"]:
            if not isinstance(item, dict):
                continue
            name = str(item.get("name") or "").strip()
            if not name:
                continue
            try:
                qty = float(item.get("quantity") or 0.0)
            except (ValueError, TypeError):
                qty = 0.0
            unit = str(item.get("unit") or "g").strip()
            notes = str(item.get("notes") or "").strip()
            inv_id = item.get("inventory_id") or item.get("matched_inventory_id")
            if not inv_id and name.lower() in inv_lookup:
                inv_id = inv_lookup[name.lower()]

            new_ing = RecipeIngredient(
                recipe_id=recipe.id,
                inventory_id=inv_id,
                name=name,
                quantity=qty,
                unit=unit,
                notes=notes
            )
            db.session.add(new_ing)

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Recipe updated successfully.",
        "recipe": recipe.to_dict(include_ingredients=True)
    }), 200


# =====================================================
# 6. DELETE RECIPE
# =====================================================

@recipe_bp.route("/<int:recipe_id>", methods=["DELETE"])
def delete_recipe(recipe_id):
    """Delete a recipe and all its ingredients."""
    recipe = db.session.get(Recipe, recipe_id)
    if not recipe:
        return jsonify({
            "success": False,
            "message": "Recipe not found."
        }), 404

    db.session.delete(recipe)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Recipe deleted successfully."
    }), 200


# =====================================================
# 7. DETERMINISTIC DEMAND-TO-INGREDIENT MULTIPLIER
# =====================================================

@recipe_bp.route("/<int:recipe_id>/calculate-requirements", methods=["GET"])
def calculate_requirements(recipe_id):
    """Calculate scaled ingredient quantities for predicted or target portion demand.

    Compares requirements directly with live inventory to flag deficits.
    """
    recipe = db.session.get(Recipe, recipe_id)
    if not recipe:
        return jsonify({
            "success": False,
            "message": "Recipe not found."
        }), 404

    portions_param = request.args.get("portions")
    try:
        portions = float(portions_param) if portions_param else float(recipe.yield_quantity or 1.0)
    except (ValueError, TypeError):
        portions = float(recipe.yield_quantity or 1.0)

    requirements = recipe.calculate_ingredient_requirements(portions)

    return jsonify({
        "success": True,
        "data": requirements
    }), 200

