# 后端技术文档

## 1 技术栈概览

| 层次 | 技术选型 |
|------|---------|
| 编程语言 | Python |
| UI / 本地服务承载 | Gradio（本地 Web UI） |
| Agent 编排 | LangGraph（`StateGraph`，含 conditional routing / loop / astream 流式事件 / HITL checkpoint） |
| LLM 接入（两条线） | LangChain `ChatOllama`（直连 `http://localhost:11434`）；OpenAI 兼容 SDK `openai`（`base_url="http://localhost:11434/v1"`） |
| RAG（向量检索） | TF‑IDF（scikit‑learn）+ 稀疏矩阵（scipy）+ 本地文件落盘（jsonl / pkl / npz） |
| GraphRAG | Microsoft GraphRAG（CLI）+ LiteLLM（OpenAI provider）+ LanceDB（向量库）+ Parquet（索引表） |

---

## 2 主要入口（Entry Points）

| 文件 | 职责 |
|------|------|
| `integrated_platform.py` | **集成平台主入口**：Gradio 三页签（问答 / 知识库 / 评测）+ LangGraph 多代理工作流 + TF‑IDF RAG + Ollama。UI 侧通过 `integrated_app.astream(state)` 流式输出 reasoning log。 |
| `langgraph_multi_agent.py` | **多 Agent 工作流命令行演示**：同步 `app.invoke()`，节点含 `classifier / coach / nutritionist / therapist / reviewer / formatter`，审核失败路由回对应专家重写（最多迭代，超限强制放行）。 |
| `build_vector_kb.py` | **知识库构建 / 测试 CLI**（`--mode build | test`）：从 `domain_docs/` 抽取 → 清洗 → 切块 → TF‑IDF → 落盘；或对问题集跑检索测试导出报告。 |
| `preprocess_docs.py` | **文档预处理 CLI**：PDF / DOCX / TXT / MD 抽取文本并规范化，写入 `cleaned_docs/` 与 `preprocess_report.json`。 |
| `graphrag_project/run_query_experiments.py` | **GraphRAG 查询实验入口**：生成 `python -m graphrag query ...` 命令并读取 `output/*.parquet` 统计索引规模。 |
| `实验七_多模态应用/multimodal_chatbot.py` | **多模态对比竞技场入口**：Gradio + OpenAI SDK（Ollama `/v1` 兼容）对两个视觉模型做双路流式输出。 |

---

## 3 LangGraph 工作流模块

| 文件 | 模式 | 说明 |
|------|------|------|
| `langgraph_multi_agent.py` | 多 Agent 协作（分类 → 专家 → 审核 → 迭代 → 排版） | 核心原型，审核失败循环路由回专家 |
| `langgraph_router.py` | 条件路由 | `add_conditional_edges` 根据 `classify` 结果路由到 physiology / methodology / safety |
| `langgraph_pipeline.py` | 串行流水线 | `research → write → review → revise → final_article` 线性连接 |
| `langgraph_iterative.py` | 循环迭代 | `should_continue` 决定回到 generate 还是 END |
| `langgraph_hitl.py` | HITL（Human-in-the-Loop） | `MemorySaver` checkpointer + 终端 `input()` 人工审核，支持 `thread_id` 状态持久化 |
| `langgraph_agent.py` | 简化三段式 | 检索文献（mock） → LLM 分析 → 报告生成 |
| `multi_rag_test.py` | 多代理 RAG 测试 | 与 `langgraph_multi_agent.py` 基本同构的测试脚本 |

---

## 4 LLM 接入（Ollama）

### 4.1 LangChain 原生（主要用于 LangGraph 节点）

```python
from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="qwen2.5:latest",   # 或 "qwen2.5"
    base_url="http://localhost:11434"
)
```

调用方：`integrated_platform.py`、`langgraph_multi_agent.py` 等所有 LangGraph 节点。

### 4.2 OpenAI 兼容 API（用于多模态 / GraphRAG）

