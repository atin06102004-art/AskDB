import streamlit as st
from agent.sql_agent import ask

st.set_page_config(page_title="Text-to-SQL Agent", page_icon="🤖")

st.title("🤖 Text-to-SQL Agent")
st.markdown("Ask any question about the Northwind database in plain English!")

st.sidebar.header("💡 Example Questions")
examples = [
    "How many customers are there?",
    "Which country has the most customers?",
    "Who are the top 5 customers by number of orders?",
    "What are the top 3 selling products?",
    "Which employee has handled the most orders?",
    "What is the total revenue per country?"
]

for example in examples:
    if st.sidebar.button(example):
        st.session_state.question = example

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input("Ask a question about the database...")

if "question" in st.session_state and st.session_state.question:
    question = st.session_state.question
    st.session_state.question = None

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer = ask(question)
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
