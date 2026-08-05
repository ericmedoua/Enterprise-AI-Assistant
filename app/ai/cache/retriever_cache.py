import hashlib

from langchain_core.documents import Document


class RetrieverCache:
    def __init__(self):
        self.cache: dict[str, list[Document]] = {}

    def _key(
        self,
        query: str,
    ) -> str:

        return hashlib.sha256(query.lower().strip().encode()).hexdigest()

    def get(
        self,
        query: str,
    ):

        return self.cache.get(self._key(query))

    def put(
        self,
        query: str,
        documents: list[Document],
    ):

        self.cache[self._key(query)] = documents
