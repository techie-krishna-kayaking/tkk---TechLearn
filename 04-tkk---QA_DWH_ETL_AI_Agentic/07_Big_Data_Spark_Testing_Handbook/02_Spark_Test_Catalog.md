# Spark Test Catalog

1. Expected partitions exist once for every business date/region.
2. Partition pruning is verified by input/output evidence.
3. Hot-key data produces correct results and remains within approved runtime.
4. Executor failure/retry does not duplicate target output.
5. Schema addition/removal follows data contract behavior.
6. Join output preserves expected grain and reconciliation totals.
7. Rerun/replay produces approved final state.
