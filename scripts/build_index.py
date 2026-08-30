"""
build_index.py

End-to-end knowledge base construction pipeline.

Pipeline:

1. Build corpus manifest
2. Split documents into chunks
3. Generate embeddings
4. Build FAISS vector index

Usage:
    python scripts/build_index.py
"""

from pathlib import Path
import subprocess
import sys
import os



PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

SCRIPTS_DIR = PROJECT_ROOT / "scripts"


PIPELINE_STEPS = [
    "scan_corpus.py",
    "build_chunks.py",
    "build_embeddings.py",
    "build_faiss_index.py",
]


def run_step(script_name: str):

    script_path = SCRIPTS_DIR / script_name

    print(f"\nRunning {script_path}")

    env = os.environ.copy()

    python_path = env.get("PYTHONPATH", "")

    env["PYTHONPATH"] = (
        str(PROJECT_ROOT)
        if not python_path
        else f"{PROJECT_ROOT}:{python_path}"
    )

    subprocess.run(
        [
            sys.executable,
            str(script_path),
        ],
        check=True,
        env=env,
    )

def main():

    print("=" * 60)
    print("Physics RAG Knowledge Base Construction")
    print("=" * 60)

    for step in PIPELINE_STEPS:
        run_step(step)

    print("\n" + "=" * 60)
    print("Knowledge base construction completed successfully.")
    print("=" * 60)


if __name__ == "__main__":
    main()