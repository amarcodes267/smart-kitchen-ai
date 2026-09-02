from app import app


def test_prediction_route_handles_fallback_model():
    payload = {
        "week": 1,
        "center_id": 55,
        "meal_id": 1885,
        "checkout_price": 158.11,
        "base_price": 159.11,
        "emailer_for_promotion": 0,
        "homepage_featured": 0,
    }

    with app.test_client() as client:
        response = client.post("/api/prediction/", json=payload)

    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert isinstance(data["prediction"]["predicted_demand"], (int, float))
