"""
Run the complete physics RAG pipeline.

Usage:

    python scripts/run_rag.py "干涉和衍射有什么区别？"
    python scripts/run_rag.py "what is the difference between interference and diffraction?"

Run without a query to enter interactive mode:

    python scripts/run_rag.py
"""

import argparse
import sys
from pathlib import Path


# Make the project root importable when this file is run directly.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


from app.config import (
    CHUNKS_PATH,
    FAISS_INDEX_PATH,
    RERANKER_TOP_K,
    RETRIEVAL_TOP_K,
)
from app.generation import (
    build_context,
    generate_answer,
)
from app.query.expansion import expand_query
from app.query.llm_rewriter import rewrite_query
from app.reranking.reranker import Reranker
from app.retrieval.retriever import Retriever


def get_rerank_queries(
    rewritten,
) -> tuple[str, str]:
    """Extract the Chinese and English queries used for reranking."""

    zh_query = None
    en_query = None

    for item in (
        rewritten.rewritten_query,
        rewritten.translated_query,
    ):
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

    return zh_query, en_query


def run_rag(
    original_query: str,
    retriever: Retriever,
    reranker: Reranker,
) -> tuple[str, str, str]:
    """Run query rewriting, retrieval, reranking and generation."""

    rewritten = rewrite_query(
        original_query
    )

    rewritten_query = (
        rewritten
        .rewritten_query
        .content
    )

    translated_query = (
        rewritten
        .translated_query
        .content
    )

    expanded_queries = expand_query(
        rewritten
    )

    candidates = retriever.search(
        expanded_queries,
        top_k=RETRIEVAL_TOP_K,
    )

    zh_query, en_query = get_rerank_queries(
        rewritten
    )

    reranked = reranker.rerank_by_language(
        zh_query,
        en_query,
        candidates,
        top_k=RERANKER_TOP_K,
    )

    context = build_context(
        reranked
    )

    answer = generate_answer(
        original_query=original_query,
        rewritten_query=rewritten_query,
        context=context,
    )

    return rewritten_query, translated_query, answer


def print_result(
    original_query: str,
    rewritten_query: str,
    translated_query: str,
    answer: str,
) -> None:
    """Print one completed RAG response."""

    print("=" * 80)
    print("Original query:")
    print(original_query)

    print("\nRewritten query:")
    print(rewritten_query)

    print("\nTranslated query:")
    print(translated_query)

    print("\n" + "=" * 80)
    print("Final answer:")
    print(answer)


def process_query(
    query: str,
    retriever: Retriever,
    reranker: Reranker,
) -> None:
    """Run and display one non-empty query."""

    rewritten_query, translated_query, answer = run_rag(
        query,
        retriever,
        reranker,
    )

    print_result(
        query,
        rewritten_query,
        translated_query,
        answer,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the physics RAG question-answering pipeline."
    )

    parser.add_argument(
        "query",
        nargs="*",
        help="Physics question. If omitted, interactive mode starts.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    retriever = Retriever(
        FAISS_INDEX_PATH,
        CHUNKS_PATH,
    )

    reranker = Reranker()

    query = " ".join(
        args.query
    ).strip()

    if query:
        process_query(
            query,
            retriever,
            reranker,
        )
        return

    print(
        "Physics RAG interactive mode. "
        "Enter a question, or type quit to exit."
    )

    while True:
        try:
            query = input("\nQuestion: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            return

        if query.lower() in {
            "q",
            "quit",
            "exit",
        }:
            print("Exiting.")
            return

        if not query:
            continue

        process_query(
            query,
            retriever,
            reranker,
        )


if __name__ == "__main__":
    main()
