import pandas as pd
import streamlit as st

from src.advisor import analyze_business_advisor, executive_summary
from src.currency import money_label
from src.inventory import inventory_guidance
from src.page_utils import render_data_filters, require_dataframe
from src.session import get_currency


st.set_page_config(page_title="Business Advisor | InsightIQ", page_icon="💼", layout="wide")
st.title("💼 Business Advisor")
st.caption("Clear decisions from your supermarket sales data. Charts stay on the Dashboard; this page focuses on actions.")
st.caption("Comparison rule: the most recent half of the available dates is compared with the preceding half. Product alerts require a 15% material change.")

df = render_data_filters(require_dataframe(), "advisor")
if df.empty:
    st.warning("No sales match these filters.")
    st.stop()

currency = get_currency()
revenue_columns = {
    column: st.column_config.NumberColumn(money_label(column.replace("_", " "), currency))
    for column in ("Recent_Revenue", "Previous_Revenue")
}
advisor = analyze_business_advisor(df, currency)
inventory = inventory_guidance(df)

st.header("Executive Summary")
summary_columns = st.columns(4)
for column, item in zip(summary_columns, executive_summary(advisor, inventory)):
    with column.container(border=True):
        st.caption(item["label"])
        st.write(item["detail"])

st.divider()

st.header("🚨 Priority Actions")
for action in advisor["actions"]:
    with st.container(border=True):
        st.markdown(f"**{action['priority']} — {action['title']}**")
        st.write(action["detail"])

st.divider()
st.header("📉 Revenue Change Explanation")
if advisor["has_comparison"]:
    start, end = advisor["recent_dates"]
    previous_start, previous_end = advisor["previous_dates"]
    st.caption(f"Recent period: {start.date()}–{end.date()} compared with {previous_start.date()}–{previous_end.date()}.")
    st.write(advisor["comparison"]["headline"])
    st.write(advisor["comparison"]["detail"])
else:
    st.info(advisor["message"])

st.divider()
st.header("📉 Declining Products")
if advisor["has_comparison"] and not advisor["declining"].empty:
    display = advisor["declining"][[
        "Product", "Recent_Revenue", "Previous_Revenue", "Revenue_Change_Percent",
        "Recent_Quantity", "Previous_Quantity",
    ]].copy()
    display["Priority / reason"] = "🔴 High Priority — material revenue decline"
    display["Revenue_Change_Percent"] = display["Revenue_Change_Percent"].map(lambda value: f"{value:.1f}%")
    st.dataframe(display, width="stretch", hide_index=True, column_config=revenue_columns)
else:
    st.info("No material declining product was detected with the current comparison rules, or there is not enough history.")

st.header("📈 Product Momentum / Demand Signals")
if advisor["has_comparison"] and not advisor["momentum"].empty:
    display = advisor["momentum"][[
        "Product", "Recent_Revenue", "Previous_Revenue", "Revenue_Change_Percent",
        "Recent_Quantity", "Previous_Quantity",
    ]].copy()
    display["Recommended action"] = "Review stock before the next order; demand is accelerating in the observed period."
    display["Revenue_Change_Percent"] = display["Revenue_Change_Percent"].map(lambda value: f"+{value:.1f}%")
    st.dataframe(display, width="stretch", hide_index=True, column_config=revenue_columns)
else:
    st.info("No material product momentum was detected with the current comparison rules, or there is not enough history.")

st.divider()
st.header("🛒 Stock / Inventory Guidance")
st.write(inventory["message"])
if inventory["available"] and not inventory["items"].empty:
    urgent = inventory["items"].head(3)[["Product", "Priority", "Recommended_Action", "Reason"]]
    st.dataframe(urgent, width="stretch", hide_index=True)
    st.caption("See the Inventory Guidance page for the full stock review.")
else:
    st.caption("InsightIQ will not estimate stock-outs or reorder quantities without actual inventory fields.")

st.divider()
st.header("📅 Seasonal / Trend Signals")
st.write(advisor["seasonal"])

st.divider()
st.header("✅ Today's Action Plan")
for number, action in enumerate(advisor["actions"], start=1):
    st.write(f"{number}. **{action['title']}** — {action['detail']}")
