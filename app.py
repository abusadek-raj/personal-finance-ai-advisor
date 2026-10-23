

from ai_utils import generate_financial_advice
from db_utils import (
    initialize_db,
    add_transaction,
    get_transactions,
    delete_transaction,
)
import sqlite3
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, timedelta
from finance_utils import (
    calculate_financial_summary,
    calculate_expense_by_category,
)

st.set_page_config(
    page_title="Personal Finance AI Advisor",
    page_icon="💰",
    layout="wide",
)

# ---------- Page styling ----------
st.title("💰 Personal Finance & Savings Advisor")
st.caption(
    "Understand your cash flow, monitor spending, "
    "and build better savings habits."
)

# ---------- Database initialization ----------
initialize_db()


# ---------- Add transaction ----------
with st.sidebar:
    st.header("➕ Add Transaction")

    # Keep this selector outside the form so it updates immediately.
    transaction_type = st.selectbox(
        "Transaction type",
        ["Income", "Expense"],
        key="transaction_type",
    )

    if transaction_type == "Income":
        categories = [
            "Salary",
            "Freelance",
            "Business",
            "Investment Income",
            "Other",
        ]
    else:
        categories = [
            "Food",
            "Housing",
            "Transport",
            "Utilities",
            "Healthcare",
            "Education",
            "Shopping",
            "Debt Payment",
            "Other",
        ]

    with st.form("transaction_form", clear_on_submit=True):
        transaction_date = st.date_input(
            "Transaction date",
            value=date.today(),
            max_value=date.today(),
        )

        category = st.selectbox(
            "Category",
            categories,
            key=f"category_{transaction_type}",
        )

        description = st.text_input(
            "Description",
            placeholder="e.g. Monthly salary",
        )

        amount = st.number_input(
            "Amount (BDT ৳)",
            min_value=0.0,
            value=0.0,
            step=100.0,
        )

        submitted = st.form_submit_button(
            "Save Transaction",
            type="primary",
            use_container_width=True,
        )

        
        if submitted:
            if amount <= 0:
                st.error("Please enter an amount greater than zero.")
            elif not description.strip():
                st.error("Please enter a transaction description.")
            else:
                try:
                    add_transaction(
                        transaction_date=transaction_date,
                        transaction_type=transaction_type,
                        category=category,
                        description=description,
                        amount=amount,
                    )
                    st.success("Transaction saved to SQLite!")
                    st.rerun()
                except (ValueError, sqlite3.Error) as error:
                    st.error(f"Could not save transaction: {error}")




# ---------- Data preparation ----------
transactions = get_transactions()

if not transactions.empty:
    transactions["Date"] = pd.to_datetime(
        transactions["Date"]
    ).dt.date

# ---------- Month filter ----------
st.subheader("📊 Financial Dashboard")

if not transactions.empty:
    transactions["Date"] = pd.to_datetime(
        transactions["Date"]
    ).dt.date

    month_options = sorted(
        {
            d.strftime("%Y-%m")
            for d in transactions["Date"]
        },
        reverse=True,
    )

    current_month = date.today().strftime("%Y-%m")
    default_month = (
        current_month
        if current_month in month_options
        else month_options[0]
    )

    selected_month = st.selectbox(
        "Select month",
        month_options,
        index=month_options.index(default_month),
    )

    monthly = transactions[
        transactions["Date"].apply(
            lambda d: d.strftime("%Y-%m") == selected_month
        )
    ].copy()
else:
    monthly = transactions.copy()

summary = calculate_financial_summary(monthly)

income = summary["income"]
expenses = summary["expenses"]
balance = summary["balance"]
savings_rate = summary["savings_rate"]

# ---------- Summary metrics ----------
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Income", f"৳{income:,.2f}")
col2.metric("Total Expenses", f"৳{expenses:,.2f}")
col3.metric(
    "Remaining Balance",
    f"৳{balance:,.2f}",
    delta=f"{balance:,.2f} BDT",
)
col4.metric("Savings Rate", f"{savings_rate:.1f}%")

