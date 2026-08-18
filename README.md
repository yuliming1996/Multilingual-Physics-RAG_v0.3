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
