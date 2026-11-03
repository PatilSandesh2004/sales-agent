# Backend Guide 📘

A quick guide on how each component works and how to run it.

## 1. How Excel Files are Loaded
We read `.xlsx` files using `pandas.read_excel()` and write them to SQLite tables using `df.to_sql(table_name, conn)`:
- `products.xlsx` -> `products` table
- `customers.xlsx` -> `customers` table
- `employees.xlsx` -> `employees` table
- `orders.xlsx` -> `orders` table
- `sales_transactions.xlsx` -> `sales_transactions` table

## 2. How the Tool Converts Queries to SQL
The tool `convert_query_to_sql(user_question)` in `src/tools/sql_tool.py`:
- Formats a prompt with table schemas.
- If `GROQ_API_KEY` is present, uses Groq `llama-3.3-70b-versatile` LLM to write the SQL query.
- If no key is set, it uses beginner rule-based pattern matching so it works immediately offline.

## 3. Running the Demo
```bash
# Run terminal demo:
python backend/src/main.py

# Run Streamlit Web UI:
streamlit run frontend/app.py
```

