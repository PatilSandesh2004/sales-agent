"""Planner: the LLM reads the question + live schema and decides HOW to answer it.

Output is a small plan: what is asked, which tables/metric, and 1-3 steps.
Each step is a plain-English sub-question that the SQL tool turns into one query.
Nothing is hardcoded - the plan is generated per question.
"""

import json
import re
from typing import List
from pydantic import BaseModel, Field

from models import get_schema_text
from prompts import PLANNER_PROMPT
from tools.sql_tool import call_llm, SQLToolError

MAX_STEPS = 3


class PlanStep(BaseModel):
    description: str
    sub_question: str


class Plan(BaseModel):
    goal: str
    tables: List[str] = Field(default_factory=list)
    metric: str = ""
    steps: List[PlanStep]


def _single_step_plan(question: str, note: str = "") -> Plan:
    """Safe fallback: treat the whole question as one step (the SQL tool still writes the query)."""
    return Plan(goal=question, steps=[PlanStep(description=note or "Answer the question directly", sub_question=question)])


def create_plan(question: str) -> Plan:
    """Asks the LLM for a JSON plan. Falls back to one step if the reply can't be parsed."""
    prompt = PLANNER_PROMPT.format(schema_info=get_schema_text(), question=question, max_steps=MAX_STEPS)
    try:
        raw = call_llm(prompt)
    except SQLToolError:
        raise  # missing API key must reach the user
    except Exception:
        return _single_step_plan(question, "Planner unavailable - answering directly")

    raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL | re.IGNORECASE)
    match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
    try:
        plan = Plan(**json.loads(match.group(0)))
        plan.steps = [s for s in plan.steps if s.sub_question.strip()][:MAX_STEPS]
        if not plan.steps:
            raise ValueError("empty plan")
        return plan
    except Exception:
        return _single_step_plan(question, "Could not parse plan - answering directly")
