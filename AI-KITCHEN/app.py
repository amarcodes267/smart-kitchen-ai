from flask import Flask, render_template
from flask import Flask, render_template, request

from backend.utils.config import Config
from backend.utils.database import db, ensure_schema_compatibility

# Database models
from backend.models import (
    Kitchen,
    MenuItem,
    Inventory,
    Sales,
    Waste,
    Prediction,
    Alert,
    Recipe,
    RecipeIngredient,
)

# API routes
from backend.routes.kitchen import kitchen_bp
from backend.routes.menu import menu_bp
from backend.routes.inventory import inventory_bp
from backend.routes.sales import sales_bp
from backend.routes.waste import waste_bp
from backend.routes.prediction import prediction_bp
from backend.routes.data import data_bp
from backend.routes.preparation import preparation_bp
from backend.routes.demand import demand_bp
from backend.routes.inventory_intelligence import inventory_intelligence_bp
from backend.routes.shopping import shopping_bp
from backend.routes.alerts import alerts_bp
from backend.routes.analytics import analytics_bp
from backend.routes.health_score import health_score_bp
from backend.routes.whatif import whatif_bp
from backend.routes.recipe import recipe_bp


app = Flask(__name__)

# Load configuration
app.config.from_object(Config)

# Initialize database
db.init_app(app)


# Register API blueprints
app.register_blueprint(kitchen_bp)
app.register_blueprint(menu_bp)
app.register_blueprint(inventory_bp)
app.register_blueprint(sales_bp)
app.register_blueprint(waste_bp)
app.register_blueprint(prediction_bp)
app.register_blueprint(data_bp)
app.register_blueprint(preparation_bp)
app.register_blueprint(demand_bp)
app.register_blueprint(inventory_intelligence_bp)
app.register_blueprint(shopping_bp)
app.register_blueprint(alerts_bp)
app.register_blueprint(analytics_bp)
app.register_blueprint(health_score_bp)
app.register_blueprint(whatif_bp)
app.register_blueprint(recipe_bp)



# Create database tables
with app.app_context():
    db.create_all()
    ensure_schema_compatibility()


# =====================================================
# CORS HEADERS
# =====================================================

@app.after_request
def add_cors_headers(response):
    response.headers.setdefault("Access-Control-Allow-Origin", "*")
    response.headers.setdefault(
        "Access-Control-Allow-Methods",
        "GET, POST, PUT, DELETE, OPTIONS"
    )
    response.headers.setdefault(
        "Access-Control-Allow-Headers",
        "Content-Type, Authorization"
    )
    if response.mimetype == "application/json" or (hasattr(request, "path") and request.path.startswith("/api/")):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
    return response


# =====================================================
# FRONTEND PAGE ROUTES
# =====================================================

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/kitchen-setup")
def kitchen_setup():
    return render_template("kitchen_setup.html")


@app.route("/inventory")
def inventory():
    return render_template("inventory.html")


@app.route("/sales")
def sales():
    return render_template("sales.html")


@app.route("/menu")
def menu():
    return render_template("menu.html")


@app.route("/waste")
def waste():
    return render_template("waste.html")


@app.route("/predictions")
def predictions():
    return render_template("predictions.html")


@app.route("/analytics")
def analytics():
    return render_template("analytics.html")


@app.route("/alerts")
def alerts():
    return render_template("alerts.html")


@app.route("/health-score")
def health_score():
    return render_template("health_score.html")


@app.route("/shopping")
def shopping():
    return render_template("shopping.html")


@app.route("/recipes")
def recipes():
    return render_template("recipes.html")



# =====================================================
# HEALTH CHECK
# =====================================================

@app.route("/health")
def health():
    return {
        "status": "healthy",
        "application": "AI Kitchen"
    }


# =====================================================
# RUN APPLICATION
# =====================================================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
