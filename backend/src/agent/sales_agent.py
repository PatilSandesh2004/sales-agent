"""Beginner-Friendly Sales Intelligence Agent."""

from tools.sql_tool import convert_query_to_sql, execute_sql_query
from schema.query_schema import QueryResponse


GREETING_WORDS = {"hi", "hello", "hey", "hola", "help", "good morning", "good evening", "good afternoon", "who are you"}


class SalesAgent:
    """Agent that orchestrates converting natural language to SQL and retrieving data."""

    def __init__(self):
        self.name = "Sales Intelligence Agent"

    def ask(self, user_question: str) -> QueryResponse:
        """Runs the simple 3-step agent workflow:

        1. Convert question to SQL using the SQL tool.
        2. Execute SQL against the Excel tables in SQLite.
        3. Format a friendly summary answer.
        """
        cleaned_q = user_question.strip().lower()

        # Handle greetings and conversational questions without running SQL
        if cleaned_q in GREETING_WORDS or len(cleaned_q) <= 2:
            return QueryResponse(
                question=user_question,
                generated_sql="-- No SQL needed for greeting",
                row_count=0,
                data=[],
                summary_answer=(
                    "Hello! 👋 I am your Sales Intelligence Assistant.\n\n"
                    "Ask me questions about your sales data in plain English, for example:\n"
                    "• *What is the total revenue generated in 2025?*\n"
                    "• *Which product generated the highest revenue?*\n"
                    "• *Which sales representative achieved the highest sales?*\n"
                    "• *Compare sales between Bengaluru and Mumbai.*\n"
                    "• *Which customers purchased more than ₹1 lakh?*"
                )
            )

        # Step 1: Tool Call to convert question -> SQL
        generated_sql = convert_query_to_sql(user_question)

        # Step 2: Tool Call to execute SQL -> DataFrame
        df_result = execute_sql_query(generated_sql)
        row_count = len(df_result)

        # Step 3: Format easy natural language summary
        summary = self._create_summary(user_question, df_result)

        # Convert dataframe to list of dicts for clean JSON/Pydantic serialization
        records = df_result.to_dict(orient="records") if not df_result.empty else []

        return QueryResponse(
            question=user_question,
            generated_sql=generated_sql,
            row_count=row_count,
            data=records,
            summary_answer=summary
        )

    def _create_summary(self, question: str, df) -> str:
        """Creates a simple, factual answer from the dataframe without hallucination."""
        if df.empty:
            return "No matching sales records were found in the Excel data."

        q = question.lower()
        first_row = df.iloc[0].to_dict()

        if "2025" in q:
            rev = first_row.get("total_revenue_2025", first_row.get("total_revenue", 0))
            orders = first_row.get("total_orders", "N/A")
            return f"In 2025, total sales revenue was ₹{rev:,.2f} across {orders} orders."
        elif "highest revenue" in q or "top product" in q:
            prod = first_row.get("product_name", "Unknown")
            rev = first_row.get("total_revenue", 0)
            return f"The product with the highest revenue is '{prod}' with ₹{rev:,.2f} in total sales."
        elif "representative" in q or "sales rep" in q:
            rep = first_row.get("employee_name", "Unknown")
            sales = first_row.get("total_sales", 0)
            dept = first_row.get("department", "")
            return f"The top sales representative is {rep} ({dept}) with total closed sales of ₹{sales:,.2f}."
        elif "bengaluru" in q and "mumbai" in q:
            return f"Comparison complete. Found {len(df)} city records. Review the data table below for details."
        elif "1 lakh" in q or "100000" in q:
            return f"Found {len(df)} high-value customers who spent more than ₹1,00,000."
        else:
            return f"Query returned {len(df)} matching record(s) from the sales database."


# Singleton agent instance
sales_agent = SalesAgent()

