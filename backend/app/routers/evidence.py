from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from app.schemas import EvidenceResponse


router = APIRouter(prefix="/claims", tags=["evidence"])


@router.get("/{claim_id}/evidence", response_model=EvidenceResponse)
def evidence(request: Request, claim_id: str):
    detail = request.app.state.claim_service.get_claim(claim_id)
    if detail is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "CLAIM_NOT_FOUND", "message": f"Claim {claim_id} was not found."},
        )
    return request.app.state.retrieval_service.evidence_for_claim(detail)

