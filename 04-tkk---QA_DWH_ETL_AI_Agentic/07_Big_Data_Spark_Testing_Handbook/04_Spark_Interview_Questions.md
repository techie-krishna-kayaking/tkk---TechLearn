# Spark & Big Data Testing — Interview Q&A

**Why does a job pass on sample but fail in production?** Distribution, skew, shuffle volume, partition/file layout, join cardinality, late data and resource/retry behavior are different at scale.

**How do you test partitions?** Inventory expected/unexpected partitions, record/key controls per partition, boundary date/timezone behavior and idempotent overwrite/retry.

**What is skew from QA view?** A small set of keys creates disproportionate workload and timeout/failure risk; test with representative hot keys and inspect P95/max partition behavior.

**What does retry testing prove?** That final data, checkpoint/state and publish status are correct after failure—not merely that the scheduler shows success.

**How do you validate distributed output?** Independent oracle on controlled data plus aggregate/key reconciliation and performance/recovery tests at representative scale.
