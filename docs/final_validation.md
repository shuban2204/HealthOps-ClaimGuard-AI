# Final Validation Checklist

Use this checklist before recording a demo, submitting the project, or making a release tag.

## Data And Model

- `data/sample_claims.csv` exists.
- `ml/artifacts/classifier.joblib` exists locally.
- `ml/artifacts/anomaly_detector.joblib` exists locally.
- `ml/artifacts/metrics.json` reports model version `hybrid-cms-admin-0.2.0`.
- `ml/artifacts/leakage_audit.json` reports `status: pass`.

## Backend

```bash
set PYTHONPATH=backend
pytest backend/tests -q
uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
```

Expected:

- `/api/v1/health` returns `status: ok`
- `/api/v1/claims?limit=1` returns at least one claim
- `/api/v1/claims/{claim_id}/evidence` returns cited policy chunks
- `/api/v1/claims/{claim_id}/brief` returns a deterministic analyst brief

## Frontend

```bash
cd frontend
npm test
npm run build
npm run dev -- --host 127.0.0.1
```

Expected:

- dashboard loads summary metrics
- claims queue filters and paginates
- claim detail shows facts, explanation, anomaly signal, evidence, and analyst brief
- model insights page shows metrics and data provenance

## Docker

```bash
docker compose config
docker compose build
docker compose up
```

Expected:

- backend health check becomes healthy
- frontend health check becomes healthy
- `http://localhost:5173` serves the workbench

## Current Verified State

- Backend tests: 12 passing
- Frontend tests: 5 passing
- Frontend build: passing
- Docker Compose config: passing
