from db.connection import DB_PATH
from db.connection import get_connection

SCHEMA = """
CREATE TABLE IF NOT EXISTS CATEGORY (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    UNIQUE (name)
);

CREATE TABLE IF NOT EXISTS EXPENSE (
    expense_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    amount      INTEGER NOT NULL CHECK (amount > 0),
    timestamp   TEXT NOT NULL,
    note        TEXT,
    created_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    category_id INTEGER NOT NULL,
    FOREIGN KEY (category_id) REFERENCES CATEGORY(category_id)
);

CREATE TABLE IF NOT EXISTS INCOME (
    income_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    amount      INTEGER NOT NULL CHECK (amount > 0),
    source      TEXT NOT NULL,
    timestamp   TEXT NOT NULL,
    note        TEXT,
    created_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_expense_timestamp ON EXPENSE(timestamp);
CREATE INDEX IF NOT EXISTS idx_income_timestamp ON INCOME(timestamp);
"""

DEFAULT_CATEGORIES = [
    "Food", "Transport", "Laundry", "Snacks", "Study", "Other",
]

def init_db() -> None:
    """Creates all tables and indexes if they don't already exist."""
    conn = get_connection()
    try:
        conn.executescript(SCHEMA)
        conn.commit()
    finally:
        conn.close()

def seed_default_categories() -> None:
    """Inserts the default category list, skipping any that already exist."""
    conn = get_connection()
    try:
        conn.executemany(
            "INSERT OR IGNORE INTO CATEGORY (name) VALUES (?);",
            [(name,) for name in DEFAULT_CATEGORIES],
        )
        conn.commit()
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
    seed_default_categories()
    print(f"Database initialized at {DB_PATH}")