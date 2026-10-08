import streamlit as st
from datetime import date

from services.categories import list_categories
from services.expenses import get_expenses, update_expense, delete_expense
from services.income import get_income, update_income, delete_income

from ui.styles import inject_theme

inject_theme()

st.title("Transactions")

tab_expenses, tab_income = st.tabs(["Expenses", "Income"])

# ---------- Expenses tab ----------
with tab_expenses:
    categories = list_categories()
    category_lookup = {c["category_id"]: c["name"] for c in categories}

    selected_month = st.date_input("Month", value=date.today(), key="expense_month")
    month_str = selected_month.strftime("%Y-%m")

    expenses = get_expenses(month=month_str)

    if not expenses:
        st.info("No jobs logged for this month.")
    else:
        for e in expenses:
            with st.expander(
                f"{e['timestamp']} — {category_lookup.get(e['category_id'], '?')} — {e['amount']}"
            ):
                new_amount = st.number_input(
                    "Amount", min_value=0, value=e["amount"], key=f"amt_{e['expense_id']}"
                )
                new_note = st.text_input(
                    "Note", value=e["note"] or "", key=f"note_{e['expense_id']}"
                )

                col1, col2 = st.columns(2)
                if col1.button("Save", key=f"save_{e['expense_id']}"):
                    try:
                        update_expense(e["expense_id"], amount=new_amount, note=new_note)
                        st.cache_data.clear()
                        st.success("Updated.")
                        st.rerun()
                    except ValueError as err:
                        st.error(str(err))

                if col2.button("Delete", key=f"del_{e['expense_id']}"):
                    try:
                        delete_expense(e["expense_id"])
                        st.cache_data.clear()
                        st.rerun()
                    except ValueError as err:
                        st.error(str(err))

# ---------- Income tab ----------
with tab_income:
    selected_month = st.date_input("Month", value=date.today(), key="income_month")
    month_str = selected_month.strftime("%Y-%m")

    income_entries = get_income(month=month_str)

    if not income_entries:
        st.info("No income for this month.")
    else:
        for i in income_entries:
            with st.expander(f"{i['timestamp']} — {i['source']} — {i['amount']}"):
                new_amount = st.number_input(
                    "Amount", min_value=0, value=i["amount"], key=f"iamt_{i['income_id']}"
                )
                new_note = st.text_input(
                    "Note", value=i["note"] or "", key=f"inote_{i['income_id']}"
                )

                col1, col2 = st.columns(2)
                if col1.button("Save", key=f"isave_{i['income_id']}"):
                    try:
                        update_income(i["income_id"], amount=new_amount, note=new_note)
                        st.cache_data.clear()
                        st.success("Updated.")
                        st.rerun()
                    except ValueError as err:
                        st.error(str(err))

                if col2.button("Delete", key=f"idel_{i['income_id']}"):
                    try:
                        delete_income(i["income_id"])
                        st.cache_data.clear()
                        st.rerun()
                    except ValueError as err:
                        st.error(str(err))