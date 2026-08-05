from langchain_core.documents import Document


class TextChunker:
    def chunk(
        self,
        documents: list[Document],
        chunk_size: int = 500,
        overlap: int = 100,
    ) -> list[Document]:

        chunked_documents = []

        for document in documents:
            text = document.page_content

            metadata = document.metadata.copy()

            start = 0

            chunk_number = 1

            while start < len(text):
                end = start + chunk_size

                chunk_text = text[start:end]

                chunked_documents.append(
                    Document(
                        page_content=chunk_text,
                        metadata={
                            **metadata,
                            "chunk": chunk_number,
                        },
                    )
                )

                chunk_number += 1

                start += chunk_size - overlap

        return chunked_documents
