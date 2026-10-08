import streamlit as st
from datetime import date, time, datetime

from services.categories import list_categories
from services.expenses import add_expense

from ui.styles import inject_theme

inject_theme()

st.title("Add Expense")

categories = list_categories()

if not categories:
    st.warning("No targets defined yet. Set up a category first.")
    st.stop()

category_names = [c["name"] for c in categories]
category_lookup = {c["name"]: c["category_id"] for c in categories}

with st.form("add_expense_form", clear_on_submit=True):
    amount = st.number_input("Amount", min_value=0, step=1)
    category_name = st.selectbox("Category", category_names)
    entry_date = st.date_input("Date", value=date.today())
    entry_time = st.time_input("Time", value=datetime.now().time())
    note = st.text_input("Note (optional)")

    submitted = st.form_submit_button("Add Expense", type="primary")

    if submitted:
        timestamp = f"{entry_date.strftime('%Y-%m-%d')} {entry_time.strftime('%H:%M:%S')}"
        try:
            add_expense(
                amount=amount,
                category_id=category_lookup[category_name],
                timestamp=timestamp,
                note=note,
            )
            st.cache_data.clear()
            st.success(f"Added expense: {amount} on {category_name}.")
        except ValueError as e:
            st.error(str(e))