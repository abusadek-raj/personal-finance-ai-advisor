

import pandas as pd


def calculate_financial_summary(transactions):
    """
    Calculate financial totals from a transaction DataFrame.

    Required columns:
        Type, Amount

    Returns:
        Dictionary containing income, expenses, balance,
        and savings_rate.
    """
    if transactions.empty:
        return {
            "income": 0.0,
            "expenses": 0.0,
            "balance": 0.0,
            "savings_rate": 0.0,
        }

    income = float(
        transactions.loc[
            transactions["Type"] == "Income", "Amount"
        ].sum()
    )

    expenses = float(
        transactions.loc[
            transactions["Type"] == "Expense", "Amount"
        ].sum()
    )

    balance = income - expenses
    savings_rate = (
        balance / income * 100 if income > 0 else 0.0
    )

    return {
        "income": income,
        "expenses": expenses,
        "balance": balance,
        "savings_rate": savings_rate,
    }


def calculate_expense_by_category(transactions):
    """
    Return expense totals grouped by category.
    """
    if transactions.empty:
        return pd.DataFrame(
            columns=["Category", "Amount"]
        )

    expenses = transactions[
        transactions["Type"] == "Expense"
    ]

    if expenses.empty:
        return pd.DataFrame(
            columns=["Category", "Amount"]
        )

    return (
        expenses.groupby("Category", as_index=False)["Amount"]
        .sum()
        .sort_values("Amount", ascending=False)
        .reset_index(drop=True)
    )
