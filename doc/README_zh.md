[English](../README.md) | [中文]

# 中英双语物理 RAG 系统

这是一个面向中英文物理问答的端到端检索增强生成（Retrieval-Augmented Generation，RAG）项目。系统会扫描本地物理资料集，对文档进行清洗和切块，使用 BGE-M3 生成多语言向量并构建 FAISS 索引；收到问题后，再依次完成中英文问题重写、翻译、查询扩展、检索和重排序，最后根据检索结果生成回答。调整配置文件和提示词后[^prompt-files]，也可将它用于其他领域的知识库。

[^prompt-files]: 问题重写与翻译的提示词位于 [`app/query/llm_rewriter.py`](../app/query/llm_rewriter.py)，答案生成的提示词位于 [`app/generation/llm_generator.py`](../app/generation/llm_generator.py)。

## 安装

### 1. 克隆仓库


```bash
git clone https://github.com/yuliming1996/Multilingual-Physics-RAG_v0.3.git
cd RAG_physics_master
```

### 2. 创建虚拟环境

本项目使用 Python 3.12 开发。

macOS/Linux：

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell：

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. 安装依赖

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

主要依赖包括 LangChain 文档处理组件、Sentence Transformers、FAISS CPU、PyPDF、Beautiful Soup、NumPy、Pydantic 和兼容 OpenAI 接口的 Python 客户端。

### 4. 添加知识资料集

将原始文档放入 `CORPUS_ROOT` 配置指向的目录。默认位置为：

```text
Physics_Knowledge_Base_full/
```

系统支持非扫描型 PDF、HTML、HTM、Markdown 和 TXT 文件，其他格式在扫描时会被忽略。如需支持新的纯文本扩展名，需要修改 `app/config.py` 中的 `SUPPORTED_SUFFIXES`，并在 `app/loaders/` 中加入对应的加载逻辑。


### 5. 配置大语言模型 API Key

默认的问题重写与答案生成配置从 `DEEPSEEK_API_KEY` 环境变量读取密钥。项目目前不会自动加载 `.env` 文件。

macOS/Linux：

```bash
export DEEPSEEK_API_KEY="your-api-key"
```

Windows PowerShell：

```powershell
$env:DEEPSEEK_API_KEY="your-api-key"
```

首次运行时，embedding 和 reranker 模型会从 Hugging Face 下载。`HF_TOKEN` 不是必需项，但配置后可以减少匿名下载的限速问题。

### 6. 构建索引

```bash
python scripts/build_index.py
```

该命令会扫描资料集、生成 SHA-256 manifest、创建 chunks、计算 embeddings，并构建 FAISS 索引。输出文件保存在 `data/processed/` 中。


### 7. 运行 RAG

直接提交一个问题：

```bash
python scripts/run_rag.py "干涉和衍射有什么区别？"
```

也可以进入连续提问模式：

```bash
python scripts/run_rag.py
```

在交互模式中输入 `q`、`quit` 或 `exit` 即可退出。

#### 使用仓库内的测试索引

仓库不包含完整的物理资料集，但 `data/*processed` 中提供了一份用于体验 RAG 流程的测试索引。如果本地还没有 `data/processed`，可以直接将测试目录重命名为程序默认读取的路径：

```bash
mv 'data/*processed' data/processed
```

如果本地已经有 `data/processed`，建议先将原目录备份，再切换到测试索引：

```bash
mv data/processed data/processed.backup
mv 'data/*processed' data/processed
```

### 8. 更新索引

新增、修改或删除文档后，不需要再次运行 `build_index.py` 进行全量构建，直接运行：

```bash
python scripts/update_index.py
```

该命令会更新发生变化的文档，并复用未变化文档的 chunks 和 embeddings。

## 配置

运行配置集中在 [`app/config.py`](../app/config.py) 中。

