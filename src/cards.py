import streamlit as st

from src.currency import DEFAULT_CURRENCY, format_money


def show_kpi_cards(metrics: dict[str, float | int], currency: str = DEFAULT_CURRENCY) -> None:
    """Render the dashboard's four core KPI cards."""
    revenue, orders, items, average_order = st.columns(4)
    revenue.metric("Total revenue", format_money(metrics['revenue'], currency))
    orders.metric("Orders", f"{metrics['orders']:,}")
    items.metric("Items sold", f"{metrics['items']:,}")
    average_order.metric("Average order", format_money(metrics['average_order'], currency))
