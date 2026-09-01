# Streaming Testing — Interview Q&A

**Exactly once means no testing needed?** No. Validate observable business effect, idempotent sinks, offsets, window/event-time behavior and recovery; delivery semantics alone do not prove correctness.

**How do you test out-of-order data?** Inject known event times/order, validate watermark/window result and allowed-lateness policy; test both accepted late revisions and rejected late events.

**What is a poison message?** A message that repeatedly fails processing. Test quarantine/DLQ, alert, traceability, replay after repair and that it does not block unrelated events.

**How do you test replay?** Replay a bounded offset/time range and reconcile sink state/audit totals to approved expected state without duplicate side effects.

**Key evidence?** Event ID/key, event/ingest time, partition/offset, consumer run, state update, sink key and latency.
