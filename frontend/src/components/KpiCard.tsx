import type { LucideIcon } from "lucide-react";

interface Props {
  icon: LucideIcon;
  label: string;
  value: string;
  tone?: "neutral" | "risk" | "accent";
  detail?: string;
}

export function KpiCard({ icon: Icon, label, value, tone = "neutral", detail }: Props) {
  return (
    <section className={`metric-card ${tone}`}>
      <Icon size={20} aria-hidden="true" />
      <span>{label}</span>
      <strong>{value}</strong>
      {detail && <small>{detail}</small>}
    </section>
  );
}

