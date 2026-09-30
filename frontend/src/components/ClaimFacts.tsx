import type { ClaimDetail } from "../types/api";
import { formatCurrency, formatPercent, humanizeFeature } from "../utils/format";
import { factMatchesSignal, type SignalKey } from "../utils/signalMap";

const fields = [
  "claim_total_charge",
  "claim_payment_amount",
  "reimbursement_ratio",
  "claim_duration_days",
  "diagnosis_count",
  "procedure_count",
  "provider_network",
  "prior_auth_required",
  "prior_auth_present",
  "documentation_complete",
  "coding_mismatch_flag",
  "duplicate_claim_flag",
  "timely_filing_flag"
];

export function ClaimFacts({ detail, activeSignal }: { detail: ClaimDetail; activeSignal: SignalKey | null }) {
  return (
    <section className="investigation-panel facts-panel">
      <h2>Claim Facts</h2>
      <div className="facts-grid">
        {fields.map((field) => (
          <div className={`fact ${factMatchesSignal(field, activeSignal) ? "highlight" : ""}`} key={field}>
            <span>{humanizeFeature(field)}</span>
            <strong>{formatValue(field, detail.claim[field])}</strong>
          </div>
        ))}
      </div>
    </section>
  );
}

function formatValue(field: string, value: string | number | boolean | null) {
  if (typeof value === "boolean") return value ? "Yes" : "No";
  if (value === null || value === undefined || value === "") return "n/a";
  if (field.includes("amount") || field.includes("charge")) return formatCurrency(Number(value));
  if (field.includes("ratio")) return formatPercent(Number(value), 1);
  return String(value).replace("_", " ");
}

