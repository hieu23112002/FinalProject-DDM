from __future__ import annotations

from pathlib import Path
import logging
import sys

import joblib
import pandas as pd
import shap
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from pydantic import BaseModel, Field


CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
MODELS_DIR = PROJECT_ROOT / "models"
SRC_DIR = str(CURRENT_DIR)
if SRC_DIR not in sys.path:
    sys.path.append(SRC_DIR)

from preprocessing import ChurnPreprocessor
from database import init_db, SessionLocal, PredictionLog

# Initialize database tables
try:
    init_db()
except Exception as e:
    logging.warning(f"Database initialization failed: {e}")


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

PREDICTION_COUNTER = Counter(
    "churn_api_predictions_total",
    "Total number of churn predictions served by the API",
)
LATENCY_HISTOGRAM = Histogram(
    "churn_api_latency_seconds",
    "Latency of the churn prediction API in seconds",
)

HEALTH_STATUS_MESSAGE = "Hệ thống đang hoạt động ổn định"


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


from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Churn Prediction Production API",
    description="Production churn prediction API with SHAP explanations and Prometheus metrics.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

classifier_model = None
shap_explainer_tool = None
model_features: list[str] | None = None
churn_preprocessor: ChurnPreprocessor | None = None
_model_load_error: str | None = None


def _load_preprocessor(feature_names: list[str]) -> ChurnPreprocessor:
    preprocessor_path = MODELS_DIR / "preprocessor.pkl"
    if preprocessor_path.exists():
        preprocessor = ChurnPreprocessor.load(preprocessor_path)
        preprocessor.feature_columns_ = feature_names
        return preprocessor

    legacy_encoders_path = PROJECT_ROOT / "data" / "processed" / "label_encoders.pkl"
    if legacy_encoders_path.exists():
        return ChurnPreprocessor.from_legacy_artifacts(feature_names, legacy_encoders_path)

    return ChurnPreprocessor.from_feature_names(feature_names)


def load_model_artifacts() -> bool:
    global classifier_model, shap_explainer_tool, model_features, churn_preprocessor, _model_load_error

    _model_load_error = None
    try:
        classifier_model = joblib.load(MODELS_DIR / "best_model.pkl")
        model_features = joblib.load(MODELS_DIR / "feature_names.pkl")
        churn_preprocessor = _load_preprocessor(model_features)
        shap_explainer_tool = shap.TreeExplainer(classifier_model)
        return True
    except Exception as error:
        classifier_model = None
        shap_explainer_tool = None
        model_features = None
        churn_preprocessor = None
        _model_load_error = str(error)
        logging.exception("Failed to load model artifacts from %s", MODELS_DIR)
        return False


load_model_artifacts()


@app.get("/metrics")
def get_prometheus_metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/")
def health_check() -> dict[str, str]:
    return {"status": HEALTH_STATUS_MESSAGE}


@app.get("/health")
def health_ready() -> dict[str, str]:
    if classifier_model is None:
        hint = _model_load_error or "No additional error details are available."
        raise HTTPException(
            status_code=503,
            detail={"message": "Model is not ready", "models_dir": str(MODELS_DIR), "error": hint},
        )

    return {"status": "ok", "models_dir": str(MODELS_DIR)}


@app.post("/predict")
@LATENCY_HISTOGRAM.time()
def predict_customer_churn(request_data: CustomerInferenceRequest) -> dict[str, object]:
    PREDICTION_COUNTER.inc()
    try:
        if classifier_model is None:
            load_model_artifacts()

        if classifier_model is None or churn_preprocessor is None or model_features is None:
            raise HTTPException(
                status_code=503,
                detail={
                    "message": "Model artifacts are not loaded. Run preprocessing and training first.",
                    "models_dir": str(MODELS_DIR),
                    "error": _model_load_error,
                },
            )

        input_dataframe = pd.DataFrame([request_data.model_dump()])
        final_processed_df = churn_preprocessor.transform_for_inference(input_dataframe)

        churn_probability = classifier_model.predict_proba(final_processed_df)[0][1]
        prediction_status = "Churn" if churn_probability > 0.5 else "Stable"

        shap_values_result = shap_explainer_tool.shap_values(final_processed_df)
        if isinstance(shap_values_result, list):
            values_to_explain = shap_values_result[1][0]
        else:
            values = shap_values_result[0]
            values_to_explain = values if values.ndim == 1 else values[1]

        feature_importance_map = dict(zip(model_features, values_to_explain))
        sorted_reasons = sorted(
            feature_importance_map.items(),
            key=lambda item: abs(float(item[1])),
            reverse=True,
        )[:3]

        response_payload = {
            "prediction_status": prediction_status,
            "probability_percent": round(float(churn_probability) * 100, 2),
            "top_risk_factors": [
                {"feature": feature, "impact_score": round(float(score), 4)}
                for feature, score in sorted_reasons
            ],
            "recommendation": (
                "Customer retention intervention recommended"
                if churn_probability > 0.5
                else "Customer appears stable"
            ),
        }

        # Log to Database (Asynchronously using Celery)
        try:
            from worker import log_prediction_to_db
            task_data = {
                "prediction_status": prediction_status,
                "probability": float(churn_probability),
                "risk_factors": response_payload["top_risk_factors"],
                "raw_input": request_data.model_dump(),
                "recommendation": response_payload["recommendation"]
            }
            log_prediction_to_db.delay(task_data)
        except Exception as async_err:
            logging.error(f"Failed to trigger async logging: {async_err}")

        return response_payload
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {error}") from error


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
