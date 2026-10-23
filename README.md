
# AI-Based Personal Finance and Savings Advisor

An AI-powered personal finance web application built with Python and Streamlit to help users track income and expenses, understand their financial position, manage savings goals, and receive personalized financial guidance.

**Live Demo:** [(https://personal-finance-ai-advisor-o7zxycccshufwsqn6hkzuh.streamlit.app/)]

## Project Overview

Managing personal finances requires monitoring income, controlling expenses, and setting realistic savings targets. This project combines traditional financial calculations with a generative AI advisor to provide a simple, interactive personal finance management experience.

Users can record financial transactions, view monthly summaries, analyze expenses by category, create savings goals, and generate AI-powered recommendations based on their financial summaries.

## Key Features

- **Transaction Management:** Record and manage income and expenses.
- **Financial Dashboard:** View income, expenses, balance, and savings rate.
- **Expense Analysis:** Examine spending by category using visualizations.
- **AI Financial Advisor:** Generate personalized financial guidance using the Groq API and the `openai/gpt-oss-20b` model.
- **Savings Goal Planner:** Create goals, track saved amounts, monitor progress, and estimate required monthly contributions.
- **Monthly Financial Reports:** Download transaction reports as CSV files.
- **SQLite Database:** Persist transactions and savings goals locally in the application environment.

## Technology Stack

| Component | Technology |
|---|---|
| Programming language | Python |
| Web application | Streamlit |
| Data manipulation | Pandas |
| Data visualization | Plotly |
| Database | SQLite |
| Generative AI | Groq API |
| Language model | `openai/gpt-oss-20b` |
| Testing | Python `unittest` |
| Version control | Git and GitHub |
| Deployment | Streamlit Community Cloud |

## Application Workflow

1. The user records income and expenses.
2. The application stores transactions in SQLite.
3. Python utilities calculate financial summaries and expense breakdowns.
4. Plotly visualizations present financial information.
5. The AI advisor uses financial summaries and expense categories to generate recommendations.
6. The user creates savings goals and tracks progress.
7. The application generates a downloadable monthly CSV report.

## Installation and Local Setup

### Prerequisites

- Python 3.12 or another compatible Python version
- Git
- A Groq API key

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd personal-finance-ai-advisor
```

Replace `YOUR_GITHUB_REPOSITORY_URL` with your actual repository URL.

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure the Groq API key

Create `.streamlit/secrets.toml` in the project directory:

```toml
GROQ_API_KEY = "your-groq-api-key"
```

Replace the placeholder with your own API key. Never commit this file or expose the key publicly.

### 5. Run the application

```bash
streamlit run app.py
```

Open the local URL displayed in the terminal.

## Running Tests

Run the automated test suite with:

```bash
python -m unittest discover -s tests -v
```

The project's existing automated tests cover financial calculations and database operations, including savings-goal functionality. Confirm the current test count and results before publishing them in project documentation.

## Deployment

The application is deployed using Streamlit Community Cloud and connected to a GitHub repository.

Deployment requires:

1. A GitHub repository containing the application code.
2. A valid `requirements.txt`.
3. The main application file, `app.py`.
4. The `GROQ_API_KEY` secret configured in Streamlit Community Cloud.
5. Appropriate handling of database persistence and sensitive financial information.

## Security and Limitations

- Never commit API keys, secret configuration files, or private financial databases.
- The application uses SQLite locally. The local database file on Streamlit Community Cloud is not guaranteed to persist indefinitely.
- A persistent database and appropriate authentication and authorization are needed before using this application for real users or sensitive financial records.
- AI-generated recommendations can be inaccurate and should be reviewed critically.
- This application is an educational project and does not provide regulated financial, investment, tax, or legal advice.

## Future Improvements

- Integrate a managed persistent database.
- Add user authentication and per-user data isolation.
- Introduce budgeting limits and spending alerts.
- Add savings-goal recommendations based on cash flow.
- Support PDF reports and richer financial analytics.
- Improve input validation, automated test coverage, and error handling.

## Project Status

**Status:** Deployed and successfully tested.

The core application supports transaction tracking, financial analysis, AI-generated recommendations, savings-goal management, and CSV report downloads.

## Acknowledgments

This project was developed as an AI/ML capstone project to demonstrate the integration of Python application development, financial data processing, relational database operations, generative AI, testing, and cloud deployment.