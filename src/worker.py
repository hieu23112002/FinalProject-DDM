import os
from celery import Celery
from database import SessionLocal, PredictionLog

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

celery_app = Celery(
    "worker",
    broker=REDIS_URL,
    backend=REDIS_URL
)

# Optional: Configuration for Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

@celery_app.task(name="log_prediction_task")
def log_prediction_to_db(prediction_data: dict):
    """
    Asynchronously log prediction data to PostgreSQL database.
    """
    try:
        db = SessionLocal()
        log_entry = PredictionLog(
            prediction_status=prediction_data["prediction_status"],
            probability=prediction_data["probability"],
            risk_factors=prediction_data["risk_factors"],
            raw_input=prediction_data["raw_input"],
            recommendation=prediction_data["recommendation"]
        )
        db.add(log_entry)
        db.commit()
        db.close()
        return "Success"
    except Exception as e:
        return f"Error: {str(e)}"
