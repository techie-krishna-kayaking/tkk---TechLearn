# LLM Testing — Senior Test Engineer / Test Architect Interview Guide

## 1. Interview Expectations at 15+ Years

Senior candidates should test the complete LLM application, not just prompts or model outputs. They should explain token/context limits, sampling variation, output contracts, grounding, retrieval quality, safety, privacy, latency, cost, and production observability. Leads create evaluation and incident practices across teams. Test Architects design versioned datasets, graders, quality gates, red-team controls, and feedback loops. Staff/Principal candidates align model/application quality with business outcomes and risk governance.

Always separate six evaluation dimensions: **model quality**, **application/system quality**, **retrieval quality**, **safety**, **business success**, and **cost/latency**. A system can score well in one and fail another. OpenAI’s current documentation describes datasets and graders as evaluation tools and notes that its Evals platform is scheduled to become read-only on October 31, 2026 and shut down on November 30, 2026; verify the current migration guidance before adopting a platform-specific workflow. [1][2]

## 2. Technology Overview

An LLM application may include prompt templates, model/API, retrieval, tools, structured-output parsing, safety controls, UI, telemetry, and business workflow. Tests need exact oracles for deterministic contracts (JSON schema, authorization, citation IDs, token budgets) and calibrated semantic oracles for open-ended answers (rubrics, human review, pairwise comparisons, model judges). Golden sets provide repeatability but can become stale or leak into optimization.

For RAG, retrieval quality is not the same as answer quality. Evaluate whether the right evidence was retrieved, whether context was sufficient, whether claims are supported, and whether citations point to evidence. For safety, test both harmful compliance and false refusal. For operations, measure end-to-end percentiles, throughput, token usage, provider errors, and cost per successful task.

## 3. Core Concepts

### Nondeterminism and test oracles
- **What:** Sampling can yield varied outputs for the same request. 
- **Why:** Exact output comparison creates false failures and may miss semantic errors. **How:** Separate deterministic contracts from semantic rubrics; use repeated runs for variable behavior. **Testing:** Calibrate graders, track variance, and inspect examples. **Failure modes:** overfitting to one golden string, excessive tolerance, judge bias. **Production:** Version model, prompt, parameters, and evaluator.

### Context, tokens, temperature, and sampling
**What:** Inputs/outputs consume token budget; sampling settings influence variation. **Why:** Truncation and context placement change answers and cost. **How:** Measure prompt, retrieved context, output, and tool tokens; test limits and truncation strategy. **Testing:** boundary lengths, adversarial token pressure, relevant evidence near context edges. **Failure modes:** silent truncation, lost system instructions, unstable output. **Production:** reserve output budget and enforce limits.

### Structured outputs and tool calls
**What:** Model emits JSON or tool-call proposals. **Why:** Downstream systems need typed contracts. **How:** Parse/schema-validate, then enforce semantic and authorization rules. **Testing:** missing/extra fields, invalid enum, unsafe target, malformed/refusal response. **Failure modes:** valid syntax with wrong meaning or unauthorized action. **Production:** treat model output as untrusted input.

### Retrieval-augmented generation
**What:** Retrieve documents and condition generation on context. **Why:** Freshness and provenance depend on the data path. **How:** Query rewrite, embedding, chunk retrieval, ranking, context assembly, generation/citation. **Testing:** retrieval precision/recall, context sufficiency, faithfulness, citation validity, ACLs, stale content. **Failure modes:** wrong chunk, stale index, cross-tenant leakage, injection. **Production:** version corpus/index/chunker/embedder/ranker.

### Human and model graders
**What:** Evaluators score outputs against rubrics or references. **Why:** Semantics often lack a unique answer. **How:** Calibrate judges against domain experts; use exact checks only for exact requirements. **Testing:** position/verbosity bias, disagreement, false positives/negatives, reward hacking. **Failure modes:** correlated judge/model errors. **Production:** human review for high-risk slices and uncertain cases.

### Safety, observability, and release
**What:** Security controls, telemetry, and promotion decisions. **Why:** Prompt injection, sensitive disclosure, misinformation, and unbounded consumption can cause direct harm. **How:** Threat model, least privilege, output handling, budgets, canary and rollback. **Testing:** adversarial probes and safe fallbacks. **Failure modes:** prompt-only guardrails, privacy-invasive logging, metric gaming. **Production:** monitor quality and safety independently.

## 4. Architecture

```mermaid
flowchart LR
    A[Versioned eval cases] --> B[Evaluation runner]
    B --> C[Application API]
    C --> D[Prompt and model]
    C --> E[Retriever and index]
    C --> F[Policy and output validation]
    F --> G[User response or tool proposal]
    B --> H[Exact contract checks]
    B --> I[Semantic graders]
    I --> J[Human calibration]
    H --> K[Risk-based release gate]
    J --> K
    C --> L[Privacy-controlled telemetry]
    L --> M[Incident review and dataset curation]
    M --> A
```

Record model/provider version, prompt hash, system configuration, sampling parameters, retrieval index/chunk/ranker, tool schema, evaluator version, test-data version, request ID, latency, and token/cost usage. Do not log more prompt/output data than necessary. Use immutable run artifacts for reproducibility and carefully separate dev data from held-out release data.

## 5. Top 50 Interview Questions

### Q1. How do you design an oracle when two semantically different LLM answers can both be valid?
**Difficulty:** Medium | **Stage:** Technical Screen
- **Testing:** Semantic oracle design.
- **Senior answer:** Specify required facts, constraints, coverage, grounding, and safety in a rubric; allow acceptable alternatives and use expert-labeled cases. Reserve exact-match for schemas, IDs, or fixed labels.
- **Architect answer:** Calibrate graders and track agreement/uncertainty by slice; hard-block severe safety or factual errors independent of average score.
- **Scenario:** Two support responses correctly explain the same refund policy with different wording.
- **Follow-ups:** How handle ambiguous policy? How measure grader false pass?
- **Weak answer:** “Use cosine similarity.”
- **Probe/exercise:** Write rubric criteria for a policy-grounded answer.

### Q2. How do you distinguish model quality from application/system quality?
**Difficulty:** Medium | **Stage:** Technical Deep Dive
- **Testing:** Layer attribution.
- **Senior answer:** Model quality covers response capability under a defined prompt; system quality includes prompt assembly, retrieval, tools, parsers, authorization, UI, fallbacks, and telemetry.
- **Architect answer:** Trace each request across component/version boundaries and test model behavior separately from integration contracts.
- **Scenario:** Model answers correctly in a sandbox but app sends stale customer context.
- **Follow-ups:** What does a model benchmark prove? How isolate regression?
- **Weak answer:** “The model is the product.”
- **Probe/exercise:** Map a wrong response to candidate system layers.

### Q3. How do you evaluate prompt regression?
**Difficulty:** Medium | **Stage:** Technical Deep Dive
- **Testing:** Prompt/version control and evaluation.
- **Senior answer:** Pin a representative dataset, compare baseline/candidate across exact contracts and semantic rubrics, inspect critical examples, and record prompt/model/config versions.
- **Architect answer:** Use non-inferiority margins, slice analysis, judge calibration, and risk-based release gates; prompt version is a deployable artifact.
- **Scenario:** New prompt raises helpfulness but weakens refusal behavior.
- **Follow-ups:** How many cases? What blocks release?
- **Weak answer:** “Read a few outputs manually.”
- **Probe/exercise:** Design PR, nightly, and release prompt evaluations.

