import { api } from "./client";
import type { ClaimFilters } from "../types/api";

export const claimsApi = {
  list: (filters: ClaimFilters) => api.claims(filters),
  detail: (claimId: string) => api.claim(claimId),
  evidence: (claimId: string) => api.evidence(claimId)
};

