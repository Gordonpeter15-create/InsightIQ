import streamlit as st

from src.page_utils import page_header, render_currency_selector, require_authenticated
from src.session import clear_dataframe, get_dataframe


require_authenticated()
page_header("Settings", "Preferences for your account and this session.", eyebrow="Account")

settings_column, _ = st.columns([3, 2])

with settings_column.container(border=True):
    st.markdown("**Currency**")
    st.caption("The currency your sales data is recorded in. Your choice is saved to your account.")
    render_currency_selector("settings_currency")

with settings_column.container(border=True):
    st.markdown("**Dataset**")
    st.caption("The sales data loaded in this browser session.")
    dataframe = get_dataframe()
    if dataframe is None:
        st.markdown("No dataset is currently loaded.")
    else:
        st.markdown(f"{len(dataframe):,} sales records loaded.")
        if st.button("Clear current dataset", icon=":material/delete:"):
            clear_dataframe()
            st.success("The current dataset has been cleared. Upload another file from the Home page.")
