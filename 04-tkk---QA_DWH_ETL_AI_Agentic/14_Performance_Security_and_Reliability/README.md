# 14 — Performance, Security and Reliability Testing

## QA focus

Prove non-functional behavior against agreed SLOs and risk limits for pipelines, APIs, data stores and AI systems.

## Coverage

Load, stress, spike, soak and capacity testing; P50/P95/P99 latency; throughput and backpressure; authentication/authorization; injection; PII leakage; secrets; encryption; availability; failover; retry; disaster recovery and chaos/fault injection.

## Practice

Create a test plan for month-end load that includes a 10x input spike, a dependency timeout, a credential-expiry event and a requirement to prevent PII appearing in LLM output or logs.

## Interview probe

Which performance results can look healthy while a small but high-value user segment experiences a severe failure?
