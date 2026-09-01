# Quality Gate Matrix

| Stage | Example gate | Failure action |
|---|---|---|
| PR | schema, unit validator, lint | block merge |
| test deploy | data reconciliation, API contract | block promotion |
| pre-prod | performance, security, AI regression | block release / approved waiver |
| post-prod | freshness, errors, safety, outcome drift | alert, contain, rollback |

Evidence must identify software/prompt/model/data/index version and environment.
