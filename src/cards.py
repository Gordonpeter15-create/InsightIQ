import streamlit as st


def show_kpi_cards(metrics: dict[str, float | int]) -> None:
    """Render the dashboard's four core KPI cards."""
    revenue, orders, items, average_order = st.columns(4)
    revenue.metric("💰 Total Revenue", f"${metrics['revenue']:,.2f}")
    orders.metric("🛒 Orders", f"{metrics['orders']:,}")
    items.metric("📦 Items Sold", f"{metrics['items']:,}")
    average_order.metric("📊 Average Order", f"${metrics['average_order']:,.2f}")
