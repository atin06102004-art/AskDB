import streamlit as st
import requests
import os

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

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

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input box
question = st.chat_input("Ask a question about the database...")

if "question" in st.session_state and st.session_state.question:
    question = st.session_state.question
    st.session_state.question = None

if question:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    # Call FastAPI
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{API_URL}/query",
                    json={"question": question}
                )
                answer = response.json()["answer"]
                st.markdown(answer)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })
            except Exception as e:
                st.error(f"Error: {str(e)}")
