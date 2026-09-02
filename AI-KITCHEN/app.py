from flask import Flask, render_template

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
)

# API routes
from backend.routes.kitchen import kitchen_bp
from backend.routes.menu import menu_bp
from backend.routes.inventory import inventory_bp
from backend.routes.sales import sales_bp
from backend.routes.waste import waste_bp
from backend.routes.prediction import prediction_bp
from backend.routes.recommendation import recommendation_bp
from backend.routes.data import data_bp


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
app.register_blueprint(recommendation_bp)
app.register_blueprint(data_bp)


# Create database tables
with app.app_context():
    db.create_all()
    ensure_schema_compatibility()


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


@app.route("/recommendations")
def recommendations():
    return render_template("recommendations.html")


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
