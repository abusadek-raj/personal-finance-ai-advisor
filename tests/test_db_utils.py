

import tempfile
import unittest
from datetime import date
from pathlib import Path

import db_utils


class TestDatabase(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_db_path = db_utils.DB_PATH
        db_utils.DB_PATH = Path(self.temp_dir.name) / "test.db"
        db_utils.initialize_db()

    def tearDown(self):
        db_utils.DB_PATH = self.original_db_path
        self.temp_dir.cleanup()

    def test_database_initialization(self):
        self.assertTrue(db_utils.DB_PATH.exists())

    def test_add_and_retrieve_transaction(self):
        db_utils.add_transaction(
            date(2026, 10, 23),
            "Income",
            "Salary",
            "Test salary",
            50000.0,
        )

        result = db_utils.get_transactions()

        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]["Type"], "Income")
        self.assertEqual(result.iloc[0]["Amount"], 50000.0)

    def test_data_persists_after_reinitialization(self):
        db_utils.add_transaction(
            date(2026, 10, 23),
            "Expense",
            "Food",
            "Test groceries",
            1500.0,
        )

        db_utils.initialize_db()
        result = db_utils.get_transactions()

        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]["Description"], "Test groceries")

    def test_reject_invalid_amount(self):
        with self.assertRaises(ValueError):
            db_utils.add_transaction(
                date.today(),
                "Expense",
                "Food",
                "Invalid expense",
                0,
            )

    def test_reject_invalid_transaction_type(self):
        with self.assertRaises(ValueError):
            db_utils.add_transaction(
                date.today(),
                "Transfer",
                "Other",
                "Invalid transaction",
                100,
            )

    def test_delete_transaction(self):
        db_utils.add_transaction(
            date.today(),
            "Expense",
            "Food",
            "Delete test",
            100.0,
        )

        result = db_utils.get_transactions()
        transaction_id = int(result.iloc[0]["ID"])

        self.assertTrue(
            db_utils.delete_transaction(transaction_id)
        )
        self.assertTrue(db_utils.get_transactions().empty)

    def test_delete_nonexistent_transaction(self):
        self.assertFalse(db_utils.delete_transaction(99999))


if __name__ == "__main__":
    unittest.main()
