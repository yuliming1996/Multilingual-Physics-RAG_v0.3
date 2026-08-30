"""
inspect_manifest.py

Analyze corpus manifest statistics.

Functions:
    - Count document formats
    - Analyze languages
    - Analyze knowledge levels
    - Check dataset roles
    - Identify large documents

This script does not modify the manifest.
"""


import json
from pathlib import Path
from collections import Counter
from app.config import (
    MANIFEST_PATH,
)





def load_manifest(
    path: Path,
) -> list[dict]:

    records = []

    with path.open(
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



def main():

    records = load_manifest(
        MANIFEST_PATH
    )


    print(
        "Total files:",
        len(records)
    )


    print("\nFormats:")

    suffix_counter = Counter(
        r["suffix"]
        for r in records
    )

    for k,v in suffix_counter.items():
        print(
            k,
            ":",
            v
        )


    print("\nLanguages:")

    language_counter = Counter(
        r["language"]
        for r in records
    )

    for k,v in language_counter.items():
        print(
            k,
            ":",
            v
        )


    print("\nLevels:")

    level_counter = Counter(
        r["level"]
        for r in records
    )

    for k,v in level_counter.items():
        print(
            k,
            ":",
            v
        )


    print("\nDataset roles:")

    role_counter = Counter(
        r["dataset_role"]
        for r in records
    )

    for k,v in role_counter.items():
        print(
            k,
            ":",
            v
        )


    print("\nLargest files:")

    largest = sorted(
        records,
        key=lambda x:x["file_size_bytes"],
        reverse=True,
    )


    for item in largest[:5]:

        print(
            item["file_name"],
            round(
                item["file_size_bytes"]/1024/1024,
                2
            ),
            "MB"
        )


if __name__ == "__main__":
    main()