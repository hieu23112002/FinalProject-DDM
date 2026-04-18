# Contributing Guide

This document defines how team members collaborate on the DDM501 final project.

## 1. Team Roles And Ownership

Update this table before final submission.

| Member | Role | Main Responsibilities | Owned Areas |
| :--- | :--- | :--- | :--- |
| Member 1 | ML Engineer | Data pipeline, feature engineering, training | `src/preprocessing.py`, `src/train.py` |
| Member 2 | Backend Engineer | API serving, DB integration, async worker | `src/app.py`, `src/database.py`, `src/worker.py` |
| Member 3 | MLOps Engineer | Docker, compose, CI/CD, monitoring | `Dockerfile`, `docker-compose.yml`, `.github/workflows/` |
| Member 4 | Frontend Engineer | Dashboard UX, API integration, validation | `frontend/` |

## 2. Branching Strategy

- Base branches:
  - `main`: production-ready branch.
  - `dev`: integration branch.
- Feature branches:
  - Naming format: `feature/<short-topic>` or `fix/<short-topic>`.
  - Example: `feature/mlflow-metrics`, `fix/loki-restart-loop`.

## 3. Commit Convention

Use meaningful commit messages with clear scope.

Recommended format:
- `feat(api): add prediction logging to celery`
- `fix(ci): resolve self-hosted safe.directory issue`
- `docs(readme): add deployment runbook`
- `chore(compose): add mlflow persistent volume`

## 4. Pull Request Workflow

1. Sync latest `dev`.
2. Create feature/fix branch.
3. Implement and test locally.
4. Open PR to `dev` with clear summary.
5. Request at least one reviewer.
6. Merge only when CI checks pass.

PR must include:
- Problem statement.
- What changed.
- How to test.
- Screenshots/logs when relevant.

## 5. Development Standards

### 5.1 Python
- Use type hints where possible.
- Keep functions focused and small.
- Do not add dead code or commented legacy blocks.
- Run tests before pushing.

### 5.2 Frontend
- Keep components readable and typed.
- Avoid `any` unless absolutely necessary.
- Pass lint checks before opening PR.

### 5.3 Docker And Infra
- Keep service names stable and descriptive.
- Avoid breaking existing ports without documenting.
- Update docs when changing runtime behavior.

## 6. Quality Gates

Before merge, each PR should pass:
- Backend lint/security checks.
- Frontend lint checks.
- API tests.
- Docker compose config validation.

## 7. Local Test Commands

### 7.1 Python Tests
```powershell
python -m pytest tests/test_api_pytest.py -v
```

### 7.2 Frontend Lint
```powershell
cd frontend
npm install
npm run lint
```

### 7.3 Full Stack Smoke Check
```powershell
docker compose up -d --build
docker compose ps
curl http://localhost:8000/health
```

## 8. Documentation Responsibilities

Any functional change must update relevant docs:
- `README.md` for setup/run instructions.
- `ARCHITECTURE.md` for design changes.
- `CONTRIBUTING.md` for process updates.

## 9. Definition Of Done

A task is done only when:
- Code is implemented.
- Tests/lint pass.
- Docs updated.
- PR reviewed and merged.
- No critical runtime errors in compose stack.
