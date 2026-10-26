from html import escape
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st

from src.auth import authenticate_user, create_user, get_user_currency, initialize_auth_db
from src.session import clear_dataframe, set_currency


ASSETS = Path(__file__).parent / "assets"

st.set_page_config(page_title="InsightIQ", page_icon=str(ASSETS / "logo_icon.svg"), layout="wide")
initialize_auth_db()


def load_css() -> None:
    stylesheet = ASSETS / "styles.css"
    if stylesheet.exists():
        st.markdown(f"<style>{stylesheet.read_text()}</style>", unsafe_allow_html=True)


def sign_in_page() -> None:
    brand_column, form_column = st.columns([1.15, 1], gap="large")
    with brand_column:
        logo = (ASSETS / "logo.svg").read_text()
        features = [
            ("1", "See what changed", "Revenue, products, and trends from your own sales records."),
            ("2", "Know what to do next", "Evidence-led priorities, with no invented figures."),
            ("3", "Stay ahead of stock", "Inventory guidance when you supply stock levels."),
        ]
        feature_html = "".join(
            f'<div class="iq-feature"><div class="iq-feature-icon">{number}</div>'
            f"<div><strong>{title}</strong><span>{detail}</span></div></div>"
            for number, title, detail in features
        )
        st.markdown(
            f"""
<div class="iq-auth-brand">
  {logo}
  <h1>Sales intelligence for modern supermarkets</h1>
  <p class="iq-lead">Turn everyday sales records into clear, practical business decisions.</p>
  {feature_html}
</div>
""",
            unsafe_allow_html=True,
        )

    with form_column:
        st.space("medium")
        with st.container(border=True):
            sign_in_tab, sign_up_tab = st.tabs(["Sign in", "Create account"])
            with sign_in_tab:
                with st.form("sign_in_form", border=False):
                    email = st.text_input("Email", placeholder="you@store.com")
                    password = st.text_input("Password", type="password")
                    submitted = st.form_submit_button("Sign in", type="primary", width="stretch")
                if submitted:
                    user_name = authenticate_user(email, password)
                    if user_name:
                        st.session_state.authenticated = True
                        st.session_state.user_name = user_name
                        st.session_state.user_email = email.strip().lower()
                        set_currency(get_user_currency(email))
                        st.rerun()
                    st.error("Incorrect email or password.")
            with sign_up_tab:
                with st.form("sign_up_form", clear_on_submit=True, border=False):
                    full_name = st.text_input("Full name")
                    email = st.text_input("Email", key="signup_email", placeholder="you@store.com")
                    password = st.text_input("Password", type="password", help="At least 8 characters.")
                    submitted = st.form_submit_button("Create account", type="primary", width="stretch")
                if submitted:
                    created, message = create_user(full_name, email, password)
                    (st.success if created else st.error)(message)
        st.markdown(
            '<p class="iq-auth-footnote">Your sales data stays in your session and is not shared.</p>',
            unsafe_allow_html=True,
        )


def sign_out() -> None:
    st.session_state.authenticated = False
    for key in ("user_name", "user_email", "currency", "chat_history", "question_history"):
        st.session_state.pop(key, None)
    clear_dataframe()


load_css()

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.navigation([st.Page(sign_in_page, title="Sign in", icon=":material/login:")], position="hidden").run()
    st.stop()

st.logo(str(ASSETS / "logo.svg"), icon_image=str(ASSETS / "logo_icon.svg"), size="large")
navigation = st.navigation(
    {
        "": [
            st.Page("pages/home.py", title="Home", icon=":material/home:", default=True),
        ],
        "Analyse": [
            st.Page("pages/dashboard.py", title="Dashboard", icon=":material/space_dashboard:"),
            st.Page("pages/business_advisor.py", title="Business Advisor", icon=":material/lightbulb:"),
            st.Page("pages/inventory.py", title="Inventory Guidance", icon=":material/inventory_2:"),
            st.Page("pages/forecasting.py", title="Forecasting", icon=":material/trending_up:"),
            st.Page("pages/ai_analyst.py", title="Ask Your Data", icon=":material/forum:", url_path="ask"),
        ],
        "Share": [
            st.Page("pages/reports.py", title="Reports", icon=":material/description:"),
        ],
        "Account": [
            st.Page("pages/profile.py", title="Profile", icon=":material/person:"),
            st.Page("pages/settings.py", title="Settings", icon=":material/settings:"),
        ],
    }
)

# The account block is pushed to the bottom of the sidebar by CSS, below any page filters.
with st.sidebar.container(key="iq_account"):
    st.markdown(
        f'<div class="iq-account"><strong>{escape(st.session_state.get("user_name", "User"))}</strong>'
        f'<span>{escape(st.session_state.get("user_email", ""))}</span></div>',
        unsafe_allow_html=True,
    )
    st.button("Sign out", icon=":material/logout:", on_click=sign_out, width="stretch")

navigation.run()