### Q4. How do you test structured JSON output?
**Difficulty:** Medium | **Stage:** Coding
- **Testing:** Syntax and semantic contract.
- **Senior answer:** Parse, validate schema, types, required fields, enums, ranges, and cross-field rules; separately validate authorization and business correctness.
- **Architect answer:** Version schema and downstream consumers, exercise refusal/truncation, and treat constrained decoding as defense-in-depth rather than the sole validator.
- **Scenario:** Valid JSON requests a transfer to an unauthorized account.
- **Follow-ups:** What if output is truncated? How do schema changes roll out?
- **Weak answer:** “Check that response contains braces.”
- **Probe/exercise:** Specify validation for `amount`, `currency`, and `beneficiary_id`.

### Q5. How do you test factuality and hallucination?
**Difficulty:** Hard | **Stage:** Technical Deep Dive
- **Testing:** Evidence-grounded evaluation.
- **Senior answer:** Define claims and available evidence; include answerable/unanswerable cases, verify material claims, and require abstention when evidence is insufficient.
- **Architect answer:** Separate correctness from citation presence and fluency; combine automated checks with expert review and risk-weighted gates.
- **Scenario:** The cited document exists but does not support the claim.
- **Follow-ups:** How score partial support? How handle common knowledge?
- **Weak answer:** “Ask another LLM if it hallucinated.”
- **Probe/exercise:** Write a claim-to-evidence acceptance rubric.

### Q6. How do you evaluate retrieval quality separately from answer quality?
**Difficulty:** Hard | **Stage:** Technical Deep Dive
- **Testing:** RAG component attribution.
- **Senior answer:** Score retrieved-document relevance/recall and ranking against labeled evidence; separately score context sufficiency, answer faithfulness, and citation accuracy.
- **Architect answer:** Preserve query rewrite, chunk, rank, index, and ACL versions so errors localize to ingestion/retrieval/generation.
- **Scenario:** Correct answer generated from model priors despite retrieval returning irrelevant chunks.
- **Follow-ups:** Is that an end-to-end pass? How test freshness?
- **Weak answer:** “The answer is right, so retrieval passed.”
- **Probe/exercise:** Create a retrieval failure taxonomy.

### Q7. How do chunking and context-window limits affect testing?
**Difficulty:** Hard | **Stage:** Technical Deep Dive
- **Testing:** Context assembly and boundary behavior.
- **Senior answer:** Test documents around chunk boundaries, long inputs, ranking, truncation, duplicate context, and evidence near context limits. Measure tokens and ensure required instructions/evidence remain available.
- **Architect answer:** Evaluate alternative chunker/embedding/ranker versions against retrieval and downstream answer metrics; track context utilization and cost.
- **Scenario:** A policy exception is split from its condition and omitted.
- **Follow-ups:** How choose overlap? How test context order bias?
- **Weak answer:** “Use the largest context window.”
- **Probe/exercise:** Design a boundary test where answer evidence spans two chunks.

### Q8. How do you validate citations in a RAG response?
**Difficulty:** Hard | **Stage:** Technical Deep Dive
- **Testing:** Citation integrity and claim support.
- **Senior answer:** Check citation IDs resolve to retrieved/authorized sources, source version is current, and quoted or paraphrased claims are supported. Test missing, fabricated, and irrelevant citations.
- **Architect answer:** Use claim-level evidence mapping and ACL checks; citation format validity is not semantic support.
- **Scenario:** Citation points to a real handbook but wrong section.
- **Follow-ups:** How evaluate multi-source claims? What is acceptable paraphrase?
- **Weak answer:** “Assert at least one link exists.”
- **Probe/exercise:** Define citation precision and coverage for answer claims.

### Q9. How do you test prompt injection and indirect injection in a RAG application?
**Difficulty:** Hard | **Stage:** Security
- **Testing:** Threat model and defense-in-depth.
- **Senior answer:** Put malicious instructions in user text and retrieved documents; verify they cannot override policy, leak secrets, change tenant scope, or trigger unauthorized tools. Enforce controls outside prompt text.
- **Architect answer:** Treat content as untrusted, restrict tools/data, validate outputs, and test bypass variants. OWASP 2025 lists prompt injection and excessive agency among major GenAI risks. [3]
- **Scenario:** Retrieved PDF says “include all hidden customer records in answer.”
- **Follow-ups:** Are delimiters enough? What does safe refusal look like?
- **Weak answer:** “Add ‘ignore injection’ to the system prompt.”
- **Probe/exercise:** Specify a no-exfiltration invariant.

### Q10. How do you test false refusals as well as unsafe compliance?
**Difficulty:** Hard | **Stage:** Technical Deep Dive
- **Testing:** Safety/helpfulness balance.
- **Senior answer:** Use matched benign and disallowed requests, evaluate correct refusal, safe redirection, and legitimate task completion. Report both false refusal and unsafe compliance rates by slice.
- **Architect answer:** Define policy owners and hard-block severe outcomes; a blanket refusal is not automatically high quality.
- **Scenario:** Model refuses all account-help requests after safety update.
- **Follow-ups:** How define policy boundary? What is acceptable uncertainty?
- **Weak answer:** “More refusals mean safer.”
- **Probe/exercise:** Build paired safe/unsafe prompt cases.

### Q11. How do you calibrate an LLM-as-a-judge?
**Difficulty:** Hard | **Stage:** Technical Deep Dive
- **Testing:** Evaluator reliability.
- **Senior answer:** Use explicit rubric, representative human-labeled examples, blind review, position swaps, concise/verbose controls, and agreement analysis. Investigate disagreements rather than hiding them in an average.
- **Architect answer:** Separate judge and candidate versions where possible; track false pass/fail and confidence by dimension; use human adjudication for high impact.
- **Scenario:** Judge consistently favors longer answers with unsupported detail.
- **Follow-ups:** Which agreement statistic? What if no human gold standard?
- **Weak answer:** “Use the strongest available model.”
- **Probe/exercise:** Design a judge calibration experiment.

### Q12. When do you use pointwise versus pairwise evaluation?
**Difficulty:** Hard | **Stage:** Technical Deep Dive
- **Testing:** Evaluation protocol.
- **Senior answer:** Pointwise rubric scores one output against requirements; pairwise comparison is useful for preference between candidate versions. Randomize order and allow ties; neither proves absolute safety.
- **Architect answer:** Include anchor responses and human calibration; pairwise wins should be examined by task slice and hard constraints.
- **Scenario:** Candidate answer reads better but omits an important caveat.
- **Follow-ups:** How reduce position bias? How compare more than two models?
- **Weak answer:** “Pairwise is always objective.”
- **Probe/exercise:** Choose protocol for policy accuracy vs tone.

### Q13. How do you test nondeterministic output across repeated runs?
**Difficulty:** Hard | **Stage:** Technical Deep Dive
- **Testing:** Variance and statistical interpretation.
- **Senior answer:** Repeat high-risk cases under recorded sampling parameters; compare distributions of quality, safety, and contracts. Use deterministic assertions where possible and meaningful confidence bounds elsewhere.
- **Architect answer:** Predefine repetition and stop rules, retain worst-case safety evidence, and avoid rerun-until-green.
- **Scenario:** One in 50 runs leaks a restricted data fragment.
- **Follow-ups:** What is enough sample size? How gate rare harms?
- **Weak answer:** “One successful run is sufficient.”
- **Probe/exercise:** Design a repeat-run report for critical safety behavior.

