# Performance and Reliability Test Plan

| Test | Acceptance evidence |
|---|---|
| expected load | P95/P99, throughput, error rate and correctness meet SLO |
| 10x spike | bounded queue/backpressure; no silent data loss/duplicate effect |
| soak | stable latency/resources and complete final reconciliation |
| dependency timeout | bounded retry, graceful degradation, alert and safe recovery |
| failover | no unauthorized/partial publish; recovered state reconciles |

Capture workload mix, data distribution, environment, run version, traces, metrics and post-test reconciliation.
