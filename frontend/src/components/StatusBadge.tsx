export function StatusBadge({ label, tone = "neutral" }: { label: string; tone?: "ready" | "neutral" | "anomaly" }) {
  return <span className={`status-badge ${tone}`}>{label}</span>;
}

