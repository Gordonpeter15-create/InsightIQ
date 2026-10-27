import streamlit as st

from src.cleaner import clean_data_with_report
from src.page_utils import page_header, render_currency_selector, require_authenticated
from src.session import get_dataframe, save_dataframe
from src.templates import demo_dataset_bytes, inventory_template_bytes
from src.uploads import read_sales_file


EXCEL_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def show_upload_report(report: dict) -> None:
    """Explain exactly which rows were skipped and why."""
    skipped = report["rows_skipped"]
    if not skipped:
        st.caption(f"All {report['rows_received']:,} rows passed the checks.")
        return
    st.warning(
        f"{skipped:,} of {report['rows_received']:,} rows were skipped. "
        "They are not included in any analysis.",
        icon=":material/warning:",
    )
    with st.expander("See why rows were skipped"):
        for reason, count in report["reasons"]:
            st.markdown(f"- **{count:,}** · {reason}")
        st.dataframe(report["skipped_rows"].head(50), width="stretch", hide_index=True)
        if skipped > 50:
            st.caption(f"Showing the first 50 of {skipped:,} skipped rows.")
        st.download_button(
            "Download skipped rows (CSV)",
            report["skipped_rows"].to_csv(index=False).encode("utf-8"),
            "insightiq_skipped_rows.csv",
            "text/csv",
            icon=":material/download:",
        )


require_authenticated()
first_name = str(st.session_state.get("user_name", "")).split(" ")[0]
greeting = "Welcome" if st.session_state.get("new_account") else "Welcome back"
page_header(
    f"{greeting}, {first_name}" if first_name else greeting,
    "Upload your sales records to see performance, priorities, and next steps for your store.",
    eyebrow="Home",
)

setup_column, samples_column = st.columns([3, 2], gap="large")

with setup_column:
    with st.container(border=True):
        st.markdown('<p class="iq-step">Step 1</p>', unsafe_allow_html=True)
        st.markdown("**Choose your currency**")
        render_currency_selector("home_currency")

    with st.container(border=True):
        st.markdown('<p class="iq-step">Step 2</p>', unsafe_allow_html=True)
        st.markdown("**Upload sales data**")
        st.caption("CSV or Excel with the columns Date, Product, Quantity, and Price.")
        uploaded_file = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"], label_visibility="collapsed")

        if uploaded_file is not None:
            try:
                dataframe, report = clean_data_with_report(read_sales_file(uploaded_file))
                if dataframe.empty:
                    st.error("No valid sales records were found. Check that Date, Product, Quantity, and Price contain valid values.")
                    show_upload_report(report)
                    st.stop()
                save_dataframe(dataframe)
                st.success(f"Data ready: {len(dataframe):,} clean sales record(s).")
                show_upload_report(report)
            except (ValueError, KeyError, TypeError) as error:
                st.error(f"We could not prepare this file: {error}")

with samples_column:
    with st.container(border=True):
        st.markdown("**Sample files**")
        st.caption(
            "Try InsightIQ with a fictional 28-day supermarket dataset, or start from the "
            "inventory-ready template to unlock stock guidance."
        )
        st.download_button(
            "Demo supermarket data",
            data=demo_dataset_bytes(),
            file_name="InsightIQ_demo_supermarket.xlsx",
            mime=EXCEL_MIME,
            icon=":material/download:",
            width="stretch",
        )
        st.download_button(
            "Inventory-ready template",
            data=inventory_template_bytes(),
            file_name="InsightIQ_inventory_template.xlsx",
            mime=EXCEL_MIME,
            icon=":material/table_view:",
            width="stretch",
        )
        st.caption(
            "For stock guidance, add `Current Stock` and `Reorder Point`. `Lead Time` in days is optional."
        )

dataframe = get_dataframe()
if dataframe is None:
    st.info("Upload a sales file to unlock the dashboard, advisor, forecast, and reports.", icon=":material/info:")
    st.stop()

st.subheader("Your data")
start, end = dataframe["Date"].min().date(), dataframe["Date"].max().date()
records, products, period = st.columns(3)
records.metric("Sales records", f"{len(dataframe):,}")
products.metric("Products", f"{dataframe['Product'].nunique():,}")
period.metric("Period", f"{(end - start).days + 1} days", help=f"{start} to {end}")
with st.expander("Preview the first 10 records"):
    st.dataframe(dataframe.head(10), width="stretch", hide_index=True)

st.subheader("Explore")
links = st.columns(3)
destinations = [
    ("pages/dashboard.py", "Dashboard", ":material/space_dashboard:", "Revenue, products, and trends."),
    ("pages/business_advisor.py", "Business Advisor", ":material/lightbulb:", "What changed, why, and what to do next."),
    ("pages/inventory.py", "Inventory Guidance", ":material/inventory_2:", "Stock priorities from supplied stock levels."),
    ("pages/forecasting.py", "Forecasting", ":material/trending_up:", "A simple 7-day revenue trend forecast."),
    ("pages/ai_analyst.py", "Ask Your Data", ":material/forum:", "Plain-English questions about your sales."),
    ("pages/reports.py", "Reports", ":material/description:", "Download an Excel business report."),
]
for index, (path, label, icon, description) in enumerate(destinations):
    with links[index % 3].container(border=True):
        st.page_link(path, label=label, icon=icon)
        st.caption(description)
