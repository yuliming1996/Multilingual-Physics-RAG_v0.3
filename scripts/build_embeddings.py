import json
from pathlib import Path

import numpy as np

from app.embedding import EmbeddingModel
#import time
from app.config import (
    EMBEDDING_BATCH_SIZE,
    EMBEDDING_MODEL,
    NORMALIZE_EMBEDDINGS,
    CHUNKS_PATH,
    EMBEDDINGS_PATH,
    EMBEDDING_METADATA_PATH,
)




def read_chunks(
    chunks_path: Path,
):
    """
    Read chunks.jsonl line by line.
    """

    with chunks_path.open(
        mode="r",
        encoding="utf-8",
    ) as file:

        for line in file:

            if not line.strip():
                continue

            yield json.loads(line)


class IncrementalReuseUnavailable(Exception):
    """Raised when existing embedding artifacts cannot be reused safely."""


def load_reusable_embeddings(
    embeddings_path: Path,
    metadata_path: Path,
):
    """Load and validate the embedding artifacts used for reuse."""

    if not embeddings_path.exists():
        raise IncrementalReuseUnavailable(
            f"Existing embeddings were not found: {embeddings_path}"
        )

    if not metadata_path.exists():
        raise IncrementalReuseUnavailable(
            f"Existing embedding metadata was not found: {metadata_path}"
        )

    try:
        old_embeddings = np.load(
            embeddings_path
        )

        with metadata_path.open(
            mode="r",
            encoding="utf-8",
        ) as file:
            old_metadata = json.load(file)

    except (OSError, ValueError, json.JSONDecodeError) as error:
        raise IncrementalReuseUnavailable(
            "Existing embedding artifacts could not be read."
        ) from error

    if not isinstance(old_metadata, dict):
        raise IncrementalReuseUnavailable(
            "Existing embedding metadata must be a JSON object."
        )

    old_chunk_ids = old_metadata.get(
        "chunk_ids"
    )

    if old_embeddings.ndim != 2:
        raise IncrementalReuseUnavailable(
            "Existing embeddings must be a 2D array."
        )

    if not isinstance(old_chunk_ids, list):
        raise IncrementalReuseUnavailable(
            "Existing embedding metadata has no chunk_ids list."
        )

    if len(old_chunk_ids) != old_embeddings.shape[0]:
        raise IncrementalReuseUnavailable(
            "Existing embedding rows do not match metadata chunk_ids."
        )

    if len(old_chunk_ids) != len(set(old_chunk_ids)):
        raise IncrementalReuseUnavailable(
            "Existing embedding metadata contains duplicate chunk_ids."
        )

    if old_metadata.get("model") != EMBEDDING_MODEL:
        raise IncrementalReuseUnavailable(
            "The embedding model has changed."
        )

    if (
        old_metadata.get("normalize_embeddings")
        != NORMALIZE_EMBEDDINGS
    ):
        raise IncrementalReuseUnavailable(
            "The embedding normalization setting has changed."
        )

    if (
        old_metadata.get("dimension")
        != old_embeddings.shape[1]
    ):
        raise IncrementalReuseUnavailable(
            "Existing embedding dimension does not match its metadata."
        )

    return old_embeddings, old_chunk_ids


def save_embedding_artifacts(
    embeddings,
    chunk_ids,
    embeddings_path: Path = EMBEDDINGS_PATH,
    metadata_path: Path = EMBEDDING_METADATA_PATH,
    batch_size: int = EMBEDDING_BATCH_SIZE,
):
    """Save an embedding matrix and its row-to-chunk mapping."""

    embeddings_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    np.save(
        embeddings_path,
        embeddings,
    )

    metadata = {
        "model": EMBEDDING_MODEL,
        "dimension": int(
            embeddings.shape[1]
        ),
        "num_vectors": int(
            embeddings.shape[0]
        ),
        "normalize_embeddings":
            NORMALIZE_EMBEDDINGS,
        "batch_size":
            batch_size,
        "chunk_ids":
            chunk_ids,
    }

    with metadata_path.open(
        mode="w",
        encoding="utf-8",
    ) as file:
        json.dump(
            metadata,
            file,
            indent=4,
            ensure_ascii=False,
        )



def build_embeddings(
    chunks_path,
    model,
    batch_size,
):

    all_embeddings = []
    all_chunk_ids = []
    batch_texts = []
    batch_chunk_ids = []

#    start = time.time()


    for record in read_chunks(chunks_path):

        batch_texts.append(
            record["page_content"]
        )

        batch_chunk_ids.append(
            record["chunk_id"]
        )

        if len(batch_texts) >= batch_size:

            embeddings = model.encode(
                batch_texts,
                batch_size=batch_size,
            )

            all_embeddings.append(
                embeddings
            )

            all_chunk_ids.extend(
                batch_chunk_ids
            )
            print('embedding:',batch_chunk_ids[0])
            batch_texts = []
            batch_chunk_ids = []
#            print(
#                "time:",
#                time.time()-start
#            )


