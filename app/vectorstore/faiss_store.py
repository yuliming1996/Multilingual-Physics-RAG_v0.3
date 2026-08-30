import faiss
import numpy as np


class FAISSVectorStore:


    def __init__(
        self,
        dimension: int,
    ):

        self.index = faiss.IndexFlatIP(
            dimension
        )


    def add(
        self,
        embeddings: np.ndarray,
    ):

        self.index.add(
            embeddings
        )


    def save(
        self,
        path,
    ):

        faiss.write_index(
            self.index,
            str(path)
        )