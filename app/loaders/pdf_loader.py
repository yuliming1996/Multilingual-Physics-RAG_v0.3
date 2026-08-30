from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document


def load_pdf(
    file_path: Path,
) -> list[Document]:

    loader = PyPDFLoader(
        str(file_path)
    )

    documents = loader.load()

    return documents