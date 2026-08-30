from pathlib import Path


# =========================
# Project paths
# =========================

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)


# =========================
# Corpus
# =========================

# Original document folder

CORPUS_ROOT = (
    PROJECT_ROOT
    / "Physics_Knowledge_Base_full"
)


# =========================
# Processed data
# =========================

PROCESSED_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
)


MANIFEST_PATH = (
    PROCESSED_DIR
    / "corpus_manifest.jsonl"
)


CHUNKS_PATH = (
    PROCESSED_DIR
    / "chunks.jsonl"
)


EMBEDDINGS_PATH = (
    PROCESSED_DIR
    / "embeddings.npy"
)


EMBEDDING_METADATA_PATH = (
    PROCESSED_DIR
    / "embedding_metadata.json"
)


FAISS_INDEX_PATH = (
    PROCESSED_DIR
    / "faiss.index"
)

# =========================
# SUPPORTED_SUFFIXES
# =========================
SUPPORTED_SUFFIXES = {
    ".pdf",
    ".html",
    ".htm",
    ".md",
    ".txt",
}




# =========================
# Chunk configuration
# =========================

CHUNK_SIZE = 1000

CHUNK_OVERLAP = 200



# =========================
# Embedding/reranker configuration
# =========================

EMBEDDING_MODEL = (
    "BAAI/bge-m3"
)
RERANKER_MODEL = (
    "BAAI/bge-reranker-v2-m3"
)


NORMALIZE_EMBEDDINGS = True


EMBEDDING_BATCH_SIZE = 8



# =========================
# Retrieval configuration
# =========================

#RETRIEVAL_TOP_K = 10
RETRIEVAL_TOP_K = 30
#RETRIEVAL_TOP_K = 50


# =========================
# reranker configuration
# =========================

RERANKER_TOP_K = 5
#RERANKER_TOP_K = 30
#RERANKER_TOP_K = 50



# =========================
# LLM configuration
# =========================
REWRITE_API_KEY = "DEEPSEEK_API_KEY"
GENERATION_API_KEY = "DEEPSEEK_API_KEY"

QUERY_REWRITE_MODEL = "deepseek-v4-flash"

REWRITE_API_BASE = (
    "https://api.deepseek.com"
)

GENERATION_MODEL = "deepseek-v4-flash"
GENERATION_API_BASE = (
    "https://api.deepseek.com"
)

ANSWER_LANGUAGE="中文"
#ANSWER_LANGUAGE="English"



