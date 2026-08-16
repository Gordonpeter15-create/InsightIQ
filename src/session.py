import streamlit as st
import pandas as pd


def save_dataframe(df: pd.DataFrame):
    st.session_state["sales_df"] = df


def get_dataframe():
    return st.session_state.get("sales_df")


def has_dataframe():
    return "sales_df" in st.session_state


def clear_dataframe():
    st.session_state.pop("sales_df", None)