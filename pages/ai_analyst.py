import streamlit as st

from src.metrics import product_performance
from src.page_utils import render_data_filters, require_dataframe
from src.questions import answer_question


st.set_page_config(page_title="Ask Your Data | InsightIQ", page_icon="💬", layout="wide")
st.title("💬 Ask Your Data")
st.caption("Ask simple questions about the currently selected sales data.")

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
        st.write(message["content"])

question = st.chat_input("Example: Which product made the most revenue?")
if question:
    st.session_state.question_history.append({"role": "user", "content": question})
    st.session_state.question_history.append({"role": "assistant", "content": answer_question(question, df, performance)})
    st.rerun()
