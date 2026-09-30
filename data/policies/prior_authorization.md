# Prior Authorization Policy

This is a synthetic policy created for the HealthOps ClaimGuard AI demonstration and does not represent CMS, Evernorth, Cigna, or any real payer policy.

## PA-01 Purpose
This demonstration policy describes how analysts should review claims when a service appears to require prior authorization. It supports denial-risk prediction and review prioritization only.

## PA-02 Authorization Requirement
High-cost outpatient services, complex procedures, and services with multiple supporting codes may require an authorization record before the claim service date.

## PA-03 Missing Authorization
If prior authorization is required but no authorization is present, the analyst should verify authorization number, date span, procedure category, and service location before any operational disposition.

## PA-04 Review Procedure
Analysts should compare the claim service dates and primary procedure against authorization details and document whether the missing authorization signal was resolved.