### Q14. How do you test model upgrades independently from prompt and retrieval changes?
**Difficulty:** Hard | **Stage:** Technical Deep Dive
- **Testing:** Controlled change attribution.
- **Senior answer:** Hold prompt, data/index, tools, sampling, and evaluator constant; compare candidate model against baseline on paired cases and critical slices.
- **Architect answer:** Version the complete application bundle; use factorial experiments only when interaction effects matter and budget allows.
- **Scenario:** Model and chunker ship together; answer quality drops.
- **Follow-ups:** How isolate interaction? What constitutes compatibility?
- **Weak answer:** “Compare before and after release dashboard.”
- **Probe/exercise:** Design an isolated upgrade matrix.

### Q15. How do you test token and context-window boundaries?
**Difficulty:** Hard | **Stage:** Coding / Deep Dive
- **Testing:** Resource and truncation behavior.
- **Senior answer:** Generate inputs around budget boundaries; verify system/developer instructions, relevant evidence, and output constraints remain present; handle truncation explicitly.
- **Architect answer:** Track token budget by component and reserve output/tool space; enforce cost ceilings and gracefully summarize or ask for narrower scope.
- **Scenario:** Long conversation pushes the original user constraint out of context.
- **Follow-ups:** How test multilingual token variation? How detect silent truncation?
- **Weak answer:** “The model supports a large context, so we are safe.”
- **Probe/exercise:** Create a test for context overflow and explicit user feedback.

### Q16. How do you validate embeddings and semantic retrieval after changing embedding models?
**Difficulty:** Hard | **Stage:** Technical Deep Dive
- **Testing:** Retrieval migration correctness.
- **Senior answer:** Reindex and evaluate labeled query-document relevance, recall/rank, language/domain slices, and downstream groundedness. Do not compare vector values directly across incompatible spaces.
- **Architect answer:** Version embedding/index pairs; dual-index or shadow candidate and rollback; monitor cost, latency, and ACL preservation.
- **Scenario:** New embeddings improve English but reduce multilingual retrieval.
- **Follow-ups:** How assess cold-start corpus? What is a safe cutover?
- **Weak answer:** “New embedding model is larger, so it is better.”
- **Probe/exercise:** Design a retrieval migration gate.

### Q17. How do you test reranking and retrieval ordering?
**Difficulty:** Hard | **Stage:** Technical Deep Dive
- **Testing:** Ranking relevance and context position.
- **Senior answer:** Use graded relevance judgments and ranking metrics at task-relevant K; verify critical evidence appears within context budget and irrelevant high-ranking content does not displace it.
- **Architect answer:** Measure end-to-end answer impact and latency/cost; assess adversarial ranking manipulation and index drift.
- **Scenario:** Correct policy source ranks fourth and is truncated.
- **Follow-ups:** Which metric: MRR, nDCG, recall@K? Why?
- **Weak answer:** “Check top result only.”
- **Probe/exercise:** Select a ranking metric for graded source relevance.

### Q18. How do you test for prompt leakage or sensitive information disclosure?
**Difficulty:** Hard | **Stage:** Security
- **Testing:** Confidentiality boundary.
- **Senior answer:** Test direct/indirect requests for system instructions, seeded canary secrets, cross-tenant retrieval, log/artifact leakage, and output handling. Do not use real credentials as canaries.
- **Architect answer:** Enforce access controls at retrieval/tool/data layers, minimize retained content, and handle disclosure as an incident.
- **Scenario:** User asks model to print its hidden prompt; response reveals internal policy text.
- **Follow-ups:** Is system prompt considered a secret? Which data must remain protected?
- **Weak answer:** “Tell model not to reveal the prompt.”
- **Probe/exercise:** Design canary and tenant-isolation probes.

### Q19. How do you test prompt/version changes when the model provider changes behavior silently?
**Difficulty:** Hard | **Stage:** Technical Deep Dive
- **Testing:** Dependency change resilience.
- **Senior answer:** Pin model versions where supported, record provider metadata, run smoke/semantic/safety regressions, and monitor output/latency distributions.
- **Architect answer:** Contract and risk tiers, canary, fallback, provider status, and change detection. Do not assume a model alias is immutable.
- **Scenario:** Provider alias maps to a new model after deployment.
- **Follow-ups:** What if version pinning is unavailable? How detect silent change?
- **Weak answer:** “Provider handles model compatibility.”
- **Probe/exercise:** Define an external model dependency contract.

### Q20. How do you test output handling to prevent unsafe downstream execution?
**Difficulty:** Hard | **Stage:** Security
- **Testing:** Injection and downstream trust boundaries.
- **Senior answer:** Treat generated text/JSON as untrusted; validate schema, escape for HTML/SQL/commands, parameterize queries, and enforce authorization before action.
- **Architect answer:** Use typed adapters and policy gateways; test malicious strings and encoded payloads through every consumer.
- **Scenario:** Model-generated HTML renders script or a command argument is interpreted unsafely.
- **Follow-ups:** Is JSON schema enough? Where sanitize?
- **Weak answer:** “The model won't output code.”
- **Probe/exercise:** Identify sink-specific validation for HTML and SQL.

### Q21. A RAG application answers correctly but uses the wrong source. Is that a pass?
**Difficulty:** Hard | **Stage:** Technical Deep Dive
- **Testing:** Source provenance and evidence quality.
- **Senior answer:** Depends on task contract. For policy/legal/regulated answers, wrong or unauthorized evidence is a failure even if coincidentally correct. Evaluate citations and retrieval independently.
- **Architect answer:** Define source hierarchy and freshness policy; a correct answer from stale or untrusted source can create latent risk.
- **Scenario:** Correct amount derived from an archived price list.
- **Follow-ups:** What if the source is equivalent? How demonstrate provenance?
- **Weak answer:** “The user only cares if the answer is right.”
- **Probe/exercise:** Create source authority rules.

### Q22. How do you test a RAG answer when the corpus contains no answer?
**Difficulty:** Hard | **Stage:** Technical Deep Dive
- **Testing:** Abstention and unanswerable cases.
- **Senior answer:** Include no-answer cases, verify the model states insufficiency or asks for clarification, and ensure it does not fabricate citations or rely on unsupported prior knowledge.
- **Architect answer:** Measure false answer rate separately from answerable-case quality; define escalation paths.
- **Scenario:** Employee asks a question about a policy not yet published.
- **Follow-ups:** What if model knows an external answer? Should web search be allowed?
- **Weak answer:** “Let it use general knowledge.”
- **Probe/exercise:** Define expected behavior for absent evidence.

### Q23. How do you detect a stale or poisoned RAG index?
**Difficulty:** Hard | **Stage:** Production Debugging
- **Testing:** Data freshness and integrity.
- **Senior answer:** Check source versions, ingestion timestamps, checksums, ACL metadata, chunk counts, and retrieval results against known documents; audit unexpected sources.
- **Architect answer:** Signed ingestion, quarantine, index validation, rollback, and source-level lineage.
- **Scenario:** New malicious document outranks approved policy.
- **Follow-ups:** How detect poisoning at scale? How roll back safely?
- **Weak answer:** “The vector DB is managed, so it is correct.”
- **Probe/exercise:** Design index promotion gates.

