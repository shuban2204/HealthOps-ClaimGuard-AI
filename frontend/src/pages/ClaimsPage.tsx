import { ChevronLeft, ChevronRight } from "lucide-react";
import { useMemo, useState } from "react";

import { ClaimsTable } from "../components/ClaimsTable";
import { FilterBar } from "../components/FilterBar";
import { PageHeader } from "../components/PageHeader";
import { EmptyState, ErrorState, Skeleton } from "../components/States";
import { useClaims } from "../hooks/queries";
import type { ClaimFilters } from "../types/api";

const pageSize = 25;

export function ClaimsPage() {
  const [filters, setFilters] = useState<ClaimFilters>(() => {
    const stored = sessionStorage.getItem("claimFilters");
    return stored ? JSON.parse(stored) : { limit: pageSize, offset: 0, sort_by: "denial_probability", sort_order: "desc" };
  });

  const claims = useClaims(filters);
  const pagination = claims.data?.pagination;
  const page = Math.floor(Number(filters.offset ?? 0) / pageSize) + 1;
  const pages = Math.max(1, Math.ceil((pagination?.total ?? 0) / pageSize));

  function updateFilters(next: Partial<ClaimFilters>) {
    setFilters((current) => {
      const updated = { ...current, ...next, limit: pageSize };
      sessionStorage.setItem("claimFilters", JSON.stringify(updated));
      return updated;
    });
  }

  function sortBy(sort_by: NonNullable<ClaimFilters["sort_by"]>) {
    updateFilters({
      sort_by,
      sort_order: filters.sort_by === sort_by && filters.sort_order === "desc" ? "asc" : "desc"
    });
  }

  const empty = useMemo(() => claims.data && claims.data.items.length === 0, [claims.data]);

  return (
    <section className="page">
      <PageHeader title="Priority Review Queue" kicker="Claims" />
      <section className="workbench-panel">
        <FilterBar filters={filters} onChange={updateFilters} />
        {claims.isError && <ErrorState message="Claims could not be loaded." onRetry={() => claims.refetch()} />}
        {claims.isLoading && <Skeleton lines={10} />}
        {empty && <EmptyState message="No claims match the current filters." />}
        {claims.data && claims.data.items.length > 0 && (
          <>
            <ClaimsTable claims={claims.data.items} sortBy={filters.sort_by} sortOrder={filters.sort_order} onSort={sortBy} />
            <div className="pagination">
              <button onClick={() => updateFilters({ offset: Math.max(0, Number(filters.offset ?? 0) - pageSize) })} disabled={page <= 1}>
                <ChevronLeft size={16} /> Previous
              </button>
              <span>
                Page {page} of {pages} · {pagination?.total.toLocaleString()} claims
              </span>
              <button onClick={() => updateFilters({ offset: Number(filters.offset ?? 0) + pageSize })} disabled={!pagination?.has_more}>
                Next <ChevronRight size={16} />
              </button>
            </div>
          </>
        )}
      </section>
    </section>
  );
}

