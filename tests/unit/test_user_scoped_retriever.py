from types import SimpleNamespace

from app.ai.retrieval import dependencies


def test_user_retriever_filters_by_current_user(monkeypatch):
    captured = {}

    class FakeChroma:
        def as_retriever(self, search_kwargs=None, **kwargs):
            captured["search_kwargs"] = search_kwargs
            return "scoped-retriever"

    monkeypatch.setattr(dependencies, "get_chroma_service", lambda: FakeChroma())

    retriever = dependencies.get_user_retriever(current_user=SimpleNamespace(id=123))

    assert retriever == "scoped-retriever"
    assert captured["search_kwargs"] == {
        "k": 4,
        "filter": {"owner_id": "123"},
    }
