from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config import (
    CHUNK_SIZE,
    CHUNK_OVERLAP,
)

MIN_CHUNK_LENGTH = 20


def split_documents(
    documents,
) -> list:

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )

    chunks = splitter.split_documents(
        documents
    )


    useful_chunks = []

    for chunk in chunks:

        text = chunk.page_content.strip()

        if len(text) < MIN_CHUNK_LENGTH:
            continue

        useful_chunks.append(chunk)


    return useful_chunks