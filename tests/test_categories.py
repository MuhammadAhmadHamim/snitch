import pytest
from services.categories import (
    add_category, list_categories, rename_category, delete_category,
)
from services.expenses import add_expense

def test_add_category(temp_db):
    category_id = add_category("Food")
    categories = list_categories()
    assert len(categories) == 1
    assert categories[0]["name"] == "Food"
    assert categories[0]["category_id"] == category_id

def test_add_duplicate_category_fails(temp_db):
    add_category("Food")
    with pytest.raises(ValueError):
        add_category("Food")

def test_add_empty_category_fails(temp_db):
    with pytest.raises(ValueError):
        add_category("   ")

def test_rename_category(temp_db):
    category_id = add_category("Food")
    rename_category(category_id, "Groceries")
    categories = list_categories()
    assert categories[0]["name"] == "Groceries"

def test_rename_nonexistent_category_fails(temp_db):
    with pytest.raises(ValueError):
        rename_category(999, "Whatever")

def test_delete_unused_category(temp_db):
    category_id = add_category("Food")
    delete_category(category_id)
    assert list_categories() == []

def test_delete_category_in_use_fails(temp_db):
    category_id = add_category("Food")
    add_expense(amount=200, category_id=category_id)
    with pytest.raises(ValueError):
        delete_category(category_id)