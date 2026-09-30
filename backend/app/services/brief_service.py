from __future__ import annotations

from typing import Any


class BriefService:
    generated_by = "deterministic-template-v0.1"
    disclaimer = "Decision support only. A qualified human reviewer must verify claim facts, policy context, and final disposition."

    def brief_for_claim(self, claim_detail: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
        claim = claim_detail["claim"]
        prediction = claim_detail["prediction"]
        anomaly = claim_detail["anomaly"]
        claim_id = str(claim["claim_id"])
        probability = float(prediction["denial_probability"])
        risk_band = prediction["risk_band"]

        summary = (
            f"Claim {claim_id} is prioritized as {risk_band} risk with a "
            f"{probability:.1%} estimated denial probability."
        )

        return {
            "claim_id": claim_id,
            "summary": summary,
            "rationale": self._rationale(claim_detail),
            "recommended_actions": self._actions(claim, anomaly),
            "citations": evidence["sources"][:3],
            "limitations": [
                "The model was trained on CMS DE-SynPUF synthetic public claims with synthetic administrative enrichment.",
                "Retrieved policies are demonstration documents and must be checked against the payer's current authoritative policy.",
                "The brief summarizes model signals and retrieved evidence; it does not approve, deny, or adjudicate the claim.",
            ],
            "disclaimer": self.disclaimer,
            "generated_by": self.generated_by,
        }

    def _rationale(self, claim_detail: dict[str, Any]) -> list[str]:
        claim = claim_detail["claim"]
        prediction = claim_detail["prediction"]
        anomaly = claim_detail["anomaly"]
        rationale = []

        for factor in prediction.get("top_factors", [])[:3]:
            direction = "raised" if factor["direction"] == "increases_risk" else "reduced"
            rationale.append(f"{factor['label']} {direction} denial risk in the model explanation.")

        if claim.get("provider_network") == "out_of_network":
            rationale.append("Provider network status is out of network, so coverage exceptions should be reviewed.")
        if claim.get("prior_auth_required") and not claim.get("prior_auth_present"):
            rationale.append("Prior authorization appears required but is not present in the claim facts.")
        if not claim.get("documentation_complete", True):
            rationale.append("Documentation is incomplete and may need reviewer follow-up.")
        if claim.get("coding_mismatch_flag"):
            rationale.append("Coding mismatch indicators are present and should be reconciled against medical records.")
        if anomaly.get("is_anomaly"):
            rationale.append("The unusual-claim detector flagged this record for pattern review.")

        return self._dedupe(rationale)[:6]

    def _actions(self, claim: dict[str, Any], anomaly: dict[str, Any]) -> list[str]:
        actions = []
        if claim.get("prior_auth_required") and not claim.get("prior_auth_present"):
            actions.append("Verify whether a valid authorization exists in the source system or supporting attachments.")
        if claim.get("provider_network") == "out_of_network":
            actions.append("Check network status, emergency exception rules, and any documented referral pathway.")
        if claim.get("coding_mismatch_flag"):
            actions.append("Review diagnosis and procedure coding consistency before disposition.")
        if claim.get("duplicate_claim_flag"):
            actions.append("Compare service dates, provider identifiers, and charge lines against possible duplicate claims.")
        if claim.get("timely_filing_flag"):
            actions.append("Validate received date and contractual filing window.")
        if not claim.get("documentation_complete", True):
            actions.append("Request or locate missing documentation before final decision.")
        if anomaly.get("is_anomaly"):
            actions.append("Escalate for analyst review because the claim pattern differs from the reference population.")

        if not actions:
            actions.append("Complete standard claim review and verify all retrieved policy citations before final action.")
        return actions[:6]

    def _dedupe(self, values: list[str]) -> list[str]:
        seen = set()
        unique = []
        for value in values:
            if value in seen:
                continue
            seen.add(value)
            unique.append(value)
        return unique
