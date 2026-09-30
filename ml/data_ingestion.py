from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
INTERIM_PATH = ROOT / "data" / "cms_normalized_claims.csv"

OUTPATIENT_SAMPLE1_URL = (
    "https://www.cms.gov/Research-Statistics-Data-and-Systems/Downloadable-Public-Use-Files/"
    "SynPUFs/Downloads/DE1_0_2008_to_2010_Outpatient_Claims_Sample_1.zip"
)
BENEFICIARY_2008_SAMPLE1_URL = (
    "https://www.cms.gov/Research-Statistics-Data-and-Systems/Downloadable-Public-Use-Files/"
    "SynPUFs/Downloads/DE1_0_2008_Beneficiary_Summary_File_Sample_1.zip"
)

OUTPATIENT_COLUMNS = [
    "DESYNPUF_ID",
    "CLM_ID",
    "CLM_FROM_DT",
    "CLM_THRU_DT",
    "PRVDR_NUM",
    "CLM_PMT_AMT",
    "NCH_PRMRY_PYR_CLM_PD_AMT",
    "AT_PHYSN_NPI",
    "OP_PHYSN_NPI",
    "OT_PHYSN_NPI",
    "NCH_BENE_BLOOD_DDCTBL_LBLTY_AM",
    "NCH_BENE_PTB_DDCTBL_AMT",
    "NCH_BENE_PTB_COINSRNC_AMT",
    "ADMTNG_ICD9_DGNS_CD",
    *[f"ICD9_DGNS_CD_{i}" for i in range(1, 11)],
    *[f"ICD9_PRCDR_CD_{i}" for i in range(1, 7)],
    *[f"HCPCS_CD_{i}" for i in range(1, 46)],
]

BENEFICIARY_COLUMNS = [
    "DESYNPUF_ID",
    "BENE_BIRTH_DT",
    "BENE_SEX_IDENT_CD",
    "BENE_HI_CVRAGE_TOT_MONS",
    "BENE_SMI_CVRAGE_TOT_MONS",
    "BENE_HMO_CVRAGE_TOT_MONS",
]


def read_csv_or_zip(path: Path, usecols: list[str] | None = None, nrows: int | None = None) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as archive:
            csv_names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
            if not csv_names:
                raise ValueError(f"No CSV found inside {path}")
            with archive.open(csv_names[0]) as handle:
                return pd.read_csv(
                    handle,
                    usecols=lambda column: usecols is None or column in usecols,
                    nrows=nrows,
                    low_memory=False,
                )
    return pd.read_csv(path, usecols=lambda column: usecols is None or column in usecols, nrows=nrows, low_memory=False)


def count_present(frame: pd.DataFrame, columns: Iterable[str]) -> pd.Series:
    existing = [column for column in columns if column in frame.columns]
    if not existing:
        return pd.Series(np.zeros(len(frame), dtype=int), index=frame.index)
    return frame[existing].notna().sum(axis=1)


def first_present(frame: pd.DataFrame, columns: Iterable[str]) -> pd.Series:
    existing = [column for column in columns if column in frame.columns]
    if not existing:
        return pd.Series([pd.NA] * len(frame), index=frame.index)
    with pd.option_context("future.no_silent_downcasting", True):
        return frame[existing].bfill(axis=1).infer_objects(copy=False).iloc[:, 0]


