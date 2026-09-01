# 19 — Production Troubleshooting Handbook

## Evidence-first incident loop

1. Confirm scope, severity and customer/business impact.
2. Preserve run IDs, traces, data snapshots, logs and current versions.
3. Compare with baseline; verify freshness, volume, schema and reconciliation.
4. Isolate source, transformation, interface, model/AI, consumer or environment layer.
5. Contain impact and communicate decision/status.
6. Validate recovery and data correction/backfill.
7. Record root cause, corrective action and preventive regression/monitor.

## Common data/AI incident patterns

Source late; schema changed; duplicate replay; join multiplication; stale index; model/prompt regression; agent authorization drift; dashboard cache; secret expiry; dependency timeout.

## Senior communication

State facts, known impact, current containment, decision owner, next evidence checkpoint and residual risk. Avoid speculative root cause presented as fact.
