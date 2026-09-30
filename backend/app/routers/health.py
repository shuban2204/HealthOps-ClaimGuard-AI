from fastapi import APIRouter, Request

from app.schemas import HealthResponse


router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health(request: Request):
    retrieval = getattr(request.app.state, "retrieval_service", None)
    return {
        "status": "ok",
        "model_loaded": bool(getattr(request.app.state, "ml_service", None)),
        "retrieval_ready": bool(getattr(retrieval, "ready", False)),
    }
