# Coding Guidelines

This is a synthetic policy created for the HealthOps ClaimGuard AI demonstration and does not represent CMS, Evernorth, Cigna, or any real payer policy.

## CODE-01 Purpose
This demonstration policy supports review of diagnosis, procedure, and coding mismatch signals.

## CODE-02 Diagnosis Procedure Consistency
The primary diagnosis, primary procedure, procedure count, and diagnosis count should be directionally consistent with the claim type and billed service profile.

## CODE-03 Coding Mismatch
Claims with a coding mismatch flag should be routed for coding review. The flag is a prioritization signal and not a medical recommendation.

## CODE-04 Review Procedure
Analysts should compare diagnosis and procedure families, modifiers if available, claim amount, and documentation support before closing the coding review item.
