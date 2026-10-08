import streamlit as st
from datetime import date, datetime

from services.income import add_income

from ui.styles import inject_theme

inject_theme()

st.title("Add Income")

COMMON_SOURCES = ["Allowance", "Part-time", "Gift", "Other"]

with st.form("add_income_form", clear_on_submit=True):
    amount = st.number_input("Amount", min_value=0, step=1)
    source = st.selectbox("Source", COMMON_SOURCES)
    entry_date = st.date_input("Date", value=date.today())
    entry_time = st.time_input("Time", value=datetime.now().time())
    note = st.text_input("Note (optional)")

    submitted = st.form_submit_button("Add Income", type="primary")

    if submitted:
        timestamp = f"{entry_date.strftime('%Y-%m-%d')} {entry_time.strftime('%H:%M:%S')}"
        try:
            add_income(amount=amount, source=source, timestamp=timestamp, note=note)
            st.cache_data.clear()
            st.success(f"Added income: {amount} from {source}.")
        except ValueError as e:
            st.error(str(e))