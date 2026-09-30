from __future__ import annotations

from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT_DIR / "data" / "sample_claims.csv"
POLICY_DIR = ROOT_DIR / "data" / "policies"
MODEL_PATH = ROOT_DIR / "ml" / "artifacts" / "classifier.joblib"
ANOMALY_PATH = ROOT_DIR / "ml" / "artifacts" / "anomaly_detector.joblib"
METRICS_PATH = ROOT_DIR / "ml" / "artifacts" / "metrics.json"
EXPLAINABILITY_PATH = ROOT_DIR / "ml" / "artifacts" / "explainability_samples.json"
DATABASE_PATH = ROOT_DIR / "data" / "claimguard.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"
MODEL_VERSION = "hybrid-cms-admin-0.2.0"
API_PREFIX = "/api/v1"
SENTENCE_TRANSFORMER_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
