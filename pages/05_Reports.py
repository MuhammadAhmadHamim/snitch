import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

from services.expenses import get_category_totals, get_daily_totals, get_expenses
from services.income import get_monthly_income_total
from services.reports import get_monthly_trend

from ui.styles import inject_theme, status_tag

inject_theme()

st.title("Reports")

# ---------- Month selector ----------
selected_month = st.date_input("Month", value=date.today())
month_str = selected_month.strftime("%Y-%m")

# ---------- Monthly summary ----------
category_totals = get_category_totals(month_str)
daily_totals = get_daily_totals(month_str)
month_income = get_monthly_income_total(month_str)
month_expenses = sum(row["total"] for row in category_totals)
balance = month_income - month_expenses
savings_rate = (balance / month_income * 100) if month_income > 0 else None

with st.container(border=True):
    st.subheader(f"Summary — {month_str}")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Income", month_income)
    col2.metric("Expenses", month_expenses)
    col3.metric("Balance", balance)
    col4.metric("Savings rate", f"{savings_rate:.0f}%" if savings_rate is not None else "—")

st.divider()

VAULT_GOLD = ["#FFD700", "#D4AF37", "#B8860B", "#F4C430", "#C9A227", "#E6BE8A"]

# ---------- Chart 1: expenses by category ----------
st.subheader("Spending by Category")
if not category_totals:
    st.info("No expenses logged for this month yet.")
else:
    df_categories = pd.DataFrame(category_totals)
    fig1 = px.pie(
        df_categories, names="category", values="total",
        hole=0.4,
        color_discrete_sequence=VAULT_GOLD
    )
    st.plotly_chart(fig1, use_container_width=True)

# ---------- Chart 2: daily spending ----------
st.subheader("Daily Spending")
if not daily_totals:
    st.info("No expenses logged for this month yet.")
else:
    df_daily = pd.DataFrame(daily_totals)
    df_daily["day"] = pd.to_datetime(df_daily["day"]).dt.strftime("%b %d")
    
    fig2 = px.line(df_daily, x="day", y="total", markers=True)
    fig2.update_traces(line_color="#D4AF37", marker=dict(color="#FFD700", size=7))
    fig2.update_xaxes(type="category")
    fig2.update_yaxes(dtick=50)
    st.plotly_chart(fig2, use_container_width=True)

# ---------- Chart 3: income vs expenses, last 6 months ----------
st.subheader("Income vs. Expenses (Last 6 Months)")
trend = get_monthly_trend(6, end_month=month_str)
df_trend = pd.DataFrame(trend)
df_trend_melted = df_trend.melt(
    id_vars="month", value_vars=["income", "expenses"],
    var_name="type", value_name="amount",
)
fig3 = px.bar(
    df_trend_melted, x="month", y="amount", color="type",
    barmode="group",
    color_discrete_map={"income": "#FFD700", "expenses": "#8B6914"}
)
fig3.update_layout(xaxis_title="Month", yaxis_title="Amount")
st.plotly_chart(fig3, use_container_width=True)

st.divider()

# ---------- CSV export ----------
st.subheader("Export")
month_expenses_list = get_expenses(month=month_str)
if month_expenses_list:
    df_export = pd.DataFrame(month_expenses_list)
    csv_data = df_export.to_csv(index=False)
    st.download_button(
        "Download this month's expenses as CSV",
        data=csv_data,
        file_name=f"snitch_expenses_{month_str}.csv",
        mime="text/csv",
        type="primary"
    )
else:
    st.caption("No expenses to export for this month.")
