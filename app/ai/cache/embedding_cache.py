import hashlib


class EmbeddingCache:
    def __init__(self):
        self._cache: dict[str, list[float]] = {}

    def _key(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def get(
        self,
        text: str,
    ) -> list[float] | None:

        return self._cache.get(self._key(text))

    def put(
        self,
        text: str,
        embedding: list[float],
    ):

        self._cache[self._key(text)] = embedding