if income == 0 and expenses == 0:
    st.info("Add transactions to see your financial summary.")
elif balance < 0:
    st.warning(
        "Your expenses exceed your income for the selected month."
    )
else:
    st.success(
        "Your income and expense summary has been calculated."
    )

# ---------- Charts ----------
left, right = st.columns(2)

with left:
    st.subheader("Expense Breakdown")

    expense_data = monthly[
        monthly["Type"] == "Expense"
    ]

    if not expense_data.empty:
        category_totals = calculate_expense_by_category(
                            expense_data
        )

        fig = px.pie(
            category_totals,
            names="Category",
            values="Amount",
            hole=0.45,
            title="Expenses by Category",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No expenses recorded for this month.")

with right:
    st.subheader("Income vs Expenses")

    comparison = pd.DataFrame(
        {
            "Type": ["Income", "Expenses"],
            "Amount": [income, expenses],
        }
    )

    fig = px.bar(
        comparison,
        x="Type",
        y="Amount",
        text="Amount",
        title="Monthly Cash Flow",
        labels={"Amount": "Amount (BDT ৳)"},
    )
    fig.update_traces(texttemplate="৳%{y:,.0f}", textposition="outside")
    st.plotly_chart(fig, use_container_width=True)


# ---------- Transaction history ----------
st.subheader("📋 Transaction History")

if not monthly.empty:
    history = monthly.sort_values(
        "Date", ascending=False
    ).copy()

    # Show the database ID internally for deletion, but not in the table.
    display_history = history.drop(
        columns=["ID"], errors="ignore"
    ).copy()

    display_history["Date"] = (
        display_history["Date"].astype(str)
    )
    display_history["Amount"] = display_history["Amount"].map(
        lambda value: f"৳{value:,.2f}"
    )

    st.dataframe(
        display_history,
        use_container_width=True,
        hide_index=True,
    )

    st.caption("Select a transaction below to delete it.")

    if "ID" in history.columns:
        transaction_options = {
            (
                f'{row["Date"]} | {row["Type"]} | '
                f'{row["Category"]} | '
                f'৳{row["Amount"]:,.2f} | '
                f'{row["Description"]}'
            ): int(row["ID"])
            for _, row in history.iterrows()
        }

        selected_label = st.selectbox(
            "Transaction to delete",
            options=list(transaction_options.keys()),
            key="transaction_to_delete",
        )

        if st.button("Delete selected transaction"):
            deleted = delete_transaction(
                transaction_options[selected_label]
            )

            if deleted:
                st.success("Transaction deleted.")
                st.rerun()
            else:
                st.warning(
                    "Transaction was not found. Refresh and try again."
                )
else:
    st.info("No transactions are available for this month.")



# ---------- AI Financial Advisor ----------
st.divider()
st.subheader("🤖 AI Financial Advisor")

st.write(
    "Get practical budgeting and savings suggestions based "
    "on your selected month's financial summary."
)

st.caption(
    "Your financial totals are calculated by Python. "
    "The AI provides general informational guidance."
)

if st.button(
    "✨ Generate My Financial Advice",
    type="primary",
):
    try:
        with st.spinner(
            "Analyzing your financial summary..."
        ):
            expense_categories = calculate_expense_by_category(
                monthly
            )

            advice = generate_financial_advice(
                income=income,
                expenses=expenses,
                balance=balance,
                savings_rate=savings_rate,
                expense_categories=expense_categories,
            )

        st.markdown("### Your Personalized Suggestions")
        st.markdown(advice)

        st.caption(
            "AI-generated guidance may be inaccurate. "
            "Review suggestions carefully before making financial decisions."
        )

    except ValueError as error:
        st.error(str(error))

    except Exception as error:
        st.error(
            "Unable to generate financial advice. "
            "Check your internet connection, Groq API key, "
            "model availability, and API usage limits."
        )
        # Details are available locally for troubleshooting.
        st.exception(error)
