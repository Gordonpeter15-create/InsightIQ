import streamlit as st

from src.cards import show_kpi_cards
from src.charts import (
    monthly_revenue_chart,
    revenue_by_product_chart,
    revenue_distribution_chart,
    revenue_over_time_chart,
)
from src.currency import format_money, money_label
from src.metrics import calculate_metrics, product_performance
from src.page_utils import render_data_filters, require_dataframe
from src.session import get_currency


st.set_page_config(page_title="Dashboard | InsightIQ", page_icon="📊", layout="wide")
st.title("📊 Sales Dashboard")
st.caption("Use the filters to focus the analysis on a product or period.")

df = render_data_filters(require_dataframe(), "dashboard")
if df.empty:
    st.warning("No sales match these filters.")
    st.stop()

currency = get_currency()
metrics = calculate_metrics(df)
performance = product_performance(df)
show_kpi_cards(metrics, currency)

best_col, lowest_col = st.columns(2)
best = performance.iloc[0]
lowest = performance.iloc[-1]
best_col.success(f"🏆 **Best product**  \n{best['Product']} — {format_money(best['Revenue'], currency)}")
lowest_col.warning(f"📉 **Lowest product**  \n{lowest['Product']} — {format_money(lowest['Revenue'], currency)}")

st.divider()
chart_left, chart_right = st.columns(2)
with chart_left:
    st.subheader("Revenue by Product")
    st.plotly_chart(revenue_by_product_chart(performance, currency), width="stretch")
with chart_right:
    st.subheader("Revenue Distribution")
    st.plotly_chart(revenue_distribution_chart(performance), width="stretch")
st.subheader("Revenue Over Time")
st.plotly_chart(revenue_over_time_chart(df, currency), width="stretch")
st.subheader("Monthly Revenue")
st.plotly_chart(monthly_revenue_chart(df, currency), width="stretch")

st.divider()
st.subheader("Product Performance")
st.dataframe(
    performance, width="stretch", hide_index=True,
    column_config={"Revenue": st.column_config.NumberColumn(money_label("Revenue", currency))},
)

with st.expander("View cleaned data"):
    st.dataframe(
        df, width="stretch", hide_index=True,
        column_config={
            column: st.column_config.NumberColumn(money_label(column, currency))
            for column in ("Price", "Revenue")
        },
    )
st.download_button("⬇ Download filtered data", df.to_csv(index=False).encode("utf-8"), "insightiq_filtered_sales.csv", "text/csv")
