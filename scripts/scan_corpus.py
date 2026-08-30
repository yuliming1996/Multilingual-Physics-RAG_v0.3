"""
scan_corpus.py

Scan physics knowledge corpus and generate document metadata.

Responsibilities:
    1. Traverse raw document directory
    2. Calculate SHA256 hash
    3. Generate document metadata records
    4. Save corpus manifest
    5. Compare corpus versions for incremental update

Supported formats:
    - PDF
    - HTML
    - Markdown
    - TXT
"""


from pathlib import Path
import hashlib
import json

from app.config import (
    CORPUS_ROOT,
    SUPPORTED_SUFFIXES,
    MANIFEST_PATH,
)

# ============================================================
# Configuration
# ============================================================


# SUPPORTED_SUFFIXES, path are alread set in app/config.py


# ============================================================
# 1. Calculate file SHA256
# ============================================================

def calculate_sha256(
    file_path: Path,
    chunk_size: int = 1024 * 1024,
) -> str:
    """
    Calculate SHA256 hash of a file.

    SHA256 is used to identify document versions.

    Args:
        file_path:
            File path.

        chunk_size:
            Reading block size.

    Returns:
        SHA256 hexadecimal string.
    """

    sha256 = hashlib.sha256()

    with file_path.open(
        mode="rb"
    ) as file:

        while True:

            chunk = file.read(
                chunk_size
            )

            if not chunk:
                break

            sha256.update(
                chunk
            )

    return sha256.hexdigest()


# ============================================================
# 2. Infer document language
# ============================================================

def infer_language(
    file_path: Path,
) -> str:
    """
    Infer document language.

    Simple heuristic:
        Chinese filename/path -> zh
        otherwise -> en

    This can be replaced by
    content-based language detection later.
    """

    text = str(
        file_path
    )

    for char in text:

        if "\u4e00" <= char <= "\u9fff":
            return "zh"

    return "en"


# ============================================================
# 3. Infer knowledge level
# ============================================================

def infer_level(
    relative_path: Path,
) -> str:
    """
    Infer knowledge level from path.
    """

    text = str(
        relative_path
    ).lower()


    if "high" in text or "高中" in text:
        return "high_school"


    if "undergraduate" in text or "大学" in text:
        return "undergraduate"


    if "lecture" in text or "note" in text:
        return "lecture"


    return "unknown"


# ============================================================
# 4. Build document record
# ============================================================

def build_record(
    file_path: Path,
    root: Path,
) -> dict:
    """
    Build metadata record for one document.
    """

    relative_path = (
        file_path.relative_to(root)
    )


    file_hash = calculate_sha256(
        file_path
    )


    return {

        # ----------------------------
        # Document identity
        # ----------------------------

        # Stable document identity
        "doc_id":
            relative_path.as_posix(),


        # Current document version
        "version_id":
            file_hash[:16],


        # ----------------------------
        # File information
        # ----------------------------

        "relative_path":
            relative_path.as_posix(),

        "file_name":
            file_path.name,

        "suffix":
            file_path.suffix.lower(),

        "file_size_bytes":
            file_path.stat().st_size,


        # ----------------------------
        # Content fingerprint
        # ----------------------------

        "sha256":
            file_hash,


        # ----------------------------
        # Metadata
        # ----------------------------

        "language":
            infer_language(
                file_path
            ),

        "level":
            infer_level(
                relative_path
            ),


        # ----------------------------
        # Retrieval control
        # ----------------------------

        "dataset_role":
            "knowledge",


        "include_in_retrieval":
            True,


        # ----------------------------
        # Processing state
        # ----------------------------

        "ingest_status":
            "pending",
    }


# ============================================================
# 5. Scan corpus
# ============================================================

def scan_corpus(
    corpus_root: Path,
) -> list[dict]:
    """
    Scan all supported documents.
    """

    records = []


    for file_path in corpus_root.rglob("*"):

        if not file_path.is_file():
            continue


        if (
            file_path.suffix.lower()
            not in SUPPORTED_SUFFIXES
        ):
            continue


        record = build_record(
            file_path,
            corpus_root,
        )


        records.append(
            record
        )


    return records


# ============================================================
# 6. Load existing manifest
# ============================================================

def load_manifest(
    manifest_path: Path,
) -> dict[str, dict]:
    """
    Load existing manifest.

    Returns:

        {
            doc_id: record
        }
    """

    if not manifest_path.exists():
        return {}


    records = {}


    with manifest_path.open(
        mode="r",
        encoding="utf-8",
    ) as file:


        for line in file:

            record = json.loads(
                line
            )

            records[
                record["doc_id"]
            ] = record


    return records


# ============================================================
# 7. Compare manifests
# ============================================================

def compare_manifests(
    old_manifest: dict[str, dict],
    new_records: list[dict],
) -> dict:
    """
    Compare old and new corpus states.

    Returns:
        added
        modified
        unchanged
        deleted
    """

    new_manifest = {

        record["doc_id"]:
            record

        for record in new_records
    }


    added = []

    modified = []

    unchanged = []


    for doc_id, new_record in new_manifest.items():


        if doc_id not in old_manifest:

            added.append(
                new_record
            )


        else:

            old_record = (
                old_manifest[doc_id]
            )


            if (
                old_record["sha256"]
                != new_record["sha256"]
            ):

                modified.append(
                    {
                        "old": old_record,
                        "new": new_record,
                    }
                )


            else:

                unchanged.append(
                    new_record
                )


    deleted = [

        record

        for doc_id, record
        in old_manifest.items()

        if doc_id not in new_manifest
    ]


    return {

        "added":
            added,

        "modified":
            modified,

        "unchanged":
            unchanged,

        "deleted":
            deleted,
    }


# ============================================================
# 8. Save manifest
# ============================================================

def save_manifest(
    records: list[dict],
    manifest_path: Path,
) -> None:
    """
    Save manifest as JSONL.

    The manifest represents the current
    corpus state, therefore overwrite is used.
    """

    manifest_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )


    with manifest_path.open(
        mode="w",
        encoding="utf-8",
    ) as file:


        for record in records:

            json_line = json.dumps(
                record,
                ensure_ascii=False,
            )


            file.write(
                json_line + "\n"
            )


# ============================================================
# Main
# ============================================================

def main():

    print(
        "Scanning corpus..."
    )


    records = scan_corpus(
        CORPUS_ROOT
    )


    print(
        f"Found {len(records)} documents."
    )


    save_manifest(
        records,
        MANIFEST_PATH,
    )


    print(
        "Manifest saved:"
    )

    print(
        MANIFEST_PATH
    )


if __name__ == "__main__":

    main()