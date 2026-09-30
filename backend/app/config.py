from __future__ import annotations

import os
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]


def path_from_env(name: str, default: Path) -> Path:
    value = os.getenv(name)
    if not value:
        return default
    path = Path(value).expanduser()
    return path.resolve() if path.is_absolute() else (ROOT_DIR / path).resolve()


DATA_PATH = path_from_env("CLAIMGUARD_DATA_PATH", ROOT_DIR / "data" / "sample_claims.csv")
POLICY_DIR = path_from_env("CLAIMGUARD_POLICY_DIR", ROOT_DIR / "data" / "policies")
MODEL_PATH = path_from_env("CLAIMGUARD_MODEL_PATH", ROOT_DIR / "ml" / "artifacts" / "classifier.joblib")
ANOMALY_PATH = path_from_env("CLAIMGUARD_ANOMALY_PATH", ROOT_DIR / "ml" / "artifacts" / "anomaly_detector.joblib")
METRICS_PATH = path_from_env("CLAIMGUARD_METRICS_PATH", ROOT_DIR / "ml" / "artifacts" / "metrics.json")
EXPLAINABILITY_PATH = path_from_env("CLAIMGUARD_EXPLAINABILITY_PATH", ROOT_DIR / "ml" / "artifacts" / "explainability_samples.json")
DATABASE_PATH = path_from_env("CLAIMGUARD_DATABASE_PATH", ROOT_DIR / "data" / "claimguard.db")
DATABASE_URL = os.getenv("CLAIMGUARD_DATABASE_URL", f"sqlite:///{DATABASE_PATH.as_posix()}")
MODEL_VERSION = os.getenv("CLAIMGUARD_MODEL_VERSION", "hybrid-cms-admin-0.2.0")
API_PREFIX = os.getenv("CLAIMGUARD_API_PREFIX", "/api/v1")
SENTENCE_TRANSFORMER_MODEL = os.getenv("CLAIMGUARD_SENTENCE_TRANSFORMER_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
