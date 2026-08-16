from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd
import streamlit as st

from src.auth import authenticate_user, create_user, initialize_auth_db
from src.cleaner import clean_data
from src.session import clear_dataframe, save_dataframe


st.set_page_config(page_title="InsightIQ", page_icon="📊", layout="wide")
initialize_auth_db()


def load_css() -> None:
    stylesheet = Path(__file__).parent / "assets" / "styles.css"
    if stylesheet.exists():
        st.markdown(f"<style>{stylesheet.read_text()}</style>", unsafe_allow_html=True)


def read_uploaded_file(uploaded_file) -> pd.DataFrame:
    if uploaded_file.name.lower().endswith(".csv"):
        return pd.read_csv(uploaded_file)
    return pd.read_excel(uploaded_file)


load_css()
hero = """
<section class="iq-hero">
  <h1>📊 InsightIQ</h1>
  <p>Turn everyday supermarket sales data into clear business decisions.</p>
</section>
"""

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown(hero, unsafe_allow_html=True)
    st.subheader("Welcome to InsightIQ")
    st.write("Create an account or sign in to upload supermarket sales data.")
    sign_in_tab, sign_up_tab = st.tabs(["Sign in", "Create account"])
    with sign_in_tab:
        with st.form("sign_in_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Sign in")
        if submitted:
            user_name = authenticate_user(email, password)
            if user_name:
                st.session_state.authenticated = True
                st.session_state.user_name = user_name
                st.rerun()
            st.error("Incorrect email or password.")
    with sign_up_tab:
        with st.form("sign_up_form", clear_on_submit=True):
            full_name = st.text_input("Your name")
            email = st.text_input("Email", key="signup_email")
            password = st.text_input("Password (at least 8 characters)", type="password")
            submitted = st.form_submit_button("Create account")
        if submitted:
            created, message = create_user(full_name, email, password)
            (st.success if created else st.error)(message)
    st.stop()

st.markdown(hero, unsafe_allow_html=True)
st.caption(f"Signed in as {st.session_state.get('user_name', 'User')}")

sidebar_logout, _ = st.sidebar.columns([1, 1])
with sidebar_logout:
    if st.button("Log out"):
        st.session_state.authenticated = False
        st.session_state.pop("user_name", None)
        st.session_state.pop("chat_history", None)
        clear_dataframe()
        st.rerun()

st.header("Upload sales data")
st.write("Your file needs these columns: `Date`, `Product`, `Quantity`, and `Price`.")
uploaded_file = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        dataframe = clean_data(read_uploaded_file(uploaded_file))
        if dataframe.empty:
            st.error("No valid sales records were found. Check that Date, Product, Quantity, and Price contain valid values.")
            st.stop()
        save_dataframe(dataframe)
        st.success(f"Data ready: {len(dataframe):,} clean sales record(s).")
        st.dataframe(dataframe.head(10), use_container_width=True, hide_index=True)
    except (ValueError, KeyError, TypeError) as error:
        st.error(f"We could not prepare this file: {error}")
else:
    st.info("Upload a sales file, then use the pages in the sidebar to explore the dashboard and Business Advisor.")

st.markdown("---")
st.subheader("Start here")
st.markdown(
    """
- **Dashboard** — see revenue, products, and trends.
- **Business Advisor** — see what is happening, why, what to do next, and what to watch.
- **Forecasting** — view a simple trend forecast when enough sales history is available.
- **Reports** — download a business report from the selected data.
"""
)
