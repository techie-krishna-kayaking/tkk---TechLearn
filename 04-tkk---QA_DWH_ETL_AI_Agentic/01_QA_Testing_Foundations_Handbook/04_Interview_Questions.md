# QA Foundations — Interview Questions & Model Answers

## 1. How do you create a test strategy for an unfamiliar system?

Start with outcome, users, SUT boundary, dependencies, data classification, scale/SLOs and failure cost. Map the flow, rank risks by impact/likelihood/detectability, then define test levels, data, oracles, automation, environments, evidence, entry/exit criteria and production monitoring. I finish with owner and waiver/rollback rules.

## 2. What makes a test case “good”?

It is traceable to a risk/requirement, uses controlled data and preconditions, has unambiguous steps, names a trusted oracle, produces reproducible evidence and says whether it should be automated. A list of clicks without an expected business result is not a test case.

## 3. How do you decide what not to test?

I do not silently omit it. I record residual risk, explain impact/likelihood and propose the lowest-cost control: sample, monitor, contract check, deferral or explicit acceptance by the risk owner. Coverage is prioritized, not accidental.

## 4. What is the difference between severity and priority?

Severity is technical/business impact; priority is urgency/order for resolution. A cosmetic issue can be high priority before a customer demo; a critical but isolated historical defect can be managed differently while containment is active. State both with evidence.

## 5. How do you handle an unclear requirement?

Turn ambiguity into examples, decision tables and acceptance questions. For data, clarify grain, source of truth, cut-off, null/default semantics, history and tolerance. For AI, agree evaluation rubric, prohibited outcomes and escalation behavior before testing.

## 6. What causes flaky tests?

Shared state, clocks/time zones, nondeterministic data/order, async timing, unstable dependencies, environment drift, random model behavior and weak assertions. Fix the cause; do not normalize reruns. If temporary quarantine is necessary, name an owner, expiry and compensating monitor.

## 7. How do you measure QA effectiveness?

Critical-risk coverage, escaped defects by severity, detection lead time, MTTD/MTTR, defect recurrence, quality-gate reliability, test-signal noise, automation feedback time and business-data quality outcomes. Raw test count is a weak metric.
