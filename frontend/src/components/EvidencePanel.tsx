import type { EvidenceResponse } from "../types/api";
import { evidenceMatchesSignal, type SignalKey } from "../utils/signalMap";

export function EvidencePanel({ evidence, activeSignal }: { evidence?: EvidenceResponse; activeSignal: SignalKey | null }) {
  return (
    <section className="investigation-panel evidence-panel">
      <h2>Policy Evidence</h2>
      <p>Source IDs are preserved for downstream citation.</p>
      <div className="evidence-stack">
        {evidence?.sources.map((source, index) => (
          <details className={evidenceMatchesSignal(source.source_id, activeSignal) ? "highlight" : ""} key={source.source_id} open={index < 2}>
            <summary>
              <span>{String(index + 1).padStart(2, "0")}</span>
              <div>
                <strong>{source.title}</strong>
                <small>
                  {source.source_id} - {source.section}
                </small>
              </div>
            </summary>
            <p>{source.text.replace(/^##\s+.+\n/, "")}</p>
            <small>Similarity {source.similarity_score.toFixed(4)}</small>
          </details>
        ))}
      </div>
    </section>
  );
}

