from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier, IsolationForest
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
    precision_recall_curve,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from generate_data import PROCESSED_PATH


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "ml" / "artifacts"
MODEL_PATH = ARTIFACT_DIR / "classifier.joblib"
ANOMALY_PATH = ARTIFACT_DIR / "anomaly_detector.joblib"
METRICS_PATH = ARTIFACT_DIR / "metrics.json"
DIAGNOSTICS_PATH = ARTIFACT_DIR / "data_diagnostics.json"
EXPLAINABILITY_PATH = ARTIFACT_DIR / "explainability_samples.json"
LEAKAGE_AUDIT_PATH = ARTIFACT_DIR / "leakage_audit.json"

OLD_STAGE2_METRICS = {
    "roc_auc": 0.764,
    "pr_auc": 0.5934,
    "f1": 0.5941,
    "precision_at_top_10pct": 0.7014,
}

CATEGORICAL_FEATURES = [
    "claim_type",
    "provider_network",
    "beneficiary_sex",
    "procedure_category",
    "diagnosis_category",
]
BOOLEAN_FEATURES = [
    "prior_auth_required",
    "prior_auth_present",
    "documentation_complete",
    "coding_mismatch_flag",
    "duplicate_claim_flag",
    "member_coverage_active",
    "timely_filing_flag",
    "high_claim_amount_flag",
    "high_provider_frequency_flag",
    "multi_physician_flag",
    "complex_claim_flag",
    "missing_required_auth",
    "late_submission_flag",
    "high_provider_denial_rate_flag",
    "network_and_auth_risk",
    "documentation_or_coding_issue",
    "complex_claim_and_high_amount",
]
NUMERIC_FEATURES = [
    "claim_duration_days",
    "diagnosis_count",
    "procedure_count",
    "claim_payment_amount",
    "claim_total_charge",
    "deductible_amount",
    "reimbursement_ratio",
    "unique_physician_count",
    "unique_diagnosis_count",
    "unique_procedure_count",
    "beneficiary_age",
    "provider_avg_claim_amount",
    "provider_claim_frequency",
    "beneficiary_claim_frequency",
    "claim_amount_vs_provider_mean",
    "claim_amount_vs_global_mean",
    "claim_amount_zscore",
    "days_since_previous_claim_for_beneficiary",
    "historical_provider_denial_rate",
    "billed_to_allowed_ratio",
    "provider_risk_interaction",
]
FEATURES = CATEGORICAL_FEATURES + BOOLEAN_FEATURES + NUMERIC_FEATURES
ANOMALY_FEATURES = [
    "claim_payment_amount",
    "claim_total_charge",
    "reimbursement_ratio",
    "claim_duration_days",
    "diagnosis_count",
    "procedure_count",
    "provider_claim_frequency",
    "claim_amount_vs_provider_mean",
    "beneficiary_claim_frequency",
]


def build_preprocessor() -> ColumnTransformer:
    return ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore", min_frequency=10), CATEGORICAL_FEATURES),
            ("bool", "passthrough", BOOLEAN_FEATURES),
            ("num", StandardScaler(), NUMERIC_FEATURES),
        ]
    )


def build_anomaly_preprocessor() -> ColumnTransformer:
    return ColumnTransformer([("num", StandardScaler(), ANOMALY_FEATURES)])


def prepare_frame(path: Path = PROCESSED_PATH) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found. Run `python ml/generate_data.py --outpatient <cms_outpatient_zip_or_csv>` first."
        )
    frame = pd.read_csv(path)
    missing = [feature for feature in FEATURES + ["denied"] if feature not in frame.columns]
    if missing:
        raise ValueError(f"Processed dataset is missing required fields: {', '.join(missing)}")
    for column in BOOLEAN_FEATURES:
        frame[column] = frame[column].astype(bool)
    for column in NUMERIC_FEATURES:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    frame[NUMERIC_FEATURES] = frame[NUMERIC_FEATURES].fillna(frame[NUMERIC_FEATURES].median(numeric_only=True))
    frame[CATEGORICAL_FEATURES] = frame[CATEGORICAL_FEATURES].fillna("unknown").astype(str)
    return frame


def split_data(frame: pd.DataFrame):
    train_val, test = train_test_split(frame, test_size=0.2, stratify=frame["denied"], random_state=42)
    train, validation = train_test_split(train_val, test_size=0.25, stratify=train_val["denied"], random_state=42)
    return train.copy(), validation.copy(), test.copy()


