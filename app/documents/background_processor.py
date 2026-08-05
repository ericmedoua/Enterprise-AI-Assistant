from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(
    max_workers=2,
)

from pathlib import Path

from app.documents.services.document_service import (
    DocumentService,
)

from app.ai.vectorstore.dependencies import (
    get_vector_store,
)

from langchain_core.documents import Document


def process_document(
    path: str,
):
    service = DocumentService()

    pages = service.process(
        Path(path),
    )

    docs = []

    for page in pages:
        docs.extend(
            [
                Document(
                    page_content=chunk["text"],
                    metadata=chunk["metadata"],
                )
                for chunk in page["chunks"]
            ]
        )

    vector_store = get_vector_store()

    vector_store.add_documents(
        docs,
    )
