from pathlib import Path
from app.loaders import load_document
from app.cleaners import clean_documents
import json

from app.splitter.split_documents import split_documents

from app.config import (
    CORPUS_ROOT,
    MANIFEST_PATH,
    CHUNKS_PATH,
)


# ============================================================
# 1. Enrich metadata
# ============================================================

def enrich_metadata(
    documents,
    record,
):
    """
    Add document-level metadata to each Document object.
    """

    for doc in documents:

        doc.metadata.update(
            {

                # Stable document identity
                "doc_id":
                    record["doc_id"],


                # Document version
                "version_id":
                    record["version_id"],


                # File fingerprint
                "sha256":
                    record["sha256"],


                # Original path
                "relative_path":
                    record["relative_path"],


                # Existing metadata
                "language":
                    record["language"],


                "level":
                    record["level"],


                "dataset_role":
                    record["dataset_role"],


                "include_in_retrieval":
                    record["include_in_retrieval"],

            }
        )


    return documents



# ============================================================
# 2. Load manifest
# ============================================================

def load_manifest(
    manifest_path: Path,
) -> list[dict]:

    records = []


    with manifest_path.open(
        mode="r",
        encoding="utf-8",
    ) as file:


        for line in file:


            if not line.strip():
                continue


            records.append(
                json.loads(line)
            )


    return records

# ============================================================
# 3. build chunks
# ============================================================
def build_chunks_for_record(
    record: dict,
) -> list[dict]:
    """
    Build all chunks for one manifest record.

    The returned records use the same structure and chunk_id
    rule as the full build.
    """

    if not record["include_in_retrieval"]:
        return []

    file_path = (
        CORPUS_ROOT
        / record["relative_path"]
    )

    print(
        "Loading:",
        file_path,
    )

    documents = load_document(
        file_path
    )

    documents = clean_documents(
        documents
    )

    documents = enrich_metadata(
        documents,
        record,
    )

    chunks = split_documents(
        documents
    )

    chunk_records = []

    for index, chunk in enumerate(chunks):

        chunk_id = (
            f"{record['doc_id']}_"
            f"{record['version_id']}_"
            f"{index:06d}"
        )

        chunk_records.append(
            {
                "chunk_id":
                    chunk_id,

                "page_content":
                    chunk.page_content,

                "metadata":
                    chunk.metadata,
            }
        )

    return chunk_records

# ============================================================
# 4. Save chunk
# ============================================================

def save_chunk(
    chunk_record: dict,
    file,
):

    json_line = json.dumps(
        chunk_record,
        ensure_ascii=False,
    )

    file.write(
        json_line + "\n"
    )



# ============================================================
# 5. Main
# ============================================================

def main():


    records = load_manifest(
        MANIFEST_PATH
    )


    total_chunks = 0


    CHUNKS_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )


    with CHUNKS_PATH.open(
        mode="w",
        encoding="utf-8",
    ) as output_file:


        for record in records:

            chunk_records = build_chunks_for_record(
                record
            )

            for chunk_record in chunk_records:

                save_chunk(
                    chunk_record,
                    output_file,
                )

                total_chunks += 1



    print(
        "Saved chunks:",
        total_chunks
    )


    print(
        "Output:",
        CHUNKS_PATH
    )



if __name__ == "__main__":
    main()