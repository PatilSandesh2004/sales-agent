"""Executable script to initialize the SQLite database from Excel files."""

import sys
from pathlib import Path

# Add src to Python path
SRC_DIR = Path(__file__).resolve().parent.parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from infrastructure.database import load_excel_to_sqlite

if __name__ == "__main__":
    print("🚀 Initializing Sales Database...")
    result = load_excel_to_sqlite()
    print("Summary of loaded tables:")
    for table, count in result.items():
        print(f"  • {table}: {count} records")

