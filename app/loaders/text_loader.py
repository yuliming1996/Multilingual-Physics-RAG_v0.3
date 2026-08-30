from pathlib import Path

from langchain_core.documents import Document


def load_text(
    file_path: Path,
) -> list[Document]:

    text = file_path.read_text(
        encoding="utf-8"
    )

    document = Document(
        page_content=text,
        metadata={
            "source": str(file_path)
        }
    )

    return [document]