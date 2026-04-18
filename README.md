# Enterprise Churn Prediction System

An end-to-end, production-ready Customer Churn Prediction system featuring a high-performance ML pipeline, a modern Next.js dashboard, and a robust observability stack.

## 🚀 Key Features

- **Scalable Architecture**: Microservices orchestrated via Docker Compose.
- **Enterprise Serving**: Unified API Gateway using Nginx.
- **Modern UI**: Next.js 14 Dashboard with real-time SHAP analysis.
- **Persistence Layer**: PostgreSQL for robust inference logging and auditing.
- **Async Processing**: Celery & Redis for offloading heavy ML background tasks.
- **Full Observability**: Metrics (Prometheus), Logging (Loki), and Visualization (Grafana).

## 📂 Project Structure

- `frontend/`: Next.js 14 Web Application (Port 80/3000)
- `src/`: Backend Core (FastAPI, ML Engine, Database logic)
- `nginx/`: API Gateway & Reverse Proxy configuration
- `monitoring/`: Full Grafana/Loki/Prometheus stack
- `models/`: Trained model binaries and preprocessors
- `data/`: Dataset storage and raw files

## 🛠️ Tech Stack

- **ML**: LightGBM, Scikit-learn, SHAP, MLflow
- **Backend**: FastAPI, SQLAlchemy, Celery, Redis
- **Frontend**: Next.js 14, Tailwind CSS, TypeScript
- **Infrastructure**: Docker, Nginx, PostgreSQL
- **DevOps**: GitHub Actions (CI/CD with Quality Gates)

## 🚦 Getting Started

### Prerequisites
- Docker & Docker Compose
- Node.js (for local frontend dev)
- Python 3.12 (for local backend dev)

### The Fast Way (Docker Compose)
The easiest way to run the entire stack is using Docker Compose:

```powershell
docker compose up -d --build
```

### Accessing Services
After startup, the system is reachable at:

| Service | URL | Description |
| :--- | :--- | :--- |
| **User Dashboard** | [http://localhost](http://localhost) | Main App UI |
| **API Docs** | [http://localhost/api/docs](http://localhost/api/docs) | Interactive API Spec |
admin
admin
| **Grafana** | [http://localhost:3000](http://localhost:3000) | Observability 
Dashboard |
Email: admin@admin.com
Password: admin
| **pgAdmin** | [http://localhost:5050](http://localhost:5050) | Database Explorer |
| **Prometheus** | [http://localhost:9090](http://localhost:9090) | Metric Storage |

## 🧪 Development & Testing

### Local Python Environment
```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Running Tests
```powershell
python -m pytest tests/test_api_pytest.py -v
```

## 🔄 CI/CD Pipeline
The project includes a multi-stage GitHub Actions workflow (`.github/workflows/ci_cd.yml`):
1. **Linting**: Automated code quality checks for both Python (Ruff/Bandit) and Frontend (ESLint).
2. **Testing**: Automated regression tests for the API.
3. **Deployment**: Zero-downtime deployment to the target server via Docker Compose.
