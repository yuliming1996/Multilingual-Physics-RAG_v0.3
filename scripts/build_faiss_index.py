"""
build_faiss_index.py

Build a FAISS vector index from the complete embedding matrix.

The FAISS index is rebuilt from the current embeddings so that
the vector index always remains consistent with chunks.jsonl
and embeddings.npy.
"""

import numpy as np

from app.vectorstore import FAISSVectorStore
from app.config import (
    EMBEDDINGS_PATH,
    FAISS_INDEX_PATH,
)


def main():

    print(
        "Loading embeddings..."
    )

    embeddings = np.load(
        EMBEDDINGS_PATH
    )


    if embeddings.ndim != 2:
        raise ValueError(
            "Embeddings must be a 2D array."
        )


    if embeddings.shape[0] == 0:
        raise ValueError(
            "Embeddings are empty."
        )


    print(
        "Embeddings:",
        embeddings.shape
    )


    dimension = embeddings.shape[1]


    store = FAISSVectorStore(
        dimension
    )


    store.add(
        embeddings
    )


    FAISS_INDEX_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )


    store.save(
        FAISS_INDEX_PATH
    )


    print(
        "FAISS index saved:"
    )

    print(
        FAISS_INDEX_PATH
    )


if __name__ == "__main__":
    main()