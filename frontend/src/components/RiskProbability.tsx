import type { RiskBand } from "../types/api";
import { formatPercent } from "../utils/format";
import { RiskBadge } from "./RiskBadge";

export function RiskProbability({ probability, band }: { probability: number; band: RiskBand }) {
  return (
    <div className="risk-probability">
      <span className={`risk-dot ${band.toLowerCase()}`} />
      <strong>{formatPercent(probability, 1)}</strong>
      <RiskBadge band={band} />
    </div>
  );
}

