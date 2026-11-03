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

            # 2. Planner
            if response.plan:
                st.subheader("🧭 Planner")
                st.write(f"**Goal:** {response.plan['goal']}")
                if response.plan.get("metric"):
                    st.caption(f"Metric: {response.plan['metric']}")

            # 3. Each executed step: SQL tool + fetched data
            for i, step in enumerate(response.steps, 1):
                st.subheader(f"Step {i}: {step.description}")
                st.caption(f"Sub-question: {step.sub_question}")
                st.markdown("**🤖 Tool 1: Generated SQL**")
                st.code(step.sql, language="sql")
                st.markdown(f"**📊 Tool 2: Fetched Data ({step.row_count} rows)**")
                if step.data:
                    st.dataframe(pd.DataFrame(step.data))
                else:
                    st.info("No matching records found in Excel data.")
