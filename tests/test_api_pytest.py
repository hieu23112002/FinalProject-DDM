import os
import re
import sys
import pytest
from fastapi.testclient import TestClient

# Thêm src vào path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from app import app

client = TestClient(app)

def test_health_endpoint():
    """Kiểm tra API có sống không."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "Hệ thống đang hoạt động ổn định"

def test_health_ready_endpoint():
    """Healthcheck Docker: 200 khi model đã nạp."""
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body.get("status") == "ok"

def test_predict_endpoint_success():
    """Kiểm tra gửi dữ liệu hợp lệ."""
    payload = {
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
        "TotalCharges": "225.0"
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "prediction_status" in data
    assert "top_risk_factors" in data

def test_metrics_endpoint():
    """Kiểm tra endpoint Prometheus: định dạng text và có metric tùy chỉnh."""
    response = client.get("/metrics")
    assert response.status_code == 200
    text = response.text
    assert "churn_api_predictions_total" in text
    assert "churn_api_latency_seconds" in text

def test_metrics_increase_after_predict():
    """Sau một lần predict, counter tăng (kiểm tra pipeline metric)."""
    before = client.get("/metrics").text

    def total_predictions(blob: str) -> int:
        m = re.search(r"churn_api_predictions_total(?:\{[^}]*\})?\s+(\d+(?:\.\d+)?(?:e[+-]\d+)?)", blob)
        return int(float(m.group(1))) if m else 0

    n0 = total_predictions(before)
    payload = {
        "gender": "Male",
        "SeniorCitizen": 0,
        "Partner": "No",
        "Dependents": "No",
        "tenure": 1,
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
        "MonthlyCharges": 50.0,
        "TotalCharges": "50.0",
    }
    assert client.post("/predict", json=payload).status_code == 200
    after = client.get("/metrics").text
    n1 = total_predictions(after)
    assert n1 >= n0 + 1