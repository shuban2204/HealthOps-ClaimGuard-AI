# Responsible AI

## Intended Role

HealthOps ClaimGuard AI is a decision-support and prioritization demo for claims operations. It helps a reviewer identify claims that may deserve closer inspection, understand model signals, inspect unusual-claim indicators, retrieve relevant demonstration policy evidence, and generate a deterministic analyst brief.

It must not be used to autonomously approve, deny, or adjudicate a claim.

## Safeguards

- Uses CMS synthetic public-use data plus synthetic administrative enrichment.
- Avoids PHI processing.
- Provides risk bands and explanations instead of final decisions.
- Shows retrieved policy evidence with source IDs.
- Generates deterministic analyst briefs with citations and limitations.
- Includes a decision-support disclaimer in the brief response.
- Avoids medical diagnosis, treatment recommendations, and clinical advice.

## Human Review Requirement

Every output should be verified by a qualified human reviewer. Reviewers should check:

- claim facts against the source system
- current payer policy and contract language
- member eligibility and authorization records
- documentation completeness
- coding consistency
- whether model explanations are plausible for the case

## Known Limitations

- The denial target is synthetic.
- The policy corpus is fictional demonstration content.
- Test metrics measure demo pipeline behavior, not real-world denial performance.
- The anomaly model identifies unusual patterns, not fraud.
- The system has not been validated for fairness, calibration, or operational impact on real populations.

## Before Real-World Use

A production path would require data governance, security review, legal and compliance review, bias and impact assessment, prospective validation, monitoring, escalation paths, and appeal-aware human decision procedures.
