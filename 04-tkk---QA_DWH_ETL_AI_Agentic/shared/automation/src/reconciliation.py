"""Small, dependency-free reconciliation helpers for data-QA exercises."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class ReconciliationResult:
    source_count: int
    target_count: int
    missing_keys: tuple[str, ...]
    unexpected_keys: tuple[str, ...]
    duplicate_target_keys: tuple[str, ...]
    amount_difference: Decimal

    @property
    def passed(self) -> bool:
        return not (
            self.missing_keys
            or self.unexpected_keys
            or self.duplicate_target_keys
            or self.amount_difference
        )


def _read_rows(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def _duplicates(keys: Iterable[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    duplicate_keys: set[str] = set()
    for key in keys:
        if key in seen:
            duplicate_keys.add(key)
        seen.add(key)
    return tuple(sorted(duplicate_keys))


def reconcile_orders(source_path: str | Path, target_path: str | Path) -> ReconciliationResult:
    """Compare order IDs and the total order amount in source and target CSVs."""
    source = _read_rows(source_path)
    target = _read_rows(target_path)
    source_keys = {row["order_id"] for row in source}
    target_keys = {row["order_id"] for row in target}
    source_amount = sum((Decimal(row["amount"]) for row in source), Decimal("0"))
    target_amount = sum((Decimal(row["amount"]) for row in target), Decimal("0"))
    return ReconciliationResult(
        source_count=len(source),
        target_count=len(target),
        missing_keys=tuple(sorted(source_keys - target_keys)),
        unexpected_keys=tuple(sorted(target_keys - source_keys)),
        duplicate_target_keys=_duplicates(row["order_id"] for row in target),
        amount_difference=target_amount - source_amount,
    )
