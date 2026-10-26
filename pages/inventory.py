import pandas as pd
import streamlit as st

from src.inventory import inventory_guidance
from src.page_utils import render_data_filters, require_dataframe
from src.templates import inventory_template_bytes


st.set_page_config(page_title="Inventory Guidance | InsightIQ", page_icon="🛒", layout="wide")
st.title("🛒 Inventory Guidance")
st.caption("Use supplied stock information with observed sales pace to prioritize stock review.")

with st.expander("Download the inventory-ready template", expanded=False):
    st.write(
        "Use this template to prepare one sales file with the stock fields InsightIQ understands. "
        "Replace the example rows before uploading it."
    )
    st.download_button(
        "Download Excel template",
        data=inventory_template_bytes(),
        file_name="InsightIQ_inventory_template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    st.caption(
        "Required: Date, Product, Quantity, Price. For stock guidance add Current Stock and Reorder Point. "
        "Lead Time (days) is optional."
    )

df = render_data_filters(require_dataframe(), "inventory")
if df.empty:
    st.warning("No sales match these filters.")
    st.stop()

guidance = inventory_guidance(df)
st.info(guidance["message"])

if not guidance["available"]:
    st.subheader("To enable inventory risk guidance")
    st.markdown(
        """
Add at least these columns to the sales file:

- `Current Stock` or `Stock Level`
- `Reorder Point`

Optional: add `Lead Time` in days. InsightIQ will show observed sales pace during that lead time,
but will not create an exact order quantity.
"""
    )
    st.stop()

items = guidance["items"]
if items.empty:
    st.warning("A stock column was found, but it contains no valid stock values for the selected data.")
    st.stop()

summary = guidance["summary"]
high_priority, watch, monitoring = st.columns(3)
high_priority.metric("High-priority products", summary["🔴 High Priority"])
watch.metric("Products to watch", summary["🟡 Watch"])
monitoring.metric("Products to monitor", summary["🟢 Opportunity"])

st.caption("Each count is based on the latest stock and reorder-point value supplied for each product.")
st.header("Priority Stock Reviews")
for item in items.itertuples():
    with st.container(border=True):
        st.markdown(f"**{item.Priority} — {item.Product}: {item.Recommended_Action}**")
        st.write(item.Reason)

st.divider()
st.subheader("Inventory Detail")
display = items.copy()
for column in ("Current_Stock", "Reorder_Point", "Lead_Time_Days", "Average_Daily_Units"):
    if column in display:
        display[column] = display[column].map(
            lambda value: "Not provided" if pd.isna(value) else f"{value:,.1f}"
        )
st.dataframe(display, width="stretch", hide_index=True)

st.caption(
    "Important: current stock and reorder points are read from the uploaded file. "
    "The page does not know deliveries, supplier reliability, damaged stock, or future promotions."
)
