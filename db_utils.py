

import sqlite3
from pathlib import Path

import pandas as pd
from datetime import date


# Keep the database in the project root.
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "finance.db"



from contextlib import contextmanager
import sqlite3

@contextmanager
def get_connection():
    """Open a SQLite connection and always close it."""
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def initialize_db():
    """Create the transactions table if it does not exist."""
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_date TEXT NOT NULL,
                transaction_type TEXT NOT NULL
                    CHECK(transaction_type IN ('Income', 'Expense')),
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                amount REAL NOT NULL CHECK(amount > 0),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def add_transaction(
    transaction_date,
    transaction_type,
    category,
    description,
    amount,
):
    """Validate and save a transaction to SQLite."""
    if transaction_type not in ("Income", "Expense"):
        raise ValueError("Transaction type must be Income or Expense.")

    if not category.strip():
        raise ValueError("Category cannot be empty.")

    if not description.strip():
        raise ValueError("Description cannot be empty.")

    if amount <= 0:
        raise ValueError("Amount must be greater than zero.")

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO transactions (
                transaction_date,
                transaction_type,
                category,
                description,
                amount
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                transaction_date.isoformat()
                if hasattr(transaction_date, "isoformat")
                else str(transaction_date),
                transaction_type,
                category.strip(),
                description.strip(),
                float(amount),
            ),
        )


def get_transactions():
    """Load all saved transactions as a DataFrame."""
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                id AS ID,
                transaction_date AS Date,
                transaction_type AS Type,
                category AS Category,
                description AS Description,
                amount AS Amount
            FROM transactions
            ORDER BY transaction_date DESC, id DESC
            """
        ).fetchall()

    columns = [
        "ID",
        "Date",
        "Type",
        "Category",
        "Description",
        "Amount",
    ]

    return pd.DataFrame(
        [dict(row) for row in rows],
        columns=columns,
    )


def delete_transaction(transaction_id):
    """Delete one transaction using its database ID."""
    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM transactions WHERE id = ?",
            (int(transaction_id),),
        )
        return cursor.rowcount > 0


def initialize_goals_table():
    """Create the savings goals table if it does not exist."""
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS savings_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal_name TEXT NOT NULL,
                target_amount REAL NOT NULL
                    CHECK(target_amount > 0),
                current_amount REAL NOT NULL DEFAULT 0
                    CHECK(current_amount >= 0),
                deadline TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def add_savings_goal(goal_name, target_amount, current_amount, deadline):
    """Save a savings goal."""
    if not goal_name.strip():
        raise ValueError("Goal name cannot be empty.")

    if target_amount <= 0:
        raise ValueError("Target amount must be greater than zero.")

    if current_amount < 0 or current_amount > target_amount:
        raise ValueError(
            "Current savings must be between zero and the target amount."
        )

    if deadline < date.today():
        raise ValueError("Deadline cannot be in the past.")

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO savings_goals
                (goal_name, target_amount, current_amount, deadline)
            VALUES (?, ?, ?, ?)
            """,
            (
                goal_name.strip(),
                float(target_amount),
                float(current_amount),
                deadline.isoformat(),
            ),
        )


def get_savings_goals():
    """Retrieve all savings goals."""
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id AS ID,
                   goal_name AS Goal,
                   target_amount AS Target,
                   current_amount AS Saved,
                   deadline AS Deadline
            FROM savings_goals
            ORDER BY deadline ASC, id DESC
            """
        ).fetchall()

    return pd.DataFrame(
        [dict(row) for row in rows],
        columns=["ID", "Goal", "Target", "Saved", "Deadline"],
    )


def update_savings_progress(goal_id, current_amount):
    """Update the amount saved toward a goal."""
    if current_amount < 0:
        raise ValueError("Saved amount cannot be negative.")

    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE savings_goals
            SET current_amount = ?
            WHERE id = ? AND target_amount >= ?
            """,
            (float(current_amount), int(goal_id), float(current_amount)),
        )

        if cursor.rowcount == 0:
            raise ValueError(
                "Goal not found, or saved amount exceeds its target."
            )


def delete_savings_goal(goal_id):
    """Delete a savings goal."""
    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM savings_goals WHERE id = ?",
            (int(goal_id),),
        )
        return cursor.rowcount > 0
