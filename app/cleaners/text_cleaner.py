import re

from langchain_core.documents import Document


def clean_text(
    text: str,
) -> str:

    # remove Windows style newline
    text = text.replace(
        "\r\n",
        "\n",
    )

    # remove trailing spaces
    lines = [
        line.strip()
        for line in text.split("\n")
    ]

    text = "\n".join(lines)


    # collapse multiple blank lines
    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text,
    )


    return text



def clean_documents(
    documents: list[Document],
) -> list[Document]:

    cleaned_documents = []


    for document in documents:

        document.page_content = clean_text(
            document.page_content
        )

        cleaned_documents.append(
            document
        )


    return cleaned_documents