def select_threshold(y_true: pd.Series, probabilities: np.ndarray) -> float:
    precision, recall, thresholds = precision_recall_curve(y_true, probabilities)
    if len(thresholds) == 0:
        return 0.5
    f1_scores = 2 * precision[:-1] * recall[:-1] / (precision[:-1] + recall[:-1] + 1e-9)
    return float(thresholds[int(np.argmax(f1_scores))])


def metrics_for_split(y_true: pd.Series, probabilities: np.ndarray, threshold: float) -> dict[str, Any]:
    predictions = (probabilities >= threshold).astype(int)
    precision, recall, f1, _ = precision_recall_fscore_support(y_true, predictions, average="binary", zero_division=0)
    top_n = max(1, int(len(y_true) * 0.1))
    top_indexes = np.argsort(probabilities)[-top_n:]
    cm = confusion_matrix(y_true, predictions).ravel()
    return {
        "roc_auc": round(float(roc_auc_score(y_true, probabilities)), 4),
        "pr_auc": round(float(average_precision_score(y_true, probabilities)), 4),
        "precision": round(float(precision), 4),
        "recall": round(float(recall), 4),
        "f1": round(float(f1), 4),
        "precision_at_top_10pct": round(float(np.asarray(y_true)[top_indexes].mean()), 4),
        "recall_at_top_10pct": round(float(np.asarray(y_true)[top_indexes].sum() / max(1, np.asarray(y_true).sum())), 4),
        "positive_prevalence": round(float(pd.Series(y_true).mean()), 4),
        "confusion_matrix": {"tn": int(cm[0]), "fp": int(cm[1]), "fn": int(cm[2]), "tp": int(cm[3])},
    }


def build_primary_model():
    try:
        from xgboost import XGBClassifier

        return (
            "xgboost",
            XGBClassifier(
                n_estimators=260,
                max_depth=4,
                learning_rate=0.045,
                subsample=0.9,
                colsample_bytree=0.9,
                eval_metric="logloss",
                random_state=42,
                n_jobs=2,
            ),
        )
    except Exception:
        return (
            "hist_gradient_boosting",
            HistGradientBoostingClassifier(max_iter=220, learning_rate=0.055, random_state=42),
        )


def train() -> dict[str, Any]:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    frame = prepare_frame()
    train_frame, validation_frame, test_frame = split_data(frame)
    diagnostics = build_diagnostics(frame, train_frame, validation_frame, test_frame)
    DIAGNOSTICS_PATH.write_text(json.dumps(diagnostics, indent=2), encoding="utf-8")

    X_train = train_frame[FEATURES]
    y_train = train_frame["denied"]
    X_validation = validation_frame[FEATURES]
    y_validation = validation_frame["denied"]
    X_test = test_frame[FEATURES]
    y_test = test_frame["denied"]

    preprocessor = build_preprocessor()
    X_train_matrix = preprocessor.fit_transform(X_train)
    X_validation_matrix = preprocessor.transform(X_validation)
    X_test_matrix = preprocessor.transform(X_test)
    feature_names = clean_feature_names(preprocessor.get_feature_names_out())

    baseline = LogisticRegression(max_iter=1200, class_weight="balanced", n_jobs=1)
    baseline.fit(X_train_matrix, y_train)
    baseline_validation_prob = baseline.predict_proba(X_validation_matrix)[:, 1]
    baseline_threshold = select_threshold(y_validation, baseline_validation_prob)

    primary_name, primary_model = build_primary_model()
    primary_model.fit(X_train_matrix, y_train)
    validation_prob = primary_model.predict_proba(X_validation_matrix)[:, 1]
    threshold = select_threshold(y_validation, validation_prob)

    train_prob = primary_model.predict_proba(X_train_matrix)[:, 1]
    test_prob = primary_model.predict_proba(X_test_matrix)[:, 1]

    anomaly_pipeline = Pipeline(
        steps=[
            ("preprocessor", build_anomaly_preprocessor()),
            ("model", IsolationForest(n_estimators=180, contamination=0.045, random_state=42)),
        ]
    )
    anomaly_pipeline.fit(train_frame[ANOMALY_FEATURES])
    frame["anomaly_score"] = anomaly_pipeline.decision_function(frame[ANOMALY_FEATURES]).round(4)
    frame["is_anomaly"] = anomaly_pipeline.predict(frame[ANOMALY_FEATURES]) == -1
    frame.to_csv(PROCESSED_PATH, index=False)

    global_importance = extract_importance(primary_model, feature_names)
    explainability = build_explainability_samples(primary_model, preprocessor, test_frame, test_prob, feature_names)
    EXPLAINABILITY_PATH.write_text(json.dumps(explainability, indent=2), encoding="utf-8")
    leakage_audit = run_leakage_audit()
    LEAKAGE_AUDIT_PATH.write_text(json.dumps(leakage_audit, indent=2), encoding="utf-8")

    metrics = {
        "model_version": "hybrid-cms-admin-0.2.0",
        "data_source": "CMS DE-SynPUF Sample 1 outpatient claims plus synthetic administrative enrichment",
        "row_count": int(len(frame)),
        "features": FEATURES,
        "target": "denied",
        "threshold": round(float(threshold), 4),
        "baseline_logistic_regression": {
            "threshold": round(float(baseline_threshold), 4),
            "validation": metrics_for_split(y_validation, baseline_validation_prob, baseline_threshold),
            "test": metrics_for_split(y_test, baseline.predict_proba(X_test_matrix)[:, 1], baseline_threshold),
        },
        "primary_model": {
            "name": primary_name,
            "train": metrics_for_split(y_train, train_prob, threshold),
            "validation": metrics_for_split(y_validation, validation_prob, threshold),
            "test": metrics_for_split(y_test, test_prob, threshold),
        },
        "old_stage2_metrics": OLD_STAGE2_METRICS,
        "global_importance": global_importance[:25],
        "leakage_audit": leakage_audit,
        "notes": [
            "Validation data selects the decision threshold.",
            "Test data is held out until final evaluation.",
            "denial_reason and denied are excluded from model inputs.",
            "Unusual claim detection is not a fraud detector.",
        ],
    }
    joblib.dump(
        {
            "preprocessor": preprocessor,
            "model": primary_model,
            "threshold": threshold,
            "features": FEATURES,
            "global_importance": global_importance,
        },
        MODEL_PATH,
    )
    joblib.dump(anomaly_pipeline, ANOMALY_PATH)
    METRICS_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return metrics


