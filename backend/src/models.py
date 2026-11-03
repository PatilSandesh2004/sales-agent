"""Database schema description, read LIVE from the database.

Nothing is hardcoded here: tables, columns, types and example values are
discovered from SQLite, so if the Excel files change the LLM sees the new
structure automatically.
"""

from infrastructure.database import get_readonly_connection

MAX_DISTINCT_TO_LIST = 15  # list every value for low-cardinality text columns


def get_schema_text() -> str:
    """Builds a schema description (tables, columns, sample values, ranges) for the LLM prompt."""
    conn = get_readonly_connection()
    try:
        cur = conn.cursor()
        tables = [r[0] for r in cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        )]
        lines = ["Database tables (SQLite):", ""]
        for table in tables:
            row_count = cur.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
            lines.append(f"Table {table} ({row_count} rows):")
            for _, col, col_type, *_ in cur.execute(f'PRAGMA table_info("{table}")').fetchall():
                lines.append(f"  - {col} ({col_type or 'TEXT'}){_describe_column(cur, table, col, col_type)}")
            lines.append("")
        return "\n".join(lines)
    finally:
        conn.close()


def _describe_column(cur, table: str, col: str, col_type: str) -> str:
    """Returns a short hint: all values for small text columns, min/max for numbers/ids/dates."""
    distinct = cur.execute(f'SELECT COUNT(DISTINCT "{col}") FROM "{table}"').fetchone()[0]
    if "TEXT" in (col_type or "").upper() and not col.endswith("_id") and distinct <= MAX_DISTINCT_TO_LIST:
        values = [str(r[0]) for r in cur.execute(
            f'SELECT DISTINCT "{col}" FROM "{table}" WHERE "{col}" IS NOT NULL ORDER BY 1'
        )]
        return f" values: {', '.join(values)}"
    low, high = cur.execute(f'SELECT MIN("{col}"), MAX("{col}") FROM "{table}"').fetchone()
    return f" range: {low} .. {high}"
