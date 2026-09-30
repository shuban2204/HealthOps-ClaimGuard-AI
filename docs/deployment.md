# Deployment Readiness

## Runtime Assumptions

- The app is a decision-support demo and should run with synthetic or de-identified data only.
- Raw CMS ZIP files stay local under `data/raw/` and are excluded from Git and Docker context.
- Trained `.joblib` artifacts are generated locally by `python ml/train.py` and are required before backend startup.
- No OpenAI key or external LLM dependency is required for the current analyst brief flow.

## Local Production Smoke

1. Install and train:

   ```bash
   python -m pip install -r ml/requirements.txt
   python ml/generate_data.py --limit-rows 50000
   python ml/train.py
   ```

2. Run backend checks:

   ```bash
   set PYTHONPATH=backend
   pytest backend/tests -q
   ```

3. Run frontend checks:

   ```bash
   cd frontend
   npm test
   npm run build
   ```

4. Run the app with Compose:

   ```bash
   docker compose build
   docker compose up
   ```

5. Verify:

   ```bash
   curl http://localhost:8000/api/v1/health
   curl "http://localhost:8000/api/v1/claims?limit=1"
   ```

## Operational Notes

- `CLAIMGUARD_*` environment variables can override backend data, policy, model, metrics, and SQLite paths.
- The backend health check validates model and retrieval readiness through `/api/v1/health`.
- The frontend nginx container serves the built React app and proxies `/api/` to the backend service.
- `.github/workflows/ci.yml` is intentionally not part of the current commits because the available GitHub token lacks workflow scope.
