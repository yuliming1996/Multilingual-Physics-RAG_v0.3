from pathlib import Path

from langchain_core.documents import Document

from .pdf_loader import load_pdf
from .html_loader import load_html
from .text_loader import load_text



def load_document(
    file_path: Path,
) -> list[Document]:

    suffix = file_path.suffix.lower()


    if suffix == ".pdf":
        return load_pdf(file_path)


    if suffix in {".html", ".htm"}:
        return load_html(file_path)


    if suffix in {".txt", ".md"}:
        return load_text(file_path)


    raise ValueError(
        f"Unsupported file type: {suffix}"
    )