# app/ai/llm/dependencies.py
from app.ai.llm.groq_client import get_llm


def get_llm_dependency():
    return get_llm()
