# Capstone — Enterprise Data & AI QA Platform

## Mission

Build the **quality engineering platform around** a hypothetical enterprise data-and-AI product. Do not build the product itself.

```text
Enterprise Data / AI System Under Test
         | ingestion, DWH, APIs, ML, RAG, agents, BI
         v
QA Platform: validation | evaluation | automation | evidence | gates
         v
Quality decision: PASS / FAIL / BLOCK
```

## Required QA deliverables

1. SUT context diagram and quality-risk register.
2. Master test strategy and test architecture.
3. ETL/DWH validation suite: schema, counts, keys, rules, aggregates and reconciliation.
4. API contract/integration suite and representative negative tests.
5. ML evaluation plan: data, feature, metric, robustness, fairness and drift checks.
6. LLM/RAG evaluation set with correctness, groundedness, citation, safety and privacy criteria.
7. Agent test suite: task success, tools, authorization, state, retries, loops and recovery.
8. Performance/security/reliability plan with SLOs and attack/failure scenarios.
9. CI/CD quality gates, artifacts, waiver policy and release dashboard outline.
10. Three realistic defects, investigation evidence, root cause, corrective action and regression coverage.

## Suggested SUT

A financial-services analytics platform ingests transactions, builds warehouse dashboards, offers a policy-document RAG assistant and uses a constrained agent to prepare—but never execute—case-management actions.

## Capstone acceptance criteria

Your evidence must make a release decision reproducible. Each critical test has an oracle, test data, owner, artifact and clear block/pass threshold. AI evaluation must distinguish deterministic validation from rubric-based judgment and retain the exact model/prompt/configuration version.

## Final presentation outline

In 15 minutes: SUT and risk map (2), strategy and coverage (3), automation/evaluation architecture (3), representative failure evidence (3), gate/monitoring/rollback (2), leadership trade-offs (2).
