import pandas as pd
import streamlit as st

from src.session import get_dataframe


def require_authenticated() -> None:
    if not st.session_state.get("authenticated", False):
        st.warning("👆 Please sign in from the Home page first.")
        st.stop()


def require_dataframe() -> pd.DataFrame:
    require_authenticated()
    df = get_dataframe()
    if df is None:
        st.warning("👆 Please upload a dataset from the Home page first.")
        st.stop()
    return df.copy()


def render_data_filters(df: pd.DataFrame, key_prefix: str) -> pd.DataFrame:
    """Render page-local filters and return a filtered copy of the shared dataframe."""
    with st.sidebar:
        st.header("Filters")
        products = ["All"] + sorted(df["Product"].dropna().unique().tolist())
        selected_product = st.selectbox("Product", products, key=f"{key_prefix}_product")
        if selected_product != "All":
            df = df[df["Product"] == selected_product]
        min_date, max_date = df["Date"].min().date(), df["Date"].max().date()
        dates = st.date_input(
            "Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date,
            key=f"{key_prefix}_dates",
        )
        if isinstance(dates, tuple) and len(dates) == 2:
            df = df[df["Date"].between(*map(pd.Timestamp, dates))]
    return df
