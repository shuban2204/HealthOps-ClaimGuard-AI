import { FileText, Loader2 } from "lucide-react";

import type { AnalystBrief } from "../types/api";

export function AnalystBriefPanel({
  brief,
  isFetching,
  isError,
  onGenerate
}: {
  brief?: AnalystBrief;
  isFetching: boolean;
  isError: boolean;
  onGenerate: () => void;
}) {
  return (
    <section className="investigation-panel brief-panel">
      <div className="panel-heading">
        <div>
          <h2>Analyst Brief</h2>
          <p>Grounded summary with cited policy evidence.</p>
        </div>
        <button className="primary-button" onClick={onGenerate} disabled={isFetching}>
          {isFetching ? <Loader2 size={16} className="spin" /> : <FileText size={16} />}
          Generate brief
        </button>
      </div>

      {isError && <p className="inline-error">Brief could not be generated. Try again after checking the claim evidence.</p>}

      {brief ? (
        <div className="brief-content">
          <p className="brief-summary">{brief.summary}</p>
          <div className="brief-grid">
            <div>
              <h3>Rationale</h3>
              <ul>
                {brief.rationale.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
            <div>
              <h3>Next Actions</h3>
              <ul>
                {brief.recommended_actions.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
          </div>
          <div className="citation-row">
            {brief.citations.map((source) => (
              <span key={source.source_id}>{source.source_id}</span>
            ))}
          </div>
          <p className="disclaimer">{brief.disclaimer}</p>
        </div>
      ) : (
        <div className="empty-brief">
          <FileText size={20} />
          <span>Generate a reviewer-ready brief after checking the claim facts and evidence.</span>
        </div>
      )}
    </section>
  );
}
