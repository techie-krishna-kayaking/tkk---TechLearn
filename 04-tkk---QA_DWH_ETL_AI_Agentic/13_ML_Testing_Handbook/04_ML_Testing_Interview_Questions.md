# ML Testing — Interview Questions & Model Answers

## 1. What is training-serving skew and how do you test it?

It is a mismatch between training and inference feature computation, schema, defaults, encoding or timing. Use shared feature definitions where possible; compare representative offline/online feature vectors, enforce contracts, test missing/boundary inputs and monitor production distributions.

## 2. What is leakage?

Training uses information unavailable at prediction time, producing unrealistically high metrics. Test time-aware splits, point-in-time joins, feature availability timestamps, target-proxy fields and label-generation logic. Leakage is a quality defect, not a model-tuning opportunity.

## 3. How do you test model fairness?

First agree protected/critical slices, applicable policy and metrics. Measure performance/error rates and calibration by slice with adequate sample confidence; investigate material disparity; test mitigations; document trade-offs and monitoring. Do not claim fairness from a single global accuracy number.

## 4. Why is a metric improvement not automatically releasable?

It may come from leakage, harm a key slice, worsen calibration, exceed latency/cost, fail robustness or not translate to business outcomes. Compare to baseline under controlled data/version, test guardrails and use shadow/canary where appropriate.

## 5. What is drift testing?

Monitor input feature distribution, prediction distribution and, when labels arrive, outcome/performance drift against approved baseline. Distinguish a data pipeline defect, expected seasonal change, population shift and concept drift; define alert, investigation and retraining/rollback decision paths.

## 6. How do you test a thresholded model?

Recompute the confusion matrix and business cost at threshold boundaries; cover exact threshold, just below/above, missing confidence and slice behavior. Ensure serving uses the approved threshold/configuration and changes are versioned/gated.
