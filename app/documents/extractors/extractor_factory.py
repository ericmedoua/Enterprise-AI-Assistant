from app.documents.extractors.pdf_extractor import PDFExtractor
from app.documents.extractors.docx_extractor import DOCXExtractor
from app.documents.extractors.txt_extractor import TXTExtractor


class ExtractorFactory:
    @staticmethod
    def get(file_name: str):

        file_name = file_name.lower()

        if file_name.endswith(".pdf"):
            return PDFExtractor()

        if file_name.endswith(".docx"):
            return DOCXExtractor()

        if file_name.endswith(".txt"):
            return TXTExtractor()

        raise ValueError(f"Unsupported document type: {file_name}")
