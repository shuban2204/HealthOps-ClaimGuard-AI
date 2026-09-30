from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


RiskBand = Literal["LOW", "MEDIUM", "HIGH"]
SortOrder = Literal["asc", "desc"]


class TopFactor(BaseModel):
    feature: str
    label: str
    feature_value: Any
    contribution: float
    direction: Literal["increases_risk", "decreases_risk"]


class Prediction(BaseModel):
    denial_probability: float = Field(ge=0, le=1)
    risk_band: RiskBand
    top_factors: list[TopFactor]


class AnomalyResult(BaseModel):
    anomaly_score: float
    is_anomaly: bool


class ClaimDetailResponse(BaseModel):
    claim: dict[str, Any]
    prediction: Prediction
    anomaly: AnomalyResult


class Pagination(BaseModel):
    total: int
    limit: int
    offset: int
    has_more: bool


class ClaimListResponse(BaseModel):
    items: list[dict[str, Any]]
    pagination: Pagination


class HealthResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    status: str
    model_loaded: bool
    retrieval_ready: bool


class EvidenceSource(BaseModel):
    source_id: str
    title: str
    section: str
    text: str
    similarity_score: float


class EvidenceResponse(BaseModel):
    claim_id: str
    query: str
    sources: list[EvidenceSource]
