# Enterprise Data & AI QA Platform

This is the buildable capstone evidence pack. It surrounds a hypothetical financial-data warehouse, policy RAG assistant and constrained case-management agent. It does **not** implement those systems.

## Run the dependency-free validation suite

```powershell
python -m unittest discover -s QA_Platform/tests -v
```

## Contents

- `framework/` — reusable schema, data-quality and reconciliation validators.
- `test_data/` — valid and deliberately invalid source/target fixtures.
- `tests/` — automated quality-rule tests and release-gate checks.
- `evals/` — ML, LLM, RAG and agent golden/evaluation specifications.
- `performance/`, `security/` — executable test design and acceptance criteria.
- `docs/` — strategy, architecture, test cases, runbook and gate decision.
- `reports/`, `defects/` — evidence/report and defect examples.
