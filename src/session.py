import streamlit as st
import pandas as pd

from src.currency import DEFAULT_CURRENCY


def save_dataframe(df: pd.DataFrame):
    st.session_state["sales_df"] = df


def get_dataframe():
    return st.session_state.get("sales_df")


def has_dataframe():
    return "sales_df" in st.session_state


def clear_dataframe():
    st.session_state.pop("sales_df", None)

def get_currency() -> str:
    return st.session_state.get("currency", DEFAULT_CURRENCY)


def set_currency(currency: str) -> None:
    st.session_state["currency"] = currency
