# 03 — Python Test Automation Handbook

> Python supports QA when it makes data validation repeatable, deterministic and evidence-rich. The objective is a testable validation framework—not application development.

## 🎯 Design principles

- Separate configuration, test data, expected result and validation code.
- Make comparison keys and tolerances explicit.
- Return actionable failures: which keys, columns, counts and controls differ.
- Keep tests deterministic; isolate time, randomness, services and credentials.
- Produce machine-readable results for CI plus readable evidence for people.

## Useful standard-library building blocks

`csv`, `json`, `decimal`, `datetime`, `pathlib`, `unittest`, `logging`, `dataclasses` and `collections.Counter` cover many portable QA exercises. Prefer `Decimal` rather than floating point for financial control totals.

## Automation layers

```text
Fast unit validators → contract/schema checks → database/API integrations → end-to-end reconciliation → production monitors
```

## What makes an assertion useful?

Weak: `assert result is not None`  
Useful: `assert missing_keys == []`, with an output file naming the missing keys, source snapshot and target run.

## QA interview line

“I automate stable, high-value controls and retain enough evidence to distinguish a product defect, bad test data, environment issue and expectation defect.”
