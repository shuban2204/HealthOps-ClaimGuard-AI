import type { AnalystBrief, ClaimDetail, ClaimFilters, ClaimList, Driver, EvidenceResponse, ModelMetrics, Summary } from "../types/api";

const BASE_URL = "/api/v1";

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`);
  if (!response.ok) {
    const body = await response.text();
    throw new Error(body || `Request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

function toQuery(filters: ClaimFilters): string {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      params.set(key, String(value));
    }
  });
  const query = params.toString();
  return query ? `?${query}` : "";
}

export const api = {
  summary: () => getJson<Summary>("/analytics/summary"),
  drivers: (limit = 12) => getJson<{ items: Driver[] }>(`/analytics/drivers?limit=${limit}`),
  claims: (filters: ClaimFilters = {}) => getJson<ClaimList>(`/claims${toQuery({ limit: 50, offset: 0, ...filters })}`),
  claim: (claimId: string) => getJson<ClaimDetail>(`/claims/${encodeURIComponent(claimId)}`),
  evidence: (claimId: string) => getJson<EvidenceResponse>(`/claims/${encodeURIComponent(claimId)}/evidence`),
  brief: (claimId: string) => getJson<AnalystBrief>(`/claims/${encodeURIComponent(claimId)}/brief`),
  metrics: () => getJson<ModelMetrics>("/model/metrics")
};
