import os
import json
import re
import asyncio
import hashlib
import logging
from typing import List, Dict, Any, Tuple
from pathlib import Path
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

# 配置日志
logger = logging.getLogger("graph_engine")

# 加载配置
env_path = Path(__file__).parent / "graphrag_project" / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:latest")
AUTH_TOKEN = os.getenv("GRAPHRAG_API_KEY", "default_token_for_dev")

llm = ChatOllama(
    model=OLLAMA_MODEL,
    temperature=0.1,
    base_url=OLLAMA_BASE_URL
)

GRAPH_DATA_PATH = Path(__file__).parent / "vector_kb" / "knowledge_graph.json"

class GraphEngine:
    def __init__(self):
        self.GRAPH_DATA_PATH = GRAPH_DATA_PATH
        self.nodes = {} # {id: {label: str, type: str, source_chunks: []}}
        self.edges = [] # [{source: id, target: id, relation: str}]
        self.processed_chunks = set() # 记录已处理的分片 ID
        self._mermaid_cache = None # 增加缓存以减少重复生成
        self._cache_key = None
        self.load_graph()

    def load_graph(self):
        if self.GRAPH_DATA_PATH.exists():
            try:
                with open(self.GRAPH_DATA_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.nodes = data.get("nodes", {})
                    self.edges = data.get("edges", [])
                    # 加载已处理的分片 ID
                    self.processed_chunks = set(data.get("processed_chunks", []))
                    self.clear_cache()
            except Exception as e:
                logger.error(f"加载图谱失败: {e}")

    def save_graph(self):
        self.GRAPH_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(self.GRAPH_DATA_PATH, "w", encoding="utf-8") as f:
            json.dump({
                "nodes": self.nodes, 
                "edges": self.edges,
                "processed_chunks": list(self.processed_chunks) # 持久化已处理的分片
            }, f, ensure_ascii=False, indent=2)
        self.clear_cache()

    def clear_cache(self):
        """清空图谱生成缓存"""
        self._mermaid_cache = None
        self._cache_key = None

    def _is_id(self, label: str) -> bool:
        """检查标签是否是 12 位十六进制 ID"""
        if not label: return True
        return bool(re.match(r'^[0-9a-f]{12}$', str(label).lower().strip()))

    def _is_metadata(self, label: str) -> bool:
        """启发式过滤：识别并过滤掉文献元数据噪音 (方案 A: Semantic Gateway)"""
        if not label: return True
        label_lower = str(label).lower().strip()
        
        # 1. 机构与学术单位关键词
        edu_keywords = ['university', 'college', 'institute', 'department', 'school', 'academy', 'faculty', 'univ.', 'inst.']
        # 2. 出版、卷号、页码等元数据
        pub_keywords = ['journal', 'proceedings', 'volume', 'issue', 'editor', 'publisher', 'published', 'copyright', 'doi:', 'issn', 'isbn', 'pp.', 'pages']
        # 3. 常见非专业噪音 (基于用户反馈与常见论文页眉页脚)
        noise_entities = ['poland', 'warsaw', 'et al', 'abstract', 'keywords', 'introduction', 'conclusion', 'references', 'table', 'figure']
        
        # 匹配关键词
        for kw in edu_keywords + pub_keywords + noise_entities:
            if kw in label_lower:
                return True
                
        # 4. 正则过滤：过滤掉纯数字年份或类似 [12] 的引用标识
        if re.match(r'^\d{4}$', label_lower): return True # 纯年份
        if re.match(r'^\[\d+\]$', label_lower): return True # 引用 [1]
        
        return False

    async def extract_triples(self, text: str, chunk_id: str) -> List[List[str]]:
        """从文本中提取三元组 (Subject, Predicate, Object)"""
        prompt = f"""你是一个专业的知识图谱构建专家。请从以下文本中提取关键的实体（名词）及其相互关系。

提取要求：
1. 识别文本中的核心概念、人物、组织、方法、技术、指标或任何重要实体。
2. 将它们表示为简洁的三元组格式：[实体1, 关系, 实体2]。
3. 关系应该是简短的动词或描述性短语（例如：“位于”、“属于”、“提高”、“导致”、“包含”、“研究”）。
4. **必须且仅**输出一个标准的 JSON 数组。
5. 如果文本中没有任何有价值的关系，请返回空数组 []。
6. 不要输出任何解释文字，不要包含 Markdown 代码块标签。

【示例】
输入文本：
高强度间歇训练（HIIT）可以显著提高运动员的最大摄氧量（VO2 max）。这项技术被国家田径队广泛采用。
输出JSON：
[["高强度间歇训练", "提高", "最大摄氧量"], ["国家田径队", "采用", "高强度间歇训练"]]

待处理文本：
{text}

JSON 输出："""
        
        try:
            # 增加超时控制：从 40s 增加到 120s，以适配本地大模型提取压力
            response = await asyncio.wait_for(llm.ainvoke([HumanMessage(content=prompt)]), timeout=120.0)
            content = response.content.strip()
            
            # 1. 清理可能的 Markdown 包装
            content = re.sub(r'```json\s*', '', content)
            content = re.sub(r'```\s*', '', content)
            content = content.strip()
            
            # 2. 尝试解析 JSON
            try:
                data = json.loads(content)
                if isinstance(data, list):
                    valid = [t for t in data if isinstance(t, list) and len(t) >= 3]
                    if valid: return valid
            except:
                pass

            # 3. 兜底正则匹配：查找所有的 ["A", "B", "C"]
            fallback_matches = re.findall(r'\[\s*"([^"]+)"\s*,\s*"([^"]+)"\s*,\s*"([^"]+)"\s*\]', content)
            if fallback_matches:
                return [list(m) for m in fallback_matches]
            
            # 4. 进一步兜底：查找 (A, B, C) 格式
            fallback_matches_tuple = re.findall(r'\(\s*([^,]+)\s*,\s*([^,]+)\s*,\s*([^,]+)\s*\)', content)
            if fallback_matches_tuple:
                return [[i.strip().strip('"').strip("'") for i in m] for m in fallback_matches_tuple]

        except asyncio.TimeoutError:
            logger.warning(f"提取超时 ({chunk_id})")
        except Exception as e:
            logger.error(f"提取三元组失败 ({chunk_id}): {e}")
        return []

    def _add_triple(self, sub: str, pred: str, obj: str, source_id: str):
        """将单个三元组添加到图谱中"""
        # 规范化 ID (移除特殊字符，保留中文和字母数字)
        def get_node_id(label):
            l = str(label).lower().strip()
            return hashlib.md5(l.encode()).hexdigest()[:12] # 使用哈希作为稳定 ID
        
        sub_id = get_node_id(sub)
        obj_id = get_node_id(obj)
        
        # 添加节点
        for n_id, n_label in [(sub_id, sub), (obj_id, obj)]:
            if not n_label: continue
            # 过滤掉 ID、元数据、或太短的标签
            if self._is_id(n_label) or self._is_metadata(n_label):
                continue
            if len(str(n_label).strip()) < 2:
                continue
                
            if n_id not in self.nodes:
                self.nodes[n_id] = {
                    "label": str(n_label),
                    "source_chunks": [source_id]
                }
            else:
                if source_id not in self.nodes[n_id]["source_chunks"]:
                    self.nodes[n_id]["source_chunks"].append(source_id)
        
        # 只有当两个节点都有效时才添加边
        if sub_id in self.nodes and obj_id in self.nodes:
            # 检查是否已存在完全相同的边，避免重复
            edge_exists = any(
                e["source"] == sub_id and 
                e["target"] == obj_id and 
                e["relation"] == str(pred) 
                for e in self.edges
            )
            if not edge_exists:
                self.edges.append({
                    "source": sub_id,
                    "target": obj_id,
                    "relation": str(pred)
                })

    async def build_graph(self, chunks: List[Dict[str, Any]], progress_callback=None, incremental: bool = True):
        """遍历所有 chunks 构建图谱"""
        if not incremental:
            logger.info("正在进行全量构建，清除现有图谱数据...")
            self.nodes = {}
            self.edges = []
            self.processed_chunks = set()
        
        if not chunks:
            logger.warning("传入的 chunks 为空，无法构建图谱")
            return len(self.nodes), len(self.edges)

        # 过滤掉已经处理过的分片
        new_chunks = [c for c in chunks if c["chunk_id"] not in self.processed_chunks]
        
        if not new_chunks:
            logger.info("所有分片均已处理，无需更新图谱。")
            return len(self.nodes), len(self.edges)

        # 对新分片进行策略性选择（如果新分片仍然很多）
        if len(new_chunks) <= 300:
            process_chunks = new_chunks
        else:
            # 取头、中、尾，确保新上传的文档能被覆盖到
            mid = len(new_chunks) // 2
            process_chunks = new_chunks[:100] + new_chunks[mid-50:mid+50] + new_chunks[-100:]
            
        total = len(process_chunks)
        logger.info(f"开始构建图谱 (增量: {incremental})，共需处理 {total} 个新分片...")
        
        extracted_count = 0
        for i, chunk in enumerate(process_chunks):
            triples = await self.extract_triples(chunk["text"], chunk["chunk_id"])
            if triples:
                extracted_count += len(triples)
                logger.info(f"[{i+1}/{total}] 成功从 {chunk['chunk_id']} 提取 {len(triples)} 条三元组 (累计: {extracted_count})")
            
            # 标记该分片已处理
            self.processed_chunks.add(chunk["chunk_id"])
            
            for triple in triples:
                if not isinstance(triple, list) or len(triple) < 3:
                    continue
                self._add_triple(triple[0], triple[1], triple[2], chunk["chunk_id"])
            
            if progress_callback:
                progress_callback(i + 1, total)
        
        self.save_graph()
        logger.info(f"图谱构建完毕：{len(self.nodes)} 节点, {len(self.edges)} 边")
        return len(self.nodes), len(self.edges)

    async def add_multimodal_description(self, description: str, source_id: str):
        """将多模态描述提取为三元组并注入图谱"""
        logger.info(f"开始处理多模态描述，来源: {source_id}")
        triples = await self.extract_triples(description, source_id)
        if triples:
            for triple in triples:
                if not isinstance(triple, list) or len(triple) < 3:
                    continue
                self._add_triple(triple[0], triple[1], triple[2], source_id)
            self.save_graph()
            logger.info(f"多模态描述注入完毕，成功提取 {len(triples)} 条三元组")
            return len(triples)
        return 0

    def search_graph(self, query_entities: List[str], max_hops: int = 2) -> Dict[str, Any]:
        """图谱搜索：基于查询实体进行多跳推理"""
        if not self.nodes:
            return {"nodes": {}, "edges": []}
            
        related_node_ids = set()
        related_edges = []
        
        # 初始种子节点匹配
        seeds = [e.lower().strip() for e in query_entities]
        current_level = []
        
        for s in seeds:
            for node_id, node_info in self.nodes.items():
                label = node_info["label"].lower()
                if s in label or label in s:
                    current_level.append(node_id)
        
        current_level = list(set(current_level))
        
        for hop in range(max_hops):
            next_level = []
            for node_id in current_level:
                related_node_ids.add(node_id)
                # 查找相关的边
                for edge in self.edges:
                    s_id = edge["source"]
                    t_id = edge["target"]
                    if s_id == node_id and t_id not in related_node_ids:
                        related_edges.append(edge)
                        next_level.append(t_id)
                    elif t_id == node_id and s_id not in related_node_ids:
                        related_edges.append(edge)
                        next_level.append(s_id)
            current_level = list(set(next_level))
            if not current_level:
                break
        
        # 【全链路健壮性重构】确保边缘包含的所有节点都存在于 node_ids 中
        related_node_ids.update(current_level)
        for edge in related_edges:
            related_node_ids.add(edge["source"])
            related_node_ids.add(edge["target"])
                
        # 最终过滤：只返回包含有效标签的节点，且过滤掉标签本身就是 ID 或元数据的节点
        final_nodes = {}
        for nid in related_node_ids:
            if nid in self.nodes:
                label = self.nodes[nid].get("label", "")
                if label and not self._is_id(label) and not self._is_metadata(label):
                    final_nodes[nid] = self.nodes[nid]

        return {
            "nodes": final_nodes,
            "edges": [e for e in related_edges if e["source"] in final_nodes and e["target"] in final_nodes]
        }

    def generate_mermaid(self, nodes: Dict = None, edges: List = None, limit: int = 50, highlight_phrases: List[str] = None) -> str:
        """生成 Mermaid 流程图代码用于可视化。支持全量或指定子图。"""
        # 针对全量图谱生成增加缓存逻辑
        if nodes is None and edges is None and limit == 50:
            current_key = f"{len(self.nodes)}_{len(self.edges)}_{hash(tuple(highlight_phrases or []))}"
            if self._mermaid_cache and self._cache_key == current_key:
                return self._mermaid_cache
            
        target_nodes = nodes if nodes is not None else self.nodes
        target_edges = edges if edges is not None else self.edges
        
        if not target_nodes:
            return "flowchart TD\n  Empty[知识图谱为空，请先构建]"
        
        # 使用 flowchart LR 并配置主题样式
        mermaid = "flowchart LR\n"
        mermaid += "    %% 样式定义：增强对比度与视觉层次\n"
        # 实体节点：深蓝色边框，黑色粗体文字，浅蓝背景
        mermaid += "    classDef entity fill:#e1f5fe,stroke:#01579b,stroke-width:2.5px,color:#000,font-weight:bold;\n"
        # 高亮节点：金黄色背景，深黄边框，黑色粗体文字
        mermaid += "    classDef highlight fill:#fff9c4,stroke:#fbc02d,stroke-width:3px,color:#000,font-weight:bold;\n"
        
        # 限制显示的边数
        display_edges = target_edges[:limit]
        
        added_nodes = set()
        
        def clean_label(l):
            l = str(l)
            l = re.sub(r'[^\w\s\u4e00-\u9fa5\.\-\(\)]', '', l)
            return l.strip()

        def word_wrap(text, width=25):
            if len(text) <= width: return text
            words = text.split()
            lines = []
            current_line = []
            current_length = 0
            for word in words:
                if current_length + len(word) > width:
                    lines.append(" ".join(current_line))
                    current_line = [word]
                    current_length = len(word)
                else:
                    current_line.append(word)
                    current_length += len(word) + 1
            if current_line:
                lines.append(" ".join(current_line))
            return "<br/>".join(lines)

        def highlight_blue(text):
            phrases = highlight_phrases or []
            has_highlight = False
            for phrase in phrases:
                if phrase.lower() in text.lower():
                    # 移除 HTML 标签，Mermaid 默认不支持，会渲染失败
                    # 仅标记为高亮节点逻辑
                    has_highlight = True
            return text, has_highlight

        for edge in display_edges:
            s_id = str(edge.get("source", "")).strip()
            t_id = str(edge.get("target", "")).strip()
            
            if not s_id or not t_id:
                continue
                
            s_raw_label = target_nodes.get(s_id, {}).get("label")
            t_raw_label = target_nodes.get(t_id, {}).get("label")
            
            # 如果没有标签，或者是 ID 或元数据 (过滤垃圾节点)，则跳过
            if not s_raw_label or not t_raw_label or self._is_id(s_raw_label) or self._is_id(t_raw_label) or self._is_metadata(s_raw_label) or self._is_metadata(t_raw_label):
                continue
                
            s_label_clean = clean_label(s_raw_label)
            t_label_clean = clean_label(t_raw_label)
            
            s_label_high, s_high = highlight_blue(s_label_clean)
            t_label_high, t_high = highlight_blue(t_label_clean)
            
            s_label = word_wrap(s_label_high)
            t_label = word_wrap(t_label_high)
            
            relation_raw = edge.get("relation", "related")
            relation_clean = clean_label(relation_raw)
            relation_high, _ = highlight_blue(relation_clean)
            relation = word_wrap(relation_high, width=20)
            
            if not s_label or not t_label:
                continue

            s_m_id = "N" + hashlib.md5(s_id.encode()).hexdigest()[:8]
            t_m_id = "N" + hashlib.md5(t_id.encode()).hexdigest()[:8]
            
            if s_m_id not in added_nodes:
                mermaid += f'    {s_m_id}["{s_label}"]\n'
                mermaid += f'    class {s_m_id} {"highlight" if s_high else "entity"}\n'
                added_nodes.add(s_m_id)
            if t_m_id not in added_nodes:
                mermaid += f'    {t_m_id}["{t_label}"]\n'
                mermaid += f'    class {t_m_id} {"highlight" if t_high else "entity"}\n'
                added_nodes.add(t_m_id)
                
            mermaid += f'    {s_m_id} -- "{relation}" --> {t_m_id}\n'
            
        if not added_nodes and nodes:
             # 如果有节点但没有边（孤立节点），也展示出来
             for nid, ninfo in nodes.items():
                 m_id = "N" + hashlib.md5(nid.encode()).hexdigest()[:8]
                 label = word_wrap(clean_label(ninfo.get("label", nid)))
                 mermaid += f'    {m_id}["{label}"]\n'
                 mermaid += f'    class {m_id} entity\n'
        
        if not added_nodes:
            res = "flowchart TD\n  Empty[暂无有效的图谱关系]"
        else:
            res = mermaid
            
        # 存入缓存
        if nodes is None and edges is None and limit == 50:
            self._mermaid_cache = res
            self._cache_key = current_key
            
        return res

graph_engine = GraphEngine()
