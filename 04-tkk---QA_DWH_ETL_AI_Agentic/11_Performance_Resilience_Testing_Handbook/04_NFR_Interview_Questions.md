# Performance & Resilience — Interview Q&A

**Load versus stress?** Load proves expected workload meets SLO; stress finds degradation/failure boundary and recovery behavior.

**Why P99?** Average hides tail pain; P95/P99 show whether high-value or unlucky users miss an SLA.

**How do you test resilience?** Inject controlled dependency/node/network failure and validate bounded retry, backpressure, alert, no corruption/duplicate effect, recovery and reconciliation.

**What belongs in an SLO?** User/business outcome, measurable indicator, threshold/window, data/workload scope and error budget/response owner.

**Performance test pass condition?** Latency/throughput/errors meet SLO *and* final state/data correctness remains intact.
