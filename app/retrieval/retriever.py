import json
import faiss

from sentence_transformers import SentenceTransformer

from app.retrieval.schema import RetrievalCandidate

from app.config import (
    EMBEDDING_MODEL,
    NORMALIZE_EMBEDDINGS,
    RETRIEVAL_TOP_K,
)


class Retriever:


    def __init__(
        self,
        FAISS_INDEX_PATH,
        CHUNKS_PATH,
        model_name=EMBEDDING_MODEL,
    ):


        self.index = faiss.read_index(
            str(FAISS_INDEX_PATH)
        )


        self.model = SentenceTransformer(
            model_name
        )


        self.chunks = []


        with open(
            CHUNKS_PATH,
            encoding="utf-8",
        ) as file:


            for line in file:

                self.chunks.append(
                    json.loads(line)
                )


    def search(
        self,
        queries,
        top_k=RETRIEVAL_TOP_K,
    ):


        candidates = []


        for query_type, query_text in queries:


            embedding = self.model.encode(
                [query_text],
                normalize_embeddings=NORMALIZE_EMBEDDINGS,
            )


            scores, indices = self.index.search(
                embedding,
                top_k,
            )


            for score, idx in zip(
                scores[0],
                indices[0],
            ):


                if idx < 0:

                    continue


                candidate = RetrievalCandidate(

                    chunk=
                        self.chunks[int(idx)],

                    score=
                        float(score),

                    query_type=
                        query_type,

                    query_text=
                        query_text,

                    index=
                        int(idx),
                )


                candidates.append(
                    candidate
                )


        return self.merge_results(
            candidates
        )


    def merge_results(
        self,
        candidates,
    ):


        merged = {}


        for candidate in candidates:


            idx = candidate.index


            if idx not in merged:

                merged[idx] = candidate


            elif (
                candidate.score
                >
                merged[idx].score
            ):

                merged[idx] = candidate


        return sorted(
            merged.values(),
            key=lambda x: x.score,
            reverse=True,
        )