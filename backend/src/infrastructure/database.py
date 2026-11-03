"""Database infrastructure: simple SQLite connection & Excel sheet loader."""

import sqlite3
from pathlib import Path
import pandas as pd
from config import DB_PATH, RAW_EXCEL_DIR


def get_connection() -> sqlite3.Connection:
    """Connects to the SQLite database."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(str(DB_PATH))


def get_readonly_connection() -> sqlite3.Connection:
    """Read-only connection: even a bad generated query can never modify the data."""
    return sqlite3.connect(f"file:{DB_PATH.as_posix()}?mode=ro", uri=True)


def load_excel_to_sqlite():
    """Reads Excel sheets using Pandas and saves each into a table in SQLite."""
    print("📂 Loading Excel sheets into SQLite database...")
    conn = get_connection()

    excel_files = {
        "products": RAW_EXCEL_DIR / "products.xlsx",
        "customers": RAW_EXCEL_DIR / "customers.xlsx",
        "employees": RAW_EXCEL_DIR / "employees.xlsx",
        "orders": RAW_EXCEL_DIR / "orders.xlsx",
        "sales_transactions": RAW_EXCEL_DIR / "sales_transactions.xlsx",
    }

    loaded_counts = {}
    for table_name, file_path in excel_files.items():
        if file_path.exists():
            df = pd.read_excel(file_path)
            # Write directly to SQLite table
            df.to_sql(table_name, conn, if_exists="replace", index=False)
            loaded_counts[table_name] = len(df)
            print(f"  ✓ Loaded table '{table_name}' ({len(df)} rows)")
        else:
            print(f"  ⚠️ Warning: {file_path.name} not found in {RAW_EXCEL_DIR}")

    conn.close()
    print("✅ All Excel sheets successfully loaded!\n")
    return loaded_counts

