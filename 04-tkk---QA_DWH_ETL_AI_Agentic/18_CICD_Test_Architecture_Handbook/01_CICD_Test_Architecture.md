# 18 — CI/CD Quality Gates & Test Architecture Handbook

## QA focus

Design layers of fast, trustworthy feedback: contracts and static checks first; deterministic unit/data validations next; integration/e2e and non-functional suites in suitable environments; production gates and monitoring after deploy.

```text
commit → fast checks → contract/data tests → integration → evaluation → release gate → deploy → monitor
```

## Gate design

Every gate needs owner, threshold, evidence, failure action, waiver authority and expiry. Do not let flaky tests silently become non-blocking; quarantine requires a named owner, date and compensating monitor.

## Architecture principles

Version test data and baselines; keep secrets out of code; make environments explicit; publish artifacts; isolate tests; use synthetic/masked data; make rollback tested rather than assumed.
