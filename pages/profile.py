import streamlit as st

from src.page_utils import page_header, require_authenticated
from src.session import get_dataframe


require_authenticated()
page_header("Profile", "Your account and current session.", eyebrow="Account")
dataframe = get_dataframe()
with st.container(border=True):
    st.markdown(f"**Name**  \n{st.session_state.get('user_name', 'User')}")
    if st.session_state.get("user_email"):
        st.markdown(f"**Email**  \n{st.session_state['user_email']}")
    st.markdown(f"**Current dataset**  \n{'Loaded' if dataframe is not None else 'Not loaded'}")
    if dataframe is not None:
        st.markdown(f"**Sales records loaded**  \n{len(dataframe):,}")