#            start = time.time()
        

    # remaining

    if batch_texts:

        embeddings = model.encode(
            batch_texts,
            batch_size=batch_size,
        )

        all_embeddings.append(
            embeddings
        )
        all_chunk_ids.extend(
            batch_chunk_ids
        )

    if not all_embeddings:
        return np.empty((0, 0)), all_chunk_ids

    return (
        np.vstack(all_embeddings),
        all_chunk_ids,
    )


def build_embeddings_incrementally(
    chunks_path: Path = CHUNKS_PATH,
    embeddings_path: Path = EMBEDDINGS_PATH,
    metadata_path: Path = EMBEDDING_METADATA_PATH,
    batch_size: int = EMBEDDING_BATCH_SIZE,
    model=None,
) -> tuple[int, int]:
    """
    Reuse embeddings by chunk_id and encode only new chunk records.

    The final matrix is assembled in the exact row order of the
    current chunks.jsonl file, so it remains aligned with FAISS.

    Returns:
        (reused_count, generated_count)
    """

    try:
        old_embeddings, old_chunk_ids = (
            load_reusable_embeddings(
                embeddings_path,
                metadata_path,
            )
        )

    except IncrementalReuseUnavailable as error:
        print(
            "Incremental embedding reuse is unavailable:"
        )
        print(error)
        print(
            "Falling back to a complete embedding rebuild."
        )

        if model is None:
            model = EmbeddingModel()

        embeddings, chunk_ids = build_embeddings(
            chunks_path,
            model,
            batch_size,
        )

        save_embedding_artifacts(
            embeddings,
            chunk_ids,
            embeddings_path,
            metadata_path,
            batch_size,
        )

        return 0, len(chunk_ids)

    old_row_by_chunk_id = {
        chunk_id: row
        for row, chunk_id
        in enumerate(old_chunk_ids)
    }

    current_chunk_ids = []
    source_rows = []
    new_positions = []
    new_texts = []
    seen_chunk_ids = set()

    for position, record in enumerate(
        read_chunks(chunks_path)
    ):
        chunk_id = record["chunk_id"]

        if chunk_id in seen_chunk_ids:
            raise ValueError(
                f"Duplicate current chunk_id: {chunk_id}"
            )

        seen_chunk_ids.add(
            chunk_id
        )

        current_chunk_ids.append(
            chunk_id
        )

        old_row = old_row_by_chunk_id.get(
            chunk_id,
            -1,
        )

        source_rows.append(
            old_row
        )

        if old_row < 0:
            new_positions.append(
                position
            )
            new_texts.append(
                record["page_content"]
            )

    if not current_chunk_ids:
        raise ValueError(
            "The current chunks file is empty."
        )

    final_embeddings = np.empty(
        (
            len(current_chunk_ids),
            old_embeddings.shape[1],
        ),
        dtype=old_embeddings.dtype,
    )

    source_rows_array = np.asarray(
        source_rows,
        dtype=np.int64,
    )

    reused_positions = np.flatnonzero(
        source_rows_array >= 0
    )

    if reused_positions.size:
        final_embeddings[reused_positions] = (
            old_embeddings[
                source_rows_array[reused_positions]
            ]
        )

    generated_count = len(
        new_positions
    )

    if generated_count:
        if model is None:
            model = EmbeddingModel()

        for start in range(
            0,
            generated_count,
            batch_size,
        ):
            end = min(
                start + batch_size,
                generated_count,
            )

            batch_embeddings = np.asarray(
                model.encode(
                    new_texts[start:end],
                    batch_size=batch_size,
                )
            )

            if (
                batch_embeddings.ndim != 2
                or batch_embeddings.shape[0]
                != end - start
                or batch_embeddings.shape[1]
                != final_embeddings.shape[1]
            ):
                raise ValueError(
                    "New embedding batch has an unexpected shape."
                )

            batch_positions = np.asarray(
                new_positions[start:end],
                dtype=np.int64,
            )

            final_embeddings[batch_positions] = (
                batch_embeddings
            )

            print(
                "Embedded new chunks:"
                f" {end}/{generated_count}"
            )

    save_embedding_artifacts(
        final_embeddings,
        current_chunk_ids,
        embeddings_path,
        metadata_path,
        batch_size,
    )

    reused_count = int(
        reused_positions.size
    )

    print(
        "Embedding shape:",
        final_embeddings.shape,
    )

    print(
        "Reused embeddings:",
        reused_count,
    )

    print(
        "Generated embeddings:",
        generated_count,
    )

    print(
        "Saved:",
        embeddings_path,
    )

    return reused_count, generated_count



def main():

    model = EmbeddingModel()


    embeddings,chunk_ids = build_embeddings(
        CHUNKS_PATH,
        model,
        EMBEDDING_BATCH_SIZE,
    )


    print(
        "Embedding shape:",
        embeddings.shape
    )


    save_embedding_artifacts(
        embeddings,
        chunk_ids,
    )


    print(
        "Saved:",
        EMBEDDINGS_PATH
    )


if __name__ == "__main__":
    main()
