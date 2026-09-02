from app import app


def test_health_endpoint():
    with app.test_client() as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json()["status"] == "healthy"


def test_menu_page_and_dataset_endpoints_are_available():
    with app.test_client() as client:
        assert client.get("/menu").status_code == 200

        centers_response = client.get("/api/data/centers")
        assert centers_response.status_code == 200
        assert centers_response.get_json()["centers"]

        meals_response = client.get("/api/data/meals")
        assert meals_response.status_code == 200
        assert meals_response.get_json()["meals"]


def test_menu_rejects_invalid_prices_without_a_server_error():
    from backend.models.kitchen import Kitchen
    from backend.utils.database import db

    with app.app_context():
        db.drop_all()
        db.create_all()
        kitchen = Kitchen(name="Validation Kitchen")
        db.session.add(kitchen)
        db.session.commit()
        kitchen_id = kitchen.id

    with app.test_client() as client:
        response = client.post(
            "/api/menu/",
            json={
                "kitchen_id": kitchen_id,
                "name": "Meal",
                "price": "bad",
            },
        )

    assert response.status_code == 400
    assert response.get_json()["success"] is False
