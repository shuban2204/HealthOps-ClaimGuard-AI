export type RiskBand = "LOW" | "MEDIUM" | "HIGH";
export type SortOrder = "asc" | "desc";

export interface TopFactor {
  feature: string;
  label: string;
  feature_value: string | number | boolean | null;
  contribution: number;
  direction: "increases_risk" | "decreases_risk";
}

export interface ClaimSummary {
  claim_id: string;
  claim_type: string;
  provider_network: string;
  claim_total_charge: number;
  denial_probability: number;
  risk_band: RiskBand;
  anomaly_score: number;
  is_anomaly: boolean;
}

export interface ClaimDetail {
  claim: Record<string, string | number | boolean | null>;
  prediction: {
    denial_probability: number;
    risk_band: RiskBand;
    top_factors: TopFactor[];
  };
  anomaly: {
    anomaly_score: number;
    is_anomaly: boolean;
  };
}

export interface Pagination {
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
}

export interface ClaimList {
  items: ClaimSummary[];
  pagination: Pagination;
}

export interface ClaimFilters {
  limit?: number;
  offset?: number;
  search?: string;
  risk_band?: RiskBand | "";
  is_anomaly?: boolean | "";
  claim_type?: string;
  provider_network?: string;
  sort_by?: "denial_probability" | "claim_total_charge" | "claim_id" | "anomaly_score";
  sort_order?: SortOrder;
}

export interface Summary {
  total_claims: number;
  high_risk_claims: number;
  medium_risk_claims: number;
  low_risk_claims: number;
  average_denial_probability: number;
  anomalous_claims: number;
  target_prevalence: number;
}

export interface EvidenceSource {
  source_id: string;
  title: string;
  section: string;
  text: string;
  similarity_score: number;
}

export interface EvidenceResponse {
  claim_id: string;
  query: string;
  sources: EvidenceSource[];
}

export interface MetricSplit {
  roc_auc: number;
  pr_auc: number;
  precision: number;
  recall: number;
  f1: number;
  precision_at_top_10pct: number;
  recall_at_top_10pct: number;
  positive_prevalence: number;
  confusion_matrix: {
    tn: number;
    fp: number;
    fn: number;
    tp: number;
  };
}

export interface ModelMetrics {
  model_version: string;
  model_name: string;
  selected_threshold: number;
  train: MetricSplit;
  validation: MetricSplit;
  test: MetricSplit;
  class_prevalence: number;
}

export interface Driver {
  feature: string;
  importance: number;
}

