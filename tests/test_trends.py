from datetime import date
from services.reports import get_top_insights, format_insight_sentence

def test_top_insights_ranks_by_rupee_amount():
    trend = [
        {"category": "Food", "current": 9600, "previous": 8000, "rupee_change": 1600, "percent_change": 20.0},
        {"category": "Stationery", "current": 300, "previous": 100, "rupee_change": 200, "percent_change": 200.0},
    ]
    insights = get_top_insights(trend, n=2)
    assert insights["by_rupee"][0]["category"] == "Food"
    assert insights["by_percent"][0]["category"] == "Stationery"

def test_top_insights_excludes_new_spending_from_percent_ranking():
    trend = [
        {"category": "Gifts", "current": 500, "previous": 0, "rupee_change": 500, "percent_change": None},
        {"category": "Food", "current": 8500, "previous": 8000, "rupee_change": 500, "percent_change": 6.25},
    ]
    insights = get_top_insights(trend, n=2)
    assert len(insights["by_percent"]) == 1
    assert insights["by_percent"][0]["category"] == "Food"

def test_format_insight_sentence_increase():
    entry = {"category": "Food", "current": 9600, "previous": 8000, "rupee_change": 1600, "percent_change": 20.0}
    sentence = format_insight_sentence(entry)
    assert "Food" in sentence
    assert "increased" in sentence
    assert "1600" in sentence
    assert "20%" in sentence

def test_format_insight_sentence_decrease():
    entry = {"category": "Transport", "current": 1600, "previous": 2000, "rupee_change": -400, "percent_change": -20.0}
    sentence = format_insight_sentence(entry)
    assert "decreased" in sentence

def test_format_insight_sentence_new_spending():
    entry = {"category": "Gifts", "current": 500, "previous": 0, "rupee_change": 500, "percent_change": None}
    sentence = format_insight_sentence(entry)
    assert "new spending" in sentence