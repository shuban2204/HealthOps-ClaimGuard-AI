# Data Provenance

## Public Claims Substrate

The project uses CMS Medicare DE-SynPUF as the realistic public claims substrate. The local run used:

- CMS 2008-2010 Data Entrepreneurs Synthetic Public Use File, DE1.0 Sample 1
- Outpatient Claims: `DE1_0_2008_to_2010_Outpatient_Claims_Sample_1`
- Beneficiary Summary: `DE1_0_2008_Beneficiary_Summary_File_Sample_1`

Raw CMS files are expected under `data/raw/` and are not committed to Git.

CMS download page:
https://www.cms.gov/data-research/statistics-trends-and-reports/medicare-claims-synthetic-public-use-files/cms-2008-2010-data-entrepreneurs-synthetic-public-use-file-de-synpuf/de10-sample-1

## Raw To Normalized Mapping

| CMS field | Normalized field |
|---|---|
| `CLM_ID` | `claim_id` |
| `DESYNPUF_ID` | `beneficiary_id` |
| `CLM_FROM_DT` | `claim_start_date` |
| `CLM_THRU_DT` | `claim_end_date` |
| `PRVDR_NUM` | `provider_id` |
| `AT_PHYSN_NPI` | `attending_physician_id` |
| `OP_PHYSN_NPI` | `operating_physician_id` |
| `ICD9_DGNS_CD_*` | diagnosis counts and primary diagnosis |
| `ICD9_PRCDR_CD_*`, `HCPCS_CD_*` | procedure counts and primary procedure |
| `CLM_PMT_AMT` | `claim_payment_amount` |
| deductible / coinsurance fields | `deductible_amount`, payment liability proxy fields |
| `BENE_BIRTH_DT` | `beneficiary_age` |
| `BENE_SEX_IDENT_CD` | `beneficiary_sex` |

DE-SynPUF outpatient claims do not expose every internal billing and operations variable needed by the product concept. In particular, prior authorization, documentation completeness, payer network status, coverage-active-at-review status, coding mismatch review flags, duplicate review flags, timely filing review flags, and denial outcomes are not directly available as internal administrative workflow fields.

## Synthetic Administrative Enrichment

`ml/admin_enrichment.py` adds synthetic operational fields after CMS normalization:

- `prior_auth_required`
- `prior_auth_present`
- `documentation_complete`
- `provider_network`
- `member_coverage_active`
- `coding_mismatch_flag`
- `duplicate_claim_flag`
- `timely_filing_flag`
- `historical_provider_denial_rate`
- `denied`
- `denial_reason`

These fields are generated from transparent rules that depend partly on CMS-derived claim amount, claim complexity, provider frequency, beneficiary claim history, and provider-level risk profiles. They are not independent row-level coin flips.

The target `denied` is synthetic and exists only to prove the system behavior for denial-risk and review prioritization. The project does not claim real-world denial prediction performance.

## Feature Engineering

The pipeline derives:

- claim duration
- diagnosis and procedure counts
- reimbursement ratio
- provider prior average claim amount
- provider and beneficiary prior claim frequency
- claim amount compared with provider and global prior means
- claim amount z-score
- days since previous beneficiary claim
- high amount, high provider frequency, multi-physician, and complex-claim flags

Provider and beneficiary aggregate features are computed as prior-claim expanding features ordered by claim date. This avoids using future rows for those behavioral features.

## Privacy

DE-SynPUF is a synthetic public use file. It is not real PHI. The administrative enrichment layer is also synthetic.

## Limitations

- CMS DE-SynPUF is synthetic and disclosure-treated.
- The administrative target is synthetic.
- `claim_total_charge` is a payment/liability total proxy because the outpatient sample does not include a submitted charge field.
- Non-positive payment-proxy rows are treated as adjustment or reversal rows and excluded from the modeling subset.
- Metrics demonstrate pipeline behavior, not deployable real-world model performance.
- Any real deployment would require governance, de-identified real claims, prospective validation, monitoring, and human review controls.
