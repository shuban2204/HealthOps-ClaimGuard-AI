import { useNavigate } from "react-router-dom";

import type { ClaimSummary } from "../types/api";
import { formatCurrency, formatPercent } from "../utils/format";
import { RiskBadge } from "./RiskBadge";

export function PriorityQueue({ claims }: { claims: ClaimSummary[] }) {
  const navigate = useNavigate();
  return (
    <div className="priority-queue">
      <div className="queue-header">
        <span>Claim</span>
        <span>Risk</span>
        <span>Primary Signal</span>
        <span>Charge</span>
        <span>Network</span>
        <span>Anomaly</span>
      </div>
      {claims.slice(0, 8).map((claim) => (
        <button key={claim.claim_id} className="queue-row" onClick={() => navigate(`/claims/${encodeURIComponent(claim.claim_id)}`)}>
          <strong>{claim.claim_id}</strong>
          <span>
            {formatPercent(claim.denial_probability, 1)} <RiskBadge band={claim.risk_band} />
          </span>
          <span>{claim.is_anomaly ? "Unusual claim signal" : claim.provider_network.replace("_", " ")}</span>
          <span>{formatCurrency(claim.claim_total_charge)}</span>
          <span>{claim.provider_network.replace("_", " ")}</span>
          <span>{claim.is_anomaly ? "Detected" : "No"}</span>
        </button>
      ))}
    </div>
  );
}

