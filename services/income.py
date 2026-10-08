import streamlit as st
from db.connection import get_connection
from services.expenses import _validate_amount, _validate_timestamp

def add_income(amount, source: str, timestamp: str = None, note: str = "") -> int:
    """Inserts a new income entry and returns its income_id."""
    amount = _validate_amount(amount)
    timestamp = _validate_timestamp(timestamp)

    source = source.strip()
    if not source:
        raise ValueError("Source cannot be empty.")

    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO INCOME (amount, source, timestamp, note)
            VALUES (?, ?, ?, ?);
            """,
            (amount, source, timestamp, note.strip() if note else None),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

@st.cache_data
def get_income(month: str = None, source: str = None) -> list[dict]:
    """Returns income entries, optionally filtered by month ('YYYY-MM') and/or source."""
    query = "SELECT * FROM INCOME WHERE 1=1"
    params = []

    if month:
        query += " AND strftime('%Y-%m', timestamp) = ?"
        params.append(month)

    if source:
        query += " AND source = ?"
        params.append(source)

    query += " ORDER BY timestamp DESC;"

    conn = get_connection()
    try:
        rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

def update_income(income_id: int, **fields) -> None:
    """Updates one or more fields (amount, source, timestamp, note) on an existing income entry."""
    if not fields:
        raise ValueError("No fields provided to update.")

    allowed = {"amount", "source", "timestamp", "note"}
    unknown = set(fields) - allowed
    if unknown:
        raise ValueError(f"Cannot update unknown fields: {unknown}")

    if "amount" in fields:
        fields["amount"] = _validate_amount(fields["amount"])
    if "timestamp" in fields:
        fields["timestamp"] = _validate_timestamp(fields["timestamp"])
    if "source" in fields:
        fields["source"] = fields["source"].strip()
        if not fields["source"]:
            raise ValueError("Source cannot be empty.")

    conn = get_connection()
    try:
        set_clause = ", ".join(f"{col} = ?" for col in fields)
        values = list(fields.values()) + [income_id]

        cursor = conn.execute(
            f"UPDATE INCOME SET {set_clause} WHERE income_id = ?;", values
        )
        if cursor.rowcount == 0:
            raise ValueError(f"No income entry with id {income_id}.")
        conn.commit()
    finally:
        conn.close()

def delete_income(income_id: int) -> None:
    """Deletes an income entry by id."""
    conn = get_connection()
    try:
        cursor = conn.execute(
            "DELETE FROM INCOME WHERE income_id = ?;", (income_id,)
        )
        if cursor.rowcount == 0:
            raise ValueError(f"No income entry with id {income_id}.")
        conn.commit()
    finally:
        conn.close()

@st.cache_data
def get_monthly_income_total(month: str) -> int:
    """
    Returns total income for the given month ('YYYY-MM'), or 0 if none.
    """
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT SUM(amount) AS total FROM INCOME WHERE strftime('%Y-%m', timestamp) = ?;",
            (month,),
        ).fetchone()
        return row["total"] or 0
    finally:
        conn.close()