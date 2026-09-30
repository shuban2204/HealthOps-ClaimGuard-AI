# Architecture

HealthOps ClaimGuard AI is a local demo system for claims operations triage. The React frontend calls a FastAPI backend under `/api/v1`. The backend scores synthetic claims with a trained scikit-learn classifier, flags unusual records with Isolation Forest, retrieves policy evidence with TF-IDF similarity, and returns a grounded analyst brief.

```mermaid
flowchart LR
  A[React dashboard] --> B[FastAPI]
  B --> C[Risk classifier]
  B --> D[Isolation Forest]
  B --> E[Policy retrieval]
  E --> F[Markdown policy corpus]
  B --> G[Synthetic claims CSV]
```

The implementation intentionally avoids PHI, autonomous claim decisions, and external LLM dependencies. The brief generator is deterministic and cites retrieved policy chunks.