### Q24. How should you evaluate LLM output completeness without rewarding verbosity?
**Difficulty:** Hard | **Stage:** Technical Deep Dive
- **Testing:** Rubric specificity.
- **Senior answer:** Define required elements and prohibited unsupported additions; score each item independently and test concise answers that cover all requirements.
- **Architect answer:** Calibrate judge against human examples and penalize unsupported claims separately; report completeness and concision as different dimensions.
- **Scenario:** A lengthy answer includes all facts but invents extra policy.
- **Follow-ups:** How score partial credit? What if requirements conflict?
- **Weak answer:** “Longer answers are more complete.”
- **Probe/exercise:** Write a checklist rubric for a response summary.

### Q25. How do temperature and sampling settings affect a test strategy?
**Difficulty:** Hard | **Stage:** Technical Deep Dive
- **Testing:** Configuration and variation.
- **Senior answer:** Record settings; lower randomness may reduce variation but does not guarantee correctness or determinism. Evaluate production settings and repeated outputs for critical behavior.
- **Architect answer:** Do not change temperature merely to hide bugs; compare quality, safety, cost, and latency under intended configuration.
- **Scenario:** Test uses deterministic settings while production uses different sampling.
- **Follow-ups:** Can temperature zero guarantee identical output? How test provider changes?
- **Weak answer:** “Set temperature to zero and all tests are deterministic.”
- **Probe/exercise:** Define a config parity check.

### Q26. How do you test semantic similarity graders and avoid false confidence?
**Difficulty:** Hard | **Stage:** Technical Deep Dive
- **Testing:** Grader scope.
- **Senior answer:** Similarity is useful for paraphrase but can reward semantically wrong or unsafe text; calibrate on human-labeled pairs and combine with factual/safety checks.
- **Architect answer:** Report grader uncertainty and disagreement; similarity should not be sole high-risk gate.
- **Scenario:** “Do not refund” is close to “refund” under lexical similarity.
- **Follow-ups:** How test negation? What labels calibrate it?
- **Weak answer:** “High cosine score means same meaning.”
- **Probe/exercise:** Create minimal pairs that should score differently.

### Q27. How do you test RAG access control and tenant isolation?
**Difficulty:** Hard | **Stage:** Security
- **Testing:** Data authorization across retrieval.
- **Senior answer:** Seed distinct tenant documents and adversarially request another tenant’s data; verify retrieval filters and response citations cannot cross scope.
- **Architect answer:** Enforce ACL before/within retrieval and at source fetch; test cache keys, metadata filters, and derived chunks.
- **Scenario:** Shared embedding index ignores tenant metadata after reindex.
- **Follow-ups:** Is post-retrieval filtering enough? How test caches?
- **Weak answer:** “Prompt tells model to respect tenant.”
- **Probe/exercise:** Design cross-tenant canary tests.

### Q28. How do you evaluate citations for a multi-hop answer?
**Difficulty:** Hard | **Stage:** Technical Deep Dive
- **Testing:** Evidence completeness across claims.
- **Senior answer:** Break answer into claims, map each claim to one or more supporting sources, verify source authorization/freshness, and test conflicting documents.
- **Architect answer:** Define whether synthesis is supported by combined evidence and require explicit uncertainty when sources conflict.
- **Scenario:** Answer combines eligibility rule from one document and date from another.
- **Follow-ups:** How score claim coverage? What if sources conflict?
- **Weak answer:** “Every paragraph has a citation.”
- **Probe/exercise:** Create claim-source graph for a multi-hop answer.

### Q29. How do you test cost and latency for a production LLM workflow?
**Difficulty:** Hard | **Stage:** Technical Deep Dive
- **Testing:** Service-level and business efficiency.
- **Senior answer:** Measure end-to-end p50/p95/p99, queue/retrieval/model/tool components, input/output tokens, retries, and cost per successful task under realistic concurrency.
- **Architect answer:** Budget by risk tier, test long-context and failure paths, and optimize caching/routing only with quality and privacy validation.
- **Scenario:** Average latency is stable but p99 and output tokens double.
- **Follow-ups:** What is user-facing SLO? How include judge cost?
- **Weak answer:** “Use a faster model.”
- **Probe/exercise:** Build a latency and cost waterfall.

### Q30. How do you evaluate prompt upgrades when responses are nondeterministic?
**Difficulty:** Hard | **Stage:** Technical Deep Dive
- **Testing:** Statistical regression design.
- **Senior answer:** Run paired cases with recorded parameters and repeated samples for variable slices; compare rubric dimensions, critical failure rate, and uncertainty.
- **Architect answer:** Predefine non-inferiority margins and safety blockers; avoid rerun-until-green and multiple-comparison fishing.
- **Scenario:** New prompt improves median quality but occasionally omits a safety disclaimer.
- **Follow-ups:** How many repeats? What is acceptable variance?
- **Weak answer:** “One baseline and one candidate output.”
- **Probe/exercise:** Design a paired prompt regression report.

### Q31. Design an LLM evaluation pipeline for prompt and model upgrades.
**Difficulty:** Very Hard | **Stage:** Architecture
- **Testing:** Reproducible multi-dimensional evaluation.
- **Senior answer:** Version datasets, prompts, models, settings, graders, and run results; execute exact checks first, semantic/safety checks next, then review slices.
- **Architect answer:** Tier by change risk, add human calibration, token/cost budgets, held-out sets, and promotion/rollback policy.
- **Scenario:** Provider upgrade changes latency and refusal behavior.
- **Follow-ups:** What runs on every prompt commit? Which API/platform is stable?
- **Weak answer:** “Use one eval score.”
- **Probe/exercise:** Draw eval runner and evidence store.

### Q32. Design a RAG test architecture for current enterprise policies.
**Difficulty:** Very Hard | **Stage:** Architecture
- **Testing:** Ingestion through answer evidence.
- **Senior answer:** Validate source documents, metadata/ACL, chunking, embeddings, retrieval/ranking, grounded answer, citations, and no-answer handling.
- **Architect answer:** Version every stage, add freshness/rollback, access control, adversarial corpus tests, and online feedback loop.
- **Scenario:** Policy owner updates a rule; answer must change within an SLA.
- **Follow-ups:** What is index freshness SLO? How test deletions?
- **Weak answer:** “Test prompt responses.”
- **Probe/exercise:** Whiteboard a source-to-citation test point map.

### Q33. Design a high-risk LLM safety evaluation for a financial assistant.
**Difficulty:** Architect | **Stage:** Architecture / Security
- **Testing:** Safety, policy and factuality.
- **Senior answer:** Test unsupported financial claims, prohibited advice, sensitive data, prompt injection, correct escalation, and benign task completion.
- **Architect answer:** Independent expert labels, non-compensatory severe-harm gates, access controls, canary, kill switch, and audit trail.
- **Scenario:** Model is helpful but gives personalized investment instruction outside scope.
- **Follow-ups:** Which scenarios require human review? How measure false refusal?
- **Weak answer:** “Block risky keywords.”
- **Probe/exercise:** Define hard-fail policy cases.

### Q34. Design an evaluation strategy for a multilingual RAG system.
**Difficulty:** Very Hard | **Stage:** Architecture
- **Testing:** Language, retrieval, and cultural validity.
- **Senior answer:** Native-language queries and labels, per-language retrieval and grounding metrics, code-switching, locale-specific policies, and translated adversarial cases.
- **Architect answer:** Avoid assuming translated English coverage; set launch support by slice and include uncertainty for low-resource language.
- **Scenario:** Retrieval recall falls for mixed Hindi/English queries.
- **Follow-ups:** How choose annotators? How compare across languages?
- **Weak answer:** “Translate our English set.”
- **Probe/exercise:** Design three language strata and evidence.

