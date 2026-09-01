# 14 — LLM & GenAI Testing Handbook

## QA focus

Evaluate task success, correctness, consistency, format, groundedness, safety, privacy, prompt-injection resistance, latency and cost using versioned test sets.

## Evaluation design

Use deterministic checks for JSON/schema, citations, policy terms and prohibited data. Use human-reviewed rubrics for subjective helpfulness/correctness. Calibrate any LLM judge against human labels and retain evaluator/model/prompt versions.

## Golden dataset fields

`case_id, input, context, expected facts, unacceptable claims, expected format, safety expectation, scoring rubric, owner, version`.

## Failure modes

Hallucination, refusal of allowed task, unsafe compliance, inconsistent answers, PII disclosure, prompt injection, broken structure, stale knowledge, excessive latency/cost and version regression.
