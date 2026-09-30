from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from data_ingestion import INTERIM_PATH, ROOT


PROCESSED_PATH = ROOT / "data" / "sample_claims.csv"
RANDOM_SEED = 42


def sigmoid(value: np.ndarray) -> np.ndarray:
    return 1 / (1 + np.exp(-value))


def enrich_administrative_fields(frame: pd.DataFrame, seed: int = RANDOM_SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    claims = frame.copy()
    amount_rank = claims["claim_total_charge"].rank(pct=True).fillna(0.5)
    complexity_score = (
        claims["diagnosis_count"].clip(upper=8) / 8
        + claims["procedure_count"].clip(upper=12) / 12
        + claims["claim_duration_days"].clip(upper=7) / 7
    ) / 3

    provider_profile = claims.groupby("provider_id").agg(
        provider_mean_amount=("claim_total_charge", "mean"),
        provider_mean_complexity=("complex_claim_flag", "mean"),
        provider_volume=("claim_id", "count"),
    )
    provider_profile["provider_base_denial_risk"] = np.clip(
        0.05
        + 0.18 * provider_profile["provider_mean_complexity"]
        + 0.08 * (provider_profile["provider_mean_amount"].rank(pct=True))
        + rng.normal(0, 0.025, len(provider_profile)),
        0.02,
        0.42,
    )
    claims = claims.merge(provider_profile[["provider_base_denial_risk"]], on="provider_id", how="left")

    prior_auth_probability = np.clip(0.12 + 0.42 * amount_rank + 0.22 * complexity_score, 0.05, 0.9)
    claims["prior_auth_required"] = rng.random(len(claims)) < prior_auth_probability
    auth_present_probability = np.where(
        claims["prior_auth_required"],
        np.clip(0.86 - 0.22 * complexity_score - 0.1 * claims["provider_base_denial_risk"], 0.55, 0.94),
        0.98,
    )
    claims["prior_auth_present"] = rng.random(len(claims)) < auth_present_probability

    documentation_probability = np.clip(0.94 - 0.22 * complexity_score - 0.05 * amount_rank, 0.66, 0.98)
    claims["documentation_complete"] = rng.random(len(claims)) < documentation_probability
    out_of_network_probability = np.clip(0.08 + 0.18 * claims["provider_base_denial_risk"] + 0.04 * amount_rank, 0.04, 0.28)
    claims["provider_network"] = np.where(rng.random(len(claims)) < out_of_network_probability, "out_of_network", "in_network")
    inactive_probability = np.clip(0.025 + 0.05 * (claims["beneficiary_claim_frequency"] == 0), 0.02, 0.08)
    claims["member_coverage_active"] = rng.random(len(claims)) >= inactive_probability

    claims["timely_filing_flag"] = claims["days_since_previous_claim_for_beneficiary"].fillna(999) > 180
    claims["coding_mismatch_flag"] = rng.random(len(claims)) < np.clip(
        0.025 + 0.13 * complexity_score + 0.05 * claims["claim_amount_zscore"].clip(lower=0), 0.02, 0.35
    )
    duplicate_score = (
        claims.duplicated(["beneficiary_id", "provider_id", "primary_procedure", "claim_start_date"], keep=False).astype(float)
    )
    claims["duplicate_claim_flag"] = rng.random(len(claims)) < np.clip(0.012 + 0.35 * duplicate_score, 0.01, 0.55)
    claims["historical_provider_denial_rate"] = np.clip(
        claims["provider_base_denial_risk"] + rng.normal(0, 0.015, len(claims)), 0.01, 0.5
    ).round(3)

    missing_required_auth = claims["prior_auth_required"] & ~claims["prior_auth_present"]
    unusual_amount = claims["claim_amount_zscore"].clip(lower=0)
    logit = np.full(len(claims), -2.35)
    logit += np.where(missing_required_auth, 1.85, 0)
    logit += np.where(~claims["documentation_complete"], 1.1, 0)
    logit += np.where(claims["provider_network"] == "out_of_network", 0.85, 0)
    logit += np.where(claims["coding_mismatch_flag"], 1.25, 0)
    logit += np.where(~claims["member_coverage_active"], 1.65, 0)
    logit += np.where(claims["duplicate_claim_flag"], 0.9, 0)
    logit += np.where(claims["timely_filing_flag"], 0.45, 0)
    logit += 2.1 * claims["historical_provider_denial_rate"]
    logit += 0.6 * complexity_score
    logit += 0.22 * unusual_amount
    logit += rng.normal(0, 0.55, len(claims))

    claims["synthetic_denial_probability"] = sigmoid(logit)
    claims["denied"] = rng.binomial(1, claims["synthetic_denial_probability"])
    claims["denial_reason"] = np.select(
        [
            missing_required_auth,
            ~claims["documentation_complete"],
            claims["provider_network"] == "out_of_network",
            claims["coding_mismatch_flag"],
            ~claims["member_coverage_active"],
            claims["duplicate_claim_flag"],
            claims["timely_filing_flag"],
        ],
        [
            "missing_prior_authorization",
            "incomplete_documentation",
            "network_coverage",
            "coding_mismatch",
            "coverage_inactive",
            "duplicate_claim",
            "timely_filing",
        ],
        default="administrative_risk",
    )
    claims["denial_reason"] = np.where(claims["denied"] == 1, claims["denial_reason"], "")

    claims["member_age"] = claims["beneficiary_age"]
    claims["payer"] = "Medicare"
    claims["procedure_category"] = claims["primary_procedure"].astype(str).str[:3].replace("", "unknown")
    claims["diagnosis_category"] = claims["primary_diagnosis"].astype(str).str[:3].replace("", "unknown")
    claims["billed_amount"] = claims["claim_total_charge"].round(2)
    claims["allowed_amount_estimate"] = claims["claim_payment_amount"].round(2)
    claims["days_from_service_to_submission"] = np.clip(
        7 + claims["claim_duration_days"] + claims["provider_claim_frequency"].mod(45), 1, 180
    ).astype(int)
    return add_model_interactions(claims)


def add_model_interactions(claims: pd.DataFrame) -> pd.DataFrame:
    output = claims.copy()
    output["missing_required_auth"] = output["prior_auth_required"] & ~output["prior_auth_present"]
    output["billed_to_allowed_ratio"] = output["claim_total_charge"] / output["claim_payment_amount"].clip(lower=1.0)
    output["late_submission_flag"] = output["days_from_service_to_submission"] > 45
    output["high_provider_denial_rate_flag"] = output["historical_provider_denial_rate"] >= 0.2
    output["network_and_auth_risk"] = (output["provider_network"] == "out_of_network") & output["missing_required_auth"]
    output["documentation_or_coding_issue"] = (~output["documentation_complete"]) | output["coding_mismatch_flag"]
    output["complex_claim_and_high_amount"] = output["complex_claim_flag"] & output["high_claim_amount_flag"]
    output["provider_risk_interaction"] = output["historical_provider_denial_rate"] * output["claim_amount_vs_provider_mean"]
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Add synthetic administrative workflow fields to normalized CMS claims.")
    parser.add_argument("--input", type=Path, default=INTERIM_PATH)
    parser.add_argument("--output", type=Path, default=PROCESSED_PATH)
    parser.add_argument("--seed", type=int, default=RANDOM_SEED)
    args = parser.parse_args()

    normalized = pd.read_csv(args.input, parse_dates=["claim_start_date", "claim_end_date"])
    enriched = enrich_administrative_fields(normalized, args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    enriched.to_csv(args.output, index=False)
    print(f"Wrote {len(enriched):,} enriched claims to {args.output}")


if __name__ == "__main__":
    main()

