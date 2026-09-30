from __future__ import annotations

import json
from typing import Any

from sqlalchemy import asc, desc, func, or_, select
from sqlalchemy.orm import Session

from app.db import ClaimRecord


class ClaimsRepository:
    def __init__(self, session: Session):
        self.session = session

    def count(self) -> int:
        return int(self.session.scalar(select(func.count()).select_from(ClaimRecord)) or 0)

    def upsert_many(self, rows: list[dict[str, Any]]) -> None:
        records = [ClaimRecord(**row) for row in rows]
        self.session.bulk_save_objects(records)

    def get(self, claim_id: str) -> dict[str, Any] | None:
        record = self.session.get(ClaimRecord, claim_id)
        return self._to_dict(record) if record else None

    def list(
        self,
        limit: int,
        offset: int,
        search: str | None = None,
        risk_band: str | None = None,
        is_anomaly: bool | None = None,
        claim_type: str | None = None,
        provider_network: str | None = None,
        sort_by: str = "denial_probability",
        sort_order: str = "desc",
    ) -> tuple[list[dict[str, Any]], int]:
        query = select(ClaimRecord)
        count_query = select(func.count()).select_from(ClaimRecord)
        filters = []
        if search:
            pattern = f"%{search}%"
            filters.append(or_(ClaimRecord.claim_id.like(pattern), ClaimRecord.claim_type.like(pattern), ClaimRecord.provider_network.like(pattern)))
        if risk_band:
            filters.append(ClaimRecord.risk_band == risk_band)
        if is_anomaly is not None:
            filters.append(ClaimRecord.is_anomaly == is_anomaly)
        if claim_type:
            filters.append(ClaimRecord.claim_type == claim_type)
        if provider_network:
            filters.append(ClaimRecord.provider_network == provider_network)
        for condition in filters:
            query = query.where(condition)
            count_query = count_query.where(condition)

        sortable = {
            "denial_probability": ClaimRecord.denial_probability,
            "claim_total_charge": ClaimRecord.claim_total_charge,
            "claim_id": ClaimRecord.claim_id,
            "anomaly_score": ClaimRecord.anomaly_score,
        }
        sort_column = sortable.get(sort_by, ClaimRecord.denial_probability)
        query = query.order_by(desc(sort_column) if sort_order == "desc" else asc(sort_column)).limit(limit).offset(offset)
        total = int(self.session.scalar(count_query) or 0)
        return [self._to_dict(record) for record in self.session.scalars(query).all()], total

    def summary_counts(self) -> dict[str, Any]:
        total = self.count()
        band_counts = dict(self.session.execute(select(ClaimRecord.risk_band, func.count()).group_by(ClaimRecord.risk_band)).all())
        avg_probability = float(self.session.scalar(select(func.avg(ClaimRecord.denial_probability))) or 0)
        anomalous = int(self.session.scalar(select(func.count()).where(ClaimRecord.is_anomaly == True)) or 0)  # noqa: E712
        prevalence = float(self.session.scalar(select(func.avg(ClaimRecord.denied))) or 0)
        return {
            "total_claims": total,
            "high_risk_claims": int(band_counts.get("HIGH", 0)),
            "medium_risk_claims": int(band_counts.get("MEDIUM", 0)),
            "low_risk_claims": int(band_counts.get("LOW", 0)),
            "average_denial_probability": round(avg_probability, 4),
            "anomalous_claims": anomalous,
            "target_prevalence": round(prevalence, 4),
        }

    def _to_dict(self, record: ClaimRecord) -> dict[str, Any]:
        base = {column.name: getattr(record, column.name) for column in ClaimRecord.__table__.columns}
        base["claim"] = json.loads(record.claim_json)
        base.pop("claim_json", None)
        return base

