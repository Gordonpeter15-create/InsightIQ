import streamlit as st

from src.ai import generate_insights
from src.metrics import calculate_metrics, product_performance
from src.page_utils import render_data_filters, require_dataframe
from src.reports import build_excel_report


st.set_page_config(page_title="Reports | InsightIQ", page_icon="📄", layout="wide")
st.title("📄 Business Reports")

df = render_data_filters(require_dataframe(), "reports")
if df.empty:
    st.warning("No sales match these filters.")
    st.stop()
metrics = calculate_metrics(df)
performance = product_performance(df)
insights = generate_insights(df, performance)
report = build_excel_report(df, metrics, performance, insights)
st.write("Download an Excel report containing the selected KPIs, product performance, insights, and sales data.")
st.download_button(
    "⬇ Download Excel Business Report", report, "insightiq_business_report.xlsx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)
