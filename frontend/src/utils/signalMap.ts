export type SignalKey = "auth" | "network" | "documentation" | "coding" | "filing" | "duplicate" | "amount";

export function signalForFeature(feature: string, label = ""): SignalKey | null {
  const text = `${feature} ${label}`.toLowerCase();
  if (text.includes("auth")) return "auth";
  if (text.includes("network")) return "network";
  if (text.includes("documentation")) return "documentation";
  if (text.includes("coding")) return "coding";
  if (text.includes("filing")) return "filing";
  if (text.includes("duplicate")) return "duplicate";
  if (text.includes("amount") || text.includes("charge")) return "amount";
  return null;
}

export function evidenceMatchesSignal(sourceId: string, signal: SignalKey | null) {
  if (!signal) return false;
  const source = sourceId.toLowerCase();
  return (
    (signal === "auth" && source.includes("prior_authorization")) ||
    (signal === "network" && source.includes("network_coverage")) ||
    (signal === "documentation" && source.includes("claim_documentation")) ||
    (signal === "coding" && source.includes("coding_guidelines")) ||
    (signal === "filing" && source.includes("timely_filing")) ||
    (signal === "duplicate" && source.includes("duplicate_claims"))
  );
}

export function factMatchesSignal(field: string, signal: SignalKey | null) {
  if (!signal) return false;
  const name = field.toLowerCase();
  return (
    (signal === "auth" && name.includes("auth")) ||
    (signal === "network" && name.includes("network")) ||
    (signal === "documentation" && name.includes("documentation")) ||
    (signal === "coding" && name.includes("coding")) ||
    (signal === "filing" && name.includes("filing")) ||
    (signal === "duplicate" && name.includes("duplicate")) ||
    (signal === "amount" && (name.includes("amount") || name.includes("charge")))
  );
}

