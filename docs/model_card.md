# Model Card

## Intended Use

Prioritize synthetic healthcare claims for analyst review by estimating denial risk, surfacing claim-level drivers, and supporting evidence-based review. The model output is decision support only.

## Data

The training data is a hybrid dataset with 49,199 rows. CMS Medicare DE-SynPUF Sample 1 outpatient claims provide the realistic public claims substrate. `ml/admin_enrichment.py` adds synthetic administrative workflow fields that are not available in the public CMS files.

The denial target is synthetic. It is designed to make the end-to-end prioritization workflow testable, not to represent real payer adjudication behavior.

## Model

The baseline model is Logistic Regression. The primary model is XGBoost when installed, with HistGradientBoosting as a fallback. The unusual-claim detector is an `IsolationForest`.

The selected model version is `hybrid-cms-admin-0.2.0`. The selected risk threshold is `0.2729`, chosen on validation data.

## Metrics

Held-out test metrics for the primary model:

| Metric | Value |
|---|---:|
| ROC-AUC | 0.7250 |
| PR-AUC | 0.5646 |
| Precision | 0.4756 |
| Recall | 0.6290 |
| F1 | 0.5416 |
| Precision at top 10 percent | 0.7093 |
| Positive prevalence | 0.2876 |

Metrics are written to `ml/artifacts/metrics.json` by `ml/train.py`, including ROC-AUC, PR-AUC, F1, selected threshold, confusion matrix, and precision at the top 10 percent of scored claims.

## Explainability

Claim-level explanations are generated from model contribution signals. Global drivers are exposed through the model metrics endpoint and frontend model insights page. The strongest global signals include missing required authorization, documentation or coding issues, prior authorization status, coverage status, and provider network status.

## Monitoring Considerations

A real deployment would need:

- prospective validation on governed real-world data
- calibration monitoring
- drift monitoring by payer, provider, service type, and population segment
- alerting on input missingness and feature distribution shifts
- regular review of false positives and false negatives by human operators
- documented threshold governance

## Limitations

The denial target remains synthetic and should not be interpreted as production performance. Outputs are for denial-risk and review prioritization only and require human review. The unusual-claim detector is not a fraud detector.
