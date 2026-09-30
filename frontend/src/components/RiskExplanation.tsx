import type { ClaimDetail } from "../types/api";
import { signalForFeature, type SignalKey } from "../utils/signalMap";

export function RiskExplanation({
  detail,
  activeSignal,
  onSignal
}: {
  detail: ClaimDetail;
  activeSignal: SignalKey | null;
  onSignal: (signal: SignalKey | null) => void;
}) {
  const maxContribution = Math.max(...detail.prediction.top_factors.map((factor) => Math.abs(factor.contribution)), 0.001);
  return (
    <section className="investigation-panel explanation-panel">
      <h2>Why This Claim Was Flagged</h2>
      <p>Explanation generated from local SHAP contributions.</p>
      <div className="factor-stack">
        {detail.prediction.top_factors.map((factor) => {
          const signal = signalForFeature(factor.feature, factor.label);
          const width = `${(Math.abs(factor.contribution) / maxContribution) * 50}%`;
          return (
            <button
              key={`${factor.feature}-${factor.contribution}`}
              className={`explanation-factor ${activeSignal === signal ? "active" : ""}`}
              onClick={() => onSignal(activeSignal === signal ? null : signal)}
            >
              <span>{factor.label}</span>
              <div className="diverging-bar">
                <i className={factor.direction === "increases_risk" ? "right" : "left"} style={{ width }} />
              </div>
              <strong>{factor.contribution.toFixed(4)}</strong>
            </button>
          );
        })}
      </div>
    </section>
  );
}

