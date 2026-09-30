from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import API_PREFIX
from app.db import init_db
from app.routers import analytics, claims, evidence, health, model
from app.services.analytics_service import AnalyticsService
from app.services.anomaly_service import AnomalyService
from app.services.brief_service import BriefService
from app.services.claim_service import ClaimService
from app.services.ml_service import MLService
from app.services.retrieval_service import RetrievalService


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    app.state.ml_service = MLService()
    app.state.anomaly_service = AnomalyService()
    app.state.claim_service = ClaimService(app.state.ml_service, app.state.anomaly_service)
    app.state.claim_service.initialize_claims()
    app.state.analytics_service = AnalyticsService(app.state.ml_service)
    app.state.retrieval_service = RetrievalService()
    app.state.brief_service = BriefService()
    yield


app = FastAPI(title="HealthOps ClaimGuard AI Backend", version="0.3.0", lifespan=lifespan)
app.include_router(health.router, prefix=API_PREFIX)
app.include_router(claims.router, prefix=API_PREFIX)
app.include_router(analytics.router, prefix=API_PREFIX)
app.include_router(model.router, prefix=API_PREFIX)
app.include_router(evidence.router, prefix=API_PREFIX)
