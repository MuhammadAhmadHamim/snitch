from services.alerts import get_budget_status, calculate_runway_days, get_category_share_insights

def test_budget_status_ok():
    assert get_budget_status(available=1000, spent=500) == "ok"

def test_budget_status_warning_at_80_percent():
    assert get_budget_status(available=1000, spent=800) == "warning"

def test_budget_status_over_at_100_percent():
    assert get_budget_status(available=1000, spent=1000) == "over"

def test_budget_status_over_when_negative_balance():
    assert get_budget_status(available=-200, spent=500) == "over"

def test_budget_status_zero_available_zero_spent():
    assert get_budget_status(available=0, spent=0) == "ok"

def test_runway_insufficient_data_returns_none():
    daily = [{"day": "2026-10-01", "total": 100}, {"day": "2026-10-02", "total": 50}]
    assert calculate_runway_days(available=1000, daily_totals=daily) is None

def test_runway_calculates_correctly():
    daily = [
        {"day": "2026-10-01", "total": 100},
        {"day": "2026-10-02", "total": 100},
        {"day": "2026-10-03", "total": 100},
        {"day": "2026-10-04", "total": 100},
    ]
    # avg daily spend = 100, available = 1000 -> 10 days
    assert calculate_runway_days(available=1000, daily_totals=daily) == 10.0

def test_runway_zero_spending_returns_none():
    daily = [
        {"day": "2026-10-01", "total": 0},
        {"day": "2026-10-02", "total": 0},
        {"day": "2026-10-03", "total": 0},
    ]
    assert calculate_runway_days(available=1000, daily_totals=daily) is None

def test_category_share_flags_above_threshold():
    totals = [
        {"category": "Food", "total": 600},
        {"category": "Transport", "total": 400},
    ]
    insights = get_category_share_insights(totals)
    assert len(insights) == 1
    assert insights[0]["category"] == "Food"
    assert insights[0]["share"] == 0.6

def test_category_share_no_flags_below_threshold():
    totals = [
        {"category": "Food", "total": 300},
        {"category": "Transport", "total": 300},
        {"category": "Study", "total": 400},
    ]
    assert get_category_share_insights(totals) == []

def test_category_share_empty_totals_returns_empty():
    assert get_category_share_insights([]) == []