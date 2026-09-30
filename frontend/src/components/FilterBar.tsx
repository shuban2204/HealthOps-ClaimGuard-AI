import { RotateCcw, Search, SlidersHorizontal } from "lucide-react";

import type { ClaimFilters, RiskBand } from "../types/api";

export function FilterBar({ filters, onChange }: { filters: ClaimFilters; onChange: (next: Partial<ClaimFilters>) => void }) {
  return (
    <div className="filter-bar">
      <label className="search-control">
        <Search size={16} />
        <input value={filters.search ?? ""} onChange={(event) => onChange({ search: event.target.value, offset: 0 })} placeholder="Search claim ID" />
      </label>
      <label>
        <SlidersHorizontal size={15} />
        <select aria-label="Risk" value={filters.risk_band ?? ""} onChange={(event) => onChange({ risk_band: event.target.value as RiskBand | "", offset: 0 })}>
          <option value="">All risk</option>
          <option value="HIGH">High</option>
          <option value="MEDIUM">Medium</option>
          <option value="LOW">Low</option>
        </select>
      </label>
      <label>
        <span>Network</span>
        <select aria-label="Network" value={filters.provider_network ?? ""} onChange={(event) => onChange({ provider_network: event.target.value, offset: 0 })}>
          <option value="">All</option>
          <option value="in_network">In network</option>
          <option value="out_of_network">Out of network</option>
        </select>
      </label>
      <label>
        <span>Claim Type</span>
        <select aria-label="Claim Type" value={filters.claim_type ?? ""} onChange={(event) => onChange({ claim_type: event.target.value, offset: 0 })}>
          <option value="">All</option>
          <option value="outpatient">Outpatient</option>
        </select>
      </label>
      <label>
        <span>Unusual</span>
        <select
          aria-label="Unusual"
          value={filters.is_anomaly === "" || filters.is_anomaly === undefined ? "" : String(filters.is_anomaly)}
          onChange={(event) => onChange({ is_anomaly: event.target.value === "" ? "" : event.target.value === "true", offset: 0 })}
        >
          <option value="">All</option>
          <option value="true">Yes</option>
          <option value="false">No</option>
        </select>
      </label>
      <button className="quiet-button" onClick={() => onChange({ search: "", risk_band: "", provider_network: "", claim_type: "", is_anomaly: "", offset: 0 })}>
        <RotateCcw size={15} />
        Clear
      </button>
    </div>
  );
}
