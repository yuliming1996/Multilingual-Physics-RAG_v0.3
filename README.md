# Multilingual Physics RAG System

# 双语物理知识增强检索生成系统

## Overview

## 项目简介

This project implements an end-to-end Retrieval-Augmented Generation (RAG) system for physics knowledge question answering. The system is designed for bilingual Chinese-English physics resources, integrating high-quality English references and Chinese educational materials into a unified retrieval pipeline.

本项目实现了一个端到端的物理知识增强检索生成（Retrieval-Augmented Generation, RAG）系统，面向中英文物理知识问答场景。系统融合英文高质量物理参考资料与中文教育资源，构建统一的跨语言知识检索与生成流程。

The goal of this project is to build a physics-specialized RAG pipeline that generates answers based on retrieved external knowledge, improving factual grounding and reducing hallucination compared with relying only on the language model's internal parameters.

项目旨在构建面向物理领域的专业化 RAG 流程，使模型能够基于检索到的外部知识生成回答，提高答案的可靠性，并降低仅依赖大语言模型参数记忆导致的幻觉问题。

This README is written in both English and Chinese. You may read either language version.

本文档提供中英文双语版本，可根据需要阅读任意一种语言。


---

# Installation

# 安装


## 1.1 Clone the Repository

## 1.1 克隆项目


```bash
git clone https://github.com/your-username/your-repository-name.git

cd RAG_project_phy
```

## 1.2 Create a Virtual Environment

## 1.2 创建虚拟环境

This project is developed and tested with Python 3.12.

本项目基于 Python 3.12 开发和测试。

Create a virtual environment:

创建虚拟环境：
```bash
python -m venv .venv
Activate the environment:
```
激活虚拟环境：

macOS / Linux:
```bash
source .venv/bin/activate
```

Windows:
```bash
.venv\Scripts\activate
```

## 1.3 Install Dependencies

## 1.3 安装依赖

Install required Python packages:

安装项目依赖：
```bash
pip install --upgrade pip

pip install -r requirements.txt
```

Main dependencies include:

主要依赖包括：

- langchain-core and langchain-community for document processing components
- langchain-text-splitters for document chunking
- sentence-transformers for embedding generation
- faiss-cpu for dense vector retrieval
- pypdf and beautifulsoup4 for multi-format document loading
- openai for LLM-based query processing and generation
  
## 1.4 Configure Environment Variables

## 1.4 配置环境变量

Create a local environment file:

创建本地环境变量文件：
```bash
cp .env.example .env
```

Configure your API key:
配置 API：
```bash
export DEEPSEEK_API_KEY=your_api_key
```

Note: Never upload .env files containing private API keys to GitHub.
注意：包含 API Key 的 .env 文件禁止上传至 GitHub。

# Features
# 核心功能
## 1. Multi-format Bilingual Physics Knowledge Base
## 1. 多格式双语物理知识库
The system supports bilingual physics resources in multiple formats:

系统支持多种格式的中英文物理知识资源：

- PDF
- HTML
- Markdown (.md)
- Plain Text (.txt)

Different document formats are processed using dedicated loaders and converted into a unified document representation before chunking, embedding, and retrieval.

针对不同文档格式，系统采用对应加载器进行解析，并在文本切分、向量化和检索前统一转换为标准化 Document 结构。

The ingestion pipeline preserves important metadata, including:

文档导入过程中保留关键 metadata 信息，包括：

- Source path
- Language
- Knowledge level
- Document role
- Retrieval availability
  
该设计使教材、课程讲义、网页资料等不同来源的物理知识能够统一接入 RAG 流程。

## 2. Intelligent Query Rewriting and Expansion
## 2. 智能问题重写与查询扩展
A large language model is used to transform user questions into retrieval-optimized queries.

系统利用大语言模型对用户问题进行检索优化。

The generated information includes:

生成内容包括：
- Rewritten physics questions
- Cross-language translations
- Chinese and English physics keywords
  
Example:

原始问题：

干涉与衍射有什么区别

Rewritten query:

光的干涉与衍射在物理定义、产生条件及现象特征上的主要区别是什么？

Translated query:

What are the main differences between light interference and diffraction in terms of physical definitions, conditions, and characteristic phenomena?

## 3. Multilingual Dense Retrieval

## 3. 多语言语义检索

The system uses the BGE-M3 multilingual embedding model to generate semantic representations.

系统采用 BGE-M3 多语言 embedding 模型进行语义向量表示。

FAISS is used as the dense vector database for efficient similarity search.

利用 FAISS 实现高效向量相似度检索。

Supported retrieval scenarios:

支持以下跨语言检索场景：

- Chinese query → English physics references
- English query → Chinese educational materials
- Cross-lingual knowledge retrieval
  
## 4. Candidate Fusion and Deduplication
## 4. 候选融合与去重

Multiple retrieval queries are executed simultaneously:

系统同时执行多个检索请求：

- Rewritten query
- Translated query
- Chinese keywords
- English keywords
  
Retrieved candidates are merged and deduplicated before reranking.

多个检索结果经过融合与去重后进入下一阶段排序。

## 5. Language-aware Reranking
## 5. 语言感知重排序
A cross-encoder based reranker is introduced to improve retrieval precision.


系统采用基于 CrossEncoder 的二阶段排序模型，提高最终检索结果质量。

The reranking process considers query-document language consistency:

排序过程考虑 query 与 document 的语言匹配关系：

- Chinese query → Chinese documents
- English query → English documents
  
This improves access to high-quality English physics references when users ask questions in Chinese.

该设计提高了中文用户获取英文高质量物理资料的能力。
## 6. Context Construction and Grounded Generation
## 6. 上下文构建与知识增强生成
Retrieved documents are converted into structured context and provided to the LLM.

检索结果被转换为结构化上下文，并输入大语言模型。

The final answer is generated based on retrieved physics knowledge.

模型基于检索到的物理知识生成最终答案。

The system supports configurable output languages:

系统支持配置输出语言：
ANSWER_LANGUAGE = "中文"
or
ANSWER_LANGUAGE = "English"
System Architecture

# 系统架构
User Question

        |
        v

LLM Query Rewrite

        |
        v

Multilingual Query Expansion

        |
        v

BGE-M3 Embedding

        |
        v

FAISS Dense Retrieval

        |
        v

Candidate Fusion

        |
        v

Language-aware Reranker

        |
        v

Context Builder

        |
        v

LLM Generation

        |
        v

Final Answer
