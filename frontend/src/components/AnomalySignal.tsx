import type { ClaimDetail } from "../types/api";

export function AnomalySignal({ detail }: { detail: ClaimDetail }) {
  return (
    <section className={`anomaly-panel ${detail.anomaly.is_anomaly ? "detected" : ""}`}>
      <span>Unusual Claim Signal</span>
      <strong>{detail.anomaly.is_anomaly ? "Detected" : "Not detected"}</strong>
      <p>Score {detail.anomaly.anomaly_score.toFixed(4)}</p>
      <small>This claim differs from typical claims based on the anomaly-detection model.</small>
    </section>
  );
}

