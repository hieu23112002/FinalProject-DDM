# DDM501 Final Project - Enterprise Churn Prediction System

End-to-end Machine Learning system for customer churn prediction, covering data pipeline, model training, experiment tracking, API serving, observability, CI/CD, and team collaboration workflow.

## 1. Problem Definition

### 1.1 Business Context
Telecom operators lose revenue when customers churn. The system predicts churn risk early so retention teams can intervene before customers leave.

### 1.2 Problem Statement
Given customer profile and service usage data, predict whether a customer is likely to churn and provide explainable risk factors.

### 1.3 Users And Use Cases
- Retention analyst:
  - Submit customer profiles for prediction.
  - Review top churn risk factors.
- Operations engineer:
  - Monitor API health, latency, and prediction throughput.
  - Track container logs and service status.
- ML engineer:
  - Re-run preprocessing and training.
  - Track experiments and model versions in MLflow.

### 1.4 Success Metrics
- Business metrics:
  - Increase targeted retention campaign efficiency.
  - Reduce false positive outreach to stable customers.
- Model metrics:
  - Accuracy, precision, recall, F1, ROC-AUC on test set.
- System metrics:
  - API availability (`/health`).
  - API latency (`churn_api_latency_seconds`).
  - Prediction throughput (`churn_api_predictions_total`).

### 1.5 Scope And Constraints
- In scope:
  - Batch preprocessing + training pipeline.
  - Real-time churn prediction API.
  - Multi-service deployment with Docker Compose.
  - Monitoring stack with Prometheus, Grafana, Loki, Promtail.
- Constraints:
  - Uses a tabular churn dataset (not streaming data).
  - Single-model serving flow (LightGBM baseline).
  - Local/self-hosted deployment focus.

## 2. System Overview

### 2.1 Main Components
- `frontend/`: Next.js dashboard.
- `nginx/`: gateway and reverse proxy.
- `src/app.py`: FastAPI serving and SHAP explanations.
- `src/preprocessing.py`: cleaning, feature engineering, train/test split.
- `src/train.py`: training, evaluation, MLflow logging, artifact export.
- `src/worker.py`: async task worker for prediction logging.
- `src/database.py`: PostgreSQL persistence model.
- `monitoring/`: Prometheus, Grafana, Loki, Promtail configuration.

### 2.2 Runtime Services
- `nginx`: external entrypoint.
- `frontend`: UI.
- `churn-api`: ML serving API.
- `mlflow`: experiment tracking server.
- `db` + `pgadmin`: persistence and DB admin UI.
- `redis` + `worker`: asynchronous background processing.
- `prometheus` + `grafana` + `loki` + `promtail`: observability stack.

## 3. Repository Structure

```text
.
|-- .github/workflows/ci_cd.yml
|-- ARCHITECTURE.md
|-- CONTRIBUTING.md
|-- Dockerfile
|-- docker-compose.yml
|-- frontend/
|-- monitoring/
|-- nginx/
|-- src/
|   |-- app.py
|   |-- data_ingestion.py
|   |-- database.py
|   |-- preprocessing.py
|   |-- train.py
|   `-- worker.py
`-- tests/
```

## 4. Local Setup

### 4.1 Prerequisites
- Docker Desktop or Docker Engine
- Docker Compose
- Python 3.12 (for local non-container runs)
- Node.js 20+ (for local frontend development)

### 4.2 Run Full Stack

```powershell
docker compose up -d --build
```

### 4.3 Stop Stack

```powershell
docker compose down
```

## 5. Service Endpoints

- Main app (Nginx): <http://localhost:8080>
- API docs (Swagger): <http://localhost:8080/api/docs>
- API direct: <http://localhost:8000>
- MLflow: <http://localhost:5000>
- Prometheus: <http://localhost:9090>
- Grafana: <http://localhost:3101>
- Loki API: <http://localhost:3100>
- pgAdmin: <http://localhost:5050>
- Redis: `localhost:6379`

