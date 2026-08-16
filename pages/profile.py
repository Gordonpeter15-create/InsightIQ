import streamlit as st

from src.page_utils import require_authenticated
from src.session import get_dataframe


st.set_page_config(page_title="Profile | InsightIQ", page_icon="👤", layout="wide")
require_authenticated()
st.title("👤 Profile")
st.write(f"**Name:** {st.session_state.get('user_name', 'User')}")
dataframe = get_dataframe()
st.write(f"**Current dataset:** {'Loaded' if dataframe is not None else 'Not loaded'}")
if dataframe is not None:
    st.write(f"**Sales records loaded:** {len(dataframe):,}")