| 配置项 | 默认值 | 作用 |
| --- | --- | --- |
| `CORPUS_ROOT` | `Physics_Knowledge_Base_full/` | 扫描原始文档的根目录。 |
| `PROCESSED_DIR` | `data/processed/` | manifest、chunks、embeddings、metadata 和 FAISS 索引的输出目录。 |
| `SUPPORTED_SUFFIXES` | PDF、HTML、HTM、MD、TXT | 资料集扫描支持的文件格式。 |
| `CHUNK_SIZE` | `1000` | 递归文本切分器使用的目标字符长度。 |
| `CHUNK_OVERLAP` | `200` | 相邻 chunks 之间的重叠字符数。 |
| `EMBEDDING_MODEL` | `BAAI/bge-m3` | 多语言稠密向量模型。 |
| `RERANKER_MODEL` | `BAAI/bge-reranker-v2-m3` | 二阶段重排序使用的 CrossEncoder 模型。 |
| `NORMALIZE_EMBEDDINGS` | `True` | 在内积检索前是否对向量进行归一化。 |
| `EMBEDDING_BATCH_SIZE` | `8` | embedding 推理的批大小；内存压力较高时可以继续调低。 |
| `RETRIEVAL_TOP_K` | `30` | 每个扩展查询召回的候选数量。 |
| `RERANKER_TOP_K` | `5` | 语言感知重排序后保留的段落数量。 |
| `QUERY_REWRITE_MODEL` | `deepseek-v4-flash` | 问题重写、翻译及关键词生成模型。 |
| `GENERATION_MODEL` | `deepseek-v4-flash` | 最终答案生成模型。 |
| `REWRITE_API_BASE` / `GENERATION_API_BASE` | `https://api.deepseek.com` | 兼容 OpenAI 协议的 API 地址。 |
| `REWRITE_API_KEY` / `GENERATION_API_KEY` | `DEEPSEEK_API_KEY` | 保存 API 凭据的环境变量名称。 |
| `ANSWER_LANGUAGE` | `中文` | 最终答案使用的语言。 |

修改 `CHUNK_SIZE`、`CHUNK_OVERLAP`、`EMBEDDING_MODEL` 或 `NORMALIZE_EMBEDDINGS` 后，需要重新运行 `build_index.py`。修改 `RETRIEVAL_TOP_K`、`RERANKER_TOP_K` 或 `ANSWER_LANGUAGE` 不需要重建索引。

## 功能特性

### 多格式资料集导入

- 加载 PDF、HTML/HTM、Markdown 和 UTF-8 文本文件。
- 删除常见的非正文 HTML 元素，并整理多余的空白和换行。
- 保留 loader 原有的 metadata，并为 chunk 添加文档标识、版本、哈希、相对路径、语言、知识层级、资料角色和检索状态。

### 文档版本与增量索引

- 使用文档相对路径作为稳定的 `doc_id`。
- 使用 SHA-256 识别新增、修改、未变化和删除的文档。
- 根据 `doc_id`、`version_id` 和 chunk 位置生成带版本的 `chunk_id`。
- 未变化文档的 chunks 和 vectors 会被保留。
- 只计算新增或修改文档的 embeddings，随后重新构建 FAISS，确保 chunks、vectors 和索引行号保持一致。

资料集发生变化后运行：

```bash
python scripts/update_index.py
```

如果旧的 embedding metadata 缺失、配置不兼容或文件损坏，程序会自动改用完整 embedding 构建。

### 中英双语查询处理

- 将原始问题改写为更适合检索的物理问题。
- 在中文和英文之间翻译重写后的问题。
- 分别生成中文和英文物理关键词查询。
- 同时使用重写问题、翻译问题及两组关键词进行检索。

### 稠密检索与重排序

- 使用多语言 BGE-M3 模型编码问题和文档。
- 使用经过归一化的内积 `IndexFlatIP` FAISS 索引。
- 合并多个查询版本的召回结果，并去除重复候选。
- 分离中英文候选，并使用对应语言的问题进行二阶段排序。

### 基于检索知识的答案生成

- 将排名靠前的 Top-K chunks 拼接到大模型提示词中。
- 提示生成模型优先参考检索内容，并在上下文不足时说明限制。
- 支持配置最终答案语言。
- 同时输出原始问题、重写问题、翻译问题和最终答案。

## 系统流程

```text
原始文档
    |
    v
资料集扫描
    |
    v
文档加载、清洗与切块
    |
    v
embeddings
    |
    v
FAISS IndexFlatIP
    |
    v
问题重写、翻译与查询扩展
    |
    v
召回、融合与去重
    |
    v
语言感知 CrossEncoder 重排序
    |
    v
上下文构建与知识增强生成
```

## 项目结构

```text
RAG_physics_master/
├── app/
│   ├── cleaners/       # 文本清洗
│   ├── embedding/      # chunks 转为 embedding vectors
│   ├── generation/     # 上下文构建与答案生成
│   ├── loaders/        # 文本加载
│   ├── query/          # 问题重写与查询扩展
│   ├── reranking/      # 对召回的 chunks 进行重排序
│   ├── retrieval/      # chunks 检索与召回
│   ├── splitter/       # 文本切块
│   ├── vectorstore/    # FAISS IndexFlatIP 封装
│   └── config.py       # 集中配置
├── scripts/
│   ├── build_index.py  # 完整索引构建流程
│   ├── update_index.py # 资料集与 embeddings 增量更新
│   ├── run_rag.py      # 单次及交互式问答入口
│   └── ...
├── data/processed/     # manifest、chunks 和索引文件的输出目录
├── doc/README_zh.md    # 中文 README
└── requirements.txt
```
