from langgraph.graph import StateGraph, START, END
from langraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from typing import Annotated, Literal

llm = init_chat_model(
    model="openai/gpt-oss-120b",
    model_provider="groq"
)
