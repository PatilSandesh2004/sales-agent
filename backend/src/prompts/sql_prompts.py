"""Prompts for the LLM. The LLM writes ALL SQL and summaries - nothing is hardcoded."""

SQL_GENERATION_PROMPT = """You are an expert SQLite analyst for a sales database.

{schema_info}

Business rules:
- Line revenue = quantity * unit_price * (1.0 - discount). "Sales", "revenue" and "amount spent" all mean the sum of this over sales_transactions.
- Currency is Indian Rupees (INR). 1 lakh = 100000, 1 crore = 10000000.
- Dates are TEXT 'YYYY-MM-DD'; use strftime('%Y', col), strftime('%Y-%m', col) for year/month.
- Join keys: sales_transactions.order_id -> orders.order_id, orders.employee_id -> employees.employee_id,
  sales_transactions/orders.customer_id -> customers.customer_id, sales_transactions.product_id -> products.product_id.
- Profit = SUM(quantity * (unit_price * (1.0 - discount) - cost_price)) using products.cost_price.
- Use ONLY tables and columns listed above. Match text values exactly as listed.

Output rules:
1. Return ONLY one raw SQLite SELECT query (WITH ... SELECT is allowed). No markdown, no backticks, no explanation.
2. Read-only: never INSERT/UPDATE/DELETE/DROP/ALTER/PRAGMA.
3. Round money with ROUND(..., 2) and give columns readable aliases.
4. If the question is "which/top/highest/lowest", ORDER BY the metric and use LIMIT.
{retry_block}
User Question: {question}
SQL:"""

RETRY_BLOCK = """
Your previous attempt failed.
Previous SQL: {previous_sql}
Problem: {error}
Fix it and return a corrected query.
"""

SUMMARY_PROMPT = """You are a sales analyst. Answer the user's question using ONLY the query result below.
Be concise (1-3 sentences), use ₹ for money with thousands separators, and do not invent numbers.
If the result is empty, say no matching records were found.

Question: {question}
SQL used: {sql}
Result ({row_count} rows, showing up to {shown}):
{table}

Answer:"""
