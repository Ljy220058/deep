# Ollama Pro GraphRAG Platform v2.0 项目执行计划书

## 1. 项目基本信息
- **项目名称**: Ollama Pro GraphRAG Platform v2.0
- **需求描述**: 
    - 升级原有 LangGraph 工作流为 Team + Subagent 混合架构。
    - 引入全流程 Token 管控模块，实现成本可视化与配额限制。
    - 深度整合前后端，增强 Gradio UI 的流式反馈与风险拦截能力。
    - 建立 AI 审计机制，确保生成内容的合规性与质量。
- **截止时间**: 2026-04-23 (7天)
- **总 Token 预算**: 5,000,000 Tokens

## 2. 里程碑节点
| 阶段 | 交付物 | 截止日期 | 责任人 |
|------|--------|----------|--------|
| M1: 架构设计 | 《混合架构设计方案》、v2.0 基础框架代码 | D+2 | PM (我) / 开发智能体 |
| M2: 核心功能 | Token 管控模块、AI 审计节点实现 | D+4 | 开发智能体 / 审计员 |
| M3: 前后端整合 | 优化后的 `integrated_platform.py` | D+5 | 前端 / 后端开发智能体 |
| M4: 验收交付 | 《联调问题报告》、《上线验收报告》 | D+7 | 测试工程师 / 审计员 |

## 3. 资源分配 (智能体矩阵)
- **后端开发智能体**: 负责 `workflow_engine.py` 的架构重构、API 接口设计与 Token 统计逻辑。
- **前端开发智能体**: 负责 `integrated_platform.py` 的 UI 交互优化、流式日志展示与前端拦截逻辑。
- **AI 整合审计员**: 负责在 `LangGraph` 中作为独立节点，对 `draft_plan` 和 `final_report` 进行质量审计。
- **测试工程师智能体**: 负责 `evaluate_workflow.py` 的升级与全链路测试。
- **PM 智能体 (我)**: 整体统筹、Token 调度与风险决策。

## 4. 验收标准
1. **混合架构**: 能够根据问题复杂度自动切换 Team (多专家) 或 Subagent (主从) 模式。
2. **Token 管控**: UI 需实时显示当前会话的 Token 消耗，且支持超过配额后的熔断。
3. **零重大事故**: 经过 AI 审计员验证，无内容合规性风险。

## 5. 功能扩展记录 (M4+)
### 5.1 Cross-Document Analytics (跨文档实体分析)
- **技术需求**: 用户在 Graph Explorer 中多选实体，自动触发多智能体跨文档聚合分析，解决实体关联推理的信息过载与碎片化问题。
- **组间实现方法**:
  - `workflow_engine.py`: 新增 `research_analyst_node`，接收多个实体列表，提取相关子图 chunk IDs，使用 Cross-Encoder (ms-marco-MiniLM-L-6-v2) 重排序并过滤 Top 15，组装后送入大模型生成分析报告。
  - `integrated_platform.py`: 修改 `entity_selector` 为多选下拉框，增加 `handle_research_analysis` 异步生成器，与 UI 中的 `analyze_entities_btn` 绑定，实时渲染 JSON 结构化分析报告。

### 5.2 Dynamic Adaptive Planning (动态自适应计划调整)
- **技术需求**: 根据用户近期的疲劳度反馈、异常心率或缺席训练记录，动态调整（Adaptive Planning）当前的马拉松训练计划，防止过度训练。
- **组间实现方法**:
  - `workflow_engine.py`: 在 `IntegratedState` 中新增 `adaptive_feedback` (疲劳度、缺席、异常、备注)。新增 `adaptive_coach_node`，专门处理带反馈的计划调整；修改 `gate_decision` 和 `after_therapist_route` 等路由节点，支持 `mode="adaptive"` 链路。
  - `integrated_platform.py`: 在 UI 中新增 "Adaptive Plan Adjustment" 手风琴面板（包含滑块和复选框）；新增 `handle_adaptive_plan` 方法封装 `handle_qa` 并注入 `adaptive` 模式与反馈数据，绑定至生成按钮。

---
*由 Senior Technical PM 生成 | 2026-04-16*
