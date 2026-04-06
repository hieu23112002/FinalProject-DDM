# Customer Churn Prediction System

Customer churn prediction system with a FastAPI service, preprocessing/training pipeline, and monitoring via Prometheus and Grafana.

## Main Structure

- `src/data_ingestion.py`: download and load the raw dataset
- `src/preprocessing.py`: data cleaning, feature engineering, and preprocessor artifact handling
- `src/train.py`: LightGBM training and model artifact export
- `src/app.py`: prediction API and Prometheus metrics endpoint
- `tests/test_api_pytest.py`: automated API tests
- `monitoring/`: Prometheus and Grafana configuration

## Run With Python

Requirement: Python 3.12

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Run the pipeline:

```powershell
python src/preprocessing.py
python src/train.py
python src/app.py
```

Available endpoints after startup:

- Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health: [http://localhost:8000/health](http://localhost:8000/health)
- Metrics: [http://localhost:8000/metrics](http://localhost:8000/metrics)

## Run Tests

```powershell
python -m pytest tests/test_api_pytest.py -v
```

## Run With Docker Compose

Requirement: Docker Desktop or Docker Engine must be running.

```powershell
docker compose up -d --build
```

Services:

- API: [http://localhost:8000](http://localhost:8000)
- Grafana: [http://localhost:3000](http://localhost:3000)
- Prometheus: [http://localhost:9090](http://localhost:9090)

Stop the stack:

```powershell
docker compose down
```

## CI/CD

The workflow in `.github/workflows/ci_cd.yml` has two jobs:

- `test`: runs on a GitHub-hosted runner, installs dependencies, and executes pytest
- `deploy`: runs on a self-hosted runner, verifies the Docker daemon, and deploys with `docker compose`

If deploy fails with a Docker daemon connection error, verify that Docker Desktop or Docker Engine is actually running on the self-hosted runner machine.
