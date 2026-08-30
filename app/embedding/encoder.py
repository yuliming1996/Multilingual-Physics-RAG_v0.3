from sentence_transformers import SentenceTransformer

from app.config import (
    EMBEDDING_MODEL,
    NORMALIZE_EMBEDDINGS,
    EMBEDDING_BATCH_SIZE,
)



class EmbeddingModel:


    def __init__(self):

        self.model = SentenceTransformer(
            EMBEDDING_MODEL
        )


    def encode(
        self,
        texts,
        batch_size=EMBEDDING_BATCH_SIZE,
    ):

        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            normalize_embeddings=
                NORMALIZE_EMBEDDINGS,
        )

        return embeddings