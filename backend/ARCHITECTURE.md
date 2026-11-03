# Architecture Overview 🏛️

This application demonstrates a simple, beginner-friendly tool-using pattern for querying Excel datasets using SQL.

## High-Level Architecture Flow

```
[User Plain English Question]
            │
            ▼
┌──────────────────────────────────────┐
│ Tool 1: convert_query_to_sql()       │
│ Converts English question to SQLite  │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│ Tool 2: execute_sql_query()          │
│ Executes SQL on SQLite tables loaded │
│ directly from Excel files            │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│ SalesAgent: Factual Summary          │
│ Displays generated SQL + data table  │
└──────────────────────────────────────┘
```

## Directory Structure
- `src/agent/`: Sales agent orchestration.
- `src/infrastructure/`: SQLite connection & Excel reader.
- `src/prompts/`: System instructions for SQL query generation.
- `src/routers/`: Request handlers.
- `src/schema/`: Pydantic data schemas.
- `src/scripts/`: Standalone scripts like `load_excel.py`.
- `src/tools/`: **Core SQL tool** converting user query to SQL and fetching data.
- `src/models.py`: Database table descriptions.
- `src/config.py`: App configurations.
- `src/main.py`: Entry point for terminal demo.

