# 08 — Kafka & Streaming Testing Handbook

## QA focus

Test event contracts, ordering, deduplication, watermarking, state, replay, dead-letter handling, consumer recovery and end-to-end latency.

## Critical distinction

“Exactly once” is not a business guarantee by itself. A duplicate may still reach a non-idempotent external sink; a correct one-time processing result can still use the wrong event-time window. Validate observable business state.

## Scenario matrix

Late event, duplicate event, out-of-order event, malformed message, poison event, producer retry, consumer restart, offset reset, schema incompatibility, backlog spike and replay.

## Evidence

Use event ID, key, producer timestamp, event time, ingestion time, partition/offset, consumer run, state-store result, sink key and end-to-end latency.
