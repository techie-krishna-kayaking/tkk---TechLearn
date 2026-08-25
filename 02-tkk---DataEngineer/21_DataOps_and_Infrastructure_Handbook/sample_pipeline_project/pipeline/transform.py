"""
transform.py — the ETL transformation logic.

Design principle: keep transformation logic as PURE FUNCTIONS (input data ->
output data, no hidden I/O). That makes it trivially unit-testable and
idempotent — the two properties CI and reliable backfills depend on.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable


VALID_STATUSES = {"placed", "shipped", "delivered", "cancelled"}


@dataclass(frozen=True)
class Order:
    order_id: str
    customer_id: str
    status: str
    amount: float
    created_at: datetime


def clean(records: Iterable[dict]) -> list[Order]:
    """Parse + validate raw records into typed Orders.

    Drops rows that violate the contract (bad status, negative amount, missing
    keys) rather than letting them corrupt downstream. Idempotent: same input
    always yields the same output.
    """
    cleaned: list[Order] = []
    for r in records:
        try:
            if not r.get("order_id") or not r.get("customer_id"):
                continue
            status = str(r["status"]).lower()
            amount = float(r["amount"])
            if status not in VALID_STATUSES or amount < 0:
                continue
            cleaned.append(
                Order(
                    order_id=str(r["order_id"]),
                    customer_id=str(r["customer_id"]),
                    status=status,
                    amount=amount,
                    created_at=r["created_at"],
                )
            )
        except (KeyError, TypeError, ValueError):
            continue
    return cleaned


def dedupe_latest(orders: list[Order]) -> list[Order]:
    """Keep the latest row per order_id (idempotent upsert semantics)."""
    latest: dict[str, Order] = {}
    for o in orders:
        cur = latest.get(o.order_id)
        if cur is None or o.created_at >= cur.created_at:
            latest[o.order_id] = o
    return sorted(latest.values(), key=lambda o: o.order_id)


def revenue_by_status(orders: list[Order]) -> dict[str, float]:
    """Aggregate net revenue per status (cancelled contributes 0)."""
    agg: dict[str, float] = {}
    for o in orders:
        agg[o.status] = round(agg.get(o.status, 0.0) + o.amount, 2)
    return agg


SAMPLE = [
    {"order_id": "O1", "customer_id": "C1", "status": "placed",
     "amount": 100.0, "created_at": datetime(2024, 6, 1, 9, 0)},
    {"order_id": "O1", "customer_id": "C1", "status": "shipped",   # newer O1
     "amount": 100.0, "created_at": datetime(2024, 6, 1, 12, 0)},
    {"order_id": "O2", "customer_id": "C2", "status": "delivered",
     "amount": 250.0, "created_at": datetime(2024, 6, 1, 10, 0)},
    {"order_id": "O3", "customer_id": "C3", "status": "cancelled",
     "amount": 0.0, "created_at": datetime(2024, 6, 1, 11, 0)},
    {"order_id": "BAD", "customer_id": "C4", "status": "returned",  # invalid -> dropped
     "amount": -5.0, "created_at": datetime(2024, 6, 1, 11, 0)},
]


def run(records: list[dict]) -> dict[str, float]:
    """Full transform: clean -> dedupe -> aggregate."""
    return revenue_by_status(dedupe_latest(clean(records)))


if __name__ == "__main__":
    result = run(SAMPLE)
    print("revenue_by_status:", result)
