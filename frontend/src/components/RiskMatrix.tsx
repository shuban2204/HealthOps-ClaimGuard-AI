import type { ClaimSummary } from "../types/api";
import { formatCurrency, formatPercent } from "../utils/format";

export function RiskMatrix({ claims, onSelect }: { claims: ClaimSummary[]; onSelect: (claimId: string) => void }) {
  const width = 640;
  const height = 300;
  const padding = 34;
  const maxCharge = Math.max(...claims.map((claim) => claim.claim_total_charge), 1);

  function x(probability: number) {
    return padding + probability * (width - padding * 2);
  }

  function y(charge: number) {
    return height - padding - (charge / maxCharge) * (height - padding * 2);
  }

  return (
    <div className="risk-matrix">
      <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Claim risk matrix">
        <line x1={padding} y1={height - padding} x2={width - padding} y2={height - padding} />
        <line x1={padding} y1={padding} x2={padding} y2={height - padding} />
        <text x={width - padding} y={height - 8} textAnchor="end">
          Denial risk
        </text>
        <text x={8} y={padding - 10}>
          Charge
        </text>
        {claims.map((claim) => (
          <circle
            key={claim.claim_id}
            cx={x(claim.denial_probability)}
            cy={y(claim.claim_total_charge)}
            r={claim.is_anomaly ? 5.5 : 4}
            className={`matrix-point ${claim.risk_band.toLowerCase()} ${claim.is_anomaly ? "anomaly" : ""}`}
            tabIndex={0}
            onClick={() => onSelect(claim.claim_id)}
          >
            <title>
              {claim.claim_id} | {formatPercent(claim.denial_probability, 1)} | {formatCurrency(claim.claim_total_charge)} |{" "}
              {claim.is_anomaly ? "Unusual" : "Typical"} | {claim.risk_band}
            </title>
          </circle>
        ))}
      </svg>
    </div>
  );
}

