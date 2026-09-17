import pytest
import sys
import os
from datetime import date, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app
from backend.utils.database import db
from backend.models.kitchen import Kitchen
from backend.models.menu import MenuItem
from backend.models.inventory import Inventory
from backend.models.sales import Sales
from backend.models.waste import Waste
from backend.models.prediction import Prediction


@pytest.fixture(autouse=True)
def clean_db():
    with app.app_context():
        db.drop_all()
        db.create_all()
    yield
    with app.app_context():
        db.session.remove()


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


# ============================================================================
# 1. HTML PAGE ROUTES
# ============================================================================

def test_all_14_html_page_routes(client):
    pages = [
        "/",
        "/dashboard",
        "/kitchen-setup",
        "/menu",
        "/inventory",
        "/sales",
        "/waste",
        "/predictions",
        "/health-score",
        "/alerts",
        "/shopping",
        "/analytics",
    ]
    for page in pages:
        res = client.get(page)
        assert res.status_code == 200, f"Page {page} failed with {res.status_code}"
        assert "text/html" in res.content_type, f"Page {page} returned non-HTML {res.content_type}"


# ============================================================================
# 2. CORS HEADERS
# ============================================================================

def test_cors_headers_present(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.headers.get("Access-Control-Allow-Origin") == "*"
    assert "GET" in res.headers.get("Access-Control-Allow-Methods", "")


# ============================================================================
# 3. KITCHEN & MENU CRUD WITH VALIDATION
# ============================================================================

def test_kitchen_and_menu_crud(client):
    # Kitchen creation without name -> 400
    bad_res = client.post("/api/kitchen/", json={"seats": 20})
    assert bad_res.status_code == 400

    # Kitchen creation valid with seed_demo: False
    k_res = client.post("/api/kitchen/", json={
        "name": "QA Master Kitchen",
        "cuisine_type": "Fusion",
        "seats": 30,
        "meals_per_day": 120,
        "seed_demo": False
    })
    assert k_res.status_code == 201
    k_data = k_res.get_json()
    assert k_data["success"] is True
    kitchen_id = k_data["kitchen"]["id"]

    # Get kitchens list
    list_res = client.get("/api/kitchen/")
    assert list_res.status_code == 200
    assert len(list_res.get_json()["kitchens"]) == 1

    # Get single kitchen
    single_res = client.get(f"/api/kitchen/{kitchen_id}")
    assert single_res.status_code == 200
    assert single_res.get_json()["kitchen"]["name"] == "QA Master Kitchen"

    # Menu item negative price -> 400
    neg_res = client.post("/api/menu/", json={"kitchen_id": kitchen_id, "name": "Curry", "price": -10})
    assert neg_res.status_code == 400

    # Menu item negative cost -> 400
    neg_cost_res = client.post("/api/menu/", json={"kitchen_id": kitchen_id, "name": "Curry", "cost_per_serving": -5})
    assert neg_cost_res.status_code == 400

    # Menu item for non-existent kitchen -> 404
    non_k = client.post("/api/menu/", json={"kitchen_id": 9999, "name": "Ghost Item"})
    assert non_k.status_code == 404

    # Valid menu items
    m1_res = client.post("/api/menu/", json={"kitchen_id": kitchen_id, "name": "Paneer Tikka", "category": "Starters", "price": 250, "cost_per_serving": 100})
    assert m1_res.status_code == 201

    m2_res = client.post("/api/menu/", json={"kitchen_id": kitchen_id, "name": "Butter Naan", "category": "Breads", "price": 50, "cost_per_serving": 15})
    assert m2_res.status_code == 201

    # Get menu items
    m_list = client.get(f"/api/menu/{kitchen_id}")
    assert m_list.status_code == 200
    assert len(m_list.get_json()["menu_items"]) == 2


# ============================================================================
# 4. INVENTORY CRUD & VALIDATION
# ============================================================================

def test_inventory_crud_and_validation(client):
    k_res = client.post("/api/kitchen/", json={"name": "Inventory Test Kitchen", "seed_demo": False})
    k_id = k_res.get_json()["kitchen"]["id"]

    # Negative quantity -> 400
    bad_qty = client.post("/api/inventory/", json={"kitchen_id": k_id, "ingredient_name": "Flour", "quantity": -5})
    assert bad_qty.status_code == 400

    # Invalid expiry date -> 400
    bad_date = client.post("/api/inventory/", json={"kitchen_id": k_id, "ingredient_name": "Flour", "quantity": 10, "expiry_date": "invalid-date"})
    assert bad_date.status_code == 400

    # Add valid inventory
    inv_res = client.post("/api/inventory/", json={
        "kitchen_id": k_id,
        "ingredient_name": "Paneer",
        "quantity": 15.5,
        "unit": "kg",
        "minimum_stock": 5.0,
        "expiry_date": (date.today() + timedelta(days=5)).isoformat()
    })
    assert inv_res.status_code == 201
    inv_id = inv_res.get_json()["inventory"]["id"]

    # Update inventory
    up_res = client.put(f"/api/inventory/{inv_id}", json={"quantity": 18.0})
    assert up_res.status_code == 200
    assert up_res.get_json()["inventory"]["quantity"] == 18.0

    # Update with negative minimum stock -> 400
    neg_stock = client.put(f"/api/inventory/{inv_id}", json={"minimum_stock": -2})
    assert neg_stock.status_code == 400

    # Delete inventory
    del_res = client.delete(f"/api/inventory/{inv_id}")
    assert del_res.status_code == 200

    # Delete non-existent -> 404
    del_404 = client.delete(f"/api/inventory/{inv_id}")
    assert del_404.status_code == 404


# ============================================================================
# 5. SALES DAILY AGGREGATION BUG FIX VERIFICATION
# ============================================================================

def test_sales_daily_aggregation_multiple_menu_items(client):
    # Setup clean kitchen with seed_demo: False
    k_res = client.post("/api/kitchen/", json={"name": "Analytics Kitchen", "seed_demo": False})
    k_id = k_res.get_json()["kitchen"]["id"]

    m1_res = client.post("/api/menu/", json={"kitchen_id": k_id, "name": "Item A", "price": 100})
    m1_id = m1_res.get_json()["menu_item"]["id"]

    m2_res = client.post("/api/menu/", json={"kitchen_id": k_id, "name": "Item B", "price": 200})
    m2_id = m2_res.get_json()["menu_item"]["id"]

    test_date = (date.today() - timedelta(days=2)).isoformat()

    # Record sale for item 1 on test_date: 5 orders, 500 revenue
    s1 = client.post("/api/sales/", json={"kitchen_id": k_id, "menu_item_id": m1_id, "sale_date": test_date, "quantity_sold": 5, "revenue": 500})
    assert s1.status_code == 201

    # Record sale for item 2 on the SAME test_date: 3 orders, 600 revenue
    s2 = client.post("/api/sales/", json={"kitchen_id": k_id, "menu_item_id": m2_id, "sale_date": test_date, "quantity_sold": 3, "revenue": 600})
    assert s2.status_code == 201

    # Query sales analytics
    analytics_res = client.get(f"/api/analytics/sales/kitchen/{k_id}?days=10")
    assert analytics_res.status_code == 200
    data = analytics_res.get_json()["analytics"]

    # Verify daily breakdown correctly accumulated both items on test_date
    daily_entry = next((d for d in data["daily_breakdown"] if d["date"] == test_date), None)
    assert daily_entry is not None
    assert daily_entry["orders"] == 8.0, f"Expected 8 orders, got {daily_entry['orders']}"
    assert daily_entry["revenue"] == 1100.0, f"Expected 1100 revenue, got {daily_entry['revenue']}"

    # Verify totals
    assert data["summary"]["total_orders"] == 8.0
    assert data["summary"]["total_revenue"] == 1100.0


# ============================================================================
# 6. WASTE ENDPOINTS & HEALTH SCORE CALCULATION
# ============================================================================

def test_waste_and_health_score(client):
    k_res = client.post("/api/kitchen/", json={"name": "Health Kitchen", "seed_demo": False})
    k_id = k_res.get_json()["kitchen"]["id"]

    m_res = client.post("/api/menu/", json={"kitchen_id": k_id, "name": "Biryani", "price": 300, "cost_per_serving": 120})
    m_id = m_res.get_json()["menu_item"]["id"]

    # Seed sales
    client.post("/api/sales/", json={"kitchen_id": k_id, "menu_item_id": m_id, "sale_date": date.today().isoformat(), "quantity_sold": 20, "revenue": 6000})

    # Negative waste quantity -> 400
    bad_w = client.post("/api/waste/", json={"kitchen_id": k_id, "menu_item_id": m_id, "waste_date": date.today().isoformat(), "quantity_wasted": -2})
    assert bad_w.status_code == 400

    # Add valid waste
    w_res = client.post("/api/waste/", json={
        "kitchen_id": k_id,
        "menu_item_id": m_id,
        "waste_date": date.today().isoformat(),
        "quantity_wasted": 2,
        "estimated_cost": 240,
        "reason": "Overcooked"
    })
    assert w_res.status_code == 201

    # Waste summary
    sum_res = client.get(f"/api/waste/{k_id}/summary")
    assert sum_res.status_code == 200
    assert sum_res.get_json()["summary"]["total_waste"] == 2.0

    # Waste by item
    by_item = client.get(f"/api/waste/{k_id}/by-item")
    assert by_item.status_code == 200
    assert len(by_item.get_json()["waste_by_item"]) == 1

    # High waste
    high_w = client.get(f"/api/waste/{k_id}/high-waste?limit=3")
    assert high_w.status_code == 200

    # Waste analytics
    w_ana = client.get(f"/api/waste/{k_id}/analytics?days=14")
    assert w_ana.status_code == 200

    # Waste costs
    w_costs = client.get(f"/api/waste/{k_id}/costs?days=14")
    assert w_costs.status_code == 200

    # Health score
    hs_res = client.get(f"/api/health-score/kitchen/{k_id}")
    assert hs_res.status_code == 200
    hs_data = hs_res.get_json()["health_score"]
    assert "overall_score" in hs_data
    assert "health_emoji" in hs_data
    assert hs_data["health_emoji"] is not None
    assert "components" in hs_data
    assert "cost_efficiency" in hs_data["components"]


# ============================================================================
# 7. DEMAND, FORECAST & PREDICTION (STRING & INT TYPES, LEGACY FALLBACK)
# ============================================================================

def test_demand_forecasting_and_prediction(client):
    k_res = client.post("/api/kitchen/", json={"name": "Forecast Kitchen", "seed_demo": False})
    k_id = k_res.get_json()["kitchen"]["id"]

    m_res = client.post("/api/menu/", json={"kitchen_id": k_id, "name": "Pizza", "price": 400})
    m_id = m_res.get_json()["menu_item"]["id"]

    # Seed 10 days of sales
    for i in range(10):
        client.post("/api/sales/", json={
            "kitchen_id": k_id,
            "menu_item_id": m_id,
            "sale_date": (date.today() - timedelta(days=10 - i)).isoformat(),
            "quantity_sold": 15 + i,
            "revenue": (15 + i) * 400
        })

    # Demand analysis
    d_res = client.get(f"/api/demand/kitchen/{k_id}?days=30")
    assert d_res.status_code == 200
    assert len(d_res.get_json()["demand"]["items"]) == 1

    # Weekly forecast
    f_res = client.get(f"/api/demand/kitchen/{k_id}/forecast?days=7")
    assert f_res.status_code == 200
    assert len(f_res.get_json()["forecast"]["forecasts"]) == 1

    # Prediction API with integer IDs
    pred_int = client.post("/api/prediction/", json={"kitchen_id": k_id, "menu_item_id": m_id})
    assert pred_int.status_code == 200
    assert pred_int.get_json()["prediction"]["predicted_demand"] > 0

    # Prediction API with string IDs
    pred_str = client.post("/api/prediction/", json={"kitchen_id": str(k_id), "menu_item_id": str(m_id)})
    assert pred_str.status_code == 200
    assert pred_str.get_json()["prediction"]["predicted_demand"] > 0

    # Prediction API with legacy food delivery payload
    pred_legacy = client.post("/api/prediction/", json={
        "week": 145,
        "center_id": 55,
        "meal_id": 1885,
        "checkout_price": 140.5,
        "base_price": 150.0
    })
    assert pred_legacy.status_code == 200
    assert pred_legacy.get_json()["prediction"]["predicted_demand"] >= 0


# ============================================================================
# 8. RECOMMENDATION & WHAT-IF (STRING COERCION)
# ============================================================================

def test_recommendation_and_whatif_endpoints(client):
    k_res = client.post("/api/kitchen/", json={"name": "Rec Kitchen", "seed_demo": False})
    k_id = k_res.get_json()["kitchen"]["id"]

    m_res = client.post("/api/menu/", json={"kitchen_id": k_id, "name": "Salad", "price": 150})
    m_id = m_res.get_json()["menu_item"]["id"]

    for i in range(8):
        client.post("/api/sales/", json={
            "kitchen_id": k_id,
            "menu_item_id": m_id,
            "sale_date": (date.today() - timedelta(days=8 - i)).isoformat(),
            "quantity_sold": 10 + i,
            "revenue": (10 + i) * 150
        })

    # What-If Demand Increase
    wi_inc = client.post("/api/whatif/demand-increase", json={"kitchen_id": str(k_id), "menu_item_id": str(m_id), "increase_pct": 25})
    assert wi_inc.status_code == 200
    assert wi_inc.get_json()["analysis"]["new_demand"] > wi_inc.get_json()["analysis"]["base_demand"]

    # What-If Preparation Reduction
    wi_red = client.post("/api/whatif/preparation-reduction", json={"kitchen_id": str(k_id), "menu_item_id": str(m_id), "reduction_pct": 15})
    assert wi_red.status_code == 200
    assert wi_red.get_json()["analysis"]["new_demand"] < wi_red.get_json()["analysis"]["base_demand"]

    # Dashboard recommendations
    dash_rec = client.get(f"/api/whatif/dashboard-recommendations/kitchen/{k_id}")
    assert dash_rec.status_code == 200
    assert dash_rec.get_json()["success"] is True


# ============================================================================
# 9. CASCADE CLEANUP ON MENU ITEM DELETION
# ============================================================================

def test_menu_item_cascade_cleanup(client):
    k_res = client.post("/api/kitchen/", json={"name": "Cascade Kitchen", "seed_demo": False})
    k_id = k_res.get_json()["kitchen"]["id"]

    m_res = client.post("/api/menu/", json={"kitchen_id": k_id, "name": "Doomed Item", "price": 200})
    m_id = m_res.get_json()["menu_item"]["id"]

    w_id = None
    # Add Sales, Waste, Prediction referencing m_id
    with app.app_context():
        s = Sales(kitchen_id=k_id, menu_item_id=m_id, sale_date=date.today(), quantity_sold=5, revenue=1000)
        w = Waste(kitchen_id=k_id, menu_item_id=m_id, waste_date=date.today(), quantity_wasted=1)
        p = Prediction(kitchen_id=k_id, menu_item_id=m_id, prediction_date=date.today(), predicted_demand=10, model_name="test")
        db.session.add_all([s, w, p])
        db.session.commit()
        w_id = w.id

    # Deleting menu item must not fail with IntegrityError
    del_res = client.delete(f"/api/menu/{m_id}")
    assert del_res.status_code == 200

    with app.app_context():
        # Sales deleted
        assert Sales.query.filter_by(menu_item_id=m_id).count() == 0
        # Prediction deleted
        assert Prediction.query.filter_by(menu_item_id=m_id).count() == 0
        # Waste menu_item_id set to None
        waste_record = db.session.get(Waste, w_id)
        assert waste_record is not None
        assert waste_record.menu_item_id is None


# ============================================================================
# 10. CLEAN KITCHEN CREATION (NO AUTOMATIC SEEDING) & KITCHEN DELETE
# ============================================================================

def test_kitchen_creation_clean_by_default(client):
    # Creating kitchen without seed_demo must NOT inject any demo data
    res = client.post("/api/kitchen/", json={"name": "Owner Blank Slate Kitchen"})
    assert res.status_code == 201
    k_id = res.get_json()["kitchen"]["id"]

    with app.app_context():
        assert MenuItem.query.filter_by(kitchen_id=k_id).count() == 0
        assert Inventory.query.filter_by(kitchen_id=k_id).count() == 0
        assert Sales.query.filter_by(kitchen_id=k_id).count() == 0
        assert Waste.query.filter_by(kitchen_id=k_id).count() == 0

    # Delete kitchen endpoint
    del_res = client.delete(f"/api/kitchen/{k_id}")
    assert del_res.status_code == 200
    assert del_res.get_json()["success"] is True

    # 404 for deleted kitchen
    del_again = client.delete(f"/api/kitchen/{k_id}")
    assert del_again.status_code == 404


def test_kitchen_explicit_seed_demo(client):
    # Explicit seed_demo: True should seed demo data
    res = client.post("/api/kitchen/", json={"name": "Demo Kitchen With Seed", "seed_demo": True})
    assert res.status_code == 201
    k_id = res.get_json()["kitchen"]["id"]

    with app.app_context():
        assert MenuItem.query.filter_by(kitchen_id=k_id).count() > 0
        assert Inventory.query.filter_by(kitchen_id=k_id).count() > 0
        assert Sales.query.filter_by(kitchen_id=k_id).count() > 0

    # Cleanup
    del_res = client.delete(f"/api/kitchen/{k_id}")
    assert del_res.status_code == 200

