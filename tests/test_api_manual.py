import json

import requests


URL = "http://localhost:8000/predict"
SAMPLE_DATA = {
    "gender": "Female",
    "SeniorCitizen": 1,
    "Partner": "Yes",
    "Dependents": "No",
    "tenure": 1,
    "PhoneService": "Yes",
    "MultipleLines": "No",
    "InternetService": "Fiber optic",
    "OnlineSecurity": "No",
    "OnlineBackup": "No",
    "DeviceProtection": "No",
    "TechSupport": "No",
    "StreamingTV": "Yes",
    "StreamingMovies": "Yes",
    "Contract": "Month-to-month",
    "PaperlessBilling": "Yes",
    "PaymentMethod": "Electronic check",
    "MonthlyCharges": 95.0,
    "TotalCharges": "95.0",
}


def run_manual_test() -> None:
    print("Sending prediction request...")
    try:
        response = requests.post(URL, json=SAMPLE_DATA, timeout=30)
        response.raise_for_status()
        print(json.dumps(response.json(), indent=4, ensure_ascii=False))
    except requests.HTTPError:
        print(f"API returned {response.status_code}: {response.text}")
    except requests.RequestException as error:
        print(f"Could not reach API: {error}")


if __name__ == "__main__":
    run_manual_test()
