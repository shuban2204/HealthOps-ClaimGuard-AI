# Demo Script

## Setup

Run the backend and frontend locally:

```bash
set PYTHONPATH=backend
uvicorn app.main:app --app-dir backend --reload
cd frontend
npm run dev -- --host 127.0.0.1
```

Open `http://localhost:5173`.

## Five Minute Walkthrough

1. Dashboard: point out the total reviewed population, high-risk count, average denial probability, unusual-claim count, top risk signals, and risk matrix.
2. Priority queue: open one of the highest-risk claims from the dashboard or claims worklist.
3. Claim facts: show the operational fields that a reviewer would inspect, including network status, prior authorization, documentation, coding mismatch, and amount signals.
4. Explanation: click an explanation factor and show the related claim facts and policy evidence highlight together.
5. Evidence: expand the policy evidence panel and call out source IDs such as `prior_authorization:PA-03`.
6. Analyst brief: click `Generate brief`, then show the summary, rationale, next actions, citations, and decision-support disclaimer.
7. Model insights: open the model page and show XGBoost metrics, threshold, global drivers, and the data provenance note.

## Talk Track

- "This is not a claim denial engine. It is a prioritization and review support workbench."
- "The CMS base data is synthetic public-use claims data, and the missing payer operations fields are synthetic administrative enrichment."
- "The brief is deterministic and grounded in retrieved policy chunks. There is no external LLM dependency."
- "The highest value is connecting model risk, anomaly detection, claim facts, and policy evidence in one reviewer workflow."

## What To Avoid Claiming

- Do not claim production denial prediction performance.
- Do not claim fraud detection.
- Do not claim medical decision-making.
- Do not claim that the synthetic policies represent CMS, Evernorth, Cigna, or any real payer policy.
