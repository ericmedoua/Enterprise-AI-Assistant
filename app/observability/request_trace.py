from app.observability.metrics import RequestMetrics
from app.observability.timer import Timer


class RequestTrace:
    def __init__(self):

        self.metrics = RequestMetrics()

        self.total_timer = Timer()

        self.stage_timer = Timer()

    def start_stage(self):

        self.stage_timer = Timer()

    def end_database(self):

        self.metrics.database_ms = self.stage_timer.elapsed_ms()

    def end_memory(self):

        self.metrics.memory_ms = self.stage_timer.elapsed_ms()

    def end_retrieval(self):

        self.metrics.retrieval_ms = self.stage_timer.elapsed_ms()

    def end_documents(self):
        self.metrics.documents_ms = self.stage_timer.elapsed_ms()

    def end_llm(self):

        self.metrics.llm_ms = self.stage_timer.elapsed_ms()

    def finish(self):

        self.metrics.total_ms = self.total_timer.elapsed_ms()

        return self.metrics
