from fastapi import FastAPI
from pydantic import BaseModel
from agent.sql_agent import ask

app = FastAPI(title="Text-to-SQL Agent API")

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    question: str
    answer: str

@app.get("/")
def root():
    return {"message": "Text-to-SQL Agent is running!"}

@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    answer = ask(request.question)
    return QueryResponse(
        question=request.question,
        answer=answer
    )