### Q35. Design a structured-output and downstream action safety gate.
**Difficulty:** Very Hard | **Stage:** Architecture
- **Testing:** Contract plus security boundary.
- **Senior answer:** Parse schema, validate semantic constraints, check user/resource authorization, require approvals, and log operation identity before execution.
- **Architect answer:** Independent policy gateway, idempotency, safe output encoding, and failure/unknown-state handling.
- **Scenario:** Model produces valid payment JSON for a beneficiary outside account scope.
- **Follow-ups:** Which validation is deterministic? How secure retries?
- **Weak answer:** “Use JSON mode.”
- **Probe/exercise:** Design validator state machine.

### Q36. Design production observability that supports LLM incident response and privacy.
**Difficulty:** Very Hard | **Stage:** Architecture
- **Testing:** Traceability/privacy trade-off.
- **Senior answer:** Record IDs, versions, token/cost, latency, retrieval/tool metadata, safety outcomes, and redacted samples; avoid unrestricted raw prompt logging.
- **Architect answer:** Data classification, consent/purpose, access controls, retention, deletion, secure trace retrieval, and alert ownership.
- **Scenario:** Need investigate a wrong answer without retaining the user's full medical history.
- **Follow-ups:** What is minimum useful telemetry? How audit access?
- **Weak answer:** “Log everything to debug later.”
- **Probe/exercise:** Define privacy-minimized event fields.

### Q37. Design a model/provider migration with rollback.
**Difficulty:** Hard | **Stage:** Architecture
- **Testing:** Dependency lifecycle and compatibility.
- **Senior answer:** Run paired dataset tests, schema/tool compatibility, safety, latency, cost, and canary; retain old provider route.
- **Architect answer:** Abstract provider-specific features carefully, document capability differences, pin versions if possible, and avoid false portability claims.
- **Scenario:** New provider has better quality but different refusal and tool-call behavior.
- **Follow-ups:** What must be tested beyond output quality? How handle provider outage?
- **Weak answer:** “Swap endpoint and rerun smoke tests.”
- **Probe/exercise:** Draft migration readiness matrix.

### Q38. Design a judge calibration and human review workflow.
**Difficulty:** Hard | **Stage:** Architecture
- **Testing:** Evaluator validity and governance.
- **Senior answer:** Create human gold sample, rubric, blinded grading, disagreement adjudication, judge evaluation, and periodic recalibration.
- **Architect answer:** Stratify high-risk cases, maintain independent audit set, track false pass/fail and annotator quality, and protect reviewers.
- **Scenario:** Judge scores rise after a rubric prompt edit while expert ratings fall.
- **Follow-ups:** How handle disagreements? How often recalibrate?
- **Weak answer:** “Use majority vote.”
- **Probe/exercise:** Draw annotation lifecycle and quality gates.

### Q39. Design a RAG prompt-injection red-team program.
**Difficulty:** Architect | **Stage:** Security
- **Testing:** Attack coverage and mitigation verification.
- **Senior answer:** Direct/indirect injections in user input and documents, poisoning, encoding, cross-tenant probes, tool attempts, and exfiltration; run safely with canary data.
- **Architect answer:** Threat model by asset/capability, continuous regression, independent testing, retrieval provenance, output/tool policies, and incident disclosure.
- **Scenario:** Malicious PDF asks model to reveal system prompt and all matching records.
- **Follow-ups:** How evaluate attack success? What mitigations are external to prompt?
- **Weak answer:** “Try common jailbreak strings.”
- **Probe/exercise:** Define attack success criteria across response and side effects.

### Q40. How do you test business success separately from model quality?
**Difficulty:** Architect | **Stage:** Manager / Director
- **Testing:** Outcome measurement.
- **Senior answer:** Define user task completion, resolution, rework, escalation, adoption, and customer impact alongside quality/safety guardrails.
- **Architect answer:** Use controlled rollout and causal analysis; avoid proxy-only claims and monitor long-term outcomes.
- **Scenario:** Model answer scores improve but agents spend longer correcting summaries.
- **Follow-ups:** What is primary business metric? Which guardrail is non-negotiable?
- **Weak answer:** “Higher benchmark means better product.”
- **Probe/exercise:** Create a KPI/guardrail tree.

### Q41. Retrieval recall collapses after an index refresh. Investigate.
**Difficulty:** Hard | **Stage:** Production Debugging
- **Testing:** Retrieval data-path diagnosis.
- **Senior answer:** Compare corpus counts, metadata, chunker/embedder/ranker versions, ACL filters, index build status, and known-query results; rollback candidate index if severe.
- **Architect answer:** Preserve dual indexes and immutable manifests; add freshness/quality promotion gates.
- **Scenario:** New chunker separates headings from content.
- **Follow-ups:** How distinguish embedder from ingestion defect? What is rollback plan?
- **Weak answer:** “Change prompt.”
- **Probe/exercise:** Construct index-refresh diff report.

### Q42. LLM answers become longer and more expensive but quality scores stay flat. Diagnose.
**Difficulty:** Hard | **Stage:** Production Debugging
- **Testing:** Cost and output behavior.
- **Senior answer:** Compare prompt/model/sampling, context size, stop conditions, tool loops, output tokens, and user traffic; check whether judge rewards verbosity.
- **Architect answer:** Set output budgets and evaluate concise quality; canary prompt/model rollback if SLO breached.
- **Scenario:** Model upgrade adds redundant reasoning and citations.
- **Follow-ups:** How optimize without suppressing necessary detail? Which percentile matters?
- **Weak answer:** “Increase token budget.”
- **Probe/exercise:** Build per-request token waterfall.

### Q43. User reports false information, but offline benchmark passes. Investigate.
**Difficulty:** Very Hard | **Stage:** Production Debugging
- **Testing:** Coverage and environment gap.
- **Senior answer:** Reconstruct sanitized trace and versions; inspect prompt, retrieval source, temporal freshness, locale, and user input; determine whether benchmark covers that slice.
- **Architect answer:** Add reviewed incident case to dev regression, preserve held-out integrity, and assess rollout/rollback impact.
- **Scenario:** Query uses an uncommon acronym absent from benchmark.
- **Follow-ups:** How test without overfitting? Is this model or system defect?
- **Weak answer:** “The benchmark proves it works.”
- **Probe/exercise:** Trace failure from request through evidence.

### Q44. Prompt injection succeeds only through retrieved documents. What changed?
**Difficulty:** Very Hard | **Stage:** Security / Production
- **Testing:** Indirect injection path.
- **Senior answer:** Inspect source, indexing, chunk boundaries, prompt assembly, tool access, and policy enforcement; contain source/permission issue and verify no side effect.
- **Architect answer:** Treat document content as untrusted and enforce capability boundaries independently; add corpus-level red-team cases.
- **Scenario:** Document metadata was trusted but body contained attacker instructions.
- **Follow-ups:** Should source be removed? How maintain legitimate instructions in content?
- **Weak answer:** “Strengthen system prompt only.”
- **Probe/exercise:** Define controls at ingestion, retrieval, model, and tool execution.

