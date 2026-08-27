from langchain_community.utilities import SQLDatabase
from langchain_groq import ChatGroq
from langchain_community.agent_toolkits import create_sql_agent
from dotenv import load_dotenv
import os

load_dotenv()

try:
    import streamlit as st
    _secrets = st.secrets
except Exception:
    _secrets = {}


def get_env(key: str) -> str:
    return os.getenv(key) or _secrets.get(key, "")


def get_db():
    db_uri = (
        f"postgresql+psycopg2://{get_env('DB_USER')}:"
        f"{get_env('DB_PASSWORD')}@{get_env('DB_HOST')}:"
        f"{get_env('DB_PORT')}/{get_env('DB_NAME')}"
    )
    return SQLDatabase.from_uri(db_uri)


def get_agent():
    db = get_db()

    llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    groq_api_key=get_env("GROQ_API_KEY")
    )

    agent = create_sql_agent(
        llm=llm,
        db=db,
        agent_type="tool-calling",
        verbose=True
    )

    return agent


def ask(question: str) -> str:
    try:
        agent = get_agent()
        result = agent.invoke({"input": question})
        return result.get("output") or result.get("answer") or str(result)
    except Exception as e:
        return f"Error: {str(e)}"
