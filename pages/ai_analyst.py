import streamlit as st

from src.metrics import product_performance
from src.page_utils import page_header, render_data_filters, require_dataframe, safe_markdown
from src.questions import answer_question
from src.session import get_currency


page_header("Ask Your Data", "Ask plain-English questions about the currently selected sales data.", eyebrow="Analyse")

df = render_data_filters(require_dataframe(), "questions")
if df.empty:
    st.warning("No sales match these filters.")
    st.stop()
performance = product_performance(df)

if "question_history" not in st.session_state:
    st.session_state.question_history = []
if st.button("Clear chat"):
    st.session_state.question_history = []
    st.rerun()
for message in st.session_state.question_history:
    with st.chat_message(message["role"]):
        st.markdown(safe_markdown(message["content"]))

question = st.chat_input("Example: Which product made the most revenue?")
if question:
    st.session_state.question_history.append({"role": "user", "content": question})
    st.session_state.question_history.append({"role": "assistant", "content": answer_question(question, df, performance, get_currency())})
    st.rerun()