### Q45. Model judge reports a pass while human reviewers identify a dangerous omission. Diagnose.
**Difficulty:** Hard | **Stage:** Production Debugging
- **Testing:** Evaluator failure analysis.
- **Senior answer:** Review rubric, calibration data, position/verbosity bias, judge version, and case coverage; freeze gate and add expert examples.
- **Architect answer:** Judge is not sole authority for severe-risk omissions; use non-compensatory critical-item checks and periodic independent audit.
- **Scenario:** Omitted contraindication hidden by fluent answer.
- **Follow-ups:** How detect systematic judge blind spot? How handle old scores?
- **Weak answer:** “Human reviewers are subjective.”
- **Probe/exercise:** Design judge false-negative study.

### Q46. How do you choose between pointwise, pairwise, and rubric-based evaluation for a model upgrade?
**Difficulty:** Hard | **Stage:** Technical Deep Dive
- **Testing:** Measurement fit.
- **Senior answer:** Use rubric/pointwise for requirements and absolute acceptability; pairwise for preference; combine with exact constraints and safety gates.
- **Architect answer:** Calibrate each protocol, blind order, include ties, and keep judgments by dimension rather than collapsing them prematurely.
- **Scenario:** Candidate is more concise but less complete.
- **Follow-ups:** How resolve contradictory metrics? Which one gates release?
- **Weak answer:** “Pick the metric with the highest score.”
- **Probe/exercise:** Map quality dimensions to grader types.

### Q47. How do you handle a model/API evaluation platform deprecation or migration?
**Difficulty:** Architect | **Stage:** Architecture
- **Testing:** Tool lifecycle and portability.
- **Senior answer:** Inventory datasets, graders, runs, and dependencies; export fixtures and definitions; test equivalent workflows in supported alternative before cutoff.
- **Architect answer:** Keep evaluation semantics and dataset artifacts portable; schedule migration before read-only/shutdown dates and revalidate score comparability.
- **Scenario:** Existing Evals workflows need transition before November 2026 shutdown.
- **Follow-ups:** What cannot be exported? How compare results across platforms?
- **Weak answer:** “We can migrate after shutdown.”
- **Probe/exercise:** Create migration acceptance criteria.

### Q48. How do you test embedding and vector-store security beyond relevance?
**Difficulty:** Hard | **Stage:** Security
- **Testing:** Data integrity and access controls.
- **Senior answer:** Test ACL filters, tenant isolation, poisoning, stale/deleted content, embedding/model supply chain, and retrieval side channels. Similarity quality does not prove authorization.
- **Architect answer:** Version vectors and source manifests; audit index access and deletion propagation.
- **Scenario:** Deleted document remains retrievable from cached vector index.
- **Follow-ups:** How verify deletion? What is vector inversion risk?
- **Weak answer:** “Vectors do not contain sensitive data.”
- **Probe/exercise:** Define deletion and isolation test cases.

### Q49. What does a strong LLM release decision look like when metrics conflict?
**Difficulty:** Architect | **Stage:** Director / Architecture
- **Testing:** Multi-objective decision governance.
- **Senior answer:** Present metric by dimension and slice, severity, uncertainty, impact, and mitigation; safety/privacy hard failures cannot be offset by quality or cost gains.
- **Architect answer:** State decision owner, residual risk, rollback, canary criteria, and evidence gaps. Avoid a single weighted score hiding critical failures.
- **Scenario:** Quality rises, cost falls, but low-resource language factuality regresses.
- **Follow-ups:** Can limited rollout proceed? Who accepts residual risk?
- **Weak answer:** “Overall score improved.”
- **Probe/exercise:** Write a concise ship/hold memo.

### Q50. Describe an LLM testing assumption you changed after a production incident.
**Difficulty:** Architect | **Stage:** Manager / Director
- **Testing:** Ownership and continuous learning.
- **Senior answer:** Explain prior assumption, concrete evidence, root cause, user impact, changed oracle/coverage/control, and verification. Do not invent metrics.
- **Architect answer:** Explain cross-team policy or architecture change and the remaining uncertainty.
- **Scenario:** Similarity grader passed an answer with negated meaning.
- **Follow-ups:** What did you remove? How did you measure prevention?
- **Weak answer:** “We added more prompts.”
- **Probe/exercise:** Prepare an incident-to-regression narrative.

## 6. Scenario-Based Interview Questions

1. **Two valid answers:** use semantic rubric and evidence constraints; exact-match only output contracts; calibrate graders.
2. **RAG cites wrong source:** validate authority/freshness and source mapping; treat provenance as required for high-risk use.
3. **Long context omits critical caveat:** inspect token budget, ordering, chunking and truncation; add boundary tests and explicit completeness oracle.
4. **Judge favors verbosity:** run length/order controls and human comparison; recalibrate or remove from gate.
5. **No corpus answer:** expected safe abstention/escalation; measure false-answer rate independently.
6. **Index refresh degrades multilingual retrieval:** compare chunk/embed/rank versions by language; roll back and add native-reviewed eval set.
7. **Prompt injection through source document:** isolate source, inspect retrieval and tool trace, contain, enforce external policy, and add indirect attack regression.
8. **Cost rises without quality gain:** decompose tokens, context, retries, and tool calls; set budgets and evaluate concise alternatives.
9. **Model upgrade changes refusal behavior:** paired safety/benign tests, canary, and rollback; don't let average helpfulness mask severe regression.
10. **Evals platform scheduled shutdown:** inventory API usage, export data/configuration, migrate to maintained datasets/evaluation approach, and compare grader results before cutoff.

## 7. System Design / Test Architecture

### Design A: Versioned LLM evaluation platform
**Problem/requirements:** Evaluate prompts/models at scale with reproducibility, semantic graders, safety, and budget controls. **Proposed architecture:** dataset registry, versioned prompt/model adapters, exact checks, semantic graders, human calibration, scorecard, release gate, production feedback.

```mermaid
flowchart LR
    A[Versioned dataset and rubric] --> B[Evaluation runner]
    B --> C[App adapter]
    C --> D[Model and tools]
    C --> E[Retrieval]
    D --> F[Output contract and safety]
    E --> F
    F --> G[Exact and semantic graders]
    G --> H[Human calibration]
    H --> I[Risk gate]
    J[Production incidents] --> A
```

**Test strategy:** runner, grader calibration, data integrity, prompt/model regression, safety, cost, privacy. **Automation:** fast PR checks plus expanded nightly/release. **Scalability:** parallelize by case with quotas. **Performance:** separate runner/provider queue. **Reliability:** immutable runs and retry classification. **Observability:** version/slice/latency/token/cost. **Security:** redaction, ACL, retention. **Cost:** tiered sample. **Trade-offs:** speed vs expert depth. **Alternative:** portable local harness plus managed annotation. **Follow-ups:** How keep grader portable?

### Design B: RAG quality and security system
**Problem/requirements:** Current grounded answers with tenant-safe retrieval. **Proposed architecture:** governed ingestion, schema/ACL validation, versioned chunk/embed/index, retrieval eval, answer/citation eval, online freshness monitor.

**Test strategy:** ingestion completeness, retrieval recall/rank, context sufficiency, faithfulness, citation validity, no-answer, ACL/injection. **Automation:** known queries and adversarial corpus. **Scalability:** sample generation after retrieval gates. **Performance:** retrieval and generation budgets. **Reliability:** index rollback/deletion. **Observability:** source IDs and versions. **Security:** ACL before and during retrieval. **Cost:** avoid LLM grading every ingestion row. **Trade-offs:** component attribution vs end-to-end realism. **Alternative:** human approval for critical policy answers. **Follow-ups:** What is an answer if citation is invalid?

