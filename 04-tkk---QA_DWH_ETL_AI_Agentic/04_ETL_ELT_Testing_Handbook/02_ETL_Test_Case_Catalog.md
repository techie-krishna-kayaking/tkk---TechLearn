# ETL Test Case Catalog

| ID | Scenario | Expected result |
|---|---|---|
| ETL-01 | first full load | all valid rows load; control totals match |
| ETL-02 | incremental insert | exactly one new target business key |
| ETL-03 | repeated incremental file | no duplicate target record or amount |
| ETL-04 | changed source record | intended update/SCD behavior only |
| ETL-05 | late record | documented late-arrival rule and audit evidence |
| ETL-06 | invalid schema | fail/quarantine before publication |
| ETL-07 | target write failure | no partial publish; safe recovery |
| ETL-08 | backfill | scoped history reconciles and downstream impact is controlled |

For every case retain input identity, source cut-off, pipeline run ID, target query, expected/actual controls and decision.
