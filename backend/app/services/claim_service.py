from __future__ import annotations

import json
from typing import Any

import pandas as pd

from app.config import DATA_PATH
from app.db import session_scope
from app.repositories.claims_repository import ClaimsRepository
from app.services.anomaly_service import AnomalyService
from app.services.ml_service import MLService
from app.utils.formatting import risk_band


class ClaimService:
    def __init__(self, ml_service: MLService, anomaly_service: AnomalyService) -> None:
        self.ml_service = ml_service
        self.anomaly_service = anomaly_service

    def initialize_claims(self) -> None:
        with session_scope() as session:
            repo = ClaimsRepository(session)
            if repo.count() > 0:
                return
            if not DATA_PATH.exists():
                raise RuntimeError(f"Processed claims dataset not found: {DATA_PATH}")
            frame = pd.read_csv(DATA_PATH)
            frame["api_claim_id"] = frame["claim_id"].astype(str)
            duplicate_order = frame.groupby("api_claim_id").cumcount()
            duplicate_mask = frame.duplicated("api_claim_id", keep=False)
            frame.loc[duplicate_mask, "api_claim_id"] = (
                frame.loc[duplicate_mask, "api_claim_id"] + "-" + (duplicate_order[duplicate_mask] + 1).astype(str)
            )
            probabilities = self.ml_service.predict_batch(frame)
            anomaly_scores, anomaly_flags = self.anomaly_service.score_batch(frame)
            rows = []
            for index, claim in frame.iterrows():
                probability = float(probabilities[index])
                claim_dict = normalize_claim_dict(claim.to_dict())
                claim_dict["source_claim_id"] = str(claim_dict["claim_id"])
                claim_dict["claim_id"] = str(claim_dict["api_claim_id"])
                claim_dict.pop("api_claim_id", None)
                rows.append(
                    {
                        "claim_id": claim_dict["claim_id"],
                        "claim_type": str(claim_dict.get("claim_type", "")),
                        "provider_network": str(claim_dict.get("provider_network", "")),
                        "risk_band": risk_band(probability, self.ml_service.threshold),
                        "is_anomaly": bool(anomaly_flags[index]),
                        "claim_payment_amount": float(claim_dict.get("claim_payment_amount", 0) or 0),
                        "claim_total_charge": float(claim_dict.get("claim_total_charge", 0) or 0),
                        "claim_duration_days": int(claim_dict.get("claim_duration_days", 0) or 0),
                        "diagnosis_count": int(claim_dict.get("diagnosis_count", 0) or 0),
                        "procedure_count": int(claim_dict.get("procedure_count", 0) or 0),
                        "reimbursement_ratio": float(claim_dict.get("reimbursement_ratio", 0) or 0),
                        "prior_auth_required": bool(claim_dict.get("prior_auth_required")),
                        "prior_auth_present": bool(claim_dict.get("prior_auth_present")),
                        "documentation_complete": bool(claim_dict.get("documentation_complete")),
                        "coding_mismatch_flag": bool(claim_dict.get("coding_mismatch_flag")),
                        "duplicate_claim_flag": bool(claim_dict.get("duplicate_claim_flag")),
                        "member_coverage_active": bool(claim_dict.get("member_coverage_active")),
                        "timely_filing_flag": bool(claim_dict.get("timely_filing_flag")),
                        "historical_provider_denial_rate": float(claim_dict.get("historical_provider_denial_rate", 0) or 0),
                        "denial_probability": round(probability, 4),
                        "anomaly_score": round(float(anomaly_scores[index]), 4),
                        "denied": int(claim_dict.get("denied", 0) or 0),
                        "claim_json": json.dumps(claim_dict, default=str),
                    }
                )
            repo.upsert_many(rows)

    def list_claims(self, **filters) -> dict[str, Any]:
        with session_scope() as session:
            repo = ClaimsRepository(session)
            items, total = repo.list(**filters)
            return {
                "items": [self._summary_item(item) for item in items],
                "pagination": {
                    "total": total,
                    "limit": filters["limit"],
                    "offset": filters["offset"],
                    "has_more": filters["offset"] + filters["limit"] < total,
                },
            }

    def get_claim(self, claim_id: str) -> dict[str, Any] | None:
        with session_scope() as session:
            record = ClaimsRepository(session).get(claim_id)
        if record is None:
            return None
        claim = record["claim"]
        return {
            "claim": claim,
            "prediction": {
                "denial_probability": record["denial_probability"],
                "risk_band": record["risk_band"],
                "top_factors": self.ml_service.explain(claim),
            },
            "anomaly": {
                "anomaly_score": record["anomaly_score"],
                "is_anomaly": record["is_anomaly"],
            },
        }

    def _summary_item(self, record: dict[str, Any]) -> dict[str, Any]:
        return {
            "claim_id": record["claim_id"],
            "claim_type": record["claim_type"],
            "provider_network": record["provider_network"],
            "claim_total_charge": record["claim_total_charge"],
            "denial_probability": record["denial_probability"],
            "risk_band": record["risk_band"],
            "anomaly_score": record["anomaly_score"],
            "is_anomaly": record["is_anomaly"],
        }


def normalize_claim_dict(claim: dict[str, Any]) -> dict[str, Any]:
    normalized = {}
    for key, value in claim.items():
        if pd.isna(value):
            normalized[key] = None
        elif hasattr(value, "item"):
            normalized[key] = value.item()
        else:
            normalized[key] = value
    return normalized