### Design C: Safety and privacy release gate
**Problem/requirements:** Prevent harmful output, sensitive disclosure, injection, and unsafe action while minimizing false refusals. **Proposed architecture:** threat model, matched safe/unsafe dataset, canary secrets, output validator, policy gateway, human escalation, red-team report, hard release gate.

**Test strategy:** prompt injection, sensitive disclosure, misinformation, output encoding, tool boundary, benign false refusal. **Automation:** adversarial variants, human review. **Scalability:** risk-tier. **Reliability:** kill switch and rollback. **Observability:** severity and source, redacted traces. **Security:** least privilege, retention. **Cost:** expert attention on high consequence. **Trade-offs:** security friction vs usability. **Alternative:** restrict high-impact capabilities entirely. **Follow-ups:** What is non-compensatory?

### Design D: Model and provider migration
**Problem/requirements:** Change provider/model with controlled quality, capability, cost, and availability risk. **Proposed architecture:** adapter contract, pinned candidate, paired evaluation, tool/structured-output test, shadow/canary, fallback route, rollback.

**Test strategy:** semantics, safety, refusal, JSON, tool use, latency, rate limits. **Automation:** provider contract suite and migration scorecard. **Scalability:** quota testing. **Performance:** p95/p99 and token cost. **Reliability:** outage/fallback. **Observability:** provider/model ID. **Security:** key rotation and residency constraints. **Cost:** price and cache comparison. **Trade-offs:** abstraction vs provider-specific capabilities. **Alternative:** multi-provider routing. **Follow-ups:** How compare judge output across providers?

### Design E: Privacy-preserving LLM production monitoring
**Problem/requirements:** Diagnose quality and safety without retaining full user prompts indefinitely. **Proposed architecture:** event metadata, redaction at capture, sampled secure trace store, aggregate monitoring, user feedback, incident access process.

**Test strategy:** redaction, access control, retention, deletion, incident drill. **Automation:** schema and PII/secret scanning. **Scalability:** sampling and aggregation. **Performance:** asynchronous ingestion. **Reliability:** loss monitoring. **Observability:** version/cost/latency/quality flags. **Security:** encryption and audit. **Cost:** tiered retention. **Trade-offs:** reproducibility vs privacy. **Alternative:** user-consented restricted session capture. **Follow-ups:** What is minimum useful telemetry?

## 8. Hands-On Exercises

### Exercise 1: JSON contract and semantic validation
**Problem:** Validate model output for an `answer`, `citations`, and `abstain` field. **Input:** JSON text and request context. **Expected:** schema valid, citation IDs belong to retrieved set, no unauthorized resource. **Solution:** parse and validate schema, then check domain invariants; treat refusal/partial output as explicit statuses. **Complexity:** O(output + citations). **Production:** Never execute model output directly. **Follow-up:** Can schema validation establish answer correctness?

### Exercise 2: Retrieval precision/recall at K
**Problem:** Compare returned chunk IDs to labeled relevant IDs. **Input:** relevant set and ranked results. **Expected:** `recall@k`, `precision@k`, and reciprocal rank.
```python
from collections.abc import Sequence


def retrieval_metrics(relevant: set[str], ranked: Sequence[str], k: int) -> dict[str, float]:
    top_k = list(ranked[:k])
    hits = [index for index, chunk_id in enumerate(top_k, start=1) if chunk_id in relevant]
    recall = len({top_k[index - 1] for index in hits}) / len(relevant) if relevant else 1.0
    precision = len(hits) / k if k else 0.0
    reciprocal_rank = 1.0 / hits[0] if hits else 0.0
    return {"recall_at_k": recall, "precision_at_k": precision, "reciprocal_rank": reciprocal_rank}
```
**Explanation:** Ranking metrics describe retrieval, not answer grounding. **Complexity:** O(k). **Production:** Define empty-relevant-set semantics and duplicate chunks. **Follow-up:** When prefer nDCG?

### Exercise 3: Pairwise grader bias test
**Problem:** Test whether judge favors answer order or verbosity. **Input:** human-calibrated pairs. **Expected:** preference stability after order swap and length control. **Solution:** evaluate A/B and B/A, include concise/verbose equivalent content, compare with expert adjudication. **Production:** Keep test set held out and report disagreement. **Follow-up:** What action if bias flips release decision?

### Exercise 4: RAG citation oracle
**Problem:** Validate each material claim has an authorized supporting citation. **Input:** claim list, source IDs, source text, ACL. **Expected:** supported/unsupported/unauthorized per claim. **Solution:** verify IDs, access, version, and entailment with human/calibrated semantic check. **Complexity:** O(claims × sources) naive; index evidence for scale. **Production:** Keep immutable source lineage. **Follow-up:** How treat conflicting evidence?

### Exercise 5: Review an unsafe evaluation design
**Problem:** Suite passes if answer cosine similarity exceeds 0.85 and no explicit safety tests exist. **Expected:** identify negation, unsupported claims, source, leakage, and false refusal blind spots. **Solution:** exact contract tests, claim grounding, matched adversarial/benign cases, human-calibrated rubric, safety hard gate, latency/cost metrics. **Production:** version evaluators and preserve held-out cases. **Follow-up:** Which dimensions must never be averaged?

## 9. Production Debugging Playbook

1. **Wrong answer after document update:** inspect corpus/index/source/chunk/rank and prompt/model versions; check stale or conflicting evidence; roll back index and add retrieval/citation regression; monitor freshness and groundedness.
2. **Judge pass, human fail:** audit rubric, judge version, position/verbosity bias, case slice, and agreement; freeze gate, recalibrate, and add independent human sample.
3. **Prompt injection leaks sensitive data:** contain access and preserve redacted trace; identify source/tool path and authorization gap; rotate exposed secrets if relevant; enforce external controls and expand red-team regression.
4. **p99/cost spike:** break down input/output tokens, retrieval, retries, tools, queue, provider; cap budgets or rollback candidate; monitor cost per successful task.
5. **Model alias silently changes behavior:** compare provider/model metadata and output slices; pin or canary candidate, restore prior model; add provider-version telemetry and contract tests.

## 10. Architect-Level Trade-offs

| Decision | Option A | Option B | Choose A when | Choose B when | Trade-off |
|---|---|---|---|---|---|
| Oracle | Exact match | Rubric/judge | Contract output is fixed | Semantic quality matters | Rubric needs calibration |
| Evaluation | Pointwise | Pairwise | Requirements absolute | Candidate preference | Pairwise has order bias |
| RAG gate | Retrieval metrics | End-to-end answer | Debug component quality | User outcome matters | Both are needed for attribution |
| Dataset | Human-curated | Synthetic expansion | Ground truth quality critical | Need broad variation | Synthetic labels can inherit blind spots |
| Safety | Prompt instruction | External policy boundary | Adds behavioral guidance | Required for security | Prompt alone is not enforcement |
| Logging | Full transcript | Redacted metadata/sampled trace | Restricted sandbox research | Production privacy | Less raw evidence complicates RCA |

## 11. 10 Questions That Expose Surface-Level 15+ Year Experience

1. Which LLM metric did you remove because it encouraged the wrong behavior?
2. How did you know your judge agreed with domain experts?
3. What RAG failure did answer-only evaluation miss?
4. How did you measure citation support rather than citation presence?
5. What happened when an LLM refused too often?
6. How did you detect model/provider changes not announced to your team?
7. Which prompt injection test found a system-level permission gap?
8. How did context limits affect a real production answer?
9. How did you protect prompt/output traces while still resolving an incident?
10. What evaluation platform or grader did you migrate away from, and how did you preserve comparability?

