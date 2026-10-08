import streamlit as st
from datetime import date

from db.schema import init_db, seed_default_categories
from services.expenses import get_category_totals
from services.reports import (
    get_month_budget,
    get_recent_daily_totals,
    get_category_trend,
    get_top_insights,
    format_rupee_insight,
    format_percent_insight,
)
from services.alerts import get_budget_status, calculate_runway_days, get_category_share_insights
from ui.styles import inject_theme, status_tag

st.set_page_config(page_title="Snitch", page_icon="💸", layout="centered")

inject_theme()

# Runs once per session start; both functions are safe to call repeatedly
# (CREATE TABLE IF NOT EXISTS / INSERT OR IGNORE), so this never duplicates anything.
init_db()
seed_default_categories()

st.title("💸 Snitch")
st.caption("Your money, your business, no snitching required... except from me.")

st.divider()

selected_month = st.date_input("Select month", value=date.today())
month_str = selected_month.strftime("%Y-%m")

budget = get_month_budget(month_str)
available = budget["available"]
total_resources = budget["opening_balance"] + budget["income"]
status = get_budget_status(total_resources, budget["expenses"])

with st.container(border=True):
    st.subheader("This Month")
    col1, col2, col3 = st.columns(3)
    col1.metric("Income", budget["income"])
    col2.metric("Expenses", budget["expenses"])
    col3.metric("Available", available)

st.markdown(status_tag(status), unsafe_allow_html=True)

if status == "over":
    st.error("Operation compromised. You've spent all your available balance this month.")
elif status == "warning":
    st.warning("Operation at risk. You've used 80% or more of your available balance this month.")

recent_daily = get_recent_daily_totals(14)
runway = calculate_runway_days(available, recent_daily)
if runway is not None:
    st.info(f"Escape route open: at your recent pace, your funds hold for roughly **{runway:.0f} more days**.")

category_totals = get_category_totals(month_str)
share_insights = get_category_share_insights(category_totals)
for insight in share_insights:
    st.warning(f"**{insight['category']}** has taken {insight['share']*100:.0f}% of this month's haul.")

st.divider()
st.caption(f"{len(category_totals)} categor(y/ies) with spending logged this month.")

st.divider()
st.subheader("Trends vs. Last Month")

trend = get_category_trend()
trend_insights = get_top_insights(trend, n=4)

col_rupee, col_percent = st.columns(2)

with col_rupee:
    st.caption("Biggest changes by amount")
    if not trend_insights["by_rupee"]:
        st.caption("Not enough data yet.")
    for entry in trend_insights["by_rupee"]:
        st.write(f"• {format_rupee_insight(entry)}")

with col_percent:
    st.caption("Biggest changes by percentage")
    if not trend_insights["by_percent"]:
        st.caption("Not enough data yet.")
    for entry in trend_insights["by_percent"]:
        st.write(f"• {format_percent_insight(entry)}")