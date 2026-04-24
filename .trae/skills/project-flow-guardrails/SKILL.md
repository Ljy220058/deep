***

name: "project-flow-guardrails"
description: "针对实验工作流与 RAG 系统（如 Marathon Coach）的防错护栏。包含实验预检、零幻觉（Zero Hallucination）策略及安全扫描规则。"
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Project Flow Guardrails

## Purpose

标准化实验与 RAG 系统工作流，避免重复出现数据范围错误、模型崩塌、引用幻觉、以及安全注入风险。

## Invoke When

- 开始或修改训练/分析/可视化实验
- 开发或调试基于 RAG/GraphRAG 的问答系统
- 出现指标异常（如曲线平坦、全零输出）或审计拦截率过高时
- 重新生成实验输出或报告时

## Required Workflow

### 1) Preflight Consistency

- Verify dataset pixel range at load and before image conversion
- Use adaptive conversion to uint8; never blindly divide by 255 twice
- Keep train/eval dataset config consistent (especially class filtering like min\_faces\_per\_person)
- Confirm model output class count matches dataset class count
- For text classification, decode label IDs to label names before remapping classes
- Reject fallback label mapping rules unless explicitly documented in report diagnostics

### 2) Training Safety

- Log prediction diversity (unique predicted classes) on validation/test
- Detect collapse early (dominant class ratio and pred\_unique checks)
- In multi-task setups, normalize regression targets before training to avoid loss-scale domination over classification
- Save diagnostics artifacts for each run (range probes, class-space probes, collapse checks)
- If collapse appears, stop downstream interpretability plots until retraining fixes it
- For sentiment tasks, if dominant\_ratio >= 0.98 or pred\_unique <= 1, treat as collapsed and require remediation before final report

### 3) Visualization Reliability

- Configure plotting fonts with explicit local font fallback for Chinese
- Use bilingual fallback labels when Chinese font is unavailable
- Clear stale output directories before rerun to avoid mixing old/new artifacts
- Keep visualization preprocessing exactly aligned with model preprocessing

### 4) Interpretability Validity

- Distinguish response strength from causal contribution
- Prefer contribution-based channel analysis via ablation on correct samples
- Report strategy definitions clearly: random baseline, response-based, contribution-based
- Reject conclusions if model diagnostics indicate unstable or collapsed predictions

### 5) Delivery Gate

- Re-run target scripts and confirm outputs are regenerated
- Validate key files exist (figures + diagnostics + report)
- Ensure report conclusions match current run artifacts, not historical leftovers

## 6) GraphRAG & Zero Hallucination (Strict Mode)

### 1. 证据优先架构 (Evidence-First Architecture)
- **强制执行 Evidence Gate**：在生成任何建议（特别是处方/计划）前，必须确认 RAG 命中了有效的原始知识库片段。
- **字符串级对齐校验**：输出中的引用内容必须通过 `normalize_for_match`（Unicode NFKC 归一化）后，在原始上下文中能找到精确匹配。
- **拒答豁免机制**：如果知识库为空或无证据，必须返回标准的拒答文本（如“知识库中未找到相关内容”），且 auditor 应对此类拒答块进行引用检查豁免。

### 2. 知识库完整性与安全 (KB Integrity & Security)
- **禁用 LLM 实体提取**：在 `STRICT_KB_ONLY` 模式下，严禁使用 LLM 提取图中不存在的实体，防止“长期幻觉”固化到图谱中。
- **全源注入扫描 (InputGuard)**：安全扫描不能仅限于用户 Query，必须覆盖 RAG 召回片段、历史对话、以及 Planner 生成的子任务描述，防止间接 Prompt Injection。
- **Verified Fact 事实锁定**：Profiler 写入的用户事实（如 PB、心率等）必须显式存在于当前 User Query 的原始字符串中，严禁基于 LLM 推测写入。

### 3. 诊断工具同步
- **KB Gap 检测**：任何引擎逻辑的变更（如正则特征、对齐算法）必须同步更新到 `kb_gap_check.py` 等诊断工具中，确保开发环境与生产引擎的判定逻辑 100% 对齐。

## Output Checklist

- Data range and class-space diagnostics present
- No single-class collapse in final model used for analysis
- Chinese text in figures renders correctly or cleanly falls back to English
- Interpretability section includes contribution-based evidence
- **[RAG]** 所有非拒答段落均有 `(证据原文: "...")` 且能通过字符串对齐
- **[Security]** 输入经过 `InputGuard` 扫描且无注入风险
- **[Integrity]** 未写入任何未经用户 Query 证实的 Profiler 事实
- Outputs are from fresh run, not stale cache

