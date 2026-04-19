# System Architecture - Enterprise Churn Prediction

This document explains the system using a workflow style similar to the reference diagram format.

---

## 1) High-Level Architecture

```text
+--------------------------------------------------------------+
|                 Churn Prediction Platform                    |
+--------------------------------------------------------------+
         |                          |                       |
         v                          v                       v
   [User/Web UI]              [ML Pipeline]         [Observability]
         |                          |                       |
         v                          v                       v
   [Nginx Gateway]            [Preprocess + Train]   [Prometheus/Grafana]
         |                          |                       |
         v                          v                       v
     [FastAPI]  <--------------> [MLflow] <----------> [Loki/Promtail]
         |
         v
 [Redis Queue] ---> [Celery Worker] ---> [PostgreSQL]
```

---

## 2) Service Responsibilities

- `nginx_gateway`: single entry point, routes `/` to frontend and `/api` to FastAPI.
- `churn_frontend`: Next.js dashboard for input and result display.
- `churn_api_service`: inference API, SHAP explanation, Prometheus metrics endpoint.
- `mlflow_service`: tracks params/metrics/models from training runs.
- `churn_redis` + `churn_worker`: async pipeline for background DB logging tasks.
- `churn_db`: stores prediction logs for audit and analysis.
- `prometheus_service`: scrapes API metrics.
- `grafana_service`: visualizes metrics/logs dashboards.
- `loki_service` + `promtail_service`: centralized log aggregation.

---

## 3) Prediction Request Workflow 

```text
+--------------------------------------------------------------+
|                 Online Prediction Workflow                   |
+--------------------------------------------------------------+

START
  |
  v
[User submits form from frontend]
  |
  v
[Nginx routes request to /api/predict]
  |
  v
[FastAPI validates payload]
  |
  +---- invalid ----> END (HTTP 422/400)
  |
  v
[Load model + preprocessor artifacts]
  |
  +---- missing artifacts ----> END (HTTP 503)
  |
  v
[Feature engineering + inference]
  |
  v
[Compute SHAP top risk factors]
  |
  v
[Return response to user]
  |
  v
[Enqueue async log task to Redis]
  |
  v
[Celery worker writes prediction log to PostgreSQL]
  |
  v
END (success)
```

---

## 4) Training And MLflow Workflow

```text
+--------------------------------------------------------------+
|                 Training + Tracking Workflow                 |
+--------------------------------------------------------------+

START
  |
  v
[Run preprocessing.py]
  |
  v
[Clean + encode + split train/test]
  |
  v
[Save processed artifacts to data/processed]
  |
  v
[Run train.py]
  |
  v
[Set MLFLOW_TRACKING_URI]
  |
  v
[Train LightGBM model]
  |
  v
[Evaluate on test set]
  |
  v
[Log params + metrics + model to MLflow]
  |
  v
[Save best_model.pkl + preprocessor.pkl to models/]
  |
  v
END
```

---

## 5) Deployment Workflow (CI/CD)

```text
+--------------------------------------------------------------+
|                   GitHub Actions Workflow                    |
+--------------------------------------------------------------+

push/PR
  |
  v
[Lint + Security]
  |
  v
[Pytest API tests]
  |
  +---- fail ----> END (pipeline failed)
  |
  v
[Self-hosted deploy job]
  |
  v
[Prepare docker + safe git directory]
  |
  v
[Start MLflow]
  |
  v
[Run preprocessing + training (pre-deploy)]
  |
  +---- fail ----> END (skip deploy)
  |
  v
[docker compose up -d --build]
  |
  v
[Health check churn_api_service]
  |
  +---- fail ----> END (deploy failed)
  |
  v
END (deploy successful)
```

---

## 6) Data And Artifact Flow

```text
raw dataset
  |
  v
data_ingestion.py
  |
  v
preprocessing.py
  |
  +--> data/processed/X_train.csv, X_test.csv, y_train.csv, y_test.csv
  +--> data/processed/preprocessor.pkl
  |
  v
train.py
  |
  +--> models/best_model.pkl
  +--> models/feature_names.pkl
  +--> models/preprocessor.pkl
  +--> MLflow run (params, metrics, artifacts)
```

---

## 7) Monitoring Workflow

```text
churn-api /metrics ----> Prometheus ----> Grafana dashboards

docker container logs --> Promtail ------> Loki -----------> Grafana logs
```

---

## 8) Trade-Offs

- Docker Compose over Kubernetes:
  - Faster setup for course scope.
  - Lower operational complexity.
  - Limited horizontal scaling features.
- Single-model serving:
  - Easier debugging and maintainability.
  - No canary or A/B model routing yet.
- Local volume-based MLflow store:
  - Simple and portable.
  - Not ideal for large-scale distributed production.

---

## 9) Future Improvements

- Add Prometheus Alertmanager rules for error rate/latency.
- Add fairness and bias evaluation report artifacts per model version.
- Add model registry stage transitions (Staging/Production) in MLflow.
- Add authentication and role-based access for production endpoints.
