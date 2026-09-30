from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from app.schemas import AnalystBriefResponse, EvidenceResponse


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


@router.get("/{claim_id}/brief", response_model=AnalystBriefResponse)
def analyst_brief(request: Request, claim_id: str):
    detail = request.app.state.claim_service.get_claim(claim_id)
    if detail is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "CLAIM_NOT_FOUND", "message": f"Claim {claim_id} was not found."},
        )
    evidence_payload = request.app.state.retrieval_service.evidence_for_claim(detail)
    return request.app.state.brief_service.brief_for_claim(detail, evidence_payload)
