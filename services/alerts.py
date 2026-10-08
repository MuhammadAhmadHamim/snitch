CATEGORY_SHARE_THRESHOLD = 0.50  # 50%

def get_budget_status(available: int, spent: int) -> str:
    """
    Returns 'ok', 'warning' (80%+ of available spent), or 'over'
    (100%+ spent, or balance already negative).
    """
    if available <= 0:
        return "over" if spent > 0 else "ok"

    spent_ratio = spent / available

    if spent_ratio >= 1.0:
        return "over"
    elif spent_ratio >= 0.8:
        return "warning"
    return "ok"

def calculate_runway_days(available: int, daily_totals: list[dict]) -> float | None:
    """
    Estimates days of runway left, based on average daily spend over the
    provided daily_totals (expects [{'day': ..., 'total': ...}, ...]).
    Returns None if there isn't enough data or spending is zero.
    """
    if len(daily_totals) < 3:
        return None

    total_spent = sum(row["total"] for row in daily_totals)
    if total_spent <= 0:
        return None

    avg_daily_spend = total_spent / len(daily_totals)
    if avg_daily_spend <= 0:
        return None

    return available / avg_daily_spend

def get_category_share_insights(category_totals: list[dict]) -> list[dict]:
    """
    Returns categories whose share of total spending meets or exceeds
    CATEGORY_SHARE_THRESHOLD, as [{'category': ..., 'share': 0.0-1.0}, ...].
    """
    total = sum(row["total"] for row in category_totals)
    if total <= 0:
        return []

    flagged = []
    for row in category_totals:
        share = row["total"] / total
        if share >= CATEGORY_SHARE_THRESHOLD:
            flagged.append({"category": row["category"], "share": share})

    return flagged