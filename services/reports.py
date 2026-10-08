import streamlit as st
from datetime import datetime, date, timedelta
from calendar import monthrange
from dateutil.relativedelta import relativedelta

from db.connection import get_connection

def get_last_n_months(n: int = 6, end_month: str = None) -> list[str]:
    """
    Returns the last n months ending at end_month ('YYYY-MM', inclusive),
    oldest first. Defaults to ending at the current month if not given.
    """
    if end_month:
        end_date = datetime.strptime(end_month, "%Y-%m").date()
    else:
        end_date = date.today()

    months = []
    for i in range(n - 1, -1, -1):
        month = end_date - relativedelta(months=i)
        months.append(month.strftime("%Y-%m"))
    return months

@st.cache_data
def get_monthly_trend(n: int = 6, end_month: str = None) -> list[dict]:
    """
    Returns income and expense totals for the n months ending at end_month
    ('YYYY-MM'), as a list of {"month": "YYYY-MM", "income": int, "expenses": int}.
    """
    months = get_last_n_months(n, end_month)
    conn = get_connection()
    try:
        result = []
        for month in months:
            income_row = conn.execute(
                "SELECT SUM(amount) AS total FROM INCOME WHERE strftime('%Y-%m', timestamp) = ?;",
                (month,),
            ).fetchone()
            expense_row = conn.execute(
                "SELECT SUM(amount) AS total FROM EXPENSE WHERE strftime('%Y-%m', timestamp) = ?;",
                (month,),
            ).fetchone()
            result.append({
                "month": month,
                "income": income_row["total"] or 0,
                "expenses": expense_row["total"] or 0,
            })
        return result
    finally:
        conn.close()

@st.cache_data
def get_month_budget(month: str) -> dict:
    """
    Returns income, opening balance, expenses, and available balance
    for the given month ('YYYY-MM').
    """
    conn = get_connection()
    try:
        # Opening balance: everything before this month
        prior_income = conn.execute(
            "SELECT SUM(amount) AS total FROM INCOME WHERE strftime('%Y-%m', timestamp) < ?;",
            (month,),
        ).fetchone()["total"] or 0

        prior_expenses = conn.execute(
            "SELECT SUM(amount) AS total FROM EXPENSE WHERE strftime('%Y-%m', timestamp) < ?;",
            (month,),
        ).fetchone()["total"] or 0

        opening_balance = prior_income - prior_expenses

        # This month's activity
        month_income = conn.execute(
            "SELECT SUM(amount) AS total FROM INCOME WHERE strftime('%Y-%m', timestamp) = ?;",
            (month,),
        ).fetchone()["total"] or 0

        month_expenses = conn.execute(
            "SELECT SUM(amount) AS total FROM EXPENSE WHERE strftime('%Y-%m', timestamp) = ?;",
            (month,),
        ).fetchone()["total"] or 0

        available = opening_balance + month_income - month_expenses

        return {
            "opening_balance": opening_balance,
            "income": month_income,
            "expenses": month_expenses,
            "available": available,
        }
    finally:
        conn.close()

@st.cache_data
def get_recent_daily_totals(days: int = 14) -> list[dict]:
    """
    Returns daily expense totals for the last `days` days (not calendar-month
    bound), used for the runway calculation.
    """
    cutoff = (date.today() - timedelta(days=days)).strftime("%Y-%m-%d")
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT DATE(timestamp) AS day, SUM(amount) AS total
            FROM EXPENSE
            WHERE DATE(timestamp) >= ?
            GROUP BY DATE(timestamp)
            ORDER BY day;
            """,
            (cutoff,),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

def _get_period_category_totals(start: str, end: str) -> dict:
    """
    Returns {category_name: total} for expenses between start and end dates
    (both 'YYYY-MM-DD', inclusive).
    """
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT c.name AS category, SUM(e.amount) AS total
            FROM EXPENSE e
            JOIN CATEGORY c ON e.category_id = c.category_id
            WHERE DATE(e.timestamp) BETWEEN ? AND ?
            GROUP BY c.name;
            """,
            (start, end),
        ).fetchall()
        return {row["category"]: row["total"] for row in rows}
    finally:
        conn.close()

@st.cache_data
def get_category_trend(reference_date: date = None) -> list[dict]:
    """
    Compares this month-so-far against the same day-range last month, per
    category. Returns a list of:
    {category, current, previous, rupee_change, percent_change (or None)}
    """
    if reference_date is None:
        reference_date = date.today()

    this_month_start = reference_date.replace(day=1)
    this_month_end = reference_date

    last_month_date = reference_date - relativedelta(months=1)
    last_month_start = last_month_date.replace(day=1)

    # Clamp the comparison day to the last valid day of the previous month
    # (e.g. comparing Oct 31 against a 30-day September falls back to Sep 30).
    last_day_of_prev_month = monthrange(last_month_date.year, last_month_date.month)[1]
    comparison_day = min(reference_date.day, last_day_of_prev_month)
    last_month_end = last_month_date.replace(day=comparison_day)

    current_totals = _get_period_category_totals(
        this_month_start.isoformat(), this_month_end.isoformat()
    )
    previous_totals = _get_period_category_totals(
        last_month_start.isoformat(), last_month_end.isoformat()
    )

    all_categories = set(current_totals) | set(previous_totals)
    trend = []

    for category in all_categories:
        current = current_totals.get(category, 0)
        previous = previous_totals.get(category, 0)
        rupee_change = current - previous

        if previous == 0:
            percent_change = None  # new spending, no baseline to compare
        else:
            percent_change = (rupee_change / previous) * 100

        trend.append({
            "category": category,
            "current": current,
            "previous": previous,
            "rupee_change": rupee_change,
            "percent_change": percent_change,
        })

    return trend

def get_top_insights(trend: list[dict], n: int = 4) -> dict:
    """
    Splits trend data into two ranked, non-overlapping views: by absolute
    rupee change, and by absolute percent change (excluding anything already
    shown in the rupee ranking, and excluding entries with no percent_change,
    i.e. new spending).
    """
    by_rupee = sorted(trend, key=lambda t: abs(t["rupee_change"]), reverse=True)[:n]
    shown_categories = {entry["category"] for entry in by_rupee}

    percent_eligible = [
        t for t in trend
        if t["percent_change"] is not None and t["category"] not in shown_categories
    ]
    by_percent = sorted(
        percent_eligible, key=lambda t: abs(t["percent_change"]), reverse=True
    )[:n]

    return {"by_rupee": by_rupee, "by_percent": by_percent}


def format_rupee_insight(entry: dict) -> str:
    """Leads with the rupee amount, mentions percent as context."""
    category = entry["category"]
    direction = "increased" if entry["rupee_change"] > 0 else "decreased"
    rupee_abs = abs(entry["rupee_change"])

    if entry["percent_change"] is None:
        return f"{category} is new spending this month: {entry['current']}."

    percent_abs = abs(entry["percent_change"])
    return f"{category} {direction} by {rupee_abs} (a {percent_abs:.0f}% change)."


def format_percent_insight(entry: dict) -> str:
    """Leads with the percentage, mentions rupee amount as context."""
    category = entry["category"]
    direction = "up" if entry["rupee_change"] > 0 else "down"
    percent_abs = abs(entry["percent_change"])
    rupee_abs = abs(entry["rupee_change"])

    return f"{category} is {direction} {percent_abs:.0f}% from last month ({rupee_abs} in rupees)."