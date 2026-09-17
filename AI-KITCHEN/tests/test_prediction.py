from datetime import date, timedelta
import pandas as pd
import pytest

from app import app
from backend.utils.database import db
from backend.models.kitchen import Kitchen
from backend.models.menu import MenuItem
from backend.models.sales import Sales
from backend.services.prediction_service import load_model as load_pred_model
from ml.predict import predict_demand, load_model as load_ml_model


def test_prediction_route_with_sales_history():
    with app.app_context():
        db.drop_all()
        db.create_all()
        kitchen = Kitchen(name="Prediction Kitchen")
        db.session.add(kitchen)
        db.session.commit()
        kitchen_id = kitchen.id

        menu = MenuItem(kitchen_id=kitchen_id, name="Prediction Meal", serving_unit="servings", cost_per_serving=50)
        db.session.add(menu)
        db.session.commit()
        meal_id = menu.id

        today = date.today()
        for i in range(10):
            s = Sales(
                kitchen_id=kitchen_id,
                menu_item_id=meal_id,
                sale_date=(today - timedelta(days=(10 - i))),
                quantity_sold=20 + i,
                revenue=(20 + i) * 50,
            )
            db.session.add(s)
        db.session.commit()

    payload = {
        "kitchen_id": kitchen_id,
        "menu_item_id": meal_id,
    }

    with app.test_client() as client:
        response = client.post("/api/prediction/", json=payload)
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["prediction"]["model"] == "XGBoost"
        assert isinstance(data["prediction"]["predicted_demand"], (int, float))
        assert data["prediction"]["predicted_demand"] > 0
        assert "ai_explanation" in data["prediction"]
        assert len(data["prediction"]["ai_explanation"]) > 10
        assert "kitchen_recommendation" in data["prediction"]
        assert len(data["prediction"]["kitchen_recommendation"]) > 10
        assert "recommended_prep" in data["prediction"]


def test_xgboost_llm_decoupled_prediction():
    """Verify ML model (XGBoost) produces numerical prediction and LLM produces operational explanation."""
    from backend.services.gemini_service import generate_prediction_explanation

    # Stage 1: XGBoost produces numerical demand (e.g. 44.5)
    xgboost_numerical_pred = 44.5
    trend = "increasing"
    trend_symbol = "↗️"
    change_pct = 100.0

    # Stage 2: LLM converts numerical prediction into explanation and practical recommendation
    llm_guidance = generate_prediction_explanation(
        item_name="samosa",
        predicted_demand=xgboost_numerical_pred,
        trend=trend,
        trend_symbol=trend_symbol,
        change_pct=change_pct,
        previous_avg=0.0,
        recent_avg=22.25,
    )

    assert "explanation" in llm_guidance
    assert "samosa" in llm_guidance["explanation"].lower() or "44.5" in llm_guidance["explanation"]
    assert "kitchen_recommendation" in llm_guidance
    assert "prep" in llm_guidance["kitchen_recommendation"].lower()
    assert llm_guidance["recommended_prep"] >= xgboost_numerical_pred



def test_xgboost_model_inference_direct():
    """Verify that XGBoost Regressor directly executes on runtime serving features without error."""
    model = load_pred_model()
    # Ensure it is a genuine trained XGBoost model instance
    assert "XGBRegressor" in type(model).__name__

    features = pd.DataFrame([{
        "day_of_week": 4,
        "month": 9,
        "previous_sales": 30.0,
        "rolling_7_day_avg": 28.5
    }])

    pred = model.predict(features)
    assert len(pred) == 1
    assert float(pred[0]) > 0.0


def test_predict_demand_boundary_cases():
    """Verify ml.predict handles normal, minimum, maximum, and extreme edge cases."""
    # Normal case
    normal = predict_demand(day_of_week=2, month=6, previous_sales=25.0, rolling_7_day_avg=24.0)
    assert isinstance(normal, int)
    assert normal > 0

    # Minimum values
    minimum = predict_demand(day_of_week=0, month=1, previous_sales=0.0, rolling_7_day_avg=0.0)
    assert isinstance(minimum, int)
    assert minimum >= 0

    # Extreme high values
    extreme = predict_demand(day_of_week=5, month=12, previous_sales=1000.0, rolling_7_day_avg=1000.0)
    assert isinstance(extreme, int)
    assert extreme > 0

    # Legacy argument format compatibility
    legacy = predict_demand(week=150, center_id=25, meal_id=100, checkout_price=180.0, base_price=175.0)
    assert isinstance(legacy, int)
    assert legacy > 0


def test_predict_demand_invalid_inputs():
    """Verify invalid non-numeric inputs raise a clean ValueError."""
    with pytest.raises(ValueError):
        predict_demand(day_of_week="invalid_string", month=5, previous_sales=20.0, rolling_7_day_avg=20.0)
