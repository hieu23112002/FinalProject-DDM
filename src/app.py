import os
import sys
import joblib
import pandas as pd
import uvicorn
import shap
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

# Thư mục gốc dự án (cha của src/) — không phụ thuộc nơi bạn chạy lệnh
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
_MODELS_DIR = os.path.join(_PROJECT_ROOT, "models")

# Đảm bảo import được Preprocessor
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from preprocessing import ChurnPreprocessor

# --- Cấu hình Giám sát (Monitoring) ---
PREDICTION_COUNTER = Counter("churn_api_predictions_total", "Tổng số lượt dự đoán khách hàng")
LATENCY_HISTOGRAM = Histogram("churn_api_latency_seconds", "Thời gian xử lý của API")

# --- Định nghĩa Schema (Fix Pydantic V2 Warning) ---
class CustomerInferenceRequest(BaseModel):
    gender: str = Field(..., json_schema_extra={"example": "Female"})
    SeniorCitizen: int = Field(..., json_schema_extra={"example": 0})
    Partner: str = Field(..., json_schema_extra={"example": "Yes"})
    Dependents: str = Field(..., json_schema_extra={"example": "No"})
    tenure: int = Field(..., json_schema_extra={"example": 12})
    PhoneService: str = Field(..., json_schema_extra={"example": "Yes"})
    MultipleLines: str = Field(..., json_schema_extra={"example": "No"})
    InternetService: str = Field(..., json_schema_extra={"example": "Fiber optic"})
    OnlineSecurity: str = Field(..., json_schema_extra={"example": "No"})
    OnlineBackup: str = Field(..., json_schema_extra={"example": "No"})
    DeviceProtection: str = Field(..., json_schema_extra={"example": "No"})
    TechSupport: str = Field(..., json_schema_extra={"example": "No"})
    StreamingTV: str = Field(..., json_schema_extra={"example": "No"})
    StreamingMovies: str = Field(..., json_schema_extra={"example": "No"})
    Contract: str = Field(..., json_schema_extra={"example": "Month-to-month"})
    PaperlessBilling: str = Field(..., json_schema_extra={"example": "Yes"})
    PaymentMethod: str = Field(..., json_schema_extra={"example": "Electronic check"})
    MonthlyCharges: float = Field(..., json_schema_extra={"example": 70.35})
    TotalCharges: str = Field(..., json_schema_extra={"example": "844.2"})

# Khởi tạo FastAPI
app = FastAPI(
    title="Churn Prediction Production API",
    description="Hệ thống dự đoán khách hàng rời bỏ tích hợp SHAP và Prometheus."
)

# Nạp các thành phần đã huấn luyện
classifier_model = None
shap_explainer_tool = None
model_features = None
churn_preprocessor = None
_model_load_error: str | None = None


def load_model_artifacts() -> bool:
    """Nạp model từ _MODELS_DIR. Trả True nếu thành công. Có thể gọi lại sau khi train xong."""
    global classifier_model, shap_explainer_tool, model_features, churn_preprocessor, _model_load_error
    _model_load_error = None
    try:
        classifier_model = joblib.load(os.path.join(_MODELS_DIR, "best_model.pkl"))
        model_features = joblib.load(os.path.join(_MODELS_DIR, "feature_names.pkl"))
        churn_preprocessor = ChurnPreprocessor()
        # Không load shap_explainer.pkl: pickle SHAP hay lỗi khi khác phiên bản Python (vd. train 3.12, Docker 3.10).
        shap_explainer_tool = shap.TreeExplainer(classifier_model)
        return True
    except Exception as error:
        classifier_model = None
        shap_explainer_tool = None
        model_features = None
        churn_preprocessor = None
        _model_load_error = str(error)
        print(f"Lỗi khi nạp hệ thống (thư mục models: {_MODELS_DIR}): {error}")
        return False


load_model_artifacts()

@app.get("/metrics")
def get_prometheus_metrics():
    """Endpoint để Prometheus thu thập dữ liệu giám sát."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/")
def health_check():
    return {"status": "Hệ thống đang hoạt động ổn định"}

@app.get("/health")
def health_ready():
    """Sẵn sàng phục vụ khi model đã nạp (dùng cho Docker healthcheck)."""
    if classifier_model is None:
        hint = _model_load_error or "Không có chi tiết. Kiểm tra file trong thư mục models/."
        raise HTTPException(
            status_code=503,
            detail={"message": "Model chưa sẵn sàng", "models_dir": _MODELS_DIR, "error": hint},
        )
    return {"status": "ok", "models_dir": _MODELS_DIR}

@app.post("/predict")
@LATENCY_HISTOGRAM.time()
def predict_customer_churn(request_data: CustomerInferenceRequest):
    PREDICTION_COUNTER.inc()
    try:
        if classifier_model is None:
            load_model_artifacts()
        if classifier_model is None or churn_preprocessor is None or model_features is None:
            raise HTTPException(
                status_code=503,
                detail={
                    "message": "Mô hình chưa được nạp. Chạy preprocessing và train trước, rồi thử lại (hoặc khởi động lại API).",
                    "models_dir": _MODELS_DIR,
                    "error": _model_load_error,
                },
            )

        # 1. Chuyển đổi dữ liệu và tiền xử lý
        input_dataframe = pd.DataFrame([request_data.model_dump()])
        cleaned_df = churn_preprocessor.clean_data(input_dataframe)
        final_processed_df = churn_preprocessor.create_features(cleaned_df)

        # Chuẩn hóa kiểu: object + category (vd. TenureGroup) → số; căn cột theo model
        non_numeric = final_processed_df.select_dtypes(
            include=["object", "category"]
        ).columns
        for col in non_numeric:
            final_processed_df[col] = 0
        for col in model_features:
            if col not in final_processed_df.columns:
                final_processed_df[col] = 0
        final_processed_df = final_processed_df[model_features]

        # 2. Thực hiện dự đoán
        churn_probability = classifier_model.predict_proba(final_processed_df)[0][1]
        is_churn_result = "Churn" if churn_probability > 0.5 else "Stable"
        
        # 3. Responsible AI: Giải thích lý do bằng SHAP
        shap_values_result = shap_explainer_tool.shap_values(final_processed_df)
        # Xử lý định dạng đầu ra của SHAP cho LightGBM
        val_to_explain = shap_values_result[1][0] if isinstance(shap_values_result, list) else shap_values_result[0]
        
        feature_importance_map = dict(zip(model_features, val_to_explain))
        sorted_reasons = sorted(feature_importance_map.items(), key=lambda x: abs(x[1]), reverse=True)[:3]

        return {
            "prediction_status": is_churn_result,
            "probability_percent": round(float(churn_probability) * 100, 2),
            "top_risk_factors": [
                {"feature": reason[0], "impact_score": round(float(reason[1]), 4)} 
                for reason in sorted_reasons
            ],
            "recommendation": "Cần can thiệp chăm sóc" if churn_probability > 0.5 else "Tiếp tục duy trì"
        }
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý dự đoán: {str(error)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)