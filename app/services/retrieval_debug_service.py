from app.ai.vectorstore.chroma_service import ChromaService
from app.ai.retrieval.dependencies import get_chroma_service
from app.schemas.debug import (
    RetrievalDebugResponse,
    RetrievalDebugResult,
)


class RetrievalDebugService:
    def search(self, query: str, k: int = 4):

        results = get_chroma_service().similarity_search_with_score(
            query=query,
            k=k,
        )

        debug_results = []

        for document, score in results:
            debug_results.append(
                RetrievalDebugResult(
                    score=round(float(score), 4),
                    source=document.metadata.get(
                        "source",
                        "Unknown",
                    ),
                    page=document.metadata.get(
                        "page",
                    ),
                    chunk=document.metadata.get(
                        "chunk",
                    ),
                    preview=document.page_content[:250],
                )
            )

        return RetrievalDebugResponse(
            query=query,
            results=debug_results,
        )
