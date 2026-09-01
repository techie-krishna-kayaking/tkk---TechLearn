# 13 — ML Model Testing Handbook

## QA focus

Test training and inference data, features, labels, leakage, reproducibility, metric calculation, robustness, slices/fairness, drift and production decision behavior.

## Core checks

| Area | QA questions |
|---|---|
| data/splits | is time leakage prevented and data versioned? |
| features | are ranges, missingness and definitions valid in train and serve? |
| labels | are labels correct, timely and not leaked? |
| metrics | are calculations, baselines and thresholds reproducible? |
| robustness | do edge/adversarial inputs fail safely? |
| fairness | are key slices measured and approved? |
| drift | are input/prediction/outcome shifts monitored? |

QA does not need to invent models. QA needs acceptance criteria, independent validation and regression evidence.
