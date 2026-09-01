# 10 — ML Model Testing

## QA focus

Test training and inference data, features, labels, leakage, reproducibility, metrics, robustness, fairness, drift and production behavior.

## Test strategy

Validate split integrity and point-in-time correctness; assert feature ranges and missingness; detect label/feature leakage; reproduce a baseline; verify metric calculations; test slices and adversarial/boundary inputs; monitor drift and delayed-label performance.

## Do not confuse

QA validates whether model quality meets explicitly agreed requirements and detects regressions. QA does not need to train a novel model to perform that role.

## Interview probe

Offline AUC improved but customer complaints rose after release. Which hypotheses, controls and rollback criteria do you use?
