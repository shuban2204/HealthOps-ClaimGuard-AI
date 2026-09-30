# Model Card

## Intended Use
Prioritize synthetic healthcare claims for analyst review by estimating denial risk and surfacing operational drivers.

## Data
The training data is a hybrid dataset. CMS Medicare DE-SynPUF Sample 1 outpatient claims provide the realistic public claims substrate. `ml/admin_enrichment.py` adds synthetic administrative workflow fields that are not available in the public CMS files.

## Model
The baseline model is Logistic Regression. The primary model is XGBoost when installed, with HistGradientBoosting as a fallback. The unusual-claim detector is an `IsolationForest`.

## Metrics
Metrics are written to `ml/artifacts/metrics.json` by `ml/train.py`, including ROC-AUC, PR-AUC, F1, selected threshold, confusion matrix, and precision at the top 10 percent of scored claims.

## Limitations
The denial target remains synthetic and should not be interpreted as production performance. Outputs are for denial-risk and review prioritization only and require human review.
