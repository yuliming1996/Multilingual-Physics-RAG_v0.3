# Multilingual Physics RAG System  
# 双语物理知识增强检索生成系统


## Overview  
## 项目简介

This project implements an end-to-end Retrieval-Augmented Generation (RAG) system for physics knowledge question answering. The system is designed for bilingual Chinese-English physics resources, combining high-quality English physics references with Chinese educational materials.

本项目实现了一个端到端的物理知识增强检索生成（Retrieval-Augmented Generation, RAG）系统，面向中英文物理知识库问答场景。系统融合英文高质量物理资料与中文教材资源，实现跨语言物理知识检索与生成。


The main goal is to build a physics-specialized RAG pipeline that can answer conceptual and theoretical physics questions using retrieved knowledge rather than relying only on the language model's internal memory.

项目目标是构建一个面向物理领域的专业 RAG 流程，使模型能够基于检索到的可靠物理资料进行回答，而不是完全依赖大语言模型自身参数记忆。


---
## Installation  
## 安装
### 1.1 Clone the Repository
### 1.1 克隆项目
            
```bash
git clone https://github.com/your-username/your-repository-name.git

cd RAG_project_phy
```

### 1.2 Create a Virtual Environment 
### 1.2 创建虚拟环境
This project is developed and tested with Python 3.12.
Create a virtual environment:

本项目基于 Python 3.12 开发和测试。
创建虚拟环境：
```bash
python -m venv .venv
```

Activate the environment:
激活环境：
macOS / Linux

```bash
source .venv/bin/activate
```

Windows
```bash
.venv\Scripts\activate
```

### 1.3 Install Dependencies
### 1.3 安装依赖
Install all required Python packages:
安装所有 Python 包
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 1.4 Configure Environment Variables
###1.4 配置环境变量
Create a local environment configuration file:
复制环境变量模板：

```bash
cp .env.example .env
```
Then update .env with your API configuration:
```bash
export DEEPSEEK_API_KEY=your_api_key
```



# Features  
# 核心功能


## 1. Multi-format Bilingual Physics Knowledge Base  
## 1. 多格式双语物理知识库

The system supports bilingual physics resources in multiple document formats, including:

- PDF
- HTML
- Markdown (`.md`)
- Plain text (`.txt`)

系统支持多种格式的中英文物理资料导入，包括：

- PDF
- HTML
- Markdown（`.md`）
- 纯文本（`.txt`）


Different document formats are processed through dedicated loaders and normalized into a unified document structure before chunking, embedding, and retrieval.

针对不同文件格式，系统采用对应的文档加载器进行解析，并在切分、向量化和检索之前统一转换为标准化文档结构。


The ingestion pipeline preserves important metadata such as source path, document language, knowledge level, document role, and retrieval eligibility whenever available.

在文档导入过程中，系统尽可能保留来源路径、语言、知识层级、文档角色以及是否参与检索等 metadata 信息。


This design allows heterogeneous physics resources—from textbooks and lecture notes to web-based materials—to be integrated into the same retrieval pipeline.

通过这种设计，不同来源和不同格式的物理资料，例如教材、课程讲义以及网页资料，都可以统一接入同一套 RAG 检索流程。


---

## 2. Intelligent Query Rewriting and Expansion  
## 2. 智能问题重写与查询扩展


A large language model is used to transform user questions into retrieval-friendly queries.

The system generates:

- Rewritten physics questions
- Cross-language translations
- Chinese and English physics keywords

系统利用大语言模型对用户问题进行检索优化。

针对每个问题生成：

- 更准确的物理问题重写
- 跨语言查询转换
- 中英文物理关键词


Example 示例: 

原始提问: 干涉与衍射有什么区别

Origin query: what's the differences between
interference and diffraction

Rewritten query:
zh : 光的干涉与衍射在物理定义、产生条件及现象特征上的主要区别是什么？

Translated query:
en : What are the main differences between light interference and diffraction in terms of physical definitions, conditions, and characteristic phenomena?

Keywords:
zh: 干涉, 衍射, 区别, 光学, 波动性, 相干条件, 光的干涉, 光的衍射
en: interference, diffraction, difference, optics, wave nature, coherencecondition, light interference, light diffraction



---

## 3. Multilingual Dense Retrieval  
## 3. 多语言语义检索


The system uses BGE-M3 embeddings to perform multilingual semantic retrieval.

FAISS is used as the vector database for efficient similarity search.

系统采用 BGE-M3 多语言 embedding 模型进行语义向量表示。

利用 FAISS 实现高效向量检索。


The retrieval process supports:

- Chinese query → English physics resources
- English query → Chinese physics resources
- Cross-lingual knowledge retrieval

系统支持：

- 中文问题检索英文物理资料
- 英文问题检索中文教材
- 跨语言知识召回


---

## 4. Candidate Fusion and Deduplication  
## 4. 候选结果融合与去重


Multiple retrieval queries are executed simultaneously:

- Rewritten query
- Translated query
- Chinese keywords
- English keywords

Retrieved candidates are merged and duplicated documents are removed before reranking.

系统同时执行多个查询：

- 重写问题
- 翻译问题
- 中文关键词
- 英文关键词

多个检索结果经过融合和去重后进入精排阶段。


---

## 5. Language-aware Reranking  
## 5. 语言感知重排序


A CrossEncoder reranker is introduced to improve retrieval precision.

Chinese queries are matched with Chinese documents, while English queries are matched with English documents.

系统采用 CrossEncoder 进行二阶段精排，提高最终上下文质量。

其中：

- 中文 query 对中文资料进行 rerank
- 英文 query 对英文资料进行 rerank


This design improves the ability to retrieve high-quality English physics references when users ask questions in Chinese.

该设计解决了中文问题容易偏向中文资料的问题，使用户可以通过中文提问获得英文高质量物理资料。


---

## 6. Context Construction and Grounded Generation  
## 6. 上下文构建与基于知识生成


The retrieved documents are converted into structured context and provided to the LLM.

The generator produces answers based on retrieved physics knowledge.

检索后的文档会被转换为结构化上下文，并输入大语言模型。

模型基于检索到的物理知识生成最终答案。


The system supports configurable output language.

系统支持通过配置控制回答语言：

```python
ANSWER_LANGUAGE = "中文"
or
ANSWER_LANGUAGE = "English"
System Architecture
系统架构
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
