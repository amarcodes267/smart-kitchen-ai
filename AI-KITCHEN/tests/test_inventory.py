from app import app
from backend.utils.database import db
from backend.models.kitchen import Kitchen


def test_inventory_routes_work_with_sqlite():
    with app.app_context():
        db.drop_all()
        db.create_all()

        kitchen = Kitchen(name="Test Kitchen", cuisine_type="Indian", seats=20, meals_per_day=200)
        db.session.add(kitchen)
        db.session.commit()

        kitchen_id = kitchen.id

    with app.test_client() as client:
        response = client.get(f"/api/inventory/{kitchen_id}")
        assert response.status_code == 200
        assert response.get_json()["success"] is True

        response = client.post(
            "/api/inventory/",
            json={
                "kitchen_id": kitchen_id,
                "ingredient_name": "Tomato",
                "quantity": 5,
                "unit": "kg",
            },
        )
        assert response.status_code == 201
        payload = response.get_json()
        assert payload["success"] is True
        assert payload["inventory"]["ingredient_name"] == "Tomato"

        item_id = payload["inventory"]["id"]
        response = client.put(
            f"/api/inventory/{item_id}",
            json={"ingredient_name": "Cherry Tomato"},
        )
        assert response.status_code == 200
        assert response.get_json()["inventory"]["ingredient_name"] == "Cherry Tomato"
