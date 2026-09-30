import { AlertTriangle, FileSearch, FileText, Gauge } from "lucide-react";
import { useNavigate } from "react-router-dom";

import { KpiCard } from "../components/KpiCard";
import { PageHeader } from "../components/PageHeader";
import { PriorityQueue } from "../components/PriorityQueue";
import { RiskMatrix } from "../components/RiskMatrix";
import { RiskSignalBars } from "../components/RiskSignalBars";
import { ErrorState, Skeleton } from "../components/States";
import { useClaims, useDrivers, useSummary } from "../hooks/queries";
import { formatPercent } from "../utils/format";

export function DashboardPage() {
  const navigate = useNavigate();
  const summary = useSummary();
  const drivers = useDrivers(10);
  const queue = useClaims({ limit: 10, sort_by: "denial_probability", sort_order: "desc" });
  const matrix = useClaims({ limit: 180, sort_by: "denial_probability", sort_order: "desc" });

  return (
    <section className="page">
      <PageHeader title="Claim Operations" kicker="Overview" />

      {summary.isError && <ErrorState message="Claims summary could not be loaded." onRetry={() => summary.refetch()} />}
      {summary.isLoading && <Skeleton lines={4} />}

      {summary.data && (
        <div className="summary-strip">
          <KpiCard icon={FileText} label="Claims" value={summary.data.total_claims.toLocaleString()} detail="CMS hybrid portfolio" />
          <KpiCard icon={AlertTriangle} label="High Priority" value={summary.data.high_risk_claims.toLocaleString()} tone="risk" />
          <KpiCard icon={Gauge} label="Average Denial Risk" value={formatPercent(summary.data.average_denial_probability, 1)} tone="accent" />
          <KpiCard icon={FileSearch} label="Unusual Claims" value={summary.data.anomalous_claims.toLocaleString()} />
        </div>
      )}

      <div className="dashboard-grid">
        <section className="workbench-panel priority-panel">
          <div className="section-heading">
            <h2>Priority Review Queue</h2>
            <button onClick={() => navigate("/claims")}>Open queue</button>
          </div>
          {queue.isLoading && <Skeleton lines={8} />}
          {queue.data && <PriorityQueue claims={queue.data.items} />}
        </section>

        <section className="workbench-panel">
          <div className="section-heading">
            <h2>Top Risk Signals</h2>
            <span>Global model importance</span>
          </div>
          {drivers.isLoading && <Skeleton lines={6} />}
          {drivers.data && <RiskSignalBars drivers={drivers.data.items} />}
        </section>

        <section className="workbench-panel matrix-panel">
          <div className="section-heading">
            <h2>Claim Risk Matrix</h2>
            <span>Risk probability by total charge</span>
          </div>
          {matrix.isLoading && <Skeleton lines={5} />}
          {matrix.data && <RiskMatrix claims={matrix.data.items} onSelect={(claimId) => navigate(`/claims/${encodeURIComponent(claimId)}`)} />}
        </section>
      </div>
    </section>
  );
}

