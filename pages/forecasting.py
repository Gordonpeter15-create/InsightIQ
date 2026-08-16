import streamlit as st

from src.forecasting import forecast_revenue, forecast_revenue_chart
from src.page_utils import render_data_filters, require_dataframe


st.set_page_config(page_title="Forecasting | InsightIQ", page_icon="🔮", layout="wide")
st.title("🔮 Revenue Forecast")
st.caption("A simple learning forecast based on daily revenue trend; it is not a financial guarantee.")

df = render_data_filters(require_dataframe(), "forecast")
if df.empty:
    st.warning("No sales match these filters.")
    st.stop()
forecast = forecast_revenue(df, days_ahead=7)
if forecast is None:
    st.info("Insufficient data to determine this reliably. Upload at least 7 different sales dates.")
else:
    st.plotly_chart(forecast_revenue_chart(df, forecast), use_container_width=True)
    st.metric("Estimated revenue for next 7 days", f"${forecast['Revenue'].sum():,.2f}")
