from __future__ import annotations

import json

from fastapi import APIRouter

from app.config import METRICS_PATH


router = APIRouter(prefix="/model", tags=["model"])


@router.get("/metrics")
def metrics():
    if not METRICS_PATH.exists():
        return {}
    data = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    primary = data["primary_model"]
    return {
        "model_version": data["model_version"],
        "model_name": primary["name"],
        "selected_threshold": data["threshold"],
        "train": primary["train"],
        "validation": primary["validation"],
        "test": primary["test"],
        "baseline_logistic_regression": data["baseline_logistic_regression"],
        "class_prevalence": primary["test"]["positive_prevalence"],
    }
