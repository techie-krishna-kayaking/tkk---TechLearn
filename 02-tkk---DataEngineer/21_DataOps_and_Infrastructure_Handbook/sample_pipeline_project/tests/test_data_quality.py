"""
Data-quality / contract tests — the 'shift-left' gate.

These assert properties of the TRANSFORM OUTPUT that must always hold before we
publish. In CI they run alongside unit tests; a failure blocks the merge/deploy.
"""
from pipeline.transform import clean, dedupe_latest, run, SAMPLE, VALID_STATUSES


def test_output_statuses_are_in_contract():
    result = run(SAMPLE)
    assert set(result).issubset(VALID_STATUSES)


def test_no_negative_revenue():
    result = run(SAMPLE)
    assert all(v >= 0 for v in result.values())


def test_order_id_uniqueness_after_dedupe():
    deduped = dedupe_latest(clean(SAMPLE))
    ids = [o.order_id for o in deduped]
    assert len(ids) == len(set(ids)), "order_id must be unique after dedupe"


def test_no_invalid_rows_survive():
    cleaned = clean(SAMPLE)
    assert all(o.amount >= 0 and o.status in VALID_STATUSES for o in cleaned)
    assert all(o.order_id and o.customer_id for o in cleaned)


def test_row_count_reconciliation():
    # Cleaned rows must never exceed input rows (no accidental fan-out).
    assert len(clean(SAMPLE)) <= len(SAMPLE)
