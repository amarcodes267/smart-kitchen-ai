import pytest
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app
from backend.utils.database import db
from backend.models.kitchen import Kitchen
from backend.models.menu import MenuItem
from backend.models.inventory import Inventory
from backend.models.sales import Sales
from backend.models.prediction import Prediction
from datetime import date, timedelta


def setup_app_db():
    with app.app_context():
        db.drop_all()
        db.create_all()


def test_frontend_routes():
    setup_app_db()
    with app.test_client() as client:
        r = client.get('/')
        assert r.status_code == 200
        r = client.get('/dashboard')
        assert r.status_code == 200


def test_prediction_api_flow():
    setup_app_db()

    with app.app_context():
        kitchen = Kitchen(name='E2E Kitchen')
        db.session.add(kitchen)
        db.session.commit()
        kitchen_id = kitchen.id

        menu = MenuItem(kitchen_id=kitchen_id, name='E2E Meal', serving_unit='servings', cost_per_serving=50)
        db.session.add(menu)
        db.session.commit()
        meal_id = menu.id

        for i in range(9):
            s = Sales(
                kitchen_id=kitchen_id,
                menu_item_id=meal_id,
                sale_date=(date.today() - timedelta(days=(9-i))),
                quantity_sold=20 + i,
                revenue=(20 + i) * 50
            )
            db.session.add(s)
        db.session.commit()

    payload = {
        "kitchen_id": kitchen_id,
        "menu_item_id": meal_id,
    }

    with app.test_client() as client:
        res = client.post('/api/prediction/', json=payload)
        assert res.status_code == 200
        data = res.get_json()
        assert data['success'] is True
        assert 'prediction' in data
        assert isinstance(data['prediction']['predicted_demand'], (int, float))