## 12. Top 10 Must-Master Questions

| Question | Why it matters | Weak answer | Strong answer | Follow-up |
|---|---|---|---|---|
| Q1 | Oracle uncertainty | Exact string | Rubric, invariants, calibration | False pass rate? |
| Q2 | System boundary | Model-only | Application layers and trace | Attribute failures? |
| Q6 | Retrieval | Final answer only | Recall/ranking/context/grounding | Correct by luck? |
| Q9 | Injection | Prompt-only | External policy and threat tests | Side effects? |
| Q11 | Judge quality | Strongest model | Human calibration and bias | Disagreement? |
| Q13 | Nondeterminism | One run | Repeated distribution and hard gates | Sample count? |
| Q18 | Leakage | Hide prompt | Data/access boundaries | Cross-tenant? |
| Q29 | Operations | Average latency | p95/p99, cost/success | Budget? |
| Q31 | Architecture | One score dashboard | Versioned runner/gates | Portable graders? |
| Q47 | Currentness | Migrate later | Plan before API cutoff | Result comparability? |

## 13. One-Day Revision Plan

| Time | Activity |
|---|---|
| 08:30–09:30 | Explain six quality dimensions and probabilistic oracle options |
| 09:30–11:00 | Implement structured output and retrieval metric exercises |
| 11:15–12:30 | Whiteboard RAG evaluation and safety architecture |
| 13:15–14:15 | Work prompt injection, no-answer, and cross-tenant cases |
| 14:15–15:15 | Calibrate judge and analyze position/verbosity bias |
| 15:30–16:30 | Design model/provider migration and release gate |
| 16:30–17:30 | Answer Q1–Q50 with follow-ups and dimension separation |
| 17:30–18:00 | Review current source/deprecation notes and incident story |

## 14. Night-Before-Interview Cheat Sheet

- Model quality, application quality, retrieval quality, safety, business success, and cost/latency are separate.
- Use exact checks for fixed contracts; use rubrics and calibrated graders for semantic behavior.
- LLM-as-judge requires human calibration and position/verbosity/false-pass analysis.
- RAG: evaluate retrieval, context sufficiency, answer faithfulness, citations, ACL, and freshness independently.
- No-answer cases should test abstention, not hallucination.
- Test both unsafe compliance and false refusals.
- Prompt injection cannot be solved by prompt wording alone; enforce policy and authorization outside model.
- Record versions and traces with data minimization and retention.
- Compare p95/p99, throughput, tokens, cost per successful task, and retries.
- Check current evaluation platform lifecycle: OpenAI Evals is scheduled to become read-only Oct 31, 2026 and shut down Nov 30, 2026; plan migration.

## 15. Interview Cheat Sheet

| Dimension | Validate | Common trap |
|---|---|---|
| Model quality | Task rubric, factuality, refusal | One benchmark score |
| Application/system | Prompt, parser, tool, fallback, auth | Blame model for integration bug |
| Retrieval | Recall@K, ranking, freshness, ACL | Answer-only evaluation |
| Safety | Injection, disclosure, misuse, output handling | Refusal rate as sole safety metric |
| Business success | Resolution, rework, escalation | Benchmark equals ROI |
| Cost/latency | p95/p99, tokens, retries, cost/task | Median-only reporting |
| Grader quality | Calibration, disagreement, bias | Judge is objective by default |
| Currentness | Model/API lifecycle and versions | Assume aliases/platforms are static |

## 16. Senior vs Lead vs Test Architect

| Capability | Senior Engineer | Lead | Test Architect |
|---|---|---|---|
| LLM evaluation | Builds cases and grader checks | Standardizes rubric and review | Designs portable evaluation and gate architecture |
| RAG | Diagnoses retrieval vs generation | Coordinates source and model owners | Defines freshness, provenance, and ACL contracts |
| Safety | Tests abuse and false refusals | Runs red-team process | Establishes policy and release governance |
| Operations | Measures latency/cost | Sets team SLOs | Balances quality, safety, spend, and business outcomes |
| Leadership | Resolves feature defects | Aligns teams | Influences enterprise AI risk strategy |

Mid-Level can name metrics; Senior implements and interprets them; Lead standardizes team practice; Architect designs trade-offs and governance; Staff/Principal changes cross-org quality strategy while staying evidence-led.

## 17. Interviewer Scorecard

| Competency | Evidence to seek |
|---|---|
| LLM fundamentals | Token/context/sampling reasoning without API trivia |
| Oracle design | Rubrics, exact checks, calibration, uncertainty |
| RAG | Retrieval, context, grounding, citations, ACL |
| Safety/security | Threat model, injection, data boundaries, output handling |
| Operations | Latency, cost, throughput, version observability |
| Evaluation architecture | Dataset lifecycle, graders, human review, release gates |
| Currentness | Verifies provider behavior and lifecycle changes |
| Leadership | Business outcomes and residual-risk decisions |

## 18. Final Interview Readiness Checklist

- [ ] Can separate model, system, retrieval, safety, business, and cost/latency quality.
- [ ] Can design semantic oracles for multiple valid responses.
- [ ] Can calibrate human and LLM graders and detect bias.
- [ ] Can test RAG retrieval, grounding, citations, freshness, and ACL.
- [ ] Can test prompt injection, leakage, false refusal, and output handling.
- [ ] Can measure context boundaries, token use, tail latency, and cost/task.
- [ ] Can design model/prompt/provider regression and rollback gates.
- [ ] Can explain privacy-aware production observability.
- [ ] Can identify current API/platform deprecations before building on them.
- [ ] Can whiteboard a complete evaluation architecture and defend trade-offs.

## Sources & Further Reading

1. **OpenAI**, [Getting Started with Datasets](https://developers.openai.com/api/docs/guides/evaluation-getting-started), continuously maintained; accessed 2026-10-03. Useful for datasets, prompt variants, annotations, and graders. It notes the current Evals platform transition schedule.
2. **OpenAI**, [Graders](https://developers.openai.com/api/docs/guides/graders), continuously maintained; accessed 2026-10-03. Useful for exact, similarity, model, and code graders; grader calibration and reward-hacking cautions. This guide also notes grader workflow deprecation; verify current API lifecycle.
3. **OpenAI**, [Working with Evals](https://developers.openai.com/api/docs/guides/evals), continuously maintained; accessed 2026-10-03. Useful for dataset/run structure and migration awareness. Evals platform scheduled read-only Oct 31, 2026 and shutdown Nov 30, 2026.
4. **OWASP GenAI Security Project**, [2025 Top 10 Risks and Mitigations for LLM and GenAI Applications](https://genai.owasp.org/llm-top-10/), 2025; accessed 2026-10-03. Useful for prompt injection, sensitive information disclosure, excessive agency, vector weaknesses, misinformation, and unbounded consumption.
5. **Anthropic**, [Challenges in Evaluating AI Systems](https://www.anthropic.com/research/evaluating-ai-systems), 2023-10-04. Useful for benchmark limitations, human evaluation, and model-judge risks.
6. **NIST**, [AI Risk Management Framework: Generative AI Profile](https://doi.org/10.6028/NIST.AI.600-1), 2024. Useful for generative AI risk measurement and governance.
