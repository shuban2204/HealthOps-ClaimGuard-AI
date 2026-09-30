import { Activity, BarChart3, FileText, Target } from "lucide-react";

import { KpiCard } from "../components/KpiCard";
import { PageHeader } from "../components/PageHeader";
import { RiskSignalBars } from "../components/RiskSignalBars";
import { ErrorState, Skeleton } from "../components/States";
import { useDrivers, useModelMetrics } from "../hooks/queries";

export function ModelInsightsPage() {
  const metrics = useModelMetrics();
  const drivers = useDrivers(12);

  return (
    <section className="page">
      <PageHeader title="Model Insights" kicker="Model monitoring" />

      {metrics.isLoading && <Skeleton lines={8} />}
      {metrics.isError && <ErrorState message="Model metrics could not be loaded." onRetry={() => metrics.refetch()} />}

      {metrics.data && (
        <>
          <div className="summary-strip compact">
            <KpiCard icon={Activity} label="Model" value={metrics.data.model_name} detail={metrics.data.model_version} />
            <KpiCard icon={BarChart3} label="Test ROC-AUC" value={metrics.data.test.roc_auc.toFixed(4)} />
            <KpiCard icon={Target} label="Precision@Top10%" value={metrics.data.test.precision_at_top_10pct.toFixed(4)} tone="accent" />
            <KpiCard icon={FileText} label="Positive prevalence" value={metrics.data.class_prevalence.toFixed(4)} />
          </div>

          <div className="model-grid">
            <section className="workbench-panel">
              <h2>Evaluation</h2>
              <table className="metrics-table">
                <thead>
                  <tr>
                    <th>Split</th>
                    <th>ROC-AUC</th>
                    <th>PR-AUC</th>
                    <th>F1</th>
                    <th>Recall@10%</th>
                  </tr>
                </thead>
                <tbody>
                  {(["train", "validation", "test"] as const).map((split) => (
                    <tr key={split}>
                      <td>{split}</td>
                      <td>{metrics.data[split].roc_auc.toFixed(4)}</td>
                      <td>{metrics.data[split].pr_auc.toFixed(4)}</td>
                      <td>{metrics.data[split].f1.toFixed(4)}</td>
                      <td>{metrics.data[split].recall_at_top_10pct.toFixed(4)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </section>

            <section className="workbench-panel">
              <h2>Top Global Drivers</h2>
              {drivers.data ? <RiskSignalBars drivers={drivers.data.items} /> : <Skeleton lines={6} />}
            </section>

            <section className="workbench-panel model-context">
              <h2>Data Foundation</h2>
              <p>CMS DE-SynPUF Sample 1 outpatient claims plus synthetic administrative enrichment.</p>
              <p>Synthetic administrative labels are not CMS truth and are used to prove system behavior.</p>
              <strong>This model is designed for analyst review prioritization. It does not make automatic claim decisions.</strong>
            </section>
          </div>
        </>
      )}
    </section>
  );
}

