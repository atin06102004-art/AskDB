from langchain_community.utilities import SQLDatabase
from langchain_groq import ChatGroq
from langchain_community.agent_toolkits import create_sql_agent
from dotenv import load_dotenv
import os

load_dotenv()

def get_db():
    db_uri = (
        f"postgresql+psycopg2://{os.getenv('DB_USER')}:"
        f"{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:"
        f"{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )
    return SQLDatabase.from_uri(db_uri)


def get_agent():
    db = get_db()

    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0,
        groq_api_key=os.getenv("GROQ_API_KEY")
    )

    agent = create_sql_agent(
        llm=llm,
        db=db,
        agent_type="openai-tools",
        verbose=True
    )

    return agent


def ask(question: str) -> str:
    try:
        agent = get_agent()
        result = agent.invoke({"input": question})
        return result["output"]
    except Exception as e:
        return f"Error: {str(e)}"