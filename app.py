

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, timedelta

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

# ---------- Session state ----------
if "transactions" not in st.session_state:
    today = date.today()

    st.session_state.transactions = [
        {
            "Date": today - timedelta(days=5),
            "Type": "Income",
            "Category": "Salary",
            "Description": "Monthly salary (demo)",
            "Amount": 50000.0,
        },
        {
            "Date": today - timedelta(days=4),
            "Type": "Expense",
            "Category": "Housing",
            "Description": "House rent (demo)",
            "Amount": 12000.0,
        },
        {
            "Date": today - timedelta(days=3),
            "Type": "Expense",
            "Category": "Food",
            "Description": "Groceries (demo)",
            "Amount": 4500.0,
        },
        {
            "Date": today - timedelta(days=2),
            "Type": "Expense",
            "Category": "Transport",
            "Description": "Transportation (demo)",
            "Amount": 1500.0,
        },
        {
            "Date": today - timedelta(days=1),
            "Type": "Expense",
            "Category": "Utilities",
            "Description": "Utility bills (demo)",
            "Amount": 2000.0,
        },
    ]


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
                st.session_state.transactions.append(
                    {
                        "Date": transaction_date,
                        "Type": transaction_type,
                        "Category": category,
                        "Description": description.strip(),
                        "Amount": float(amount),
                    }
                )
                st.success("Transaction added successfully!")
                st.rerun()



# ---------- Data preparation ----------
transactions = pd.DataFrame(
    st.session_state.transactions
)

if transactions.empty:
    transactions = pd.DataFrame(
        columns=[
            "Date",
            "Type",
            "Category",
            "Description",
            "Amount",
        ]
    )

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

income = monthly.loc[
    monthly["Type"] == "Income", "Amount"
].sum()

expenses = monthly.loc[
    monthly["Type"] == "Expense", "Amount"
].sum()

balance = income - expenses
savings_rate = (balance / income * 100) if income > 0 else 0.0

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
        category_totals = (
            expense_data.groupby("Category", as_index=False)["Amount"]
            .sum()
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

    history["Date"] = history["Date"].astype(str)
    history["Amount"] = history["Amount"].map(
        lambda value: f"৳{value:,.2f}"
    )

    st.dataframe(
        history,
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("No transactions are available for this month.")

st.caption(
    "Demo version: transactions are held in session memory "
    "and are not permanently saved. Sample transactions are "
    "illustrative, not real financial records."
)
