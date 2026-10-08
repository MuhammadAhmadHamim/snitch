"""
Generates realistic sample data into demo.db, for screenshots and anyone
cloning the repo to try the app without needing their own real data.

Run with: python -m scripts.seed_demo
"""
import os
os.environ["SNITCH_DB"] = "demo.db"

import random
from datetime import date, timedelta

from db.schema import init_db, seed_default_categories
from services.categories import list_categories
from services.expenses import add_expense
from services.income import add_income

random.seed(42)  # reproducible output, run it twice, get the same data

init_db()
seed_default_categories()

categories = {c["name"]: c["category_id"] for c in list_categories()}

# Rough weekly spending patterns per category, (min, max) per transaction
PATTERNS = {
    "Food": (80, 350),
    "Transport": (30, 150),
    "Laundry": (50, 100),
    "Snacks": (20, 80),
    "Study": (100, 500),
    "Other": (30, 200),
}

today = date.today()
start = today - timedelta(days=150)  # 5 months back

current = start
while current <= today:
    # 1-3 expenses on roughly 70% of days
    if random.random() < 0.7:
        for _ in range(random.randint(1, 3)):
            category_name = random.choice(list(PATTERNS.keys()))
            low, high = PATTERNS[category_name]
            amount = random.randint(low, high)
            hour = random.choice([8, 9, 13, 14, 19, 20, 21])
            minute = random.randint(0, 59)
            timestamp = f"{current.isoformat()} {hour:02d}:{minute:02d}:00"

            add_expense(
                amount=amount,
                category_id=categories[category_name],
                timestamp=timestamp,
                note="",
            )
    current += timedelta(days=1)

# Monthly allowance, first of each month, plus a few irregular gifts
current = start.replace(day=1)
while current <= today:
    timestamp = f"{current.isoformat()} 09:00:00"
    add_income(amount=15000, source="Allowance", timestamp=timestamp)
    current += timedelta(days=32)
    current = current.replace(day=1)

# A few irregular extra income events
for _ in range(4):
    offset = random.randint(0, 150)
    income_date = start + timedelta(days=offset)
    timestamp = f"{income_date.isoformat()} 12:00:00"
    add_income(
        amount=random.choice([1000, 2000, 3000]),
        source=random.choice(["Gift", "Part-time"]),
        timestamp=timestamp,
    )

print("Demo data seeded into demo.db")