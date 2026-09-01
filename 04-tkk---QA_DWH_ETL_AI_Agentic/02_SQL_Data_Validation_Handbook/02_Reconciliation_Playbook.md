# Source-to-Target Reconciliation Playbook

## Order of investigation

1. Confirm both extracts use the same cut-off, filters and grain.
2. Compare expected versus actual volume and key coverage.
3. Identify duplicate keys independently in source and target.
4. Reconcile critical attributes and monetary aggregates by business slice.
5. Trace sampled mismatches through staging/transformation logs.
6. Decide contain, correct, backfill and regression coverage.

## Tolerance policy

Do not invent tolerances after a mismatch. Financial ledgers may require exact penny-level agreement. Telemetry metrics may allow an agreed sampling/latency tolerance. Record who approved it, why and for how long.

## Required evidence

Source/target snapshot identifiers, query text, execution timestamp, data cut-off, row/key/aggregate results, mismatch extract and release decision.
