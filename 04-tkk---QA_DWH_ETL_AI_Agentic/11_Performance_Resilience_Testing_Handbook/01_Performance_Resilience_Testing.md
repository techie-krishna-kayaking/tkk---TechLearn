# 11 — Performance & Resilience Testing Handbook

## QA focus

Prove behavior under expected and adverse conditions: load, stress, spike, soak, capacity, P50/P95/P99 latency, throughput, error rate, backpressure, failover and recovery.

## Test types

| Test | Question answered |
|---|---|
| load | does expected concurrent volume meet SLO? |
| stress | where does it degrade/fail and how? |
| spike | can sudden demand recover without corruption? |
| soak | do leaks, queues or data drift appear over time? |
| failover | does dependency/node loss preserve correctness? |

Correctness remains part of performance testing: a fast pipeline that drops or duplicates records fails.

## Checklist

- [ ] Define workload mix, data shape, SLOs and acceptance thresholds.
- [ ] Measure P50/P95/P99, errors, throughput, resource and queue behavior.
- [ ] Test realistic large/skewed data, not empty synthetic requests only.
- [ ] Inject dependency failure and validate retry/backpressure/reconciliation.
