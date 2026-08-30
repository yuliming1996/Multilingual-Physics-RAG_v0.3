from sentence_transformers import CrossEncoder

from app.config import (
    RERANKER_TOP_K,
    RERANKER_MODEL,
)



class Reranker:


    def __init__(
        self,
        model_name=RERANKER_MODEL,
    ):

        self.model = CrossEncoder(
            model_name
        )



    def rerank(
        self,
        query,
        candidates,
        top_k=RERANKER_TOP_K,
    ):


        if not candidates:

            return []


        pairs = []


        for candidate in candidates:


            text = (
                candidate
                .chunk["page_content"]
            )


            pairs.append(
                [
                    query,
                    text
                ]
            )


        scores = self.model.predict(
            pairs
        )


        ranked = sorted(
            zip(
                candidates,
                scores
            ),
            key=lambda x:x[1],
            reverse=True,
        )


        results = []


        for candidate, score in ranked[:top_k]:


            candidate.rerank_score = (
                float(score)
            )


            results.append(
                candidate
            )


        return results



    def rerank_by_language(
        self,
        zh_query,
        en_query,
        candidates,
        top_k=RERANKER_TOP_K,
    ):


        zh_candidates = []

        en_candidates = []


        for candidate in candidates:


            language = (
                candidate
                .chunk["metadata"]
                .get(
                    "language",
                    "unknown"
                )
            )


            if language == "zh":

                zh_candidates.append(
                    candidate
                )


            else:

                en_candidates.append(
                    candidate
                )



        zh_results = self.rerank(
            zh_query,
            zh_candidates,
            top_k,
        )


        en_results = self.rerank(
            en_query,
            en_candidates,
            top_k,
        )



        merged = (
            zh_results
            +
            en_results
        )


        merged = sorted(
            merged,
            key=lambda x:x.rerank_score,
            reverse=True,
        )


        return merged[:top_k]