import sqlite3
from datetime import datetime
import streamlit as st

from db.connection import get_connection

def _validate_amount(amount) -> int:
    if not isinstance(amount, (int, float)) or amount <= 0:
        raise ValueError("Amount must be a positive number.")
    return int(amount)

def _validate_timestamp(timestamp: str | None) -> str:
    if timestamp is None:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        parsed = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        raise ValueError(
            "Timestamp must be in 'YYYY-MM-DD HH:MM:SS' format."
        )

    if parsed > datetime.now():
        raise ValueError("Timestamp cannot be in the future.")

    return timestamp

def _category_exists(conn, category_id: int) -> bool:
    row = conn.execute(
        "SELECT 1 FROM CATEGORY WHERE category_id = ?;", (category_id,)
    ).fetchone()
    return row is not None

def add_expense(amount, category_id: int, timestamp: str = None, note: str = "") -> int:
    """Inserts a new expense and returns its expense_id."""
    amount = _validate_amount(amount)
    timestamp = _validate_timestamp(timestamp)

    conn = get_connection()
    try:
        if not _category_exists(conn, category_id):
            raise ValueError(f"Category {category_id} does not exist.")

        cursor = conn.execute(
            """
            INSERT INTO EXPENSE (amount, category_id, timestamp, note)
            VALUES (?, ?, ?, ?);
            """,
            (amount, category_id, timestamp, note.strip() if note else None),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

@st.cache_data
def get_expenses(month: str = None, category_id: int = None) -> list[dict]:
    """Returns expenses, optionally filtered by month ('YYYY-MM') and/or category_id."""
    query = "SELECT * FROM EXPENSE WHERE 1=1"
    params = []

    if month:
        query += " AND strftime('%Y-%m', timestamp) = ?"
        params.append(month)

    if category_id:
        query += " AND category_id = ?"
        params.append(category_id)

    query += " ORDER BY timestamp DESC;"

    conn = get_connection()
    try:
        rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

def update_expense(expense_id: int, **fields) -> None:
    """Updates one or more fields (amount, category_id, timestamp, note) on an existing expense."""
    if not fields:
        raise ValueError("No fields provided to update.")

    allowed = {"amount", "category_id", "timestamp", "note"}
    unknown = set(fields) - allowed
    if unknown:
        raise ValueError(f"Cannot update unknown fields: {unknown}")

    if "amount" in fields:
        fields["amount"] = _validate_amount(fields["amount"])
    if "timestamp" in fields:
        fields["timestamp"] = _validate_timestamp(fields["timestamp"])

    conn = get_connection()
    try:
        if "category_id" in fields and not _category_exists(conn, fields["category_id"]):
            raise ValueError(f"Category {fields['category_id']} does not exist.")

        set_clause = ", ".join(f"{col} = ?" for col in fields)
        values = list(fields.values()) + [expense_id]

        cursor = conn.execute(
            f"UPDATE EXPENSE SET {set_clause} WHERE expense_id = ?;", values
        )
        if cursor.rowcount == 0:
            raise ValueError(f"No expense with id {expense_id}.")
        conn.commit()
    finally:
        conn.close()

def delete_expense(expense_id: int) -> None:
    """Deletes an expense by id."""
    conn = get_connection()
    try:
        cursor = conn.execute(
            "DELETE FROM EXPENSE WHERE expense_id = ?;", (expense_id,)
        )
        if cursor.rowcount == 0:
            raise ValueError(f"No expense with id {expense_id}.")
        conn.commit()
    finally:
        conn.close()

@st.cache_data
def get_category_totals(month: str) -> list[dict]:
    """
    Returns total spending per category for the given month ('YYYY-MM'),
    only including categories that have at least one expense that month.
    """
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT c.name AS category, SUM(e.amount) AS total
            FROM EXPENSE e
            JOIN CATEGORY c ON e.category_id = c.category_id
            WHERE strftime('%Y-%m', e.timestamp) = ?
            GROUP BY c.name
            ORDER BY total DESC;
            """,
            (month,),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

@st.cache_data
def get_daily_totals(month: str) -> list[dict]:
    """
    Returns total spending per day for the given month ('YYYY-MM').
    """
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT DATE(timestamp) AS day, SUM(amount) AS total
            FROM EXPENSE
            WHERE strftime('%Y-%m', timestamp) = ?
            GROUP BY DATE(timestamp)
            ORDER BY day;
            """,
            (month,),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()