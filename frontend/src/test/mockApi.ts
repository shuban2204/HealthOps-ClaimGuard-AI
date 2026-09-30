import type { AnalystBrief, ClaimDetail, ClaimList, EvidenceResponse, ModelMetrics, Summary } from "../types/api";
import { vi } from "vitest";

export const summary: Summary = {
  total_claims: 49199,
  high_risk_claims: 8421,
  medium_risk_claims: 18000,
  low_risk_claims: 22778,
  average_denial_probability: 0.2876,
  anomalous_claims: 1204,
  target_prevalence: 0.2876
};

export const claims: ClaimList = {
  pagination: { total: 2, limit: 25, offset: 0, has_more: false },
  items: [
    {
      claim_id: "CLM-1",
      claim_type: "outpatient",
      provider_network: "out_of_network",
      claim_total_charge: 3400,
      denial_probability: 0.966,
      risk_band: "HIGH",
      anomaly_score: -0.039,
      is_anomaly: true
    },
    {
      claim_id: "CLM-2",
      claim_type: "outpatient",
      provider_network: "in_network",
      claim_total_charge: 120,
      denial_probability: 0.182,
      risk_band: "LOW",
      anomaly_score: 0.2,
      is_anomaly: false
    }
  ]
};

export const detail: ClaimDetail = {
  claim: {
    claim_id: "CLM-1",
    claim_type: "outpatient",
    claim_total_charge: 3400,
    claim_payment_amount: 2300,
    reimbursement_ratio: 0.676,
    claim_duration_days: 2,
    diagnosis_count: 8,
    procedure_count: 13,
    provider_network: "out_of_network",
    prior_auth_required: true,
    prior_auth_present: false,
    documentation_complete: false,
    coding_mismatch_flag: true,
    duplicate_claim_flag: false,
    timely_filing_flag: false
  },
  prediction: {
    denial_probability: 0.966,
    risk_band: "HIGH",
    top_factors: [
      {
        feature: "missing_required_auth",
        label: "Missing required authorization",
        feature_value: true,
        contribution: 1.0677,
        direction: "increases_risk"
      }
    ]
  },
  anomaly: { anomaly_score: -0.039, is_anomaly: true }
};

export const evidence: EvidenceResponse = {
  claim_id: "CLM-1",
  query: "missing required prior authorization",
  sources: [
    {
      source_id: "prior_authorization:PA-03",
      title: "Prior Authorization Policy",
      section: "PA-03 Missing Authorization",
      text: "## PA-03 Missing Authorization\nVerify authorization details before disposition.",
      similarity_score: 0.81
    }
  ]
};

export const brief: AnalystBrief = {
  claim_id: "CLM-1",
  summary: "Claim CLM-1 is prioritized as HIGH risk with a 96.6% estimated denial probability.",
  rationale: ["Missing required authorization raised denial risk in the model explanation."],
  recommended_actions: ["Verify whether a valid authorization exists in the source system or supporting attachments."],
  citations: evidence.sources,
  limitations: ["The brief summarizes model signals and retrieved evidence; it does not approve, deny, or adjudicate the claim."],
  disclaimer: "Decision support only. A qualified human reviewer must verify claim facts, policy context, and final disposition.",
  generated_by: "deterministic-template-v0.1"
};

export const metrics: ModelMetrics = {
  model_version: "hybrid-cms-admin-0.2.0",
  model_name: "xgboost",
  selected_threshold: 0.2729,
  class_prevalence: 0.2876,
  train: metricSplit(0.7614),
  validation: metricSplit(0.7324),
  test: metricSplit(0.725)
};

export const drivers = {
  items: [
    { feature: "missing_required_auth", importance: 0.12 },
    { feature: "documentation_or_coding_issue", importance: 0.08 }
  ]
};

function metricSplit(roc_auc: number) {
  return {
    roc_auc,
    pr_auc: 0.56,
    precision: 0.48,
    recall: 0.63,
    f1: 0.54,
    precision_at_top_10pct: 0.71,
    recall_at_top_10pct: 0.24,
    positive_prevalence: 0.2876,
    confusion_matrix: { tn: 1, fp: 1, fn: 1, tp: 1 }
  };
}

export function installMockFetch() {
  vi.stubGlobal(
    "fetch",
    vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/analytics/summary")) return json(summary);
      if (url.includes("/analytics/drivers")) return json(drivers);
      if (url.includes("/model/metrics")) return json(metrics);
      if (url.includes("/claims/CLM-404")) return new Response("not found", { status: 404 });
      if (url.includes("/claims/CLM-1/brief")) return json(brief);
      if (url.includes("/claims/CLM-1/evidence")) return json(evidence);
      if (url.includes("/claims/CLM-1")) return json(detail);
      if (url.includes("/claims")) return json(claims);
      return new Response("not found", { status: 404 });
    })
  );
}

function json(body: unknown) {
  return new Response(JSON.stringify(body), { status: 200, headers: { "Content-Type": "application/json" } });
}