def clean_feature_names(names: np.ndarray) -> list[str]:
    cleaned = []
    for name in names:
        cleaned.append(
            str(name)
            .replace("cat__", "")
            .replace("bool__", "")
            .replace("num__", "")
            .replace("remainder__", "")
        )
    return cleaned


def extract_importance(model: Any, feature_names: list[str]) -> list[dict[str, Any]]:
    if hasattr(model, "feature_importances_"):
        scores = model.feature_importances_
    elif hasattr(model, "coef_"):
        scores = np.abs(model.coef_[0])
    else:
        scores = np.zeros(len(feature_names))
    importance = [
        {"feature": feature, "importance": round(float(score), 6)}
        for feature, score in zip(feature_names, scores)
    ]
    return sorted(importance, key=lambda item: item["importance"], reverse=True)


def build_explainability_samples(
    model: Any,
    preprocessor: ColumnTransformer,
    test_frame: pd.DataFrame,
    probabilities: np.ndarray,
    feature_names: list[str],
) -> dict[str, Any]:
    sample = test_frame.head(5).copy()
    matrix = preprocessor.transform(sample[FEATURES])
    shap_status = "not_attempted"
    local_rows: list[dict[str, Any]] = []
    shap_summary: list[dict[str, Any]] = []
    try:
        import shap

        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(matrix)
        if isinstance(shap_values, list):
            shap_values = shap_values[-1]
        shap_status = "computed"
        abs_mean = np.abs(shap_values).mean(axis=0)
        shap_summary = sorted(
            [
                {"feature": feature, "mean_abs_shap": round(float(score), 6)}
                for feature, score in zip(feature_names, abs_mean)
            ],
            key=lambda item: item["mean_abs_shap"],
            reverse=True,
        )[:20]
        for row_idx, (_, row) in enumerate(sample.iterrows()):
            local = sorted(
                [
                    {"feature": feature, "shap": round(float(value), 6)}
                    for feature, value in zip(feature_names, shap_values[row_idx])
                ],
                key=lambda item: abs(item["shap"]),
                reverse=True,
            )[:8]
            probability = float(probabilities[row_idx])
            local_rows.append(
                {
                    "claim_id": row["claim_id"],
                    "denial_probability": round(probability, 4),
                    "risk_band": risk_band(probability),
                    "top_local_factors": local,
                }
            )
    except Exception as exc:
        shap_status = f"fallback_no_shap: {type(exc).__name__}: {exc}"
        global_importance = extract_importance(model, feature_names)[:8]
        for row_idx, (_, row) in enumerate(sample.iterrows()):
            probability = float(probabilities[row_idx])
            local_rows.append(
                {
                    "claim_id": row["claim_id"],
                    "denial_probability": round(probability, 4),
                    "risk_band": risk_band(probability),
                    "top_local_factors": global_importance,
                }
            )
    return {"shap_status": shap_status, "shap_summary": shap_summary, "sample_claims": local_rows}


