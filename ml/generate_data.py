from __future__ import annotations

import argparse
from pathlib import Path

from admin_enrichment import PROCESSED_PATH, enrich_administrative_fields
from data_ingestion import INTERIM_PATH, normalize_outpatient_claims


def build_hybrid_dataset(
    outpatient_path: Path,
    beneficiary_path: Path | None,
    limit_rows: int,
    output_path: Path = PROCESSED_PATH,
) -> int:
    normalized = normalize_outpatient_claims(outpatient_path, beneficiary_path, limit_rows)
    INTERIM_PATH.parent.mkdir(parents=True, exist_ok=True)
    normalized.to_csv(INTERIM_PATH, index=False)
    enriched = enrich_administrative_fields(normalized)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    enriched.to_csv(output_path, index=False)
    return len(enriched)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build hybrid CMS DE-SynPUF plus synthetic administrative dataset.")
    parser.add_argument(
        "--outpatient",
        type=Path,
        default=Path("data/raw/DE1_0_2008_to_2010_Outpatient_Claims_Sample_1.zip"),
    )
    parser.add_argument(
        "--beneficiary",
        type=Path,
        default=Path("data/raw/DE1_0_2008_Beneficiary_Summary_File_Sample_1.zip"),
    )
    parser.add_argument("--limit-rows", type=int, default=50000)
    parser.add_argument("--output", type=Path, default=PROCESSED_PATH)
    args = parser.parse_args()

    beneficiary_path = args.beneficiary if args.beneficiary.exists() else None
    row_count = build_hybrid_dataset(args.outpatient, beneficiary_path, args.limit_rows, args.output)
    print(f"Wrote {row_count:,} hybrid claims to {args.output}")


if __name__ == "__main__":
    main()

