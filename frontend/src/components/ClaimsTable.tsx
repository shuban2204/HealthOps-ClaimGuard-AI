import { flexRender, getCoreRowModel, useReactTable, type ColumnDef } from "@tanstack/react-table";
import { ArrowDown, ArrowUp } from "lucide-react";
import { useMemo } from "react";
import { useNavigate } from "react-router-dom";

import type { ClaimFilters, ClaimSummary } from "../types/api";
import { formatCurrency, formatPercent } from "../utils/format";
import { RiskProbability } from "./RiskProbability";

export function ClaimsTable({
  claims,
  sortBy,
  sortOrder,
  onSort
}: {
  claims: ClaimSummary[];
  sortBy: ClaimFilters["sort_by"];
  sortOrder: ClaimFilters["sort_order"];
  onSort: (sortBy: NonNullable<ClaimFilters["sort_by"]>) => void;
}) {
  const navigate = useNavigate();
  const columns = useMemo<ColumnDef<ClaimSummary>[]>(
    () => [
      { accessorKey: "claim_id", header: "Claim" },
      {
        accessorKey: "risk_band",
        header: "Risk",
        cell: ({ row }) => <RiskProbability probability={row.original.denial_probability} band={row.original.risk_band} />
      },
      {
        id: "primary_signal",
        header: "Primary Signal",
        cell: ({ row }) => (row.original.is_anomaly ? "Unusual claim signal" : row.original.provider_network.replace("_", " "))
      },
      {
        accessorKey: "claim_total_charge",
        header: "Total Charge",
        cell: ({ row }) => formatCurrency(row.original.claim_total_charge)
      },
      { accessorKey: "claim_type", header: "Claim Type" },
      {
        accessorKey: "provider_network",
        header: "Network",
        cell: ({ row }) => row.original.provider_network.replace("_", " ")
      },
      {
        accessorKey: "is_anomaly",
        header: "Unusual",
        cell: ({ row }) => (row.original.is_anomaly ? <span className="anomaly-chip">Detected</span> : "No")
      }
    ],
    []
  );
  const table = useReactTable({ data: claims, columns, getCoreRowModel: getCoreRowModel() });
  const sortableHeaders: Record<string, NonNullable<ClaimFilters["sort_by"]>> = {
    Claim: "claim_id",
    Risk: "denial_probability",
    "Total Charge": "claim_total_charge",
    Unusual: "anomaly_score"
  };

  return (
    <div className="table-wrap">
      <table className="claims-table">
        <thead>
          {table.getHeaderGroups().map((group) => (
            <tr key={group.id}>
              {group.headers.map((header) => {
                const label = String(header.column.columnDef.header);
                const sortKey = sortableHeaders[label];
                return (
                  <th key={header.id}>
                    {sortKey ? (
                      <button className="table-sort" onClick={() => onSort(sortKey)}>
                        {flexRender(header.column.columnDef.header, header.getContext())}
                        {sortBy === sortKey && (sortOrder === "asc" ? <ArrowUp size={13} /> : <ArrowDown size={13} />)}
                      </button>
                    ) : (
                      flexRender(header.column.columnDef.header, header.getContext())
                    )}
                  </th>
                );
              })}
            </tr>
          ))}
        </thead>
        <tbody>
          {table.getRowModel().rows.map((row) => (
            <tr key={row.id} onClick={() => navigate(`/claims/${encodeURIComponent(row.original.claim_id)}`)} tabIndex={0}>
              {row.getVisibleCells().map((cell) => (
                <td key={cell.id}>{flexRender(cell.column.columnDef.cell, cell.getContext())}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      {claims.length === 0 && <div className="empty-row">No claims match the current filters.</div>}
    </div>
  );
}

