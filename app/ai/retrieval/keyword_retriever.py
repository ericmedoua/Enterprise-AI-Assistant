from rank_bm25 import BM25Okapi
from langchain_core.documents import Document


class KeywordRetriever:
    def __init__(self):
        self.documents: list[Document] = []
        self.bm25 = None

    def index(
        self,
        documents: list[Document],
    ):

        self.documents = documents

        corpus = [doc.page_content.split() for doc in documents]

        self.bm25 = BM25Okapi(corpus)

    def retrieve(
        self,
        query: str,
        k: int = 4,
    ) -> list[Document]:

        if self.bm25 is None:
            return []

        tokens = query.split()

        return self.bm25.get_top_n(
            tokens,
            self.documents,
            n=k,
        )
