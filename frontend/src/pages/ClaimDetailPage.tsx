import { ArrowLeft } from "lucide-react";
import { useState } from "react";
import { Link, useParams } from "react-router-dom";

import { AnalystBriefPanel } from "../components/AnalystBriefPanel";
import { AnomalySignal } from "../components/AnomalySignal";
import { ClaimFacts } from "../components/ClaimFacts";
import { EvidencePanel } from "../components/EvidencePanel";
import { PageHeader } from "../components/PageHeader";
import { RiskBadge } from "../components/RiskBadge";
import { RiskExplanation } from "../components/RiskExplanation";
import { ErrorState, Skeleton } from "../components/States";
import { useAnalystBrief, useClaimDetail, useEvidence } from "../hooks/queries";
import { formatCurrency, formatPercent } from "../utils/format";
import type { SignalKey } from "../utils/signalMap";

export function ClaimDetailPage() {
  const { claimId } = useParams();
  const detail = useClaimDetail(claimId);
  const evidence = useEvidence(claimId);
  const brief = useAnalystBrief(claimId);
  const [activeSignal, setActiveSignal] = useState<SignalKey | null>(null);

  return (
    <section className="page">
      <PageHeader title="Claim Investigation" kicker="Claim review" />
      <Link className="back-link" to="/claims">
        <ArrowLeft size={16} /> Back to claims
      </Link>

      {detail.isLoading && <Skeleton lines={10} />}
      {detail.isError && <ErrorState message="Claim could not be loaded." onRetry={() => detail.refetch()} />}

      {detail.data && (
        <>
          <header className="claim-hero">
            <div>
              <p>Claim {String(detail.data.claim.claim_id)}</p>
              <h2>{String(detail.data.claim.claim_type).toUpperCase()}</h2>
            </div>
            <div className="hero-risk">
              <RiskBadge band={detail.data.prediction.risk_band} />
              <strong>{formatPercent(detail.data.prediction.denial_probability, 1)}</strong>
            </div>
          </header>

          <div className="fact-strip">
            <span>Total charge <strong>{formatCurrency(Number(detail.data.claim.claim_total_charge ?? 0))}</strong></span>
            <span>Network <strong>{String(detail.data.claim.provider_network ?? "").replace("_", " ")}</strong></span>
            <span>Procedure count <strong>{String(detail.data.claim.procedure_count ?? "n/a")}</strong></span>
            <span>Anomaly <strong>{detail.data.anomaly.is_anomaly ? "Detected" : "Not detected"}</strong></span>
          </div>

          <div className="investigation-layout">
            <ClaimFacts detail={detail.data} activeSignal={activeSignal} />
            <div className="center-column">
              <RiskExplanation detail={detail.data} activeSignal={activeSignal} onSignal={setActiveSignal} />
              <AnomalySignal detail={detail.data} />
              <AnalystBriefPanel
                brief={brief.data}
                isFetching={brief.isPending}
                isError={brief.isError}
                onGenerate={() => brief.mutate()}
              />
            </div>
            {evidence.isLoading ? <Skeleton lines={8} /> : <EvidencePanel evidence={evidence.data} activeSignal={activeSignal} />}
          </div>
        </>
      )}
    </section>
  );
}
