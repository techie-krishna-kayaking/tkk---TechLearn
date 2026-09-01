# 15 — CI/CD Quality Gates and Test Architecture

## QA focus

Design layered, fast-feedback quality gates that make risk visible without creating blind dependence on automation.

## Architecture principles

Version tests and test data; separate environment configuration; run cheap deterministic checks first; quarantine only with ownership/expiry; publish evidence; gate critical failures; preserve traces/artifacts; enable safe rollback and post-deploy monitoring.

## Included example

See `../.github/workflows/quality-gate.yml` for a small Python validation gate. Adapt it to run SQL, data, API, AI-evaluation and security suites in appropriate environments.

## Interview probe

How would you prevent a flaky non-critical test from blocking releases while ensuring a critical flaky test is not ignored?
