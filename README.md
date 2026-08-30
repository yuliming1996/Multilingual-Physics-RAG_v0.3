English | [中文](doc/README_zh.md)

# Multilingual Physics RAG System

This is an end-to-end Retrieval-Augmented Generation (RAG) project for physics questions in Chinese and English. It cleans and chunks a local document collection, creates multilingual embeddings with BGE-M3, and builds a FAISS index. At query time, it rewrites and translates the question, expands the search in both languages, retrieves and reranks relevant chunks, and generates an answer from the retrieved context. Th is pipeline can  be easily adapted to other domains by changing the configuration and prompts.[^prompt-files]

[^prompt-files]: The query-rewriting and translation prompt is defined in [`app/query/llm_rewriter.py`](app/query/llm_rewriter.py), while the answer-generation prompt is in [`app/generation/llm_generator.py`](app/generation/llm_generator.py). [`app/reranking/reranker.py`](app/reranking/reranker.py) uses a CrossEncoder and does not currently contain a prompt.

## Installation

### 1. Clone the repository


```bash
git clone https://github.com/yuliming1996/Multilingual-Physics-RAG_v0.3.git
cd Multilingual-Physics-RAG_v0.3
```

### 2. Create a virtual environment

The project was developed with Python 3.12.

macOS/Linux:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The main dependencies include LangChain document utilities, Sentence Transformers, FAISS CPU, PyPDF, Beautiful Soup, NumPy, Pydantic, and the OpenAI-compatible Python client.

### 4. Add the knowledge corpus

Place source documents under the directory configured by `CORPUS_ROOT`. The default location is:

```text
Physics_Knowledge_Base_full/
```

The built-in loaders support text-based PDFs, HTML/HTM, Markdown, and TXT files. Other formats are skipped during scanning. To support another text format, add its suffix to `SUPPORTED_SUFFIXES` in `app/config.py` and provide the corresponding loader logic under `app/loaders/`.

### 5. Configure the LLM API key

The default query-rewriting and answer-generation configuration reads the `DEEPSEEK_API_KEY` environment variable. The project does not automatically load a `.env` file.

macOS/Linux:

```bash
export DEEPSEEK_API_KEY="your-api-key"
```

Windows PowerShell:

```powershell
$env:DEEPSEEK_API_KEY="your-api-key"
```

The embedding and reranker models are downloaded from Hugging Face on first use. `HF_TOKEN` is optional, but can help avoid anonymous-download rate limits.

### 6. Build the index

```bash
python scripts/build_index.py
```

This command scans the corpus, writes a SHA-256 manifest, creates chunks and embeddings, and builds the FAISS index. The output is saved under `data/processed/`.

### 7. Run the RAG application

Ask one question directly:

```bash
python scripts/run_rag.py "What is the difference between interference and diffraction?"
```

Or start interactive mode:

```bash
python scripts/run_rag.py
```

Type `q`, `quit`, or `exit` to leave interactive mode.

You can change the answer language to English by setting  `ANSWER_LANGUAGE="English"` in `app/config.py`


#### Use the included test index

The repository does not include the full physics corpus, but `data/*processed` contains a small prebuilt index for trying the RAG pipeline. If `data/processed` does not exist yet, rename the test directory to the default path expected by the application:

```bash
mv 'data/*processed' data/processed
```

If `data/processed` already exists, back it up before switching to the test index:

```bash
mv data/processed data/processed.backup
mv 'data/*processed' data/processed
```

### 8. Update the index

After adding, editing, or deleting documents, you do not need to run a full build again. Use:

```bash
python scripts/update_index.py
```

The update script processes changed documents while reusing chunks and embeddings from documents that have not changed.

## Configuration

Runtime settings are centralized in [`app/config.py`](app/config.py).

