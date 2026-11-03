"""Sales Intelligence Agent: question -> LLM-written SQL -> data -> grounded answer."""

import pandas as pd
from tools.sql_tool import ask_sales_tool, call_llm, SQLToolError
from prompts import SUMMARY_PROMPT
from schema.query_schema import QueryResponse, StepResult
from agent.planner import create_plan

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

        # Step 0: PLANNER - LLM decides how to answer (1-3 sub-questions)
        try:
            plan = create_plan(user_question)
            plan_hint = f"Goal: {plan.goal}\nTables: {', '.join(plan.tables)}\nMetric: {plan.metric}"
        except SQLToolError as e:
            return self._error_response(user_question, e)

        # Steps 1..n: for each plan step -> Tool 1 (LLM -> SQL) + Tool 2 (execute)
        results = []
        for step in plan.steps:
            try:
                r = ask_sales_tool(step.sub_question, plan_hint=f"{plan_hint}\nThis step: {step.description}")
            except SQLToolError as e:
                return self._error_response(user_question, e, plan=plan.model_dump())
            df = r["data"]
            results.append(StepResult(
                description=step.description, sub_question=step.sub_question, sql=r["sql"],
                row_count=r["row_count"], data=df.to_dict(orient="records") if not df.empty else [],
            ))

        last = results[-1]
        return QueryResponse(
            question=user_question,
            generated_sql="\n\n".join(r.sql for r in results),
            row_count=last.row_count,
            data=last.data,
            summary_answer=self._create_summary(user_question, results),
            plan=plan.model_dump(),
            steps=results,
        )

    @staticmethod
    def _error_response(question, error, plan=None) -> QueryResponse:
        return QueryResponse(
            question=question, generated_sql="-- SQL could not be generated", row_count=0,
            data=[], summary_answer=f"⚠️ {error}", plan=plan,
        )

    def _create_summary(self, question: str, results) -> str:
        """LLM writes the answer from ALL step results; generic fallback if the LLM call fails."""
        if all(r.row_count == 0 for r in results):
            return "No matching records were found in the sales data."
        sql_text = "\n".join(r.sql for r in results)
        tables = []
        for i, r in enumerate(results, 1):
            shown = pd.DataFrame(r.data).head(MAX_ROWS_FOR_SUMMARY)
            tables.append(f"[Step {i}: {r.description}] ({r.row_count} rows)\n" + (shown.to_string(index=False) if not shown.empty else "(no rows)"))
        try:
            return call_llm(SUMMARY_PROMPT.format(
                question=question, sql=sql_text, row_count=sum(r.row_count for r in results),
                shown=MAX_ROWS_FOR_SUMMARY, table="\n\n".join(tables),
            ))
        except Exception:
            return f"Query returned {results[-1].row_count} record(s). See the data table for details."


sales_agent = SalesAgent()
