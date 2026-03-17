"""Tests unitaires pour l'API FastAPI."""

from fastapi.testclient import TestClient

from src.energystock_ai.api.main import app


client = TestClient(app)


def test_predict_missing_data():
    response = client.post("/predict", json={"ticker": "NEE", "as_of_date": "2100-01-01"})
    assert response.status_code == 404
