import streamlit as st

from src.page_utils import page_header, render_currency_selector, require_authenticated
from src.session import clear_dataframe, get_dataframe


require_authenticated()
page_header("Settings", "Preferences for your account and this session.", eyebrow="Account")

st.subheader("Currency")
st.write("Choose the currency your sales data is recorded in. Your choice is saved to your account.")
currency_column, _ = st.columns([1, 2])
with currency_column:
    render_currency_selector("settings_currency")

st.subheader("Dataset")
st.write("Manage the sales dataset stored for your current browser session.")
if get_dataframe() is None:
    st.info("No dataset is currently loaded.")
elif st.button("Clear current dataset"):
    clear_dataframe()
    st.success("The current dataset has been cleared. Upload another file from the Home page.")
