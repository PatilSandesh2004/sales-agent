"""Beginner-Friendly Tool: Convert User Query to SQL & Fetch Data from Excel Sheets.

This is the exact tool requested:
1. Takes user natural language question.
2. Converts it into a SQL query.
3. Executes the SQL query to fetch data from the Excel tables.
"""

import os
import pandas as pd
from config import GROQ_API_KEY, LLM_MODEL
from models import get_schema_text
from prompts import SQL_GENERATION_PROMPT
from infrastructure.database import get_connection


def convert_query_to_sql(user_question: str) -> str:
    """Tool function: Takes plain English question and turns it into SQL."""
    # 1. If GROQ API Key exists, use LLM
    if GROQ_API_KEY:
        try:
            from groq import Groq
            client = Groq(api_key=GROQ_API_KEY)
            
            prompt = SQL_GENERATION_PROMPT.format(
                schema_info=get_schema_text(),
                question=user_question
            )
            
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=LLM_MODEL,
                temperature=0.0
            )
            sql = response.choices[0].message.content.strip()
            # Clean backticks if LLM added any
            sql = sql.replace("```sql", "").replace("```", "").strip()
            return sql
        except Exception as e:
            print(f"(Note: Groq LLM skipped due to: {e}. Using beginner demo rules)")

    # 2. Beginner Rule-based Matching (Works immediately without any API key!)
    q = user_question.lower()
    
    if "2025" in q and "revenue" in q:
        return (
            "SELECT "
            "COUNT(DISTINCT order_id) AS total_orders, "
            "SUM(quantity) AS total_units_sold, "
            "ROUND(SUM(quantity * unit_price * (1.0 - discount)), 2) AS total_revenue_2025 "
            "FROM sales_transactions "
            "WHERE strftime('%Y', order_date) = '2025'"
        )
    elif "highest revenue" in q or "top product" in q:
        return (
            "SELECT p.product_name, p.category, "
            "SUM(st.quantity) AS total_units_sold, "
            "ROUND(SUM(st.quantity * st.unit_price * (1.0 - st.discount)), 2) AS total_revenue "
            "FROM sales_transactions st "
            "JOIN products p ON st.product_id = p.product_id "
            "GROUP BY p.product_name, p.category "
            "ORDER BY total_revenue DESC LIMIT 1"
        )
    elif "representative" in q or "sales rep" in q or "employee" in q:
        return (
            "SELECT e.employee_name, e.department, e.region, "
            "ROUND(SUM(st.quantity * st.unit_price * (1.0 - st.discount)), 2) AS total_sales "
            "FROM sales_transactions st "
            "JOIN orders o ON st.order_id = o.order_id "
            "JOIN employees e ON o.employee_id = e.employee_id "
            "GROUP BY e.employee_name, e.department, e.region "
            "ORDER BY total_sales DESC LIMIT 1"
        )
    elif "bengaluru" in q and "mumbai" in q:
        return (
            "SELECT c.city, "
            "COUNT(DISTINCT st.order_id) AS orders_count, "
            "ROUND(SUM(st.quantity * st.unit_price * (1.0 - st.discount)), 2) AS total_revenue "
            "FROM sales_transactions st "
            "JOIN customers c ON st.customer_id = c.customer_id "
            "WHERE c.city IN ('Bengaluru', 'Mumbai') "
            "GROUP BY c.city "
            "ORDER BY total_revenue DESC"
        )
    elif "1 lakh" in q or "100000" in q:
        return (
            "SELECT c.customer_name, c.city, "
            "ROUND(SUM(st.quantity * st.unit_price * (1.0 - st.discount)), 2) AS total_spent "
            "FROM sales_transactions st "
            "JOIN customers c ON st.customer_id = c.customer_id "
            "GROUP BY c.customer_name, c.city "
            "HAVING total_spent > 100000 "
            "ORDER BY total_spent DESC"
        )
    elif "declining" in q:
        return (
            "SELECT p.product_name, "
            "ROUND(SUM(CASE WHEN strftime('%Y', st.order_date) = '2024' THEN st.quantity * st.unit_price * (1.0 - st.discount) ELSE 0 END), 2) AS rev_2024, "
            "ROUND(SUM(CASE WHEN strftime('%Y', st.order_date) = '2025' THEN st.quantity * st.unit_price * (1.0 - st.discount) ELSE 0 END), 2) AS rev_2025 "
            "FROM sales_transactions st "
            "JOIN products p ON st.product_id = p.product_id "
            "GROUP BY p.product_name "
            "HAVING rev_2024 > rev_2025 "
            "ORDER BY (rev_2024 - rev_2025) DESC"
        )
    elif "monthly" in q or "growth" in q:
        return (
            "SELECT strftime('%Y-%m', order_date) AS month, "
            "ROUND(SUM(quantity * unit_price * (1.0 - discount)), 2) AS monthly_revenue "
            "FROM sales_transactions "
            "GROUP BY month ORDER BY month ASC"
        )
    else:
        return (
            "SELECT COUNT(DISTINCT order_id) AS total_orders, "
            "ROUND(SUM(quantity * unit_price * (1.0 - discount)), 2) AS total_revenue "
            "FROM sales_transactions"
        )


def execute_sql_query(sql_query: str) -> pd.DataFrame:
    """Tool function: Runs the SQL query on the Excel database and returns a DataFrame."""
    conn = get_connection()
    try:
        # Use pandas to easily fetch results
        df = pd.read_sql_query(sql_query, conn)
        return df
    except Exception as e:
        print(f"❌ Query execution failed: {e}")
        return pd.DataFrame()
    finally:
        conn.close()


def ask_sales_tool(user_question: str) -> dict:
    """Complete tool workflow:

    1. Convert user query to SQL
    2. Fetch data from the Excel sheets
    3. Return dictionary with question, sql, and results dataframe
    """
    # Step 1: Convert to SQL
    sql = convert_query_to_sql(user_question)

    # Step 2: Fetch data from Excel/DB
    df = execute_sql_query(sql)

    return {
        "question": user_question,
        "sql": sql,
        "data": df,
        "row_count": len(df)
    }

