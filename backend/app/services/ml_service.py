from __future__ import annotations

from typing import Any

import joblib
import numpy as np
import pandas as pd

from app.config import MODEL_PATH, MODEL_VERSION
from app.utils.formatting import humanize_feature_name, risk_band


class MLService:
    def __init__(self) -> None:
        if not MODEL_PATH.exists():
            raise RuntimeError(f"Model artifact not found: {MODEL_PATH}")
        artifact = joblib.load(MODEL_PATH)
        self.preprocessor = artifact["preprocessor"]
        self.model = artifact["model"]
        self.threshold = float(artifact["threshold"])
        self.features = artifact["features"]
        self.global_importance = artifact["global_importance"]
        self.feature_names = [
            str(name).replace("cat__", "").replace("bool__", "").replace("num__", "")
            for name in self.preprocessor.get_feature_names_out()
        ]
        self._explainer = None

    @property
    def loaded(self) -> bool:
        return True

    def predict_batch(self, frame: pd.DataFrame) -> np.ndarray:
        return self.model.predict_proba(self.preprocessor.transform(frame[self.features]))[:, 1]

    def predict(self, claim: dict[str, Any]) -> dict[str, Any]:
        probability = float(self.predict_batch(pd.DataFrame([claim]))[0])
        return {
            "denial_probability": round(probability, 4),
            "risk_band": risk_band(probability, self.threshold),
            "top_factors": self.explain(claim),
            "model_version": MODEL_VERSION,
        }

    def explain(self, claim: dict[str, Any], limit: int = 5) -> list[dict[str, Any]]:
        matrix = self.preprocessor.transform(pd.DataFrame([claim])[self.features])
        try:
            import shap

            if self._explainer is None:
                self._explainer = shap.TreeExplainer(self.model)
            values = self._explainer.shap_values(matrix)
            if isinstance(values, list):
                values = values[-1]
            contributions = values[0]
        except Exception:
            importance_lookup = {item["feature"]: item["importance"] for item in self.global_importance}
            contributions = np.array([importance_lookup.get(name, 0.0) for name in self.feature_names])

        ordered = sorted(
            zip(self.feature_names, contributions),
            key=lambda item: abs(float(item[1])),
            reverse=True,
        )
        factors = []
        for feature, contribution in ordered[:limit]:
            raw_feature = self._raw_feature_name(feature)
            factors.append(
                {
                    "feature": raw_feature,
                    "label": humanize_feature_name(raw_feature),
                    "feature_value": claim.get(raw_feature, self._encoded_value(feature)),
                    "contribution": round(float(contribution), 4),
                    "direction": "increases_risk" if float(contribution) >= 0 else "decreases_risk",
                }
            )
        return factors

    def _raw_feature_name(self, feature: str) -> str:
        for raw in sorted(self.features, key=len, reverse=True):
            if feature == raw or feature.startswith(f"{raw}_"):
                return raw
        return feature

    def _encoded_value(self, feature: str) -> str:
        raw = self._raw_feature_name(feature)
        return feature.replace(f"{raw}_", "") if feature != raw else ""