def normalize_outpatient_claims(outpatient_path: Path, beneficiary_path: Path | None = None, limit_rows: int | None = 50000) -> pd.DataFrame:
    raw = read_csv_or_zip(outpatient_path, OUTPATIENT_COLUMNS, nrows=limit_rows)
    validate_schema(raw, ["DESYNPUF_ID", "CLM_ID", "CLM_FROM_DT", "CLM_THRU_DT", "PRVDR_NUM", "CLM_PMT_AMT"])

    diagnosis_columns = ["ADMTNG_ICD9_DGNS_CD", *[f"ICD9_DGNS_CD_{i}" for i in range(1, 11)]]
    procedure_columns = [*[f"ICD9_PRCDR_CD_{i}" for i in range(1, 7)], *[f"HCPCS_CD_{i}" for i in range(1, 46)]]
    physician_columns = ["AT_PHYSN_NPI", "OP_PHYSN_NPI", "OT_PHYSN_NPI"]

    normalized = pd.DataFrame(
        {
            "claim_id": raw["CLM_ID"].astype(str),
            "beneficiary_id": raw["DESYNPUF_ID"].astype(str),
            "claim_start_date": pd.to_datetime(raw["CLM_FROM_DT"], format="%Y%m%d", errors="coerce"),
            "claim_end_date": pd.to_datetime(raw["CLM_THRU_DT"], format="%Y%m%d", errors="coerce"),
            "claim_type": "outpatient",
            "provider_id": raw["PRVDR_NUM"].astype(str),
            "attending_physician_id": raw["AT_PHYSN_NPI"].astype("Int64").astype(str).replace("<NA>", ""),
            "operating_physician_id": raw["OP_PHYSN_NPI"].astype("Int64").astype(str).replace("<NA>", ""),
            "other_physician_id": raw["OT_PHYSN_NPI"].astype("Int64").astype(str).replace("<NA>", ""),
            "diagnosis_count": count_present(raw, diagnosis_columns),
            "procedure_count": count_present(raw, procedure_columns),
            "primary_diagnosis": first_present(raw, diagnosis_columns).astype(str).replace("<NA>", ""),
            "primary_procedure": first_present(raw, procedure_columns).astype(str).replace("<NA>", ""),
            "claim_payment_amount": pd.to_numeric(raw["CLM_PMT_AMT"], errors="coerce").fillna(0.0),
            "primary_payer_paid_amount": pd.to_numeric(raw["NCH_PRMRY_PYR_CLM_PD_AMT"], errors="coerce").fillna(0.0),
            "blood_deductible_amount": pd.to_numeric(raw["NCH_BENE_BLOOD_DDCTBL_LBLTY_AM"], errors="coerce").fillna(0.0),
            "deductible_amount": pd.to_numeric(raw["NCH_BENE_PTB_DDCTBL_AMT"], errors="coerce").fillna(0.0),
            "coinsurance_amount": pd.to_numeric(raw["NCH_BENE_PTB_COINSRNC_AMT"], errors="coerce").fillna(0.0),
        }
    )
    normalized["claim_duration_days"] = (
        normalized["claim_end_date"].sub(normalized["claim_start_date"]).dt.days.fillna(0).clip(lower=0) + 1
    )
    normalized["claim_total_charge"] = (
        normalized["claim_payment_amount"]
        + normalized["primary_payer_paid_amount"]
        + normalized["blood_deductible_amount"]
        + normalized["deductible_amount"]
        + normalized["coinsurance_amount"]
    )
    normalized = normalized[(normalized["claim_total_charge"] > 0) & (normalized["claim_payment_amount"] >= 0)].copy()
    normalized["reimbursement_ratio"] = normalized["claim_payment_amount"] / normalized["claim_total_charge"].clip(lower=1.0)
    normalized["reimbursement_ratio"] = normalized["reimbursement_ratio"].clip(lower=0, upper=1)
    normalized["unique_physician_count"] = raw[physician_columns].nunique(axis=1, dropna=True)
    normalized["unique_diagnosis_count"] = raw[[col for col in diagnosis_columns if col in raw.columns]].nunique(axis=1, dropna=True)
    normalized["unique_procedure_count"] = raw[[col for col in procedure_columns if col in raw.columns]].nunique(axis=1, dropna=True)

    if beneficiary_path:
        beneficiary = read_csv_or_zip(beneficiary_path, BENEFICIARY_COLUMNS)
        normalized = join_beneficiary(normalized, beneficiary)
    else:
        normalized["beneficiary_age"] = pd.NA
        normalized["beneficiary_sex"] = pd.NA

    normalized = add_claim_behavior_features(normalized)
    normalized["claim_start_date"] = normalized["claim_start_date"].dt.strftime("%Y-%m-%d")
    normalized["claim_end_date"] = normalized["claim_end_date"].dt.strftime("%Y-%m-%d")
    return normalized


def join_beneficiary(claims: pd.DataFrame, beneficiary: pd.DataFrame) -> pd.DataFrame:
    validate_schema(beneficiary, ["DESYNPUF_ID", "BENE_BIRTH_DT", "BENE_SEX_IDENT_CD"])
    bene = beneficiary.rename(columns={"DESYNPUF_ID": "beneficiary_id"}).copy()
    bene["birth_date"] = pd.to_datetime(bene["BENE_BIRTH_DT"], format="%Y%m%d", errors="coerce")
    bene["beneficiary_sex"] = bene["BENE_SEX_IDENT_CD"].map({1: "male", 2: "female"}).fillna("unknown")
    bene = bene[["beneficiary_id", "birth_date", "beneficiary_sex"]]
    merged = claims.merge(bene, on="beneficiary_id", how="left")
    merged["beneficiary_age"] = (
        (merged["claim_start_date"] - merged["birth_date"]).dt.days.div(365.25).round().astype("Int64")
    )
    return merged.drop(columns=["birth_date"])


