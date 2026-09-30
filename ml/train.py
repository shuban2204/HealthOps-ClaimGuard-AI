from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier, IsolationForest, RandomForestClassifier
from sklearn.metrics import average_precision_score, confusion_matrix, f1_score, precision_recall_curve, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from generate_data import DATA_PATH, generate_claims


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "ml" / "artifacts"
MODEL_PATH = ARTIFACT_DIR / "classifier.joblib"
ANOMALY_PATH = ARTIFACT_DIR / "anomaly_detector.joblib"
METRICS_PATH = ARTIFACT_DIR / "metrics.json"

CATEGORICAL_FEATURES = [
    "payer",
    "claim_type",
    "procedure_category",
    "diagnosis_category",
    "provider_network",
]
BOOLEAN_FEATURES = [
    "prior_auth_required",
    "prior_auth_present",
    "documentation_complete",
    "duplicate_claim_flag",
    "coding_mismatch_flag",
    "member_coverage_active",
]
NUMERIC_FEATURES = [
    "member_age",
    "days_from_service_to_submission",
    "billed_amount",
    "allowed_amount_estimate",
    "historical_provider_denial_rate",
]
FEATURES = CATEGORICAL_FEATURES + BOOLEAN_FEATURES + NUMERIC_FEATURES


def build_preprocessor() -> ColumnTransformer:
    return ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
            ("bool", "passthrough", BOOLEAN_FEATURES),
            ("num", StandardScaler(), NUMERIC_FEATURES),
        ]
    )


def select_threshold(y_true, probabilities) -> float:
    precision, recall, thresholds = precision_recall_curve(y_true, probabilities)
    f1_scores = 2 * precision * recall / (precision + recall + 1e-9)
    if len(thresholds) == 0:
        return 0.5
    best_index = int(f1_scores[:-1].argmax())
    return float(thresholds[best_index])


def train() -> dict:
    if not DATA_PATH.exists():
        DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
        generate_claims().to_csv(DATA_PATH, index=False)

    df = pd.read_csv(DATA_PATH)
    X = df[FEATURES]
    y = df["denied"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, test_size=0.24, random_state=42)

    classifier = Pipeline(
        steps=[
            ("preprocessor", build_preprocessor()),
            ("model", HistGradientBoostingClassifier(max_iter=180, learning_rate=0.055, random_state=42)),
        ]
    )
    classifier.fit(X_train, y_train)
    probabilities = classifier.predict_proba(X_test)[:, 1]
    threshold = select_threshold(y_test, probabilities)
    predictions = (probabilities >= threshold).astype(int)
    cm = confusion_matrix(y_test, predictions).ravel()

    explanation_model = Pipeline(
        steps=[
            ("preprocessor", build_preprocessor()),
            ("model", RandomForestClassifier(n_estimators=180, min_samples_leaf=8, random_state=42, n_jobs=-1)),
        ]
    )
    explanation_model.fit(X_train, y_train)
    importances = explanation_model.named_steps["model"].feature_importances_
    feature_names = explanation_model.named_steps["preprocessor"].get_feature_names_out()
    global_importance = sorted(
        [
            {"feature": name.replace("cat__", "").replace("bool__", "").replace("num__", ""), "importance": float(score)}
            for name, score in zip(feature_names, importances)
        ],
        key=lambda item: item["importance"],
        reverse=True,
    )[:20]

    anomaly = Pipeline(
        steps=[
            ("preprocessor", build_preprocessor()),
            ("model", IsolationForest(n_estimators=160, contamination=0.045, random_state=42)),
        ]
    )
    anomaly.fit(X)

    metrics = {
        "model_version": "local-0.1.0",
        "roc_auc": round(float(roc_auc_score(y_test, probabilities)), 4),
        "pr_auc": round(float(average_precision_score(y_test, probabilities)), 4),
        "f1": round(float(f1_score(y_test, predictions)), 4),
        "threshold": round(threshold, 4),
        "confusion_matrix": {"tn": int(cm[0]), "fp": int(cm[1]), "fn": int(cm[2]), "tp": int(cm[3])},
        "precision_at_top_10pct": round(float(y_test.iloc[probabilities.argsort()[-max(1, len(y_test) // 10) :]].mean()), 4),
        "global_importance": global_importance,
        "features": FEATURES,
    }

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump({"pipeline": classifier, "threshold": threshold, "features": FEATURES, "global_importance": global_importance}, MODEL_PATH)
    joblib.dump(anomaly, ANOMALY_PATH)
    METRICS_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return metrics


if __name__ == "__main__":
    print(json.dumps(train(), indent=2))

