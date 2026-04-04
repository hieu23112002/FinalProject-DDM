Customer Churn Prediction System

Hệ thống dự đoán khả năng khách hàng rời bỏ 
🛠 Cách chạy hệ thống nhanh nhất

Yêu cầu: Docker Desktop.

docker-compose up --build


API Docs: http://localhost:8000/docs

Prometheus UI: http://localhost:9090

🐍 Cách chạy bằng Python cục bộ

py -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

py src/preprocessing.py
py src/train.py
py src/app.py


🧪 Chạy Kiểm thử

py -m pytest tests/test_api_pytest.py
