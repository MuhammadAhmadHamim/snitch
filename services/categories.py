import sqlite3
from db.connection import get_connection

def list_categories() -> list[dict]:
    """Returns all categories, ordered alphabetically."""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT category_id, name FROM CATEGORY ORDER BY name;"
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

def add_category(name: str) -> int:
    """Inserts a new category and returns its category_id."""
    name = name.strip()
    if not name:
        raise ValueError("Category name cannot be empty.")

    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO CATEGORY (name) VALUES (?);", (name,)
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        raise ValueError(f"Category '{name}' already exists.")
    finally:
        conn.close()

def rename_category(category_id: int, new_name: str) -> None:
    """Renames an existing category."""
    new_name = new_name.strip()
    if not new_name:
        raise ValueError("Category name cannot be empty.")

    conn = get_connection()
    try:
        cursor = conn.execute(
            "UPDATE CATEGORY SET name = ? WHERE category_id = ?;",
            (new_name, category_id),
        )
        if cursor.rowcount == 0:
            raise ValueError(f"No category with id {category_id}.")
        conn.commit()
    except sqlite3.IntegrityError:
        raise ValueError(f"Category '{new_name}' already exists.")
    finally:
        conn.close()

def delete_category(category_id: int) -> None:
    """Deletes a category, refusing if any expense still references it."""
    conn = get_connection()
    try:
        in_use = conn.execute(
            "SELECT COUNT(*) FROM EXPENSE WHERE category_id = ?;",
            (category_id,),
        ).fetchone()[0]

        if in_use > 0:
            raise ValueError(
                f"Cannot delete category: {in_use} expense(s) still use it."
            )

        cursor = conn.execute(
            "DELETE FROM CATEGORY WHERE category_id = ?;", (category_id,)
        )
        if cursor.rowcount == 0:
            raise ValueError(f"No category with id {category_id}.")
        conn.commit()
    finally:
        conn.close()