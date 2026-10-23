

import unittest
import pandas as pd

from finance_utils import (
    calculate_financial_summary,
    calculate_expense_by_category,
)


class TestFinancialSummary(unittest.TestCase):

    def setUp(self):
        self.transactions = pd.DataFrame([
            {"Type": "Income", "Category": "Salary",
             "Amount": 50000.0},
            {"Type": "Expense", "Category": "Food",
             "Amount": 5000.0},
            {"Type": "Expense", "Category": "Housing",
             "Amount": 12000.0},
        ])

    def test_income_and_expenses(self):
        result = calculate_financial_summary(
            self.transactions
        )
        self.assertEqual(result["income"], 50000.0)
        self.assertEqual(result["expenses"], 17000.0)

    def test_balance(self):
        result = calculate_financial_summary(
            self.transactions
        )
        self.assertEqual(result["balance"], 33000.0)

    def test_savings_rate(self):
        result = calculate_financial_summary(
            self.transactions
        )
        self.assertAlmostEqual(result["savings_rate"], 66.0)

    def test_negative_balance(self):
        data = pd.DataFrame([
            {"Type": "Income", "Category": "Salary",
             "Amount": 10000.0},
            {"Type": "Expense", "Category": "Food",
             "Amount": 12000.0},
        ])
        result = calculate_financial_summary(data)
        self.assertEqual(result["balance"], -2000.0)
        self.assertAlmostEqual(result["savings_rate"], -20.0)

    def test_zero_income(self):
        data = pd.DataFrame([
            {"Type": "Expense", "Category": "Food",
             "Amount": 2000.0},
        ])
        result = calculate_financial_summary(data)
        self.assertEqual(result["income"], 0.0)
        self.assertEqual(result["savings_rate"], 0.0)

    def test_empty_transactions(self):
        data = pd.DataFrame(columns=["Type", "Amount"])
        result = calculate_financial_summary(data)
        self.assertEqual(result["income"], 0.0)
        self.assertEqual(result["expenses"], 0.0)
        self.assertEqual(result["balance"], 0.0)
        self.assertEqual(result["savings_rate"], 0.0)

    def test_expense_categories(self):
        result = calculate_expense_by_category(
            self.transactions
        )
        amounts = dict(
            zip(result["Category"], result["Amount"])
        )
        self.assertEqual(amounts["Food"], 5000.0)
        self.assertEqual(amounts["Housing"], 12000.0)
        self.assertNotIn("Salary", amounts)

    def test_empty_expense_categories(self):
        data = pd.DataFrame(
            columns=["Type", "Category", "Amount"]
        )
        result = calculate_expense_by_category(data)
        self.assertTrue(result.empty)
        self.assertIn("Category", result.columns)


if __name__ == "__main__":
    unittest.main()
