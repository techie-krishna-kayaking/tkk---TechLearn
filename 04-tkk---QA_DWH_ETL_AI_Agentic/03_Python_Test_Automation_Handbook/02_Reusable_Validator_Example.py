"""Dependency-free data QA example. Run: python 02_Reusable_Validator_Example.py"""
from collections import Counter
from decimal import Decimal


def reconcile(source, target, key="id", amount="amount"):
    source_keys = {row[key] for row in source}
    target_keys = {row[key] for row in target}
    duplicates = sorted(k for k, n in Counter(row[key] for row in target).items() if n > 1)
    difference = sum((Decimal(r[amount]) for r in target), Decimal()) - sum(
        (Decimal(r[amount]) for r in source), Decimal()
    )
    return {"missing": sorted(source_keys - target_keys), "unexpected": sorted(target_keys - source_keys),
            "duplicates": duplicates, "amount_difference": difference}


if __name__ == "__main__":
    clean = [{"id": "1", "amount": "10.00"}, {"id": "2", "amount": "5.00"}]
    assert reconcile(clean, clean) == {"missing": [], "unexpected": [], "duplicates": [], "amount_difference": Decimal("0")}
    corrupt = [{"id": "1", "amount": "10.00"}, {"id": "1", "amount": "10.00"}]
    result = reconcile(clean, corrupt)
    assert result["missing"] == ["2"] and result["duplicates"] == ["1"]
    print("PASS: validator exposes expected reconciliation failures", result)
