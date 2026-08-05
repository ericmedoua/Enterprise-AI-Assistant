from app.ai.retrieval.keyword_retriever import KeywordRetriever
from app.ai.retrieval.merger import merge_results
import asyncio


class HybridRetriever:
    def __init__(
        self,
        semantic_retriever,
        keyword_retriever: KeywordRetriever,
    ):
        self.semantic = semantic_retriever
        self.keyword = keyword_retriever

    def retrieve(
        self,
        query: str,
        k: int = 4,
    ):

        semantic_docs = self.semantic.invoke(query)

        keyword_docs = self.keyword.retrieve(
            query,
            k=k,
        )

        return merge_results(
            semantic_docs,
            keyword_docs,
        )

    async def aretrieve(
        self,
        query: str,
    ):
        return await asyncio.to_thread(
            self.retrieve,
            query,
        )
