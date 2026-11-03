"""Simple query router / handler."""

from agent.sales_agent import sales_agent
from schema.query_schema import QueryRequest, QueryResponse


def handle_user_query(request: QueryRequest) -> QueryResponse:
    """Processes user query through the sales agent and returns structured response."""
    return sales_agent.ask(request.question)

