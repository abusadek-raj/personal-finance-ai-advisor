

import streamlit as st

st.set_page_config(
    page_title="Personal Finance AI Advisor",
    page_icon="💰",
    layout="wide",
)

st.title("💰 AI-Based Personal Finance and Savings Advisor")

st.write(
    "Welcome! This application will help you understand "
    "your spending, manage your budget, and plan your savings."
)

st.info(
    "Project status: Initial setup. "
    "Financial tracking and AI features will be added in later stages."
)

st.subheader("Project Objectives")

col1, col2, col3 = st.columns(3)

col1.metric("Income Tracking", "Planned")
col2.metric("Expense Analysis", "Planned")
col3.metric("AI Savings Advice", "Planned")
