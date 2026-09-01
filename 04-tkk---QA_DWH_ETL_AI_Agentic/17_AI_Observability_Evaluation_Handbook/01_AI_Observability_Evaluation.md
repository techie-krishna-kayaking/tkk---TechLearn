# 17 — AI Observability & Evaluation Handbook

## QA focus

Make AI quality measurable after release. Preserve request context, prompt/version, model/configuration, retrieved chunks, tool calls, outputs, safety decisions, latency, tokens/cost and human/user feedback—subject to privacy policy.

## Offline versus online evidence

Offline golden-set evaluation is fast and reproducible but may not reflect new user behavior. Online monitoring measures actual quality/feedback but needs safety controls, sampling, privacy and a rollback path. Use offline gates before release and online signals after it.

## Evaluation reliability

Track evaluator agreement with humans, rubric drift, sample coverage and confidence. An uncalibrated “LLM-as-judge” is a hypothesis, not a release oracle.

## Checklist

- [ ] Trace every evaluated response without exposing sensitive content.
- [ ] Version prompts, model, tools, index, policies and evaluator.
- [ ] Monitor task success, safety, groundedness proxy, latency and cost.
- [ ] Alert on regression and preserve rollback evidence.
