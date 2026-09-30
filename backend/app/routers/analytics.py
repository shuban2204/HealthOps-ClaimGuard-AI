from fastapi import APIRouter, Query, Request


router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary")
def summary(request: Request):
    return request.app.state.analytics_service.summary()


@router.get("/drivers")
def drivers(request: Request, limit: int = Query(default=15, ge=1, le=30)):
    return request.app.state.analytics_service.drivers(limit=limit)
