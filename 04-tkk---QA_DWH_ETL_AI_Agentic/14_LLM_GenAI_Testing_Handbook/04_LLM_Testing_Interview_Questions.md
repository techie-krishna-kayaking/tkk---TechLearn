# LLM / GenAI Testing — Interview Questions & Model Answers

## 1. How do you define correctness for an LLM?

Break it into task-specific observable criteria: factual claims, grounding/source support, required actions, format, completeness, safety and refusal behavior. Use deterministic checks when possible and a human-calibrated rubric where judgment is needed. “Looks good” is not an oracle.

## 2. What is an LLM golden dataset?

A versioned, representative and adversarial set of inputs with expected facts, allowed sources/context, unacceptable claims, format requirements, safety expectation and scoring rubric. It becomes the regression baseline across model, prompt, tool and retrieval changes.

## 3. How do you test hallucination?

Use known-answer and unsupported-answer cases. Verify claims/citations against approved context, penalize fabricated facts/citations and test whether the system abstains/escalates when evidence is absent. Include misleading and conflicting context.

## 4. Can an LLM judge be trusted?

Only as a calibrated evaluator. Compare judge labels to human-reviewed reference cases, measure agreement/bias, version its prompt/model and keep human review for critical/ambiguous decisions. It should not be an opaque automatic release authority.

## 5. How do you test prompt injection?

Use direct and indirect malicious instructions, data exfiltration attempts, conflicting instructions and tool-use coercion. Assert policy priority, safe refusal/redaction, no unauthorized tool call, traceability and non-leakage in output/logs.

## 6. What must be captured for reproducible LLM test evidence?

Input, system/prompt/template version, model and decoding parameters, tools and results, retrieved context/index version, output, evaluator/rubric version, scores, trace ID, timestamp and data-access context.
