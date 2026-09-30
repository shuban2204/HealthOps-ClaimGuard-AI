# Portfolio Summary

## One Sentence

HealthOps ClaimGuard AI is an end-to-end claims review workbench that combines explainable denial-risk modeling, unusual-claim detection, policy evidence retrieval, and deterministic analyst brief generation.

## What Makes It Strong

- Uses a public CMS synthetic claims substrate instead of a toy CSV.
- Separates public claims-derived fields from synthetic administrative workflow enrichment.
- Trains and evaluates a supervised risk model with leakage checks and held-out metrics.
- Adds an Isolation Forest signal for unusual claims without representing it as fraud detection.
- Grounds reviewer evidence in a synthetic policy corpus with stable source IDs.
- Provides a real FastAPI backend and React operations workbench.
- Generates deterministic, cited analyst briefs without relying on an external LLM.
- Documents responsible AI boundaries and deployment assumptions.

## Suggested Resume Bullet

Built HealthOps ClaimGuard AI, an end-to-end healthcare claims review platform using CMS DE-SynPUF data, synthetic administrative enrichment, XGBoost risk scoring, Isolation Forest anomaly detection, FastAPI, React, FAISS policy retrieval, and deterministic cited analyst briefs.

## Suggested Demo Pitch

This project shows how an AI-assisted operations workflow can support claims reviewers without replacing them. A reviewer starts with a prioritized queue, drills into a claim, sees model drivers and unusual-claim signals, reviews policy evidence, and generates a cited analyst brief. The system is intentionally bounded: synthetic data, no PHI, no autonomous denials, and no uncited generated claims.
