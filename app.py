

from datetime import date
import io

from db_utils import (
    initialize_goals_table,
    add_savings_goal,
    get_savings_goals,
    update_savings_progress,
    delete_savings_goal,
)

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
initialize_goals_table()


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



# ---------- Savings Goal Planner ----------
st.divider()
st.header("🎯 Savings Goal Planner")

st.write(
    "Set a savings target, track your progress, "
    "and estimate the monthly contribution required."
)

with st.expander("Create a new savings goal", expanded=False):
    with st.form("savings_goal_form", clear_on_submit=True):
        goal_name = st.text_input(
            "Goal name",
            placeholder="e.g. Emergency fund",
        )

        target_amount = st.number_input(
            "Target amount (BDT ৳)",
            min_value=1.0,
            value=50000.0,
            step=1000.0,
        )

        current_amount = st.number_input(
            "Amount already saved (BDT ৳)",
            min_value=0.0,
            value=0.0,
            step=500.0,
        )

        deadline = st.date_input(
            "Target date",
            value=date.today(),
            min_value=date.today(),
        )

        goal_submitted = st.form_submit_button(
            "Create Savings Goal",
            type="primary",
        )

        if goal_submitted:
            try:
                add_savings_goal(
                    goal_name,
                    target_amount,
                    current_amount,
                    deadline,
                )
                st.success("Savings goal created successfully!")
                st.rerun()
            except ValueError as error:
                st.error(str(error))

goals = get_savings_goals()

if goals.empty:
    st.info("You have not created any savings goals yet.")
else:
    for _, goal in goals.iterrows():
        goal_id = int(goal["ID"])
        target = float(goal["Target"])
        saved = float(goal["Saved"])
        remaining = max(target - saved, 0.0)
        progress = min(saved / target, 1.0)

        st.subheader(str(goal["Goal"]))

        metric1, metric2, metric3 = st.columns(3)
        metric1.metric("Target", f"৳{target:,.2f}")
        metric2.metric("Saved", f"৳{saved:,.2f}")
        metric3.metric("Remaining", f"৳{remaining:,.2f}")

        st.progress(progress)
        st.caption(f"Progress: {progress * 100:.1f}%")

        deadline_date = date.fromisoformat(str(goal["Deadline"]))
        days_left = max((deadline_date - date.today()).days, 0)
        months_left = max(
            (deadline_date.year - date.today().year) * 12
            + deadline_date.month - date.today().month
            + (1 if deadline_date.day > date.today().day else 0),
            1,
        )

        if remaining == 0:
            st.success("Congratulations! This goal is complete.")
        else:
            st.write(
                f"Deadline: {deadline_date.isoformat()} "
                f"({days_left} days remaining)"
            )
            st.write(
                f"Estimated monthly saving needed: "
                f"৳{remaining / months_left:,.2f}"
            )

        with st.form(f"goal_progress_{goal_id}"):
            new_saved = st.number_input(
                "Update total saved (BDT ৳)",
                min_value=0.0,
                max_value=target,
                value=saved,
                step=500.0,
                key=f"saved_{goal_id}",
            )

            update_clicked = st.form_submit_button(
                "Update Progress"
            )

            if update_clicked:
                try:
                    update_savings_progress(
                        goal_id, new_saved
                    )
                    st.success("Savings progress updated.")
                    st.rerun()
                except ValueError as error:
                    st.error(str(error))

        if st.button(
            "Delete this goal",
            key=f"delete_goal_{goal_id}",
        ):
            delete_savings_goal(goal_id)
            st.rerun()

        st.divider()



# ---------- Monthly Financial Report ----------
st.header("📄 Monthly Financial Report")

report_data = monthly.copy()

if not report_data.empty:
    report_income = float(
        report_data.loc[
            report_data["Type"] == "Income", "Amount"
        ].sum()
    )

    report_expenses = float(
        report_data.loc[
            report_data["Type"] == "Expense", "Amount"
        ].sum()
    )

    report_balance = report_income - report_expenses

    report = pd.DataFrame(
        [
            {"Metric": "Total Income (BDT)", "Amount": report_income},
            {"Metric": "Total Expenses (BDT)", "Amount": report_expenses},
            {"Metric": "Remaining Balance (BDT)", "Amount": report_balance},
            {
                "Metric": "Savings Rate (%)",
                "Amount": (
                    report_balance / report_income * 100
                    if report_income > 0 else 0.0
                ),
            },
        ]
    )

    st.dataframe(report, use_container_width=True, hide_index=True)

    csv_buffer = io.StringIO()
    report_data.to_csv(
        csv_buffer,
        index=False,
        date_format="%Y-%m-%d",
    )

    st.download_button(
        "⬇️ Download Monthly Transactions (CSV)",
        data=csv_buffer.getvalue(),
        file_name=f"finance_report_{selected_month}.csv",
        mime="text/csv",
    )
else:
    st.info(
        "No transactions are available for the selected month."
    )
