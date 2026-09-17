import json
import pytest
from app import app
from backend.utils.database import db
from backend.models.kitchen import Kitchen
from backend.models.menu import MenuItem
from backend.models.inventory import Inventory
from backend.models.recipe import Recipe, RecipeIngredient
from backend.services.recipe_service import (
    generate_ai_recipe,
    match_recipe_ingredients_with_inventory
)


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.app_context():
        db.drop_all()
        db.create_all()
        kitchen = Kitchen(name="Recipe Test Kitchen", cuisine_type="Indian", seats=50, meals_per_day=300)
        db.session.add(kitchen)
        db.session.commit()
        kitchen_id = kitchen.id

    with app.test_client() as test_client:
        test_client.kitchen_id = kitchen_id
        yield test_client

    with app.app_context():
        db.session.remove()
        db.drop_all()


def test_recipe_page_route(client):
    """Test frontend page route for recipes renders successfully."""
    response = client.get("/recipes")
    assert response.status_code == 200
    assert b"AI Recipe Management" in response.data


def test_recipe_model_creation_and_cascade(client):
    """Test Recipe and RecipeIngredient models, steps serialization, and cascade delete."""
    kitchen_id = client.kitchen_id

    with app.app_context():
        recipe = Recipe(
            kitchen_id=kitchen_id,
            food_item_name="Vegetable Samosa",
            category="Snacks",
            cooking_method="Deep Frying",
            prep_time_minutes=25,
            cook_time_minutes=20,
            yield_quantity=4.0,
            yield_unit="pieces",
            storage_instructions="Store in dry airtight box."
        )
        recipe.set_steps_list([
            "Prepare the pastry dough with flour and water.",
            "Make spiced potato filling.",
            "Stuff cones and deep fry until crisp."
        ])
        db.session.add(recipe)
        db.session.commit()

        ing1 = RecipeIngredient(
            recipe_id=recipe.id,
            name="Potatoes",
            quantity=300.0,
            unit="g",
            notes="boiled and diced"
        )
        ing2 = RecipeIngredient(
            recipe_id=recipe.id,
            name="Maida",
            quantity=200.0,
            unit="g",
            notes="sifted"
        )
        db.session.add_all([ing1, ing2])
        db.session.commit()

        recipe_id = recipe.id
        assert len(recipe.ingredients) == 2
        assert len(recipe.get_steps_list()) == 3

        # Test dictionary serialization
        data = recipe.to_dict()
        assert data["food_item_name"] == "Vegetable Samosa"
        assert data["ingredient_count"] == 2
        assert data["total_time_minutes"] == 45

        # Test cascade delete: deleting recipe must delete its ingredients
        db.session.delete(recipe)
        db.session.commit()

        assert db.session.get(Recipe, recipe_id) is None
        assert RecipeIngredient.query.filter_by(recipe_id=recipe_id).count() == 0


def test_generate_ai_recipe_structure():
    """Test AI structured recipe generation produces valid schema with fallback."""
    # Known dish (curated domain fallback)
    recipe = generate_ai_recipe("Samosa", category="Snacks", target_servings=4)
    assert recipe is not None
    assert "food_item_name" in recipe
    assert "ingredients" in recipe
    assert len(recipe["ingredients"]) > 0
    assert "preparation_steps" in recipe
    assert len(recipe["preparation_steps"]) > 0
    assert recipe["yield_quantity"] == 4.0

    # Unknown / arbitrary custom dish (procedural domain fallback)
    custom = generate_ai_recipe("Zesty Tofu Taco", category="Snacks", target_servings=6)
    assert custom is not None
    assert "Zesty Tofu Taco" in custom["food_item_name"]
    assert custom["yield_quantity"] == 6.0
    assert len(custom["ingredients"]) >= 5


def test_recipe_api_generate_is_non_destructive(client):
    """Test that generating a recipe via API returns structured JSON without saving to DB."""
    kitchen_id = client.kitchen_id

    response = client.post(
        "/api/recipe/generate",
        json={
            "kitchen_id": kitchen_id,
            "dish_name": "Paneer Butter Masala",
            "category": "Main Course",
            "target_servings": 4
        }
    )

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["success"] is True
    recipe = json_data["recipe"]
    assert "Paneer Butter Masala" in recipe["food_item_name"]
    assert len(recipe["ingredients"]) > 0

    # Verify NON-DESTRUCTIVE: database has zero recipes saved!
    with app.app_context():
        assert Recipe.query.count() == 0
        assert RecipeIngredient.query.count() == 0


