# Practice — Incremental Load QA

Design a test pack for a daily order feed with `order_id`, `updated_at`, `status`, `amount` and `currency`.

- Define the target grain and business key.
- Cover insert, correction, cancellation, duplicate delivery and late arrival.
- State expected behavior for a rerun after the target load fails halfway through.
- Define key and money reconciliation by business date.
- State five release blockers and the exact evidence each requires.