| Setting | Default | Purpose |
| --- | --- | --- |
| `CORPUS_ROOT` | `Physics_Knowledge_Base_full/` | Root directory scanned for source documents. |
| `PROCESSED_DIR` | `data/processed/` | Output directory for the manifest, chunks, embeddings, metadata, and FAISS index. |
| `SUPPORTED_SUFFIXES` | PDF, HTML, HTM, MD, TXT | File types included in the corpus scan. |
| `CHUNK_SIZE` | `1000` | Character-based target size used by the recursive text splitter. |
| `CHUNK_OVERLAP` | `200` | Character overlap between adjacent chunks. |
| `EMBEDDING_MODEL` | `BAAI/bge-m3` | Multilingual dense embedding model. |
| `RERANKER_MODEL` | `BAAI/bge-reranker-v2-m3` | Cross-encoder used for second-stage reranking. |
| `NORMALIZE_EMBEDDINGS` | `True` | Whether vectors are normalized before inner-product retrieval. |
| `EMBEDDING_BATCH_SIZE` | `8` | Batch size for embedding inference; lower it if memory pressure is high. |
| `RETRIEVAL_TOP_K` | `30` | Number of candidates retrieved for each expanded query. |
| `RERANKER_TOP_K` | `5` | Number of passages retained after language-aware reranking. |
| `QUERY_REWRITE_MODEL` | `deepseek-v4-flash` | Model used for query rewriting, translation, and keyword generation. |
| `GENERATION_MODEL` | `deepseek-v4-flash` | Model used to generate the final answer. |
| `REWRITE_API_BASE` / `GENERATION_API_BASE` | `https://api.deepseek.com` | OpenAI-compatible API endpoints. |
| `REWRITE_API_KEY` / `GENERATION_API_KEY` | `DEEPSEEK_API_KEY` | Names of the environment variables containing API credentials. |
| `ANSWER_LANGUAGE` | `中文` | Language used for the final answer. |

Run `build_index.py` again after changing `CHUNK_SIZE`, `CHUNK_OVERLAP`, `EMBEDDING_MODEL`, or `NORMALIZE_EMBEDDINGS`. Changes to `RETRIEVAL_TOP_K`, `RERANKER_TOP_K`, or `ANSWER_LANGUAGE` do not require an index rebuild.

## Features

### Multiformat corpus ingestion

- Loads PDF, HTML/HTM, Markdown, and UTF-8 text files.
- Removes common non-content HTML elements and cleans up extra whitespace and line breaks.
- Keeps metadata provided by the loader and adds document identity, version, hash, relative path, language, level, dataset role, and retrieval status to each chunk.

### Versioned and incremental indexing

- Uses each relative path as a stable `doc_id`.
- Uses SHA-256 to detect added, modified, unchanged, and deleted documents.
- Generates versioned chunk IDs from `doc_id`, `version_id`, and chunk position.
- Keeps chunks and vectors from documents that have not changed.
- Embeds only added or modified documents, then rebuilds FAISS so chunk rows, vectors, and index positions stay aligned.

After changing the corpus, run:

```bash
python scripts/update_index.py
```

If the previous embedding metadata is missing, incompatible, or unreadable, the script automatically falls back to a full embedding build.

### Bilingual query processing

- Rewrites the original question into a form that works better for physics retrieval.
- Translates the rewritten query between Chinese and English.
- Produces Chinese and English keyword queries.
- Searches with the rewritten query, translated query, and both keyword sets.

### Dense retrieval and reranking

- Encodes queries and documents with the multilingual BGE-M3 model.
- Uses a normalized inner-product `IndexFlatIP` FAISS index.
- Combines results from multiple query variants and removes duplicate candidates.
- Separates Chinese and English candidates and reranks them with language-matched queries.

### Grounded answer generation

- Adds the top-ranked chunks to the LLM prompt.
- Prompts the generation model to rely on retrieved content and acknowledge when the available context is not enough.
- Supports a configurable output language.
- Prints the original, rewritten, and translated queries together with the final answer.

## Pipeline

```text
Source documents
      |
      v
Corpus scan
      |
      v
Loading, cleaning, and chunking
      |
      v
BGE-M3 embeddings
      |
      v
FAISS IndexFlatIP
      |
      v
Question rewrite, translation, and expansion
      |
      v
Retrieval, fusion, and deduplication
      |
      v
Language-aware cross-encoder reranking
      |
      v
Context construction and grounded generation
```

## Project Structure

```text
RAG_physics_master/
├── app/
│   ├── cleaners/       # Text cleaning
│   ├── embedding/      # Convert chunks into embedding vectors
│   ├── generation/     # Context construction and answer generation
│   ├── loaders/        # Document loading
│   ├── query/          # Query rewriting and expansion
│   ├── reranking/      # Rerank retrieved chunks
│   ├── retrieval/      # Chunk retrieval
│   ├── splitter/       # Text chunking
│   ├── vectorstore/    # FAISS IndexFlatIP wrapper
│   └── config.py       # Shared configuration
├── scripts/
│   ├── build_index.py  # Full index build
│   ├── update_index.py # Incremental corpus and embedding update
│   ├── run_rag.py      # One-shot and interactive RAG entry point
│   └── ...
├── data/processed/     # Output directory for the manifest, chunks, and index files
├── doc/README_zh.md    # Chinese README
└── requirements.txt
```
