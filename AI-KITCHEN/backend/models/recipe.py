import json
from backend.utils.database import db


class Recipe(db.Model):
    __tablename__ = "recipes"

    id = db.Column(db.Integer, primary_key=True)

    kitchen_id = db.Column(
        db.Integer,
        db.ForeignKey("kitchens.id"),
        nullable=False
    )

    menu_item_id = db.Column(
        db.Integer,
        db.ForeignKey("menu_items.id"),
        nullable=True
    )

    food_item_name = db.Column(
        db.String(150),
        nullable=False
    )

    category = db.Column(
        db.String(100),
        nullable=True
    )

    cooking_method = db.Column(
        db.String(100),
        nullable=True
    )

    prep_time_minutes = db.Column(
        db.Integer,
        nullable=True,
        default=0
    )

    cook_time_minutes = db.Column(
        db.Integer,
        nullable=True,
        default=0
    )

    yield_quantity = db.Column(
        db.Float,
        nullable=False,
        default=1.0
    )

    yield_unit = db.Column(
        db.String(50),
        nullable=False,
        default="servings"
    )

    preparation_steps = db.Column(
        db.Text,
        nullable=True
    )

    storage_instructions = db.Column(
        db.String(255),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        onupdate=db.func.now()
    )

    # Relationships
    ingredients = db.relationship(
        "RecipeIngredient",
        backref="recipe",
        cascade="all, delete-orphan",
        lazy="joined"
    )

    kitchen = db.relationship(
        "Kitchen",
        backref=db.backref("recipes", lazy="dynamic")
    )

    menu_item = db.relationship(
        "MenuItem",
        backref=db.backref("recipes", lazy="dynamic")
    )

    def get_steps_list(self):
        """Parse preparation_steps into a clean list of strings."""
        if not self.preparation_steps:
            return []
        try:
            parsed = json.loads(self.preparation_steps)
            if isinstance(parsed, list):
                return [str(step).strip() for step in parsed if step]
            return [str(parsed).strip()]
        except (json.JSONDecodeError, TypeError):
            # If plain text with newlines
            return [
                line.strip().lstrip("0123456789.-) ")
                for line in self.preparation_steps.splitlines()
                if line.strip()
            ]

    def set_steps_list(self, steps):
        """Serialize a list of step strings into JSON format."""
        if isinstance(steps, list):
            self.preparation_steps = json.dumps([str(s).strip() for s in steps if s])
        elif isinstance(steps, str):
            # Check if it's already JSON
            try:
                parsed = json.loads(steps)
                if isinstance(parsed, list):
                    self.preparation_steps = json.dumps(parsed)
                    return
            except (json.JSONDecodeError, TypeError):
                pass
            lines = [l.strip() for l in steps.splitlines() if l.strip()]
            self.preparation_steps = json.dumps(lines)
        else:
            self.preparation_steps = json.dumps([])

    def to_dict(self, include_ingredients=True):
        data = {
            "id": self.id,
            "kitchen_id": self.kitchen_id,
            "menu_item_id": self.menu_item_id,
            "food_item_name": self.food_item_name,
            "category": self.category,
            "cooking_method": self.cooking_method,
            "prep_time_minutes": self.prep_time_minutes or 0,
            "cook_time_minutes": self.cook_time_minutes or 0,
            "total_time_minutes": (self.prep_time_minutes or 0) + (self.cook_time_minutes or 0),
            "yield_quantity": float(self.yield_quantity or 1.0),
            "yield_unit": self.yield_unit or "servings",
            "preparation_steps": self.get_steps_list(),
            "storage_instructions": self.storage_instructions or "",
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

        if self.menu_item:
            data["menu_item_name"] = self.menu_item.name
        else:
            data["menu_item_name"] = None

        if include_ingredients:
            data["ingredients"] = [ing.to_dict() for ing in (self.ingredients or [])]
            data["ingredient_count"] = len(self.ingredients or [])
        else:
            data["ingredient_count"] = len(self.ingredients or [])

        return data

    def calculate_ingredient_requirements(self, target_portions):
        """Deterministic ingredient calculation for forecasted portion demand."""
        try:
            target_portions = float(target_portions)
        except (ValueError, TypeError):
            target_portions = float(self.yield_quantity or 1.0)

        base_yield = float(self.yield_quantity or 1.0)
        if base_yield <= 0:
            base_yield = 1.0

        multiplier = target_portions / base_yield

        scaled_ingredients = []
        total_items = len(self.ingredients)
        linked_items = 0
        missing_stock_count = 0

        for ing in self.ingredients:
            scaled_qty = round(float(ing.quantity or 0.0) * multiplier, 3)
            current_stock = None
            is_linked = False
            has_sufficient_stock = None
            deficit = 0.0

            if ing.inventory_item:
                is_linked = True
                linked_items += 1
                current_stock = float(ing.inventory_item.quantity or 0.0)
                if current_stock >= scaled_qty:
                    has_sufficient_stock = True
                else:
                    has_sufficient_stock = False
                    deficit = round(scaled_qty - current_stock, 3)
                    missing_stock_count += 1

            scaled_ingredients.append({
                "recipe_ingredient_id": ing.id,
                "name": ing.name,
                "base_quantity": ing.quantity,
                "scaled_quantity": scaled_qty,
                "unit": ing.unit,
                "notes": ing.notes,
                "inventory_id": ing.inventory_id,
                "is_linked": is_linked,
                "current_stock": current_stock,
                "has_sufficient_stock": has_sufficient_stock,
                "deficit": deficit
            })

        return {
            "recipe_id": self.id,
            "food_item_name": self.food_item_name,
            "base_yield": base_yield,
            "target_portions": target_portions,
            "multiplier": round(multiplier, 3),
            "total_ingredients": total_items,
            "linked_ingredients": linked_items,
            "missing_stock_count": missing_stock_count,
            "ingredients": scaled_ingredients
        }


class RecipeIngredient(db.Model):
    __tablename__ = "recipe_ingredients"

    id = db.Column(db.Integer, primary_key=True)

    recipe_id = db.Column(
        db.Integer,
        db.ForeignKey("recipes.id"),
        nullable=False
    )

    inventory_id = db.Column(
        db.Integer,
        db.ForeignKey("inventory.id"),
        nullable=True
    )

    name = db.Column(
        db.String(150),
        nullable=False
    )

    quantity = db.Column(
        db.Float,
        nullable=False,
        default=0.0
    )

    unit = db.Column(
        db.String(50),
        nullable=False,
        default="g"
    )

    notes = db.Column(
        db.String(255),
        nullable=True
    )

    # Relationship to Inventory
    inventory_item = db.relationship(
        "Inventory",
        backref=db.backref("recipe_ingredients", lazy="dynamic")
    )

    def to_dict(self):
        data = {
            "id": self.id,
            "recipe_id": self.recipe_id,
            "inventory_id": self.inventory_id,
            "name": self.name,
            "quantity": float(self.quantity or 0.0),
            "unit": self.unit or "g",
            "notes": self.notes or "",
            "is_linked": self.inventory_id is not None,
            "inventory_name": None,
            "current_stock": None,
            "stock_unit": None,
        }

        if self.inventory_item:
            data["inventory_name"] = self.inventory_item.ingredient_name
            data["current_stock"] = float(self.inventory_item.quantity or 0.0)
            data["stock_unit"] = self.inventory_item.unit

        return data

