from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "sample_claims.csv"
RANDOM_SEED = 42


def sigmoid(value: np.ndarray) -> np.ndarray:
    return 1 / (1 + np.exp(-value))


def generate_claims(rows: int = 6000, seed: int = RANDOM_SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    claim_types = np.array(["inpatient", "outpatient", "professional", "pharmacy"])
    procedures = np.array(["imaging", "surgery", "lab", "therapy", "evaluation", "pharmacy"])
    diagnoses = np.array(["cardiology", "orthopedics", "oncology", "respiratory", "general"])
    payers = np.array(["Aetna", "BlueCross", "Cigna", "Humana", "United"])

    claim_type = rng.choice(claim_types, rows, p=[0.16, 0.42, 0.3, 0.12])
    procedure_category = rng.choice(procedures, rows, p=[0.18, 0.1, 0.2, 0.15, 0.25, 0.12])
    diagnosis_category = rng.choice(diagnoses, rows)
    provider_network = rng.choice(["in_network", "out_of_network"], rows, p=[0.82, 0.18])
    payer = rng.choice(payers, rows)

    prior_auth_required = np.isin(procedure_category, ["imaging", "surgery", "therapy"]) | (
        claim_type == "inpatient"
    )
    prior_auth_required = prior_auth_required | (rng.random(rows) < 0.08)
    prior_auth_present = np.where(prior_auth_required, rng.random(rows) < 0.74, rng.random(rows) < 0.96)
    documentation_complete = rng.random(rows) < 0.86
    duplicate_claim_flag = rng.random(rows) < 0.035
    coding_mismatch_flag = rng.random(rows) < 0.08
    member_coverage_active = rng.random(rows) < 0.94
    member_age = rng.integers(18, 90, rows)
    days_to_submit = np.clip(rng.gamma(shape=2.2, scale=13, size=rows).astype(int), 0, 160)
    historical_provider_denial_rate = np.clip(rng.beta(2.2, 12, rows), 0.01, 0.65)

    base_amount = {
        "imaging": 1250,
        "surgery": 8500,
        "lab": 220,
        "therapy": 450,
        "evaluation": 310,
        "pharmacy": 180,
    }
    billed_amount = np.array([base_amount[p] for p in procedure_category], dtype=float)
    billed_amount *= rng.lognormal(mean=0.08, sigma=0.45, size=rows)
    billed_amount *= np.where(provider_network == "out_of_network", 1.35, 1.0)
    allowed_amount = billed_amount * rng.uniform(0.52, 0.86, rows)

    logit = np.full(rows, -2.55)
    logit += np.where(prior_auth_required & ~prior_auth_present, 2.2, 0)
    logit += np.where(~documentation_complete, 1.35, 0)
    logit += np.where(provider_network == "out_of_network", 1.1, 0)
    logit += np.where(coding_mismatch_flag, 1.65, 0)
    logit += np.where(~member_coverage_active, 2.0, 0)
    logit += np.where(duplicate_claim_flag, 1.25, 0)
    logit += 0.018 * np.maximum(days_to_submit - 45, 0)
    logit += 2.6 * historical_provider_denial_rate
    logit += rng.normal(0, 0.38, rows)

    denial_probability = sigmoid(logit)
    denied = rng.binomial(1, denial_probability)
    denial_reason = np.full(rows, "", dtype=object)
    denial_reason = np.where(prior_auth_required & ~prior_auth_present, "missing_prior_authorization", denial_reason)
    denial_reason = np.where(~documentation_complete, "incomplete_documentation", denial_reason)
    denial_reason = np.where(provider_network == "out_of_network", "network_coverage", denial_reason)
    denial_reason = np.where(coding_mismatch_flag, "coding_mismatch", denial_reason)
    denial_reason = np.where(~member_coverage_active, "coverage_inactive", denial_reason)
    denial_reason = np.where(duplicate_claim_flag, "duplicate_claim", denial_reason)
    denial_reason = np.where((days_to_submit > 95) & (denial_reason == ""), "timely_filing", denial_reason)
    denial_reason = np.where(denied == 1, denial_reason, "")

    return pd.DataFrame(
        {
            "claim_id": [f"CLM{i:06d}" for i in range(1, rows + 1)],
            "member_age": member_age,
            "payer": payer,
            "claim_type": claim_type,
            "procedure_category": procedure_category,
            "diagnosis_category": diagnosis_category,
            "provider_network": provider_network,
            "prior_auth_required": prior_auth_required,
            "prior_auth_present": prior_auth_present,
            "documentation_complete": documentation_complete,
            "days_from_service_to_submission": days_to_submit,
            "billed_amount": billed_amount.round(2),
            "allowed_amount_estimate": allowed_amount.round(2),
            "historical_provider_denial_rate": historical_provider_denial_rate.round(3),
            "duplicate_claim_flag": duplicate_claim_flag,
            "coding_mismatch_flag": coding_mismatch_flag,
            "member_coverage_active": member_coverage_active,
            "denial_reason": denial_reason,
            "denied": denied,
        }
    )


def main() -> None:
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    generate_claims().to_csv(DATA_PATH, index=False)
    print(f"Wrote {DATA_PATH}")


if __name__ == "__main__":
    main()

