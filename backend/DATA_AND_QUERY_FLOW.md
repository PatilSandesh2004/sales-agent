# Sales Agent – Dataset, Database & Query Flow

## 1. Big picture

```
 User question (plain English)
        │
        ▼
 ┌───────────────┐   reads live schema    ┌──────────────────────┐
 │  SalesAgent   │ ─────────────────────▶ │  models.py           │
 │ (sales_agent) │                        │  get_schema_text()   │
 └──────┬────────┘                        └──────────┬───────────┘
        │ Tool 1                                      │ PRAGMA / SELECT on sales.db
        ▼                                             ▼
 ┌─────────────────────┐  prompt + schema   ┌──────────────────┐
 │ convert_query_to_sql│ ─────────────────▶ │ Groq LLM         │
 │ (sql_tool.py)       │ ◀───────────────── │ gpt-oss / qwen   │
 └──────┬──────────────┘     raw SQL        └──────────────────┘
        │ clean + validate (SELECT only)
        ▼ Tool 2
 ┌─────────────────────┐  read-only conn    ┌──────────────────┐
 │ execute_sql_query   │ ─────────────────▶ │ SQLite sales.db  │
 └──────┬──────────────┘ ◀───────────────── │ (from Excel)     │
        │  DataFrame                         └──────────────────┘
        │  error? → send error back to LLM, regenerate (max 2 retries)
        ▼
 LLM writes a short answer from the real rows → QueryResponse
 (question, generated_sql, row_count, data, summary_answer)
```

**No SQL is hardcoded anywhere.** The LLM writes every query from the user's question and the live schema.

## 2. The dataset (Excel)

Location: `backend/data/raw/` – five related sheets (a star-like sales model):

| File → table | Rows | Key columns |
|---|---|---|
| `products.xlsx` → `products` | 12 | product_id, product_name, category, cost_price, selling_price |
| `customers.xlsx` → `customers` | 15 | customer_id, customer_name, city, state, customer_segment |
| `employees.xlsx` → `employees` | 8 | employee_id, employee_name, department, region |
| `orders.xlsx` → `orders` | 160 | order_id, customer_id, employee_id, order_date, order_status |
| `sales_transactions.xlsx` → `sales_transactions` | 401 | transaction_id, order_id, product_id, customer_id, quantity, unit_price, discount, order_date |

Relationships (join keys):

```
customers ─┐
           ├─< orders >─ employees
           │     │
           │     └─< sales_transactions >─ products
           └──────────────^ (customer_id)
```

Date range: 2024-01-15 → 2025-12-22. Revenue = `quantity * unit_price * (1 - discount)`.

Verified: no nulls, no duplicate IDs, no orphan foreign keys, order/transaction dates and customers agree, no sale priced below cost.

## 3. How Excel becomes a database

File: `src/infrastructure/database.py` → `load_excel_to_sqlite()`

1. For each Excel file, `pandas.read_excel()` loads the sheet into a DataFrame.
2. `df.to_sql(table_name, conn, if_exists="replace")` writes it as a table in SQLite.
3. The SQLite file is `backend/data/sales.db` (created automatically; git-ignored).
4. `main.py` reloads the Excel files on every start, so the DB always matches the sheets. The Streamlit app has a "Reload Excel Sheets" button.

Config (`src/config.py`): `DB_PATH`, `RAW_EXCEL_DIR`, `GROQ_API_KEY`, `LLM_MODEL` (read from `backend/.env`).

## 4. How the DB is connected

Two connection helpers in `database.py`:

- `get_connection()` – read/write, used **only** by the Excel loader.
- `get_readonly_connection()` – opens SQLite with `mode=ro`. Used for schema discovery and for **every query the LLM generates**, so a generated query can never change data.

## 5. How a question becomes a query (step by step)

Example: *"Which sales representative achieved the highest sales?"*

1. **Schema discovery** (`models.py → get_schema_text()`): reads table names, columns, types, row counts, and either all distinct values (small text columns such as `city`, `category`, `region`) or min..max (ids, dates, numbers). This tells the LLM exact spellings like `Bengaluru`. Because it is read from the DB, adding a column or sheet needs no code change.
2. **Prompt building** (`prompts/sql_prompts.py`): schema + business rules (revenue formula, INR / lakh = 100000, SQLite date functions, join keys, SELECT-only) + the user's question.
3. **Tool 1 – `convert_query_to_sql`** (`tools/sql_tool.py`): sends the prompt to Groq (`temperature=0`), then:
   - `clean_sql()` removes ```` ``` ```` fences, `<think>…</think>` blocks (Qwen) and trailing `;`.
   - `validate_sql()` accepts only one `SELECT`/`WITH` statement and rejects `INSERT/UPDATE/DELETE/DROP/ALTER/PRAGMA/ATTACH…`.
4. **Tool 2 – `execute_sql_query`**: runs the SQL with `pandas.read_sql_query` on the read-only connection and returns a DataFrame.
5. **Self-correction** (`ask_sales_tool`): if the SQL errors (wrong column, syntax…), the failed SQL and the error message are put into the next prompt and the LLM regenerates. Up to 2 retries.
6. **Answer** (`agent/sales_agent.py`): the LLM gets the question, the SQL and up to 20 result rows and writes a 1–3 sentence answer using only those numbers. If that call fails, a generic "N records returned" message is used.
7. **Response** (`schema/query_schema.py → QueryResponse`): returned to the CLI (`main.py`) or Streamlit (`frontend/app.py`), which show the answer, the generated SQL, and the data table.

Greetings ("hi", "help") skip SQL. If the API key is missing, or no working query can be produced, the user gets a clear message instead of a fake answer.

## 6. Files at a glance

| File | Role |
|---|---|
| `data/raw/*.xlsx` | Source data |
| `src/config.py` | Paths, API key, model name |
| `src/infrastructure/database.py` | Excel → SQLite loader, DB connections |
| `src/models.py` | Live schema description for the prompt |
| `src/prompts/sql_prompts.py` | SQL, retry and summary prompts |
| `src/tools/sql_tool.py` | Tool 1 (question → SQL), Tool 2 (execute), validation, retry |
| `src/agent/sales_agent.py` | Orchestrates the tools and writes the answer |
| `src/main.py` | Interactive CLI |
| `../frontend/app.py` | Streamlit UI |

## 7. Setup & running

`backend/.env` (git-ignored – never commit it):

```
GROQ_API_KEY=<your key>
LLM_MODEL=openai/gpt-oss-120b      # or qwen/qwen3-32b
```

Run:

```
pip install -r requirements.txt
cd backend
python src/main.py                 # CLI  (Windows: set PYTHONIOENCODING=utf-8 first)
# or, from the project root:
streamlit run frontend/app.py      # UI
```

To switch models, change only `LLM_MODEL` in `.env`.

## 8. Limitations (demo scope)

- Answer quality depends on the LLM; the retry loop fixes most SQL errors but not wrong interpretations – always check the displayed SQL.
- Each question is independent (no conversation memory).
- Data is small and static; the schema sampler is designed for small dimension tables, not large databases.
