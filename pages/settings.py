import streamlit as st

from src.page_utils import require_authenticated
from src.session import clear_dataframe, get_dataframe


st.set_page_config(page_title="Settings | InsightIQ", page_icon="⚙️", layout="wide")
require_authenticated()
st.title("⚙️ Settings")
st.write("Manage the sales dataset stored for your current browser session.")
if get_dataframe() is None:
    st.info("No dataset is currently loaded.")
elif st.button("Clear current dataset"):
    clear_dataframe()
    st.success("The current dataset has been cleared. Upload another file from the Home page.")
