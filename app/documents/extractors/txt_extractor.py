from pathlib import Path

from langchain_core.documents import Document


class TXTExtractor:
    def extract(
        self,
        path: str,
    ) -> list[Document]:

        with open(
            path,
            encoding="utf-8",
        ) as file:
            text = file.read()

        return [
            Document(
                page_content=text,
                metadata={
                    "source": Path(path).name,
                    "page": 1,
                },
            )
        ]
