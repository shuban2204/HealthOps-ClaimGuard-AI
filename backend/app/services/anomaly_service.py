from __future__ import annotations

from typing import Any

import joblib
import pandas as pd

from app.config import ANOMALY_PATH


class AnomalyService:
    def __init__(self) -> None:
        if not ANOMALY_PATH.exists():
            raise RuntimeError(f"Anomaly artifact not found: {ANOMALY_PATH}")
        self.pipeline = joblib.load(ANOMALY_PATH)
        self.features = list(self.pipeline.named_steps["preprocessor"].feature_names_in_)

    @property
    def loaded(self) -> bool:
        return True

    def score_batch(self, frame: pd.DataFrame) -> tuple:
        scores = self.pipeline.decision_function(frame[self.features])
        flags = self.pipeline.predict(frame[self.features]) == -1
        return scores, flags

    def score(self, claim: dict[str, Any]) -> dict[str, Any]:
        frame = pd.DataFrame([claim])
        scores, flags = self.score_batch(frame)
        return {"anomaly_score": round(float(scores[0]), 4), "is_anomaly": bool(flags[0])}

