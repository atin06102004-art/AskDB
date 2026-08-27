import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from agent.sql_agent import (
    ask, build_sqlite_from_uploads, get_db_from_sqlite,
    get_agent_for_db, ask_with_agent
)

st.set_page_config(page_title="Text-to-SQL Agent", page_icon="🤖")
st.title("🤖 Text-to-SQL Agent")

mode = st.radio("Data source", ["Northwind demo database", "Upload your own data"])

uploaded_agent = None

if mode == "Upload your own data":
    files = st.file_uploader(
        "Upload one or more CSV or Excel files",
        type=["csv", "xlsx", "xls"],
        accept_multiple_files=True
    )
    if files:
        # Only rebuild if the set of uploaded files changed
        file_signature = tuple(f.name + str(f.size) for f in files)
        if st.session_state.get("upload_signature") != file_signature:
            with st.spinner("Loading your files..."):
                db_path = build_sqlite_from_uploads(files)
                db = get_db_from_sqlite(db_path)
                st.session_state.uploaded_agent = get_agent_for_db(db)
                st.session_state.upload_signature = file_signature
                st.session_state.messages = []  # reset chat on new upload
            st.success(f"Loaded {len(files)} file(s). Ask away!")
        uploaded_agent = st.session_state.get("uploaded_agent")
    else:
        st.info("Upload at least one file to start asking questions.")
else:
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

question = st.chat_input("Ask a question about the data...")

if "question" in st.session_state and st.session_state.question:
    question = st.session_state.question
    st.session_state.question = None

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            if mode == "Upload your own data":
                if uploaded_agent:
                    answer = ask_with_agent(uploaded_agent, question)
                else:
                    answer = "Please upload a file first."
            else:
                answer = ask(question)
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