def test_recipe_save_and_inventory_auto_matching(client):
    """Test saving a recipe to DB automatically matches and links existing inventory items."""
    kitchen_id = client.kitchen_id

    # Create raw inventory item first
    with app.app_context():
        inv_item = Inventory(
            kitchen_id=kitchen_id,
            ingredient_name="Potatoes",
            quantity=15.0,
            unit="kg",
            minimum_stock=2.0
        )
        db.session.add(inv_item)
        db.session.commit()
        inv_id = inv_item.id

    # Save recipe with "Potatoes" ingredient without passing inventory_id
    save_payload = {
        "kitchen_id": kitchen_id,
        "food_item_name": "Samosa",
        "category": "Snacks",
        "cooking_method": "Deep Frying",
        "prep_time_minutes": 25,
        "cook_time_minutes": 15,
        "yield_quantity": 4,
        "yield_unit": "pieces",
        "storage_instructions": "Keep cool and dry.",
        "preparation_steps": ["Step 1: prep", "Step 2: fry"],
        "ingredients": [
            {"name": "Potatoes", "quantity": 300, "unit": "g", "notes": "mashed"},
            {"name": "Garam Masala", "quantity": 10, "unit": "g", "notes": "ground"}
        ]
    }

    response = client.post("/api/recipe/", json=save_payload)
    assert response.status_code == 201
    res_data = response.get_json()
    assert res_data["success"] is True
    saved_recipe = res_data["recipe"]
    recipe_id = saved_recipe["id"]

    with app.app_context():
        rec = db.session.get(Recipe, recipe_id)
        assert rec is not None
        assert len(rec.ingredients) == 2

        # Check that Potatoes was auto-matched and linked to existing inventory!
        potato_ing = next(i for i in rec.ingredients if i.name == "Potatoes")
        assert potato_ing.inventory_id == inv_id
        assert potato_ing.inventory_item.ingredient_name == "Potatoes"

        # Check Garam Masala is unlinked (inventory_id is None)
        masala_ing = next(i for i in rec.ingredients if i.name == "Garam Masala")
        assert masala_ing.inventory_id is None


def test_recipe_crud_and_deterministic_scaling(client):
    """Test full CRUD endpoints and deterministic demand scaling calculations."""
    kitchen_id = client.kitchen_id

    # Create inventory item
    with app.app_context():
        cheese = Inventory(
            kitchen_id=kitchen_id,
            ingredient_name="Mozzarella Cheese",
            quantity=2.0,  # 2.0 kg
            unit="kg"
        )
        db.session.add(cheese)
        db.session.commit()
        cheese_id = cheese.id

    # 1. Create Recipe
    create_res = client.post(
        "/api/recipe/",
        json={
            "kitchen_id": kitchen_id,
            "food_item_name": "Margherita Pizza",
            "category": "Main Course",
            "cooking_method": "Baking",
            "prep_time_minutes": 20,
            "cook_time_minutes": 15,
            "yield_quantity": 2.0,
            "yield_unit": "pizzas",
            "ingredients": [
                {"name": "Mozzarella Cheese", "quantity": 0.3, "unit": "kg", "inventory_id": cheese_id},
                {"name": "Flour", "quantity": 0.5, "unit": "kg"}
            ],
            "preparation_steps": ["Roll dough", "Top with cheese", "Bake"]
        }
    )
    assert create_res.status_code == 201
    recipe_id = create_res.get_json()["recipe"]["id"]

    # 2. List Recipes
    list_res = client.get(f"/api/recipe/kitchen/{kitchen_id}")
    assert list_res.status_code == 200
    assert list_res.get_json()["count"] == 1

    # 3. Get Single Recipe
    get_res = client.get(f"/api/recipe/{recipe_id}")
    assert get_res.status_code == 200
    assert get_res.get_json()["recipe"]["food_item_name"] == "Margherita Pizza"

    # 4. Deterministic Scaling Calculation:
    # Base yield = 2 pizzas, requires 0.3 kg cheese.
    # Target portions = 10 pizzas -> Multiplier = 5.0
    # Required cheese = 0.3 * 5.0 = 1.5 kg. Available cheese = 2.0 kg -> Sufficient!
    scale_res = client.get(f"/api/recipe/{recipe_id}/calculate-requirements?portions=10")
    assert scale_res.status_code == 200
    scale_data = scale_res.get_json()["data"]
    assert scale_data["target_portions"] == 10.0
    assert scale_data["multiplier"] == 5.0
    cheese_calc = next(i for i in scale_data["ingredients"] if i["name"] == "Mozzarella Cheese")
    assert cheese_calc["scaled_quantity"] == 1.5
    assert cheese_calc["has_sufficient_stock"] is True
    assert cheese_calc["deficit"] == 0.0

    # Target portions = 20 pizzas -> Multiplier = 10.0
    # Required cheese = 0.3 * 10 = 3.0 kg. Available = 2.0 kg -> Deficit of 1.0 kg!
    scale_res_large = client.get(f"/api/recipe/{recipe_id}/calculate-requirements?portions=20")
    scale_data_large = scale_res_large.get_json()["data"]
    assert scale_data_large["missing_stock_count"] == 1
    cheese_calc_large = next(i for i in scale_data_large["ingredients"] if i["name"] == "Mozzarella Cheese")
    assert cheese_calc_large["scaled_quantity"] == 3.0
    assert cheese_calc_large["has_sufficient_stock"] is False
    assert cheese_calc_large["deficit"] == 1.0

    # 5. Update Recipe
    put_res = client.put(
        f"/api/recipe/{recipe_id}",
        json={
            "prep_time_minutes": 25,
            "cooking_method": "Woodfire Oven"
        }
    )
    assert put_res.status_code == 200
    assert put_res.get_json()["recipe"]["prep_time_minutes"] == 25
    assert put_res.get_json()["recipe"]["cooking_method"] == "Woodfire Oven"

    # 6. Delete Recipe
    del_res = client.delete(f"/api/recipe/{recipe_id}")
    assert del_res.status_code == 200
    assert del_res.get_json()["success"] is True

    # Verify deleted
    assert client.get(f"/api/recipe/{recipe_id}").status_code == 404

