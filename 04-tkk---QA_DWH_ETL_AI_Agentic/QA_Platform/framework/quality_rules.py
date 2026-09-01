"""Standard-library QA framework for schema, rule and reconciliation evidence."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Iterable


@dataclass(frozen=True)
class Finding:
    rule: str
    severity: str
    records: tuple[str, ...]
    message: str


def required_fields(rows: Iterable[dict[str, str]], fields: tuple[str, ...]) -> list[Finding]:
    failures = []
    for field in fields:
        bad = tuple(str(row.get("order_id", "<unknown>")) for row in rows if not row.get(field))
        if bad:
            failures.append(Finding("required_" + field, "BLOCK", bad, f"{field} is mandatory"))
    return failures


def unique_key(rows: Iterable[dict[str, str]], key: str) -> list[Finding]:
    values = [row.get(key, "") for row in rows]
    duplicates = tuple(sorted(value for value, count in Counter(values).items() if count > 1))
    return [Finding("unique_" + key, "BLOCK", duplicates, f"duplicate {key}")] if duplicates else []


def amount_range(rows: Iterable[dict[str, str]], field: str = "amount") -> list[Finding]:
    bad = []
    for row in rows:
        try:
            if Decimal(row[field]) < 0:
                bad.append(row.get("order_id", "<unknown>"))
        except (InvalidOperation, KeyError):
            bad.append(row.get("order_id", "<unknown>"))
    return [Finding("valid_" + field, "BLOCK", tuple(sorted(bad)), "amount must be a non-negative decimal")] if bad else []


def reconcile(source: Iterable[dict[str, str]], target: Iterable[dict[str, str]]) -> list[Finding]:
    source, target = list(source), list(target)
    source_keys, target_keys = {r["order_id"] for r in source}, {r["order_id"] for r in target}
    findings = []
    missing = tuple(sorted(source_keys - target_keys))
    unexpected = tuple(sorted(target_keys - source_keys))
    if missing:
        findings.append(Finding("source_target_key_coverage", "BLOCK", missing, "source keys missing in target"))
    if unexpected:
        findings.append(Finding("source_target_key_coverage", "BLOCK", unexpected, "unexpected target keys"))
    source_total = sum((Decimal(r["amount"]) for r in source), Decimal())
    target_total = sum((Decimal(r["amount"]) for r in target), Decimal())
    if source_total != target_total:
        findings.append(Finding("source_target_amount", "BLOCK", (), f"amount difference: {target_total - source_total}"))
    return findings


def release_decision(findings: Iterable[Finding]) -> str:
    return "BLOCK" if any(finding.severity == "BLOCK" for finding in findings) else "PASS"
