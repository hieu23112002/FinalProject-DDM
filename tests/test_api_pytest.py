import os
import re
import sys

from fastapi.testclient import TestClient


sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from app import HEALTH_STATUS_MESSAGE, app


client = TestClient(app)

VALID_PAYLOAD = {
    "gender": "Male",
    "SeniorCitizen": 0,
    "Partner": "No",
    "Dependents": "No",
    "tenure": 5,
    "PhoneService": "Yes",
    "MultipleLines": "No",
    "InternetService": "DSL",
    "OnlineSecurity": "No",
    "OnlineBackup": "No",
    "DeviceProtection": "No",
    "TechSupport": "No",
    "StreamingTV": "No",
    "StreamingMovies": "No",
    "Contract": "Month-to-month",
    "PaperlessBilling": "Yes",
    "PaymentMethod": "Mailed check",
    "MonthlyCharges": 45.0,
    "TotalCharges": "225.0",
}


def test_health_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == HEALTH_STATUS_MESSAGE


def test_health_ready_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body == {
        "status": "ok",
        "models_dir": body["models_dir"],
    }
    assert body["models_dir"].endswith("models")


def test_predict_endpoint_success():
    response = client.post("/predict", json=VALID_PAYLOAD)
    assert response.status_code == 200

    data = response.json()
    assert data["prediction_status"] in {"Churn", "Stable"}
    assert 0 <= data["probability_percent"] <= 100
    assert isinstance(data["top_risk_factors"], list)
    assert 1 <= len(data["top_risk_factors"]) <= 3
    assert isinstance(data["recommendation"], str)

    for factor in data["top_risk_factors"]:
        assert set(factor) == {"feature", "impact_score"}
        assert isinstance(factor["feature"], str)
        assert isinstance(factor["impact_score"], float)


def test_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")

    text = response.text
    assert "churn_api_predictions_total" in text
    assert "churn_api_latency_seconds" in text


def test_metrics_increase_after_predict():
    before = client.get("/metrics").text

    def total_predictions(blob: str) -> int:
        match = re.search(r"churn_api_predictions_total(?:\{[^}]*\})?\s+(\d+(?:\.\d+)?(?:e[+-]\d+)?)", blob)
        return int(float(match.group(1))) if match else 0

    n0 = total_predictions(before)
    assert client.post("/predict", json=VALID_PAYLOAD).status_code == 200
    after = client.get("/metrics").text
    n1 = total_predictions(after)
    assert n1 >= n0 + 1
