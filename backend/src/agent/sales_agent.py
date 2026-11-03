"""Sales Intelligence Agent: question -> LLM-written SQL -> data -> grounded answer."""

from tools.sql_tool import ask_sales_tool, call_llm, SQLToolError
from prompts import SUMMARY_PROMPT
from schema.query_schema import QueryResponse

GREETING_WORDS = {"hi", "hello", "hey", "hola", "help", "good morning", "good evening", "good afternoon", "who are you"}
MAX_ROWS_FOR_SUMMARY = 20


class SalesAgent:
    """Agent that orchestrates the two tools and explains the result."""

    def __init__(self):
        self.name = "Sales Intelligence Agent"

    def ask(self, user_question: str) -> QueryResponse:
        cleaned_q = user_question.strip().lower()

        if cleaned_q in GREETING_WORDS or len(cleaned_q) <= 2:
            return QueryResponse(
                question=user_question,
                generated_sql="-- No SQL needed for greeting",
                row_count=0,
                data=[],
                summary_answer=(
                    "Hello! 👋 I am your Sales Intelligence Assistant.\n\n"
                    "Ask me anything about your sales data in plain English, e.g.:\n"
                    "• What is the total revenue generated in 2025?\n"
                    "• Which product generated the highest revenue?\n"
                    "• Which sales representative achieved the highest sales?\n"
                    "• Compare sales between Bengaluru and Mumbai.\n"
                    "• Which customers purchased more than ₹1 lakh?"
                ),
            )

        try:
            result = ask_sales_tool(user_question)  # Tool 1 (LLM -> SQL) + Tool 2 (execute)
        except SQLToolError as e:
            return QueryResponse(
                question=user_question,
                generated_sql="-- SQL could not be generated",
                row_count=0,
                data=[],
                summary_answer=f"⚠️ {e}",
            )

        df = result["data"]
        return QueryResponse(
            question=user_question,
            generated_sql=result["sql"],
            row_count=result["row_count"],
            data=df.to_dict(orient="records") if not df.empty else [],
            summary_answer=self._create_summary(user_question, result["sql"], df),
        )

    def _create_summary(self, question: str, sql: str, df) -> str:
        """LLM writes the answer from the real result rows; generic fallback if the LLM call fails."""
        if df.empty:
            return "No matching records were found in the sales data."
        shown = df.head(MAX_ROWS_FOR_SUMMARY)
        try:
            return call_llm(SUMMARY_PROMPT.format(
                question=question, sql=sql, row_count=len(df), shown=len(shown),
                table=shown.to_string(index=False),
            ))
        except Exception:
            return f"Query returned {len(df)} record(s). See the data table for details."


sales_agent = SalesAgent()
