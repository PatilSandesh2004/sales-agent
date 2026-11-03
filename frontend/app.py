"""Simple & Beginner-Friendly Streamlit Frontend."""

import sys
from pathlib import Path
import streamlit as st
import pandas as pd

# Add backend/src to path
ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_SRC = ROOT_DIR / "backend" / "src"
if str(BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(BACKEND_SRC))

from config import DB_PATH
from infrastructure.database import load_excel_to_sqlite
from agent.sales_agent import sales_agent

st.set_page_config(page_title="Sales Data AI Tool", page_icon="📈", layout="centered")

st.title("📈 Sales Intelligence AI Tool")
st.write("Ask questions in **plain English** to fetch and analyze data from multiple Excel sheets!")

# Check Database
if not DB_PATH.exists():
    with st.spinner("Setting up database from Excel sheets..."):
        load_excel_to_sqlite()

with st.sidebar:
    st.header("⚙️ Controls")
    if st.button("🔄 Reload Excel Sheets"):
        with st.spinner("Reading Excel sheets into database..."):
            load_excel_to_sqlite()
            st.success("Excel sheets reloaded!")

    st.subheader("💡 Example Questions to Try:")
    sample_queries = [
        "What is the total revenue generated in 2025?",
        "Which product generated the highest revenue?",
        "Which sales representative achieved the highest sales?",
        "Compare sales between Bengaluru and Mumbai.",
        "Which customers purchased more than ₹1 lakh?"
    ]
    chosen_sample = st.selectbox("Pick an example:", [""] + sample_queries)

# Input
query = st.text_input("Enter your sales question:", value=chosen_sample)

if st.button("🚀 Run Query", type="primary"):
    if not query.strip():
        st.warning("Please type a question or choose an example from the sidebar.")
    else:
        with st.spinner("AI Tool working..."):
            response = sales_agent.ask(query)

            # 1. Answer
            st.success(f"### 💡 Answer:\n{response.summary_answer}")

            # 2. Tool 1: SQL Generated (if SQL was generated)
            if response.generated_sql and not response.generated_sql.startswith("--"):
                st.subheader("🤖 Tool 1: Generated SQL Query")
                st.code(response.generated_sql, language="sql")

                # 3. Tool 2: Fetched Table
                st.subheader(f"📊 Tool 2: Fetched Data ({response.row_count} rows)")
                if response.data:
                    df = pd.DataFrame(response.data)
                    st.dataframe(df)
                else:
                    st.info("No matching records found in Excel data.")

