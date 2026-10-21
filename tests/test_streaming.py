from app.ai.streaming.stream_service import StreamingService
from app.ai.streaming.dependencies import get_streaming_service
from app.ai.retrieval.dependencies import get_user_retriever


class FakeChain:
    def __init__(self):
        self.inputs = []

    async def astream(self, payload):
        self.inputs.append(payload)
        yield "Hello "
        yield "world"


def test_streaming_service_streams_rag_chain(monkeypatch):
    fake_chain = FakeChain()
    captured = {}

    def fake_build_rag_chain(*, retriever, llm):
        captured["retriever"] = retriever
        captured["llm"] = llm
        return fake_chain

    monkeypatch.setattr(
        "app.ai.streaming.stream_service.build_rag_chain",
        fake_build_rag_chain,
    )

    retriever = object()
    llm = object()
    service = StreamingService(llm=llm, retriever=retriever)

    async def collect():
        return [chunk async for chunk in service.stream("What does the policy say?")]

    assert captured == {"retriever": retriever, "llm": llm}
    assert asyncio_run(collect()) == ["Hello ", "world"]
    assert fake_chain.inputs == [
        {
            "question": "What does the policy say?",
            "history": [],
            "summary": "",
        }
    ]


def asyncio_run(coro):
    import asyncio

    return asyncio.run(coro)


def test_streaming_dependency_uses_authenticated_user_retriever():
    import inspect

    parameter = inspect.signature(get_streaming_service).parameters["retriever"]
    assert parameter.default.dependency is get_user_retriever
