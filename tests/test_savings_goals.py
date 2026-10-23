

import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

import db_utils


class TestSavingsGoals(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_db_path = db_utils.DB_PATH
        db_utils.DB_PATH = Path(self.temp_dir.name) / "test.db"

        db_utils.initialize_db()
        db_utils.initialize_goals_table()

    def tearDown(self):
        db_utils.DB_PATH = self.original_db_path
        self.temp_dir.cleanup()

    def test_add_and_retrieve_goal(self):
        db_utils.add_savings_goal(
            "Emergency Fund",
            50000,
            10000,
            date.today() + timedelta(days=150),
        )

        goals = db_utils.get_savings_goals()

        self.assertEqual(len(goals), 1)
        self.assertEqual(goals.iloc[0]["Goal"], "Emergency Fund")
        self.assertEqual(goals.iloc[0]["Target"], 50000)
        self.assertEqual(goals.iloc[0]["Saved"], 10000)

    def test_update_progress(self):
        db_utils.add_savings_goal(
            "Vacation",
            30000,
            0,
            date.today() + timedelta(days=90),
        )

        goal_id = int(db_utils.get_savings_goals().iloc[0]["ID"])
        db_utils.update_savings_progress(goal_id, 5000)

        goals = db_utils.get_savings_goals()
        self.assertEqual(goals.iloc[0]["Saved"], 5000)

    def test_reject_invalid_target(self):
        with self.assertRaises(ValueError):
            db_utils.add_savings_goal(
                "Invalid Goal",
                0,
                0,
                date.today() + timedelta(days=30),
            )

    def test_reject_savings_above_target(self):
        with self.assertRaises(ValueError):
            db_utils.add_savings_goal(
                "Invalid Goal",
                10000,
                15000,
                date.today() + timedelta(days=30),
            )

    def test_delete_goal(self):
        db_utils.add_savings_goal(
            "Delete Test",
            10000,
            0,
            date.today() + timedelta(days=30),
        )

        goal_id = int(db_utils.get_savings_goals().iloc[0]["ID"])
        self.assertTrue(db_utils.delete_savings_goal(goal_id))
        self.assertTrue(db_utils.get_savings_goals().empty)


if __name__ == "__main__":
    unittest.main()
