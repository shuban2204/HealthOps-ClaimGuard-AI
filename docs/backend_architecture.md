# Backend Architecture

## Overview

The backend is a FastAPI application under `/api/v1`. It provides denial-risk prediction, review prioritization, unusual claim detection, analytics, model metrics, policy evidence retrieval, and deterministic analyst brief generation for the CMS DE-SynPUF hybrid dataset.

## Service Boundaries

- `MLService` loads the Stage 2 preprocessing pipeline, XGBoost model, validation-selected threshold, and global feature importance.
- `AnomalyService` loads the Isolation Forest artifact for unusual claim detection.
- `ClaimService` seeds processed claims into SQLite and returns paginated claim detail.
- `AnalyticsService` reads aggregate counts and model driver summaries.
- `RetrievalService` loads synthetic demonstration policy documents, embeds sections with `sentence-transformers/all-MiniLM-L6-v2`, and indexes them with FAISS.
- `BriefService` creates a deterministic analyst brief from claim facts, model explanations, unusual-claim signals, and retrieved evidence.
- `ClaimsRepository` isolates SQLite persistence and query behavior.

## Startup

Application startup:

1. Creates SQLite tables if needed.
2. Loads model and anomaly artifacts once.
3. Seeds SQLite from `data/sample_claims.csv` if empty.
4. Builds the FAISS policy index from `data/policies`.

If a required artifact cannot load, startup fails with a clear error.

## Database Design

SQLite stores a compact claim row with:

- claim identifiers and filter fields
- key CMS-derived fields
- synthetic administrative fields
- precomputed denial probability, risk band, anomaly score, and anomaly flag
- full claim JSON for detail responses

Duplicate CMS claim IDs are converted into stable API IDs with numeric suffixes during persistence. The original value remains available as `source_claim_id`.

## Risk Bands

Risk bands use the Stage 2 validation-selected threshold:

- `LOW`: probability below selected threshold
- `MEDIUM`: probability from selected threshold to high threshold
- `HIGH`: probability at or above `max(0.65, selected_threshold + 0.35)`

## Retrieval Design

Policy files are fictional demonstration policies. Each section becomes a stable source chunk such as `prior_authorization:PA-03`. Claim-to-policy queries are deterministic and use claim state plus top explanation factors.

## Analyst Briefs

Briefs are deterministic and do not call an external LLM. The brief endpoint returns a summary, rationale, recommended reviewer actions, top policy citations, limitations, and a decision-support disclaimer. It is intended to help reviewers prepare an investigation, not to adjudicate a claim.

## Policy Disclaimer

Policy documents are synthetic and do not represent CMS, Evernorth, Cigna, or any real payer policy. Retrieved evidence is for analyst decision support only.

## Endpoints

- `GET /api/v1/health`
- `GET /api/v1/claims`
- `GET /api/v1/claims/{claim_id}`
- `GET /api/v1/claims/{claim_id}/evidence`
- `GET /api/v1/claims/{claim_id}/brief`
- `GET /api/v1/analytics/summary`
- `GET /api/v1/analytics/drivers`
- `GET /api/v1/model/metrics`
