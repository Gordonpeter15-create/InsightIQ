import streamlit as st

from src.cards import show_kpi_cards
from src.charts import (
    day_of_week_chart,
    monthly_revenue_chart,
    revenue_by_product_chart,
    revenue_distribution_chart,
    revenue_over_time_chart,
)
from src.advisor import day_of_week_pattern
from src.currency import format_money, money_label
from src.metrics import calculate_metrics, product_performance
from src.page_utils import page_header, readable_columns, render_data_filters, require_dataframe, safe_markdown
from src.session import get_currency


page_header("Sales Dashboard", "Revenue, products, and trends. Use the sidebar filters to focus on a product or period.", eyebrow="Analyse")

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
with best_col.container(border=True):
    st.caption(":material/arrow_upward: Best product")
    st.markdown(safe_markdown(f"**{best['Product']}** · {format_money(best['Revenue'], currency)}"))
with lowest_col.container(border=True):
    st.caption(":material/arrow_downward: Lowest product")
    st.markdown(safe_markdown(f"**{lowest['Product']}** · {format_money(lowest['Revenue'], currency)}"))

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
weekday_column, monthly_column = st.columns(2)
with weekday_column:
    st.subheader("Revenue by Day of Week")
    weekdays = day_of_week_pattern(df, currency)
    if weekdays["available"]:
        st.plotly_chart(day_of_week_chart(weekdays["table"], currency), width="stretch")
    else:
        st.info(weekdays["message"])
with monthly_column:
    st.subheader("Monthly Revenue")
    st.plotly_chart(monthly_revenue_chart(df, currency), width="stretch")

st.divider()
st.subheader("Product Performance")
st.dataframe(
    readable_columns(performance), width="stretch", hide_index=True,
    column_config={"Revenue": st.column_config.NumberColumn(money_label("Revenue", currency), format="localized")},
)

with st.expander("View cleaned data"):
    st.dataframe(
        readable_columns(df), width="stretch", hide_index=True,
        column_config={
            column: st.column_config.NumberColumn(money_label(column, currency), format="localized")
            for column in ("Price", "Revenue")
        },
    )
st.download_button(
    "Download filtered data (CSV)", df.to_csv(index=False).encode("utf-8"), "insightiq_filtered_sales.csv", "text/csv",
    icon=":material/download:",
)
