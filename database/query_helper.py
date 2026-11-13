from datetime import date, datetime
from decimal import Decimal
from typing import Any

from django.db import connection

def insert_one(sql: str, params: list | None = None) -> int:
    with connection.cursor() as cursor:
        cursor.execute(sql,params or [])
        return cursor.lastrowid
    
def fetch_one(sql: str, params: list | None = None) -> dict | None:
    with connection.cursor() as cursor:
        cursor.execute(sql, params or [])
        row = cursor.fetchone()
        if row is None:
            return None
        columns = _columns_from_cursor(cursor)
        return _row_to_dict(row, columns)

def _columns_from_cursor(cursor)-> list[str]:
    if cursor.description is None:
        return []
    columns = [col[0] for col in cursor.description]
    return columns

def _row_to_dict(row:tuple,columns:list[str])-> dict:
    return dict(zip(columns,row))

def fetchall(sql: str, params: list | None = None) -> list[dict]:
    with connection.cursor() as cursor:
        cursor.execute(sql,params or [])
        columns = _columns_from_cursor(cursor)
        return [_row_to_dict(row, columns) for row in cursor.fetchall()]

def fetch_scalar(
    sql: str, params: list | None = None
) -> Any:
    """
    Execute a query and return a single scalar value.

    Example:
        count = fetch_scalar(
            "SELECT COUNT(*) FROM products WHERE status = %s", ["active"]
        )
    """
    with connection.cursor() as cursor:
        cursor.execute(sql, params or [])
        row = cursor.fetchone()
        if row is None:
            return None
        return row[0]

def serialize_value(value: Any) -> Any:
    """Convert a single DB value to a JSON-serializable type."""
    if value is None:
        return None
    if isinstance(value, Decimal):
        # Keep precision: return as string to avoid float rounding
        return str(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value
    
def serialize_rows(rows: list[dict]) -> list[dict]:
    """Serialize a list of dict rows for JSON output."""
    return [serialize_row(r) for r in rows]

def serialize_row(row: dict) -> dict:
    """Serialize all values in a dict row for JSON output."""
    return {k: serialize_value(v) for k, v in row.items()}