import pytest
from datetime import datetime, timedelta
from services.categories import add_category
from services.expenses import add_expense, get_expenses, update_expense, delete_expense

def test_add_expense(temp_db):
    category_id = add_category("Food")
    expense_id = add_expense(amount=250, category_id=category_id, note="Lunch")
    expenses = get_expenses()
    assert len(expenses) == 1
    assert expenses[0]["amount"] == 250
    assert expenses[0]["note"] == "Lunch"
    assert expenses[0]["expense_id"] == expense_id

def test_add_expense_zero_amount_fails(temp_db):
    category_id = add_category("Food")
    with pytest.raises(ValueError):
        add_expense(amount=0, category_id=category_id)

def test_add_expense_negative_amount_fails(temp_db):
    category_id = add_category("Food")
    with pytest.raises(ValueError):
        add_expense(amount=-50, category_id=category_id)

def test_add_expense_nonexistent_category_fails(temp_db):
    with pytest.raises(ValueError):
        add_expense(amount=100, category_id=999)

def test_add_expense_future_timestamp_fails(temp_db):
    category_id = add_category("Food")
    future = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    with pytest.raises(ValueError):
        add_expense(amount=100, category_id=category_id, timestamp=future)

def test_add_expense_default_timestamp(temp_db):
    category_id = add_category("Food")
    add_expense(amount=100, category_id=category_id)
    expenses = get_expenses()
    # just confirm it parses as a valid, well-formed timestamp
    datetime.strptime(expenses[0]["timestamp"], "%Y-%m-%d %H:%M:%S")

def test_get_expenses_filtered_by_category(temp_db):
    food_id = add_category("Food")
    transport_id = add_category("Transport")
    add_expense(amount=100, category_id=food_id)
    add_expense(amount=200, category_id=transport_id)

    food_expenses = get_expenses(category_id=food_id)
    assert len(food_expenses) == 1
    assert food_expenses[0]["amount"] == 100

def test_get_expenses_filtered_by_month(temp_db):
    category_id = add_category("Food")
    add_expense(amount=100, category_id=category_id, timestamp="2026-09-15 12:00:00")
    add_expense(amount=200, category_id=category_id, timestamp="2026-10-01 09:00:00")

    september = get_expenses(month="2026-09")
    assert len(september) == 1
    assert september[0]["amount"] == 100

def test_update_expense_amount(temp_db):
    category_id = add_category("Food")
    expense_id = add_expense(amount=100, category_id=category_id)
    update_expense(expense_id, amount=300)
    expenses = get_expenses()
    assert expenses[0]["amount"] == 300

def test_update_expense_to_nonexistent_category_fails(temp_db):
    category_id = add_category("Food")
    expense_id = add_expense(amount=100, category_id=category_id)
    with pytest.raises(ValueError):
        update_expense(expense_id, category_id=999)

def test_update_expense_unknown_field_fails(temp_db):
    category_id = add_category("Food")
    expense_id = add_expense(amount=100, category_id=category_id)
    with pytest.raises(ValueError):
        update_expense(expense_id, not_a_real_column=5)

def test_update_nonexistent_expense_fails(temp_db):
    with pytest.raises(ValueError):
        update_expense(999, amount=100)

def test_delete_expense(temp_db):
    category_id = add_category("Food")
    expense_id = add_expense(amount=100, category_id=category_id)
    delete_expense(expense_id)
    assert get_expenses() == []

def test_delete_nonexistent_expense_fails(temp_db):
    with pytest.raises(ValueError):
        delete_expense(999)