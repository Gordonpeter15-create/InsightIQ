from pathlib import Path

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

AVATARS = {
    "user": ":material/person:",
    "assistant": str(Path(__file__).resolve().parents[1] / "assets" / "logo_icon.svg"),
}
SUGGESTED_QUESTIONS = [
    "What is the total revenue?",
    "Which product made the most revenue?",
    "Which product sold the most units?",
    "Which product had the lowest revenue?",
    "What was the highest revenue day?",
]


def ask(question: str) -> None:
    st.session_state.question_history.append({"role": "user", "content": question})
    st.session_state.question_history.append(
        {"role": "assistant", "content": answer_question(question, df, performance, get_currency())}
    )


if "question_history" not in st.session_state:
    st.session_state.question_history = []

if not st.session_state.question_history:
    with st.container(border=True):
        st.markdown("**Try a question**")
        st.caption("Answers come only from the sales data and filters you have selected.")
        suggestion = st.pills(
            "Suggested questions", SUGGESTED_QUESTIONS, label_visibility="collapsed", key="suggested_question"
        )
    if suggestion:
        ask(suggestion)
        st.session_state.pop("suggested_question", None)
        st.rerun()
else:
    if st.button("Clear chat", icon=":material/delete_sweep:"):
        st.session_state.question_history = []
        st.rerun()

for message in st.session_state.question_history:
    with st.chat_message(message["role"], avatar=AVATARS[message["role"]]):
        st.markdown(safe_markdown(message["content"]))

question = st.chat_input("Ask about revenue, products, units sold, or your best day")
if question:
    ask(question)
    st.rerun()
