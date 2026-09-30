from __future__ import annotations


FEATURE_LABELS = {
    "missing_required_auth": "Missing required authorization",
    "documentation_or_coding_issue": "Documentation or coding issue",
    "prior_auth_present": "Prior authorization present",
    "prior_auth_required": "Prior authorization required",
    "member_coverage_active": "Member coverage active",
    "provider_network": "Provider network",
    "provider_network_in_network": "In-network provider",
    "provider_network_out_of_network": "Out-of-network provider",
    "documentation_complete": "Documentation complete",
    "timely_filing_flag": "Timely filing risk",
    "coding_mismatch_flag": "Coding mismatch flag",
    "complex_claim_flag": "Complex claim flag",
    "claim_total_charge": "Claim total charge",
    "claim_amount_vs_global_mean": "Claim amount vs global mean",
    "historical_provider_denial_rate": "Historical provider denial rate",
    "days_since_previous_claim_for_beneficiary": "Days since previous beneficiary claim",
    "duplicate_claim_flag": "Duplicate claim flag",
    "claim_duration_days": "Claim duration days",
    "procedure_count": "Procedure count",
    "provider_risk_interaction": "Provider risk interaction",
}


def humanize_feature_name(feature: str) -> str:
    return FEATURE_LABELS.get(feature, feature.replace("_", " ").title())


def risk_band(probability: float, threshold: float) -> str:
    high_threshold = max(0.65, threshold + 0.35)
    if probability >= high_threshold:
        return "HIGH"
    if probability >= threshold:
        return "MEDIUM"
    return "LOW"

