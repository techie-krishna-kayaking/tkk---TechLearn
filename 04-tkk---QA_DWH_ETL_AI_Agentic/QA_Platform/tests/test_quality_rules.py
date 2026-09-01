import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "framework"))
from quality_rules import amount_range, release_decision, reconcile, required_fields, unique_key  # noqa: E402


def rows(name: str):
    return json.loads((ROOT / "test_data" / name).read_text(encoding="utf-8"))


class QualityPlatformTests(unittest.TestCase):
    def test_valid_load_passes_all_critical_controls(self):
        source, target = rows("orders_source.json"), rows("orders_target_valid.json")
        findings = required_fields(target, ("order_id", "customer_id", "amount", "status")) + unique_key(target, "order_id") + amount_range(target) + reconcile(source, target)
        self.assertEqual(findings, [])
        self.assertEqual(release_decision(findings), "PASS")

    def test_invalid_load_blocks_release_with_actionable_evidence(self):
        source, target = rows("orders_source.json"), rows("orders_target_invalid.json")
        findings = required_fields(target, ("order_id", "customer_id", "amount", "status")) + unique_key(target, "order_id") + amount_range(target) + reconcile(source, target)
        self.assertEqual(release_decision(findings), "BLOCK")
        self.assertTrue(any(f.rule == "unique_order_id" for f in findings))
        self.assertTrue(any(f.rule == "source_target_key_coverage" for f in findings))
        self.assertTrue(any(f.rule == "source_target_amount" for f in findings))


if __name__ == "__main__":
    unittest.main()
