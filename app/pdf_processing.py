from PyPDF2 import PdfReader
from langchain_core.documents import Document

class DocumentProcessor:
    """
    Processes uploaded PDFs and splits them into pages
    """
    def __init__(self):
        self.pages = []

    def ingest_documents(self, uploaded_file=None):
        """
        Process a PDF file from Streamlit file uploader
        """
        if uploaded_file is None:
            return

        reader = PdfReader(uploaded_file)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                self.pages.append(Document(page_content=text))
