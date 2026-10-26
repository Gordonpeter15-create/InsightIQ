import streamlit as st

from src.ai import generate_insights
from src.metrics import calculate_metrics, product_performance
from src.page_utils import page_header, render_data_filters, require_dataframe
from src.reports import build_excel_report
from src.session import get_currency


page_header("Business Reports", "Download an Excel report with the selected KPIs, product performance, insights, and sales data.", eyebrow="Share")

df = render_data_filters(require_dataframe(), "reports")
if df.empty:
    st.warning("No sales match these filters.")
    st.stop()
metrics = calculate_metrics(df)
performance = product_performance(df)
currency = get_currency()
insights = generate_insights(df, performance, currency)
report = build_excel_report(df, metrics, performance, insights, currency)
st.download_button(
    "Download Excel business report", report, "insightiq_business_report.xlsx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    type="primary", icon=":material/download:",
)