def add_claim_behavior_features(frame: pd.DataFrame) -> pd.DataFrame:
    claims = frame.sort_values(["claim_start_date", "claim_id"]).copy()
    global_expanding_mean = claims["claim_total_charge"].expanding().mean().shift(1)
    claims["global_prior_mean_claim_amount"] = global_expanding_mean.fillna(claims["claim_total_charge"].median())

    provider_group = claims.groupby("provider_id", sort=False)
    beneficiary_group = claims.groupby("beneficiary_id", sort=False)
    claims["provider_claim_frequency"] = provider_group.cumcount()
    claims["beneficiary_claim_frequency"] = beneficiary_group.cumcount()
    claims["provider_avg_claim_amount"] = (
        provider_group["claim_total_charge"].transform(lambda values: values.expanding().mean().shift(1))
    )
    claims["provider_avg_claim_amount"] = claims["provider_avg_claim_amount"].fillna(claims["global_prior_mean_claim_amount"])
    claims["claim_amount_vs_provider_mean"] = claims["claim_total_charge"] / claims["provider_avg_claim_amount"].clip(lower=1.0)
    claims["claim_amount_vs_global_mean"] = claims["claim_total_charge"] / claims["global_prior_mean_claim_amount"].clip(lower=1.0)

    amount_mean = claims["claim_total_charge"].mean()
    amount_std = claims["claim_total_charge"].std(ddof=0) or 1.0
    claims["claim_amount_zscore"] = (claims["claim_total_charge"] - amount_mean) / amount_std
    claims["days_since_previous_claim_for_beneficiary"] = (
        beneficiary_group["claim_start_date"].diff().dt.days.fillna(999).clip(lower=0)
    )
    claims["high_claim_amount_flag"] = claims["claim_amount_zscore"] >= 2.0
    claims["high_provider_frequency_flag"] = claims["provider_claim_frequency"] >= claims["provider_claim_frequency"].quantile(0.9)
    claims["multi_physician_flag"] = claims["unique_physician_count"] > 1
    claims["complex_claim_flag"] = (
        (claims["diagnosis_count"] >= 4) | (claims["procedure_count"] >= 6) | (claims["claim_duration_days"] >= 3)
    )
    return claims.sort_index()


def validate_schema(frame: pd.DataFrame, required_columns: list[str]) -> None:
    missing = [column for column in required_columns if column not in frame.columns]
    if missing:
        raise ValueError(f"Missing required CMS columns: {', '.join(missing)}")


def write_mapping(path: Path) -> None:
    mapping = {
        "source": "CMS Medicare DE-SynPUF Sample 1 outpatient claims with optional 2008 beneficiary summary",
        "download_urls": {
            "outpatient_sample_1": OUTPATIENT_SAMPLE1_URL,
            "beneficiary_2008_sample_1": BENEFICIARY_2008_SAMPLE1_URL,
        },
        "raw_to_normalized": {
            "CLM_ID": "claim_id",
            "DESYNPUF_ID": "beneficiary_id",
            "CLM_FROM_DT": "claim_start_date",
            "CLM_THRU_DT": "claim_end_date",
            "PRVDR_NUM": "provider_id",
            "AT_PHYSN_NPI": "attending_physician_id",
            "OP_PHYSN_NPI": "operating_physician_id",
            "CLM_PMT_AMT": "claim_payment_amount",
            "NCH_BENE_PTB_DDCTBL_AMT": "deductible_amount",
            "ICD9_DGNS_CD_*": "diagnosis_count, primary_diagnosis, unique_diagnosis_count",
            "ICD9_PRCDR_CD_* and HCPCS_CD_*": "procedure_count, primary_procedure, unique_procedure_count",
            "BENE_BIRTH_DT": "beneficiary_age",
            "BENE_SEX_IDENT_CD": "beneficiary_sex",
        },
        "charge_note": "DE-SynPUF outpatient sample lacks a submitted charge field. claim_total_charge is a payment/liability total proxy composed from claim payment, primary payer payment, deductible, blood deductible, and coinsurance. Non-positive proxy rows are treated as adjustment/reversal rows and excluded from the modeling subset.",
    }
    path.write_text(json.dumps(mapping, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize CMS DE-SynPUF outpatient claims.")
    parser.add_argument("--outpatient", type=Path, default=RAW_DIR / "DE1_0_2008_to_2010_Outpatient_Claims_Sample_1.zip")
    parser.add_argument("--beneficiary", type=Path, default=RAW_DIR / "DE1_0_2008_Beneficiary_Summary_File_Sample_1.zip")
    parser.add_argument("--limit-rows", type=int, default=50000)
    parser.add_argument("--output", type=Path, default=INTERIM_PATH)
    args = parser.parse_args()

    beneficiary = args.beneficiary if args.beneficiary.exists() else None
    normalized = normalize_outpatient_claims(args.outpatient, beneficiary, args.limit_rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    normalized.to_csv(args.output, index=False)
    write_mapping(ROOT / "ml" / "artifacts" / "schema_mapping.json")
    print(f"Wrote {len(normalized):,} normalized claims to {args.output}")


if __name__ == "__main__":
    main()
