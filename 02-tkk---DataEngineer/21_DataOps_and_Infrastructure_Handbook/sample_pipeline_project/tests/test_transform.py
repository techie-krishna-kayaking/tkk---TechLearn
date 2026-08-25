"""Unit tests for the transform logic (fast, deterministic, many)."""
from datetime import datetime

from pipeline.transform import clean, dedupe_latest, revenue_by_status, run, SAMPLE


def _rec(oid, cid, status, amount, hour):
    return {"order_id": oid, "customer_id": cid, "status": status,
            "amount": amount, "created_at": datetime(2024, 6, 1, hour, 0)}


def test_clean_drops_invalid_rows():
    recs = [
        _rec("O1", "C1", "placed", 100.0, 9),
        _rec("O2", "C2", "returned", 50.0, 9),   # bad status -> dropped
        _rec("O3", "C3", "placed", -1.0, 9),      # negative amount -> dropped
        _rec("", "C4", "placed", 10.0, 9),        # missing id -> dropped
    ]
    cleaned = clean(recs)
    assert [o.order_id for o in cleaned] == ["O1"]


def test_clean_lowercases_status():
    cleaned = clean([_rec("O1", "C1", "PLACED", 100.0, 9)])
    assert cleaned[0].status == "placed"


def test_dedupe_keeps_latest():
    orders = clean([
        _rec("O1", "C1", "placed", 100.0, 9),
        _rec("O1", "C1", "shipped", 100.0, 12),   # newer -> wins
    ])
    deduped = dedupe_latest(orders)
    assert len(deduped) == 1
    assert deduped[0].status == "shipped"


def test_revenue_by_status():
    orders = clean([
        _rec("O1", "C1", "delivered", 100.0, 9),
        _rec("O2", "C2", "delivered", 50.0, 9),
        _rec("O3", "C3", "cancelled", 0.0, 9),
    ])
    assert revenue_by_status(orders) == {"delivered": 150.0, "cancelled": 0.0}


def test_run_is_idempotent():
    # Running twice on the same input yields the same result (rerun-safe).
    assert run(SAMPLE) == run(SAMPLE)


def test_run_end_to_end():
    result = run(SAMPLE)
    # O1 deduped to 'shipped', O2 delivered, O3 cancelled, BAD dropped
    assert result == {"shipped": 100.0, "delivered": 250.0, "cancelled": 0.0}
