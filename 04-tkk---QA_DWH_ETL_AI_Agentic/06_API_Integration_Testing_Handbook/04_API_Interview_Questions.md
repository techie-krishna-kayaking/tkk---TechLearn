# API & Integration Testing — Interview Q&A

**Why is a 200 response insufficient?** It says transport succeeded, not that downstream work completed correctly. Verify final state/event with correlation IDs.

**How do you test idempotency?** Repeat same request/key and prove one business effect, correct response semantics, audit trace and safe retry after timeout.

**How do you test pagination?** Boundary page sizes, empty/last page, stable ordering, duplicate/lost records across pages, filters and authorization context.

**What are contract tests?** Automated checks that producer/consumer schema and behavior expectations remain compatible before integration breaks in production.

**How do you test async APIs?** Capture request/event IDs, poll/subscribe to completion, validate timeout/retry/DLQ and reconcile final persisted output.