```python
from openai import OpenAI

client = OpenAI(
    api_key="ollama",
    base_url="http://localhost:11434/v1"
)
```

调用方：
- `实验七_多模态应用/multimodal_chatbot.py`（视觉模型对比）
- `graphrag_project/settings.yaml`（GraphRAG 的 LiteLLM provider）

---

## 5 本地 RAG（TF‑IDF）

### 5.1 预处理 / 文档抽取

- **脚本**：`preprocess_docs.py`
- **输入**：PDF（PyMuPDF `fitz` 优先，fallback `pypdf`）、DOCX（`python-docx`）、TXT、MD
- **输出**：`cleaned_docs/*.cleaned.txt` + `preprocess_report.json`

### 5.2 向量库构建 / 加载 / 检索

- **脚本**：`build_vector_kb.py`
- **切块**：`split_text(chunk_size, chunk_overlap)`，每块带 `chunk_id`
- **向量化**：`sklearn.feature_extraction.text.TfidfVectorizer`
- **持久化**：
  - `chunks.jsonl`（文本块列表）
  - `tfidf_vectorizer.pkl`（模型）
  - `tfidf_matrix.npz`（稀疏矩阵，fallback 纯 `pkl`）
- **检索**：`retrieve(query, top_k)` — query 归一化 + 关键词 hints 扩展 + 余弦 / 点积相似度

### 5.3 知识库目录结构

```
domain_docs/          # 原始领域文档（PDF 等）
cleaned_docs/         # 清洗后的 .cleaned.txt
vector_kb/             # 全局 TF‑IDF 知识库（chunks.jsonl / vectorizer.pkl / matrix.npz）
uploaded_docs/         # Gradio 上传的用户文档（临时）
vector_kb_user/        # Gradio 上传后重建的用户知识库产物
```

---

## 6 GraphRAG（知识图谱 + 向量库）

### 6.1 配置

- **文件**：`graphrag_project/settings.yaml`
- **模型**：LLM `llama3` + Embedding `nomic-embed-text:latest`，均通过 `http://localhost:11434/v1` 走 LiteLLM
- **向量库**：LanceDB（`output/lancedb`）
- **索引表**：Parquet 形式落地到 `output/`

### 6.2 工作流定义

`settings.yaml` 中定义了 GraphRAG indexing 工作流：
`extract_graph → create_communities → generate_text_embeddings → ...`

### 6.3 查询实验

- **脚本**：`graphrag_project/run_query_experiments.py`
- 生成 global / local 查询命令并汇总 `output/*.parquet` 统计索引规模。

---

## 7 评测与报告

| 文件 | 职责 |
|------|------|
| `evaluate_workflow.py` | 调用 `langgraph_multi_agent.app` 批量跑测试用例，捕获 stdout 日志并生成 `workflow_evaluation_report.md` |
| `run.py` | 极简导入检查脚本（确认 `langgraph_multi_agent` 可 import） |
| `download_marathon_papers.py` / `download_specific_papers.py` | 语料获取辅助脚本，供 `domain_docs/` 或 GraphRAG input 使用 |
| `visualize_graph.py` | 工作流 / 图谱结果可视化（输出 `workflow_graph.png` / `graph_visualization.png`） |

---

## 8 模块依赖关系（简化）

```
integrated_platform.py（主入口）
├── langgraph_multi_agent.py（工作流定义 + app）
│   ├── build_vector_kb.py（TF-IDF retrieve）
│   │   └── preprocess_docs.py（文档抽取）
│   └── ChatOllama（LLM）
│
graphrag_project/
├── settings.yaml（GraphRAG 配置 + LiteLLM）
├── run_query_experiments.py（查询实验）
└── （外部 Microsoft GraphRAG CLI）

实验七_多模态应用/multimodal_chatbot.py
└── openai SDK（Ollama /v1 兼容）
```

---

*文档版本：2025-07-01（随代码变更同步更新）*
