

import sqlite3
from pathlib import Path

import pandas as pd


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
