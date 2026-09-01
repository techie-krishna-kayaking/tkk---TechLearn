# AI Observability & Evaluation — Interview Q&A

**What must an AI trace include?** Input/redacted context, prompt/model/config, retrieved chunks, tools/results, output, policy decisions, evaluator score/version, latency/cost and correlation ID.

**Why calibrate LLM judges?** Judges can be biased/inconsistent; compare with human labels, monitor agreement and keep humans in critical decisions.

**Offline versus online eval?** Offline is reproducible/pre-release; online captures real behavior but needs privacy, safety, sampling and rollback controls.

**How do you detect regression?** Versioned golden suite plus thresholds by category, confidence/human review and post-release outcome/safety/latency monitoring.

**What is evaluator drift?** Evaluation model/rubric behavior changes, making scores non-comparable; version/calibrate evaluator and retain reference set.
