import pytest
from datetime import datetime, timedelta
from services.income import add_income, get_income, update_income, delete_income

def test_add_income(temp_db):
    income_id = add_income(amount=5000, source="Allowance", note="Monthly")
    income = get_income()
    assert len(income) == 1
    assert income[0]["amount"] == 5000
    assert income[0]["source"] == "Allowance"
    assert income[0]["income_id"] == income_id

def test_add_income_zero_amount_fails(temp_db):
    with pytest.raises(ValueError):
        add_income(amount=0, source="Allowance")

def test_add_income_empty_source_fails(temp_db):
    with pytest.raises(ValueError):
        add_income(amount=1000, source="   ")

def test_add_income_future_timestamp_fails(temp_db):
    future = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    with pytest.raises(ValueError):
        add_income(amount=1000, source="Allowance", timestamp=future)

def test_get_income_filtered_by_source(temp_db):
    add_income(amount=5000, source="Allowance")
    add_income(amount=1000, source="Gift")

    allowance_only = get_income(source="Allowance")
    assert len(allowance_only) == 1
    assert allowance_only[0]["amount"] == 5000

def test_get_income_filtered_by_month(temp_db):
    add_income(amount=5000, source="Allowance", timestamp="2026-09-01 10:00:00")
    add_income(amount=1000, source="Gift", timestamp="2026-10-01 10:00:00")

    september = get_income(month="2026-09")
    assert len(september) == 1
    assert september[0]["amount"] == 5000

def test_update_income_amount(temp_db):
    income_id = add_income(amount=5000, source="Allowance")
    update_income(income_id, amount=6000)
    income = get_income()
    assert income[0]["amount"] == 6000

def test_update_income_to_empty_source_fails(temp_db):
    income_id = add_income(amount=5000, source="Allowance")
    with pytest.raises(ValueError):
        update_income(income_id, source="   ")

def test_update_nonexistent_income_fails(temp_db):
    with pytest.raises(ValueError):
        update_income(999, amount=100)

def test_delete_income(temp_db):
    income_id = add_income(amount=5000, source="Allowance")
    delete_income(income_id)
    assert get_income() == []

def test_delete_nonexistent_income_fails(temp_db):
    with pytest.raises(ValueError):
        delete_income(999)