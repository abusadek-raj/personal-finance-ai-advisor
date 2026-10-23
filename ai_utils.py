

import os

import streamlit as st
from groq import Groq


MODEL_NAME = "openai/gpt-oss-20b"


def get_groq_api_key():
    """Read the API key from environment variables or Streamlit secrets."""
    api_key = os.getenv("GROQ_API_KEY")

    if api_key:
        return api_key

    try:
        return st.secrets["GROQ_API_KEY"]
    except Exception:
        return None


def generate_financial_advice(
    income,
    expenses,
    balance,
    savings_rate,
    expense_categories,
):
    """
    Generate budgeting guidance from calculated financial summaries.

    Monetary calculations are performed in Python, not by the LLM.
    """
    api_key = get_groq_api_key()

    if not api_key:
        raise ValueError(
            "Groq API key not found. Configure GROQ_API_KEY "
            "in .streamlit/secrets.toml or your environment."
        )

    client = Groq(api_key=api_key)

    category_lines = (
        "\n".join(
            f"- {row['Category']}: BDT {row['Amount']:,.2f}"
            for _, row in expense_categories.iterrows()
        )
        if not expense_categories.empty
        else "No expenses recorded."
    )

    financial_summary = f"""
Monthly financial summary (BDT):
- Income: {income:,.2f}
- Expenses: {expenses:,.2f}
- Remaining balance: {balance:,.2f}
- Savings rate: {savings_rate:.2f}%

Expenses by category:
{category_lines}
"""

    system_prompt = """
You are a responsible personal budgeting and savings assistant.

Your task is to explain the supplied financial summary and offer
practical, realistic ways to manage expenses and improve savings.

Rules:
1. Use only the figures provided in the financial summary.
2. Do not invent income, expenses, debts, or personal circumstances.
3. Do not recalculate or contradict the supplied financial totals.
4. If the balance is negative, explain that expenses exceed income.
5. Suggest realistic budgeting actions without shaming the user.
6. Do not recommend specific investments or promise returns.
7. Do not request bank credentials, account numbers, or other secrets.
8. Clearly state that the response is general informational guidance.
9. Keep the response concise, with headings and actionable bullet points.
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": (
                    "Analyze this monthly summary and provide "
                    "personalized budgeting and savings suggestions:\n"
                    + financial_summary
                ),
            },
        ],
        temperature=0.3,
        max_completion_tokens=900,
    )

    advice = response.choices[0].message.content

    if not advice or not advice.strip():
        raise RuntimeError("The AI returned an empty response.")

    return advice.strip()
