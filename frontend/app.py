from langchain_community.utilities import SQLDatabase
from langchain_groq import ChatGroq
from langchain_community.agent_toolkits import create_sql_agent
from dotenv import load_dotenv
import os
import tempfile
import re
import sqlite3
import pandas as pd

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


def sanitize_table_name(name: str) -> str:
    name = re.sub(r'\W+', '_', name).strip('_').lower()
    if not name or name[0].isdigit():
        name = f"t_{name}"
    return name


def build_sqlite_from_uploads(uploaded_files) -> str:
    """
    uploaded_files: list of Streamlit UploadedFile objects (.csv, .xlsx, .xls)
    Each CSV becomes one table. Each sheet in an Excel file becomes its own table.
    Returns the path to a temp SQLite database file containing all of them.
    """
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    db_path = tmp_file.name
    tmp_file.close()

    conn = sqlite3.connect(db_path)
    used_names = set()

    def unique_name(base):
        name = base
        i = 1
        while name in used_names:
            name = f"{base}_{i}"
            i += 1
        used_names.add(name)
        return name

    for f in uploaded_files:
        base_name = sanitize_table_name(f.name.rsplit(".", 1)[0])
        ext = f.name.rsplit(".", 1)[-1].lower()

        if ext == "csv":
            df = pd.read_csv(f)
            table_name = unique_name(base_name)
            df.to_sql(table_name, conn, if_exists="replace", index=False)

        elif ext in ("xlsx", "xls"):
            sheets = pd.read_excel(f, sheet_name=None)
            for sheet_name, df in sheets.items():
                table_name = unique_name(sanitize_table_name(f"{base_name}_{sheet_name}"))
                df.to_sql(table_name, conn, if_exists="replace", index=False)

    conn.close()
    return db_path


def get_db_from_sqlite(db_path: str):
    return SQLDatabase.from_uri(f"sqlite:///{db_path}")


def get_agent_for_db(db):
    llm = ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0,
        groq_api_key=get_env("GROQ_API_KEY")
    )
    return create_sql_agent(
        llm=llm,
        db=db,
        agent_type="tool-calling",
        verbose=True
    )


def ask_with_agent(agent, question: str) -> str:
    try:
        result = agent.invoke({"input": question})
        return result.get("output") or result.get("answer") or str(result)
    except Exception as e:
        return f"Error: {str(e)}"