def risk_band(probability: float) -> str:
    if probability >= 0.65:
        return "HIGH"
    if probability >= 0.35:
        return "MEDIUM"
    return "LOW"


def build_diagnostics(
    frame: pd.DataFrame,
    train_frame: pd.DataFrame,
    validation_frame: pd.DataFrame,
    test_frame: pd.DataFrame,
) -> dict[str, Any]:
    buckets = frame.copy()
    buckets["claim_complexity_bucket"] = pd.cut(
        buckets["diagnosis_count"] + buckets["procedure_count"],
        bins=[-1, 3, 8, 100],
        labels=["low", "medium", "high"],
    )
    buckets["claim_amount_bucket"] = pd.qcut(
        buckets["claim_total_charge"].rank(method="first"),
        q=4,
        labels=["q1_low", "q2", "q3", "q4_high"],
    )
    denial_groups = {
        "prior_authorization_status": denial_rate_by(buckets, "missing_required_auth"),
        "network_status": denial_rate_by(buckets, "provider_network"),
        "documentation_status": denial_rate_by(buckets, "documentation_complete"),
        "coding_mismatch": denial_rate_by(buckets, "coding_mismatch_flag"),
        "filing_status": denial_rate_by(buckets, "timely_filing_flag"),
        "claim_complexity_bucket": denial_rate_by(buckets, "claim_complexity_bucket"),
        "claim_amount_bucket": denial_rate_by(buckets, "claim_amount_bucket"),
    }
    return {
        "row_count": int(len(frame)),
        "positive_class_prevalence": round(float(frame["denied"].mean()), 4),
        "missing_value_percentages": {
            column: round(float(percent), 4)
            for column, percent in (frame.isna().mean() * 100).sort_values(ascending=False).head(30).items()
        },
        "numeric_summary": frame[NUMERIC_FEATURES].describe().round(4).to_dict(),
        "categorical_cardinalities": {
            column: int(frame[column].nunique(dropna=True)) for column in CATEGORICAL_FEATURES
        },
        "denial_rate_by": denial_groups,
        "feature_target_association": feature_target_association(frame),
        "split_sizes": {
            "train": int(len(train_frame)),
            "validation": int(len(validation_frame)),
            "test": int(len(test_frame)),
        },
    }


def denial_rate_by(frame: pd.DataFrame, column: str) -> list[dict[str, Any]]:
    grouped = frame.groupby(column, dropna=False, observed=True)["denied"].agg(["count", "mean"]).reset_index()
    return [
        {"value": str(row[column]), "count": int(row["count"]), "denial_rate": round(float(row["mean"]), 4)}
        for _, row in grouped.iterrows()
    ]


def feature_target_association(frame: pd.DataFrame) -> dict[str, Any]:
    associations: dict[str, Any] = {}
    for column in NUMERIC_FEATURES:
        associations[column] = round(float(frame[column].corr(frame["denied"])), 4)
    for column in CATEGORICAL_FEATURES + BOOLEAN_FEATURES:
        rates = frame.groupby(column)["denied"].mean()
        associations[column] = round(float(rates.max() - rates.min()), 4) if len(rates) > 1 else 0.0
    return dict(sorted(associations.items(), key=lambda item: abs(item[1]), reverse=True)[:30])


def run_leakage_audit() -> dict[str, Any]:
    forbidden = {"denied", "denial_reason", "synthetic_denial_probability", "anomaly_score", "is_anomaly"}
    forbidden_used = sorted(forbidden.intersection(FEATURES))
    aggregate_notes = [
        "Provider and beneficiary claim frequency features are generated from prior claims ordered by claim_start_date.",
        "Provider average amount is an expanding prior mean and does not use future rows.",
        "historical_provider_denial_rate is synthetic provider profile risk generated before the denied label.",
        "denial_reason is generated after the target and excluded from model inputs.",
        "Final threshold is selected on validation data, not test data.",
    ]
    return {
        "status": "pass" if not forbidden_used else "fail",
        "forbidden_target_or_post_outcome_features_used": forbidden_used,
        "aggregate_feature_review": aggregate_notes,
        "manual_review_required_before_real_world_use": True,
    }


if __name__ == "__main__":
    print(json.dumps(train(), indent=2))
