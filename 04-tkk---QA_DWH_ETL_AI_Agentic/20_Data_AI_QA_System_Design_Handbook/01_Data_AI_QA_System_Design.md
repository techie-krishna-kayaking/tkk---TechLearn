# 20 — Data & AI QA System Design Handbook

## How to answer a senior system-design question

1. Clarify SUT, users, critical outcomes, scale, data sensitivity and SLOs.
2. Draw the business/data/AI flow and boundaries.
3. Identify quality risks by impact and likelihood.
4. Propose test layers, data/oracle strategy and automation architecture.
5. Cover security, reliability, performance, recovery and observability.
6. Define quality metrics/gates, ownership, waiver and rollback.

## Reference QA architecture

```text
Contracts + test data → validators / API tests / pipeline checks / AI evals
                           ↓
                    evidence store + reports
                           ↓
              CI/CD quality gate → release decision
                           ↓
              production monitors + incident runbooks
```

The system under test may be data/AI. The system you design is the quality platform around it.
