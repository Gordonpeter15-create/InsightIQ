import streamlit as st

from src.forecasting import forecast_revenue, forecast_revenue_chart
from src.currency import format_money
from src.page_utils import page_header, render_data_filters, require_dataframe
from src.session import get_currency


page_header(
    "Revenue Forecast",
    "A simple trend forecast based on daily revenue. It is an estimate, not a financial guarantee.",
    eyebrow="Analyse",
)

df = render_data_filters(require_dataframe(), "forecast")
if df.empty:
    st.warning("No sales match these filters.")
    st.stop()
currency = get_currency()
forecast = forecast_revenue(df, days_ahead=7)
if forecast is None:
    st.info("Insufficient data to determine this reliably. Upload at least 7 different sales dates.")
else:
    st.plotly_chart(forecast_revenue_chart(df, forecast, currency), width="stretch")
    st.metric("Estimated revenue for next 7 days", format_money(forecast['Revenue'].sum(), currency))
