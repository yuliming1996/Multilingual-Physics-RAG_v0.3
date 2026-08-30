"""
update_index.py

Incrementally update the physics RAG knowledge base.

Strategy:

1. Scan the current corpus.
2. Compare it with the existing manifest.
3. Keep chunks from unchanged documents.
4. Remove chunks from modified or deleted documents.
5. Generate chunks only for added or modified documents.
6. Reuse embeddings for unchanged chunks and encode only new chunks.
7. Rebuild the FAISS index.
8. Save the new manifest only after the complete update succeeds.

Usage:

    python scripts/update_index.py
"""

import json
import sys
import gc
from pathlib import Path


# ============================================================
# 1. Make project root importable
# ============================================================
PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:

    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )

from app.config import (
    CORPUS_ROOT,
    MANIFEST_PATH,
    CHUNKS_PATH,
)


from scan_corpus import (
    scan_corpus,
    load_manifest,
    compare_manifests,
    save_manifest,
)

from build_chunks import (
    build_chunks_for_record,
)

from build_embeddings import (
    build_embeddings_incrementally,
)

from build_faiss_index import (
    main as build_faiss_index_main,
)


# ============================================================
# 3. Load existing chunks
# ============================================================

def load_chunks(
    chunks_path: Path,
) -> list[dict]:
    """
    Load existing chunks.jsonl.

    If the file does not exist, return an empty list.
    """

    if not chunks_path.exists():
        return []

    chunks = []

    with chunks_path.open(
        mode="r",
        encoding="utf-8",
    ) as file:

        for line in file:

            if not line.strip():
                continue

            chunks.append(
                json.loads(line)
            )

    return chunks


# ============================================================
# 4. Build chunks for changed documents
# ============================================================

def build_chunks_for_records(
    records: list[dict],
) -> list[dict]:

    new_chunks = []

    for record in records:

        new_chunks.extend(
            build_chunks_for_record(
                record
            )
        )

    return new_chunks


# ============================================================
# 5. Save complete chunk collection
# ============================================================

def save_chunks(
    chunks: list[dict],
    chunks_path: Path,
) -> None:
    """
    Save the complete current chunk collection.

    Existing chunk records are written unchanged, so chunks from
    unchanged documents keep their original chunk_id values.
    """

    chunks_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with chunks_path.open(
        mode="w",
        encoding="utf-8",
    ) as file:

        for chunk in chunks:

            file.write(
                json.dumps(
                    chunk,
                    ensure_ascii=False,
                )
                + "\n"
            )


# ============================================================
# 6. Main update pipeline
# ============================================================

def main():

    print(
        "=" * 60
    )

    print(
        "Physics RAG Incremental Index Update"
    )

    print(
        "=" * 60
    )


    # --------------------------------------------------------
    # Step 1: Check initial build files
    # --------------------------------------------------------

    if not MANIFEST_PATH.exists():

        raise FileNotFoundError(
            "Existing corpus manifest was not found. "
            "Run scripts/build_index.py first."
        )


    if not CHUNKS_PATH.exists():

        raise FileNotFoundError(
            "Existing chunks file was not found. "
            "Run scripts/build_index.py first."
        )


    # --------------------------------------------------------
    # Step 2: Load previous corpus state
    # --------------------------------------------------------

    print(
        "\n[1/7] Loading existing manifest..."
    )

    old_manifest = load_manifest(
        MANIFEST_PATH
    )


    # --------------------------------------------------------
    # Step 3: Scan current corpus
    # --------------------------------------------------------

    print(
        "\n[2/7] Scanning current corpus..."
    )

    new_records = scan_corpus(
        CORPUS_ROOT
    )


    # --------------------------------------------------------
    # Step 4: Compare corpus versions
    # --------------------------------------------------------

    print(
        "\n[3/7] Comparing corpus versions..."
    )

    changes = compare_manifests(
        old_manifest,
        new_records,
    )


    added = changes["added"]

    modified = changes["modified"]

    deleted = changes["deleted"]

    unchanged = changes["unchanged"]


    print(
        f"Added:     {len(added)}"
    )

    print(
        f"Modified:  {len(modified)}"
    )

    print(
        f"Deleted:   {len(deleted)}"
    )

    print(
        f"Unchanged: {len(unchanged)}"
    )


    # --------------------------------------------------------
    # No changes -> stop
    # --------------------------------------------------------

    if (
        not added
        and not modified
        and not deleted
    ):

        print(
            "\nNo corpus changes detected."
        )

        print(
            "Index update is not required."
        )

        return


    # --------------------------------------------------------
    # Step 5: Determine old document IDs to remove
    # --------------------------------------------------------

    print(
        "\n[4/7] Updating chunks..."
    )


    old_doc_ids_to_remove = {
        record["doc_id"]
        for record in deleted
    }

    # compare_manifests() returns modified entries as
    # {"old": old_record, "new": new_record}.
    old_doc_ids_to_remove.update(
        change["old"]["doc_id"]
        for change in modified
    )


    # --------------------------------------------------------
    # Step 6: Keep chunks from unchanged documents
    # --------------------------------------------------------

    existing_chunks = load_chunks(
        CHUNKS_PATH
    )


    kept_chunks = []


    for chunk in existing_chunks:

        chunk_doc_id = (
            chunk
            .get("metadata", {})
            .get("doc_id")
        )


        if (
            chunk_doc_id
            not in old_doc_ids_to_remove
        ):

            kept_chunks.append(
                chunk
            )


    removed_chunk_count = (
        len(existing_chunks)
        - len(kept_chunks)
    )


    print(
        "Removed old chunks:",
        removed_chunk_count,
    )


    # --------------------------------------------------------
    # Step 7: Generate chunks for added and modified documents
    # --------------------------------------------------------

    modified_new_records = [

        change["new"]

        for change in modified

    ]


    changed_records = (
        added
        + modified_new_records
    )


    generated_chunks = (
        build_chunks_for_records(
            changed_records
        )
    )


    print(
        "Generated new chunks:",
        len(generated_chunks),
    )


    # --------------------------------------------------------
    # Merge current chunks
    # --------------------------------------------------------

    final_chunks = (
        kept_chunks
        + generated_chunks
    )


    save_chunks(
        final_chunks,
        CHUNKS_PATH,
    )


    print(
        "Current chunks:",
        len(final_chunks),
    )


    # --------------------------------------------------------
    # Step 8: Incrementally update embeddings
    # --------------------------------------------------------

    print(
        "\n[5/7] Updating embeddings..."
    )

    # The complete chunk records are no longer needed in memory.
    # The incremental embedding builder reads the saved JSONL file.
    del existing_chunks
    del kept_chunks
    del generated_chunks
    del final_chunks

    gc.collect()

    (
        reused_embedding_count,
        generated_embedding_count,
    ) = build_embeddings_incrementally()

    print(
        "Reused embedding vectors:",
        reused_embedding_count,
    )

    print(
        "Generated embedding vectors:",
        generated_embedding_count,
    )

    gc.collect()


    # --------------------------------------------------------
    # Step 9: Rebuild FAISS
    # --------------------------------------------------------

    print(
        "\n[6/7] Rebuilding FAISS index..."
    )

    build_faiss_index_main()


    # --------------------------------------------------------
    # Step 10: Save new manifest
    # --------------------------------------------------------

    print(
        "\n[7/7] Saving updated manifest..."
    )

    save_manifest(
        records=new_records,
        manifest_path=MANIFEST_PATH,
    )


    print(
        "\n"
        + "=" * 60
    )

    print(
        "Knowledge base update completed successfully."
    )

    print(
        "=" * 60
    )


if __name__ == "__main__":

    main()
