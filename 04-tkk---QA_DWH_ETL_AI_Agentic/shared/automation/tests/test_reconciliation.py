import sys
import unittest
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "automation" / "src"))

from reconciliation import reconcile_orders  # noqa: E402


DATA = ROOT / "test_data"


class ReconciliationTests(unittest.TestCase):
    def test_matching_files_pass(self):
        result = reconcile_orders(DATA / "orders_source.csv", DATA / "orders_target_valid.csv")
        self.assertTrue(result.passed)
        self.assertEqual(result.amount_difference, Decimal("0.00"))

    def test_bad_target_exposes_each_reconciliation_signal(self):
        result = reconcile_orders(DATA / "orders_source.csv", DATA / "orders_target_invalid.csv")
        self.assertFalse(result.passed)
        self.assertEqual(result.missing_keys, ("1003",))
        self.assertEqual(result.duplicate_target_keys, ("1002",))
        self.assertEqual(result.amount_difference, Decimal("85.00"))


if __name__ == "__main__":
    unittest.main()
