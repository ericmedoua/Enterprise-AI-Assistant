from app.schemas.citation import Citation
from app.schemas.retrieval import RetrievalResult


def build_retrieval_results(results):

    formatted = []

    for document, score in results:
        formatted.append(
            RetrievalResult(
                citation=Citation(
                    source=document.metadata.get("source"),
                    page=document.metadata.get("page"),
                    chunk=document.metadata.get("chunk"),
                ),
                score=round(float(score), 4),
            )
        )

    return formatted
