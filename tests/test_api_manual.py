import requests
import json

def run_manual_test():
    url = "http://localhost:8000/predict"
    sample_data = {
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
        "TotalCharges": "95.0"
    }
    
    print("--- Đang gửi yêu cầu dự đoán ---")
    try:
        response = requests.post(url, json=sample_data)
        if response.status_code == 200:
            print(json.dumps(response.json(), indent=4, ensure_ascii=False))
        else:
            print(f"Lỗi API: {response.status_code}")
    except Exception as e:
        print(f"Không thể kết nối API: {e}")

if __name__ == "__main__":
    run_manual_test()