# 09 — Cloud Data Platform Testing Handbook

## QA focus

Test cloud-hosted data systems through contracts and observable outcomes: IAM, network access, secrets, storage layout, encryption, retention, scaling, failover, service limits and cost-safe failure handling.

## Shared-cloud test questions

- Is the workload isolated by environment/account/project/tenant?
- Can only the intended role read, write, decrypt or invoke it?
- Does a retry or autoscaling event preserve data correctness?
- Are backups, retention and disaster-recovery claims testable?
- Are logs/metrics free of sensitive payloads and usable during incident response?

## Do not test by broad privilege

Use dedicated non-production roles and synthetic/masked data. Security QA verifies least privilege and denial paths as rigorously as allowed paths.
