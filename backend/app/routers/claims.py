from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, Request

from app.schemas import ClaimDetailResponse, ClaimListResponse, RiskBand, SortOrder


router = APIRouter(prefix="/claims", tags=["claims"])


@router.get("", response_model=ClaimListResponse)
def list_claims(
    request: Request,
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    search: str | None = None,
    risk_band: RiskBand | None = None,
    is_anomaly: bool | None = None,
    claim_type: str | None = None,
    provider_network: str | None = None,
    sort_by: str = Query(default="denial_probability", pattern="^(denial_probability|claim_total_charge|claim_id|anomaly_score)$"),
    sort_order: SortOrder = "desc",
):
    return request.app.state.claim_service.list_claims(
        limit=limit,
        offset=offset,
        search=search,
        risk_band=risk_band,
        is_anomaly=is_anomaly,
        claim_type=claim_type,
        provider_network=provider_network,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get("/{claim_id}", response_model=ClaimDetailResponse)
def get_claim(request: Request, claim_id: str):
    detail = request.app.state.claim_service.get_claim(claim_id)
    if detail is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "CLAIM_NOT_FOUND", "message": f"Claim {claim_id} was not found."},
        )
    return detail
