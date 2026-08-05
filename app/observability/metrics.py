from dataclasses import dataclass


@dataclass
class RequestMetrics:
    database_ms: float = 0

    memory_ms: float = 0

    retrieval_ms: float = 0

    llm_ms: float = 0

    total_ms: float = 0

    # retrieved_documents: int = 0

    documents_ms: int = 0

    prompt_tokens: int = 0

    completion_tokens: int = 0
