import { useMutation, useQuery } from "@tanstack/react-query";

import { analyticsApi } from "../api/analytics";
import { claimsApi } from "../api/claims";
import { modelApi } from "../api/model";
import type { ClaimFilters } from "../types/api";

export function useSummary() {
  return useQuery({ queryKey: ["summary"], queryFn: analyticsApi.summary });
}

export function useDrivers(limit = 12) {
  return useQuery({ queryKey: ["drivers", limit], queryFn: () => analyticsApi.drivers(limit) });
}

export function useClaims(filters: ClaimFilters) {
  return useQuery({ queryKey: ["claims", filters], queryFn: () => claimsApi.list(filters), placeholderData: (previous) => previous });
}

export function useClaimDetail(claimId?: string) {
  return useQuery({
    queryKey: ["claim", claimId],
    queryFn: () => claimsApi.detail(claimId ?? ""),
    enabled: Boolean(claimId)
  });
}

export function useEvidence(claimId?: string) {
  return useQuery({
    queryKey: ["evidence", claimId],
    queryFn: () => claimsApi.evidence(claimId ?? ""),
    enabled: Boolean(claimId)
  });
}

export function useAnalystBrief(claimId?: string) {
  return useMutation({
    mutationKey: ["brief", claimId],
    mutationFn: () => claimsApi.brief(claimId ?? "")
  });
}

export function useModelMetrics() {
  return useQuery({ queryKey: ["model-metrics"], queryFn: modelApi.metrics });
}
