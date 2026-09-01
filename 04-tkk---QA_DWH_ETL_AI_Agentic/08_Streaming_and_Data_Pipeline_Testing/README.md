# 08 — Streaming and Data Pipeline Testing

## QA focus

Test event contracts, ordering, watermarking, deduplication, state, exactly-once/effectively-once guarantees, replay and dead-letter recovery.

## Scenario set

Late events, duplicate events, out-of-order events, poison messages, schema incompatibility, consumer restart, producer retry, backlog surge, clock skew and replay from an offset.

## Evidence

Capture event IDs, offsets, ingestion/event timestamps, state-store outcomes, sink records and latency distribution. Reconcile input events to final materialized output.

## Interview probe

How can a system claim exactly-once processing yet still produce an incorrect business total?
