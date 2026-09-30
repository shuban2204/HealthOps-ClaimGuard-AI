from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from app.config import POLICY_DIR, SENTENCE_TRANSFORMER_MODEL


@dataclass
class PolicyChunk:
    source_id: str
    title: str
    section: str
    text: str


class RetrievalService:
    def __init__(self) -> None:
        if not POLICY_DIR.exists():
            raise RuntimeError(f"Policy directory not found: {POLICY_DIR}")
        self.chunks = self._load_policy_chunks()
        if not self.chunks:
            raise RuntimeError("No policy chunks available for retrieval.")
        self.encoder = SentenceTransformer(SENTENCE_TRANSFORMER_MODEL)
        embeddings = self.encoder.encode([chunk.text for chunk in self.chunks], normalize_embeddings=True)
        self.embeddings = np.asarray(embeddings, dtype="float32")
        self.index = faiss.IndexFlatIP(self.embeddings.shape[1])
        self.index.add(self.embeddings)

    @property
    def ready(self) -> bool:
        return bool(self.index.ntotal)

    def evidence_for_claim(self, claim_detail: dict[str, Any], top_k: int = 5) -> dict[str, Any]:
        query = self.build_query(claim_detail)
        query_embedding = np.asarray(self.encoder.encode([query], normalize_embeddings=True), dtype="float32")
        scores, indexes = self.index.search(query_embedding, top_k)
        sources = []
        for score, index in zip(scores[0], indexes[0]):
            if index < 0:
                continue
            chunk = self.chunks[int(index)]
            sources.append(
                {
                    "source_id": chunk.source_id,
                    "title": chunk.title,
                    "section": chunk.section,
                    "text": chunk.text,
                    "similarity_score": round(float(score), 4),
                }
            )
        return {"claim_id": str(claim_detail["claim"]["claim_id"]), "query": query, "sources": sources}

    def build_query(self, claim_detail: dict[str, Any]) -> str:
        claim = claim_detail["claim"]
        signals = []
        if claim.get("missing_required_auth") or (claim.get("prior_auth_required") and not claim.get("prior_auth_present")):
            signals.append("missing required prior authorization authorization requirement")
        if claim.get("provider_network") == "out_of_network":
            signals.append("out-of-network provider network coverage exception")
        if claim.get("coding_mismatch_flag"):
            signals.append("coding mismatch diagnosis procedure coding review")
        if "timely_filing_flag" in claim:
            if claim.get("timely_filing_flag"):
                signals.append("late filing timely filing submission window")
            else:
                signals.append("timely filing verification submission window")
        if claim.get("duplicate_claim_flag"):
            signals.append("duplicate claim repeated service review")
        if not claim.get("documentation_complete", True):
            signals.append("incomplete documentation medical record support")
        factors = [factor["label"] for factor in claim_detail["prediction"].get("top_factors", [])]
        joined = ", ".join(signals + factors)
        return (
            "Retrieve synthetic demonstration policy guidance for claim review prioritization. "
            f"Claim signals: {joined or 'general outpatient claim review'}."
        )

    def _load_policy_chunks(self) -> list[PolicyChunk]:
        chunks: list[PolicyChunk] = []
        for path in sorted(Path(POLICY_DIR).glob("*.md")):
            text = path.read_text(encoding="utf-8")
            title = self._extract_title(text, path.stem)
            sections = re.split(r"\n(?=##\s+)", text)
            for section_text in sections:
                match = re.search(r"^##\s+(.+)$", section_text, flags=re.MULTILINE)
                if not match:
                    continue
                section = match.group(1).strip()
                section_key = section.split()[0].replace(".", "").replace(":", "")
                source_id = f"{path.stem}:{section_key}"
                chunks.append(PolicyChunk(source_id=source_id, title=title, section=section, text=section_text.strip()))
        return chunks

    def _extract_title(self, text: str, fallback: str) -> str:
        for line in text.splitlines():
            if line.startswith("# "):
                return line.replace("# ", "").strip()
        return fallback.replace("_", " ").title()
