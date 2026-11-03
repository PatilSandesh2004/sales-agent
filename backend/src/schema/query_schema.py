"""Pydantic schemas for questions and query results."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """User input question."""
    question: str = Field(..., description="Sales intelligence question in plain English")


class QueryResponse(BaseModel):
    """Agent response containing answer, SQL, and data table."""
    question: str
    generated_sql: str
    row_count: int
    data: List[Dict[str, Any]] = Field(default_factory=list)
    summary_answer: str

