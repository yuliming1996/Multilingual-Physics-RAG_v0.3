from pathlib import Path

from bs4 import BeautifulSoup
from langchain_core.documents import Document


def load_html(
    file_path: Path,
) -> list[Document]:

    with file_path.open(
        encoding="utf-8"
    ) as file:

        html = file.read()


    soup = BeautifulSoup(
        html,
        "html.parser"
    )


    # remove useless html elements
    for element in soup(
        [
            "script",
            "style",
            "nav",
            "footer",
            "header",
        ]
    ):
        element.decompose()


    text = soup.get_text(
        separator="\n"
    )


    document = Document(
        page_content=text,
        metadata={
            "source": str(file_path)
        }
    )


    return [document]