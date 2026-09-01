# Quality Gate and Incident Runbook

| Signal | Example threshold | Action |
|---|---|---|
| freshness | table older than 30 minutes | hold publish, identify source vs pipeline delay |
| key coverage | below 99.99% | block release, publish mismatch extract |
| financial variance | non-zero or approved limit breach | block and reconcile by slice |
| schema | breaking contract change | reject/quarantine and notify owner |
| anomaly | material unexplained volume/drop | investigate lineage and data cut-off |

Incident sequence: assess impact → preserve run/query/trace evidence → isolate source/transformation/consumer layer → contain → validate recovery → root cause → targeted regression and preventive control.
