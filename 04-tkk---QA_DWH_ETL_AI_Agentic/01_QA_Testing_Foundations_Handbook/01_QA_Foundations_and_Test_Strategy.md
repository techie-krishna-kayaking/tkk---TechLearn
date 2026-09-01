# 01 — QA & Testing Foundations Handbook

> A senior Data/AI QA engineer does not begin with tools or test cases. They establish the **system under test (SUT)**, business risk, quality attributes, evidence model and release decision. This handbook treats testing as risk reduction, not checkbox execution.

---

## 🎯 Section 1: The QA role around data and AI systems

Your job is to create confidence in a system built by data, platform, application and AI teams. You own the quality approach around it:

```text
Understand SUT → identify risk → design tests → prepare data → execute/automate
       → investigate evidence → decide PASS / FAIL / BLOCK → monitor production
```

The core question is always: **How can this system produce an unacceptable outcome, and how will we detect or prevent it?**

### What “quality” means here

| Attribute | Data / AI example | QA evidence |
|---|---|---|
| Correctness | revenue is calculated at the right grain | record and aggregate reconciliation |
| Completeness | all expected source records arrive | key coverage / missing-record report |
| Timeliness | dashboard refreshes by 08:00 | freshness SLI and run history |
| Safety | agent cannot execute payment action | authorization and side-effect tests |
| Reliability | retry does not double-count | replay/idempotency test evidence |
| Security | PII never appears in an answer or log | red-team cases and scan results |

---

## 🧭 Section 2: Test strategy that senior interviewers expect

A useful strategy specifies the SUT boundary, owners, risks, test levels, environments, data, oracles, automation, exit criteria and monitoring. It does not say only “we will do unit, integration and UAT.”

### Risk-driven prioritization

Prioritize by `business impact × likelihood × detectability`. A financial reconciliation defect may be low frequency but is still release-blocking. A cosmetic dashboard label defect may not be.

```text
Critical flow: source transaction → ETL → warehouse fact → semantic metric → dashboard / AI answer
Critical risks: loss, duplication, incorrect transformation, stale data, unauthorized access, unsafe action
```

### Test levels for a data/AI SUT

1. **Contract/component:** schema, functions, prompts, model wrappers, tool contracts.
2. **Pipeline/integration:** data movement, transformation, interfaces, permissions.
3. **End-to-end:** source-to-consumer business scenario and reconciliation.
4. **Non-functional:** performance, security, reliability, recovery, scalability.
5. **Production controls:** monitoring, alerting, audit trace and incident runbook.

---

## 🧪 Section 3: The test-design checklist

For each requirement ask:

- What is the positive flow and its trusted oracle?
- What is missing, malformed, duplicated, delayed, reordered or out of range?
- Which business boundaries matter: dates, currency, limits, permissions, schema versions?
- What happens when a dependency is slow, unavailable or returns invalid data?
- How will a release and later production incident be detected?

### Example — daily orders pipeline

| Scenario | Expected quality result | Evidence |
|---|---|---|
| normal input | exact business-rule result | source/target key + amount comparison |
| duplicate delivery | no double-count after rerun | idempotency key and target query |
| late source file | alert and defined hold/degrade behavior | freshness alert + run log |
| invalid currency | reject/quarantine with traceable reason | reject file and defect record |
| partial target write | rollback/recovery prevents publish | run trace and post-recovery reconciliation |

---

## ❓ Section 4: Rapid-fire Q&A

**Q: What is the difference between QA and testing?**  
**A:** Testing detects defects in a product. QA designs the process, controls, evidence and feedback loops that prevent defects and make release risk visible.

**Q: When do you block a release?**  
**A:** When a critical requirement fails, a critical quality signal is unknown, reconciliation/safety/security evidence is missing, or residual risk exceeds the approved threshold. “Most tests passed” is not a release criterion.

**Q: What is a test oracle?**  
**A:** The source of truth that determines whether a result is acceptable: a business rule, contract, golden dataset, independently calculated control total, or human-reviewed rubric.

---

## ✅ Mastery checklist

- [ ] Define SUT boundary, dependencies, owners and data classifications.
- [ ] Convert business objectives into measurable quality risks.
- [ ] Write positive, negative, boundary and recovery scenarios.
- [ ] Name an oracle and evidence artifact for every critical test.
- [ ] Explain entry/exit criteria, waiver authority and rollback.
- [ ] Give an evidence-based PASS / FAIL / BLOCK recommendation.
