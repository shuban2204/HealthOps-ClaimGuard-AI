import type { RiskBand } from "../types/api";

export function RiskBadge({ band }: { band: RiskBand }) {
  return <span className={`risk-badge ${band.toLowerCase()}`}>{band}</span>;
}

