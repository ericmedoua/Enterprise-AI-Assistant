from app.ai.vectorstore.chroma_service import ChromaService
from app.schemas.debug import (
    RetrievalDebugResponse,
    RetrievalDebugResult,
)


class RetrievalDebugService:
    def __init__(self):

        self.vectorstore = ChromaService()

    def search(
        self,
        query: str,
        k: int = 4,
    ) -> RetrievalDebugResponse:

        results = self.vectorstore.similarity_search_with_score(
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
