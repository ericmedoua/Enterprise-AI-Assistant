from langchain_core.runnables import Runnable
from app.observability.timer import Timer


class TimedRetriever(Runnable):
    def __init__(
        self,
        retriever,
        metrics,
    ):
        self.retriever = retriever
        self.metrics = metrics

    def invoke(
        self,
        input,
        config=None,
    ):
        timer = Timer()

        docs = self.retriever.invoke(
            input,
            config=config,
        )

        self.metrics.retrieval_ms = timer.elapsed_ms()

        self.metrics.retrieved_documents = len(docs)

        return docs
