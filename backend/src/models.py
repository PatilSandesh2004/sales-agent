"""Database Models & Table Descriptions (Beginner Friendly)."""

# List of all tables and columns present in our Excel files and database
TABLE_SCHEMAS = {
    "products": [
        "product_id (e.g. P101)",
        "product_name (e.g. UltraHD 4K Smart TV)",
        "category (Electronics, Audio, Furniture, etc.)",
        "cost_price",
        "selling_price"
    ],
    "customers": [
        "customer_id (e.g. C001)",
        "customer_name",
        "city (Bengaluru, Mumbai, Delhi, etc.)",
        "state",
        "customer_segment (Enterprise, SME, Corporate, Consumer)"
    ],
    "employees": [
        "employee_id (e.g. E001)",
        "employee_name",
        "department",
        "region (South, West, North)"
    ],
    "orders": [
        "order_id (e.g. ORD-1001)",
        "customer_id",
        "employee_id",
        "order_date (YYYY-MM-DD)",
        "order_status (Completed, Delivered)"
    ],
    "sales_transactions": [
        "transaction_id (e.g. TXN-5001)",
        "order_id",
        "product_id",
        "customer_id",
        "quantity",
        "unit_price",
        "discount (0.0 to 1.0)",
        "order_date (YYYY-MM-DD)"
    ]
}

def get_schema_text() -> str:
    """Returns a simple text summary of all database tables for the AI prompt."""
    text_lines = ["Available Database Tables & Columns:\n"]
    for table_name, cols in TABLE_SCHEMAS.items():
        text_lines.append(f"Table '{table_name}':")
        for col in cols:
            text_lines.append(f"  - {col}")
        text_lines.append("")
    text_lines.append("Formulas:")
    text_lines.append("- Revenue = quantity * unit_price * (1.0 - discount)")
    return "\n".join(text_lines)

