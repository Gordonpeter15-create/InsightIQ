import pandas as pd
import streamlit as st

from src.advisor import analyze_business_advisor, executive_summary
from src.currency import money_label
from src.inventory import inventory_guidance
from src.page_utils import (
    page_header,
    priority_badge,
    readable_columns,
    render_data_filters,
    require_dataframe,
    safe_markdown,
)
from src.session import get_currency


page_header(
    "Business Advisor",
    "Clear decisions from your sales data. The most recent half of the available dates is compared "
    "with the preceding half; product alerts require a 15% material change.",
    eyebrow="Analyse",
)

df = render_data_filters(require_dataframe(), "advisor")
if df.empty:
    st.warning("No sales match these filters.")
    st.stop()

currency = get_currency()
revenue_columns = {
    column: st.column_config.NumberColumn(money_label(column, currency), format="localized")
    for column in ("Recent revenue", "Previous revenue")
}
advisor = analyze_business_advisor(df, currency)
inventory = inventory_guidance(df)

st.subheader("Executive summary")
summary_columns = st.columns(4)
for column, item in zip(summary_columns, executive_summary(advisor, inventory)):
    with column.container(border=True):
        st.caption(item["label"])
        st.markdown(safe_markdown(item["detail"]))

st.divider()

st.subheader("Priority actions")
for action in advisor["actions"]:
    with st.container(border=True):
        st.markdown(f"{priority_badge(action['priority'])} **{safe_markdown(action['title'])}**")
        st.markdown(safe_markdown(action["detail"]))

st.divider()
st.subheader("Revenue change explanation")
if advisor["has_comparison"]:
    start, end = advisor["recent_dates"]
    previous_start, previous_end = advisor["previous_dates"]
    st.caption(f"Recent period: {start.date()}–{end.date()} compared with {previous_start.date()}–{previous_end.date()}.")
    st.markdown(safe_markdown(advisor["comparison"]["headline"]))
    st.markdown(safe_markdown(advisor["comparison"]["detail"]))
else:
    st.info(advisor["message"])

st.divider()
st.subheader("Declining products")
if advisor["has_comparison"] and not advisor["declining"].empty:
    display = advisor["declining"][[
        "Product", "Recent_Revenue", "Previous_Revenue", "Revenue_Change_Percent",
        "Recent_Quantity", "Previous_Quantity",
    ]].copy()
    display["Priority / reason"] = "🔴 High Priority — material revenue decline"
    display["Revenue_Change_Percent"] = display["Revenue_Change_Percent"].map(lambda value: f"{value:.1f}%")
    st.dataframe(readable_columns(display), width="stretch", hide_index=True, column_config=revenue_columns)
else:
    st.info("No material declining product was detected with the current comparison rules, or there is not enough history.")

st.subheader("Product momentum and demand signals")
if advisor["has_comparison"] and not advisor["momentum"].empty:
    display = advisor["momentum"][[
        "Product", "Recent_Revenue", "Previous_Revenue", "Revenue_Change_Percent",
        "Recent_Quantity", "Previous_Quantity",
    ]].copy()
    display["Recommended action"] = "Review stock before the next order; demand is accelerating in the observed period."
    display["Revenue_Change_Percent"] = display["Revenue_Change_Percent"].map(lambda value: f"+{value:.1f}%")
    st.dataframe(readable_columns(display), width="stretch", hide_index=True, column_config=revenue_columns)
else:
    st.info("No material product momentum was detected with the current comparison rules, or there is not enough history.")

st.divider()
st.subheader("Stock and inventory guidance")
st.markdown(safe_markdown(inventory["message"]))
if inventory["available"] and not inventory["items"].empty:
    urgent = inventory["items"].head(3)[["Product", "Priority", "Recommended_Action", "Reason"]]
    st.dataframe(readable_columns(urgent), width="stretch", hide_index=True)
    st.caption("See the Inventory Guidance page for the full stock review.")
else:
    st.caption("InsightIQ will not estimate stock-outs or reorder quantities without actual inventory fields.")

st.divider()
st.subheader("Seasonal and trend signals")
st.markdown(safe_markdown(advisor["seasonal"]))

st.divider()
st.subheader("Today's action plan")
for number, action in enumerate(advisor["actions"], start=1):
    st.markdown(f"{number}. **{safe_markdown(action['title'])}** — {safe_markdown(action['detail'])}")
