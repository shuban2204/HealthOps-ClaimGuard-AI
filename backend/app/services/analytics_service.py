from __future__ import annotations

from typing import Any

from app.db import session_scope
from app.repositories.claims_repository import ClaimsRepository
from app.services.ml_service import MLService


class AnalyticsService:
    def __init__(self, ml_service: MLService):
        self.ml_service = ml_service

    def summary(self) -> dict[str, Any]:
        with session_scope() as session:
            return ClaimsRepository(session).summary_counts()

    def drivers(self, limit: int = 15) -> dict[str, Any]:
        return {"items": self.ml_service.global_importance[:limit]}

