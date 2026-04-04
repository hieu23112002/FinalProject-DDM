Tài liệu Kiến trúc Hệ thống (System Architecture)

1. Tổng quan (High-level Architecture)

Hệ thống được thiết kế theo kiến trúc Microservices đóng gói bằng Docker. Luồng dữ liệu chính đi từ yêu cầu của người dùng qua API đến mô hình học máy và trả về kết quả kèm giải thích.

2. Thành phần hệ thống

Data Pipeline: Xử lý dữ liệu thô từ CSV, thực hiện Feature Engineering và chia tập Train/Test.

ML Engine (LightGBM): Mô hình dự báo được tối ưu hóa cho dữ liệu mất cân bằng.

Responsible AI (SHAP): Giải thích các quyết định của mô hình cho từng khách hàng cụ thể.

FastAPI Server: Cung cấp các endpoint RESTful để phục vụ dự đoán thời gian thực.

Monitoring Stack: Prometheus thu thập các chỉ số hệ thống và chỉ số ML (tỷ lệ Churn, độ trễ).

3. Luồng dữ liệu (Data Flow)

User gửi JSON qua POST /predict.

FastAPI gọi ChurnPreprocessor để làm sạch và tạo đặc trưng.

Mô hình best_model.pkl dự báo xác suất.

SHAP Explainer tính toán mức độ ảnh hưởng của các đặc trưng.

API trả về kết quả dự báo kèm top_reasons.

4. Công nghệ sử dụng (Tech Stack)

Ngôn ngữ: Python 3.12

Framework: FastAPI, Scikit-learn, LightGBM

Theo dõi: MLflow, Prometheus

Đóng gói: Docker, Docker Compose

CI/CD: GitHub Actions