Default credentials:
- Grafana: `admin / admin`
- pgAdmin: `admin@admin.com / admin`
- PostgreSQL: `user / password` (DB: `churn_db`)

## 6. ML Pipeline

### 6.1 Preprocessing
```powershell
docker compose exec -T churn-api python src/preprocessing.py
```

Artifacts created under `data/processed/`:
- `X_train.csv`, `X_test.csv`
- `y_train.csv`, `y_test.csv`
- `label_encoders.pkl`
- `preprocessor.pkl`

### 6.2 Training
```powershell
docker compose exec -T churn-api python src/train.py
```

Training outputs:
- Model artifacts in `models/`.
- MLflow run in experiment `Churn_Prediction_Production`.
- Logged params + evaluation metrics + model artifact.

## 7. API Usage

### 7.1 Health
```powershell
curl http://localhost:8000/health
```

### 7.2 Predict
```powershell
curl -X POST "http://localhost:8000/predict" `
  -H "Content-Type: application/json" `
  -d "{\"gender\":\"Female\",\"SeniorCitizen\":0,\"Partner\":\"Yes\",\"Dependents\":\"No\",\"tenure\":12,\"PhoneService\":\"Yes\",\"MultipleLines\":\"No\",\"InternetService\":\"Fiber optic\",\"OnlineSecurity\":\"No\",\"OnlineBackup\":\"No\",\"DeviceProtection\":\"No\",\"TechSupport\":\"No\",\"StreamingTV\":\"No\",\"StreamingMovies\":\"No\",\"Contract\":\"Month-to-month\",\"PaperlessBilling\":\"Yes\",\"PaymentMethod\":\"Electronic check\",\"MonthlyCharges\":70.35,\"TotalCharges\":\"844.2\"}"
```

## 8. Monitoring And Operations

### 8.1 Check Containers
```powershell
docker compose ps
```

### 8.2 Check Logs
```powershell
docker compose logs -f churn-api
docker compose logs -f worker
docker compose logs -f mlflow
```

### 8.3 Key Prometheus Metrics
- `churn_api_predictions_total`
- `churn_api_latency_seconds`
- `up{job="churn-api-service"}`

## 9. Testing

### 9.1 API Tests
```powershell
python -m pytest tests/test_api_pytest.py -v
```

### 9.2 Manual API Test
```powershell
python tests/test_api_manual.py
```

## 10. CI/CD Pipeline

Workflow: `.github/workflows/ci_cd.yml`

Pipeline flow:
1. Lint and security scan (`ruff`, `bandit`, `eslint`).
2. API tests (`pytest`).
3. Self-hosted deploy (main branch only).
4. Pre-deploy training inside Docker stack.
5. Production stack deployment with health verification.

## 11. Responsible AI Notes

- Explainability:
  - SHAP is used in serving flow to return top risk factors.
- Fairness and bias:
  - Should be evaluated explicitly by protected groups before production decisions.
- Privacy:
  - Do not commit sensitive customer data.
  - Keep credentials in environment variables for production.
- Ethical use:
  - Predictions are decision support, not sole decision authority.

## 12. Required Submission Files

- [README.md](C:/MSA/DDM/FinalProject/README.md)
- [ARCHITECTURE.md](C:/MSA/DDM/FinalProject/ARCHITECTURE.md)
- [CONTRIBUTING.md](C:/MSA/DDM/FinalProject/CONTRIBUTING.md)
- [requirements.txt](C:/MSA/DDM/FinalProject/requirements.txt)
- [Dockerfile](C:/MSA/DDM/FinalProject/Dockerfile)
- [docker-compose.yml](C:/MSA/DDM/FinalProject/docker-compose.yml)
- [.github/workflows/ci_cd.yml](C:/MSA/DDM/FinalProject/.github/workflows/ci_cd.yml)
