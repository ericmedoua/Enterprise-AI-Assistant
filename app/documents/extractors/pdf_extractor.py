from pathlib import Path

from langchain_core.documents import Document
from pypdf import PdfReader


class PDFExtractor:
    def extract(
        self,
        path: str,
    ) -> list[Document]:

        reader = PdfReader(path)

        filename = Path(path).name

        documents = []

        for page_number, page in enumerate(
            reader.pages,
            start=1,
        ):
            text = page.extract_text()

            if not text:
                continue

            documents.append(
                Document(
                    page_content=text,
                    metadata={
                        "source": filename,
                        "page": page_number,
                    },
                )
            )

        return documents
