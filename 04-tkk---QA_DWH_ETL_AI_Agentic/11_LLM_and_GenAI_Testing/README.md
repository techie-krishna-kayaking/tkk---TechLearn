# 11 — LLM and GenAI Testing

## QA focus

Evaluate task success, correctness, groundedness, consistency, safety, privacy, structured-output validity, latency and cost with versioned golden datasets.

## Essential test sets

Representative tasks, edge cases, adversarial/prompt-injection prompts, PII/secrets probes, multilingual inputs, refusals, formatting constraints and regression prompts.

## Evaluation approach

Use deterministic checks where possible; use human-reviewed rubrics for subjective criteria; calibrate any LLM judge against human labels; preserve prompt/model/configuration/version and evidence for every run.

## Interview probe

How do you establish a release gate for an assistant when answer quality is not strictly binary?
