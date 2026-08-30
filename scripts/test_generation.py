from app.query.llm_rewriter import rewrite_query
from app.query.expansion import expand_query

from app.retrieval.retriever import Retriever
from app.reranking.reranker import Reranker

from app.generation import (
    build_context,
    generate_answer,
)

from app.config import (
    FAISS_INDEX_PATH,
    CHUNKS_PATH,
    RETRIEVAL_TOP_K,
    RERANKER_TOP_K,
)


def main():


    # ==========================
    # 1. User query
    # ==========================

    original_query = (
        "干涉和衍射有什么区别？"
    )


    # ==========================
    # 2. LLM query rewriting
    # ==========================

    rewritten = rewrite_query(
        original_query
    )


    rewritten_query = (
        rewritten
        .rewritten_query
        .content
    )


    # ==========================
    # 3. Query expansion
    # ==========================

    expanded_queries = expand_query(
        rewritten
    )


    # ==========================
    # 4. Retrieval
    # ==========================

    retriever = Retriever(
        FAISS_INDEX_PATH,
        CHUNKS_PATH,
    )


    candidates = retriever.search(
        expanded_queries,
        top_k=RETRIEVAL_TOP_K,
    )


    # ==========================
    # 5. Prepare bilingual
    #    rerank queries
    # ==========================

    zh_query = None

    en_query = None


    for item in [
        rewritten.rewritten_query,
        rewritten.translated_query,
    ]:


        if item.type == "zh":

            zh_query = item.content


        elif item.type == "en":

            en_query = item.content


    if zh_query is None:

        raise ValueError(
            "Missing Chinese rerank query"
        )


    if en_query is None:

        raise ValueError(
            "Missing English rerank query"
        )


    # ==========================
    # 6. Reranking
    # ==========================

    reranker = Reranker()


    reranked = reranker.rerank_by_language(
        zh_query,
        en_query,
        candidates,
        top_k=RERANKER_TOP_K,
    )


    # ==========================
    # 7. Context construction
    # ==========================

    context = build_context(
        reranked
    )


    # ==========================
    # 8. Answer generation
    # ==========================

    answer = generate_answer(
        original_query=
            original_query,

        rewritten_query=
            rewritten_query,

        context=
            context,
    )


    # ==========================
    # 9. Output
    # ==========================

    print("=" * 80)

    print(
        "Original query:"
    )

    print(
        original_query
    )


    print("\nRewritten query:")

    print(
        rewritten_query
    )


    print("\n")

    print("=" * 80)

    print(
        "Final answer:"
    )

    print(
        answer
    )


if __name__ == "__main__":

    main()