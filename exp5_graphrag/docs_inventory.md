# 实验五：领域方向与文档收集计划（跑步/马拉松备赛 · 丹尼尔斯体系相关）

## 1. 领域方向（Domain）

本项目领域方向确定为：**科学跑步训练与马拉松备赛**，重点覆盖与《丹尼尔斯经典跑步训练法》强相关的知识面：

1. 训练强度与生理指标：VO2max、乳酸阈值、跑步经济性
2. 训练方法：间歇训练、耐力训练、训练负荷与恢复
3. 风险与安全：热相关疾病、运动损伤、过度训练

目标是为后续 RAG/Agent 系统提供“可检索、可引用、可解释”的领域基础材料。

## 2. 文档收集原则（Collection Principles）

1. **可公开获取**：优先选用公开网页内容（百科/政府健康机构/公共医学信息网站）
2. **保留原始载体**：保存为 PDF 原文件（不另存 Markdown），便于保真与复核
3. **可用于文本检索**：后续通过“PDF 文本抽取 → 清洗/切分 → 向量化/索引”形成可检索语料
4. **可追溯**：清单中记录每份 PDF 的来源（URL 或原始下载路径）、主题关键词、文件大小
5. **覆盖面**：至少覆盖 10 篇文档，包含“训练生理 + 训练方法 + 安全风险”三类

## 3. 收集流程（Plan）

1. 确定主题清单（训练生理/训练方法/风险预防）
2. 收集 PDF 原文（论文/训练计划/教材/指南等），统一放入 `domain_docs/`
3. 规范记录“来源/主题/大小”，用于后续抽取与质量控制
4. 执行 PDF 文本抽取（优先文本层抽取；无文本层则 OCR）
5. 将抽取后的文本作为后续 RAG/Agent 的检索语料（可附带页码/章节元数据）

## 4. 文档清单

| ID | 文件名（domain\_docs/）                              | 文档标题（从文件名推断）                 | 来源（URL/原始路径）                                               | 主题关键词                     | 授权/引用说明                              |                    大小 |
| -: | ----------------------------------------------- | ---------------------------------- | ---------------------------------------------------------- | -------------------------- | ------------------------------------- | --------------------: |
| 01 | NKF-Hues-Booklet.pdf                             | NKF Hues Booklet                   | "C:\Users\26318\Downloads\NKF-Hues-Booklet.pdf"             | 跑步健康/补给/指南               | 本地 PDF（请补充来源页面与版权/引用要求）          | 1734.99 KB（1776631 B） |
| 02 | 2016+-+Nutrition+for+Marathon+Running.pdf         | Nutrition for Marathon Running     | "C:\Users\26318\Downloads\2016+-+Nutrition+for+Marathon+Running.pdf" | 跑步营养/补给/马拉松               | 本地 PDF（请补充来源页面与版权/引用要求）          | 213.90 KB（219030 B） |
| 03 | EWM-Training-Guides-Base-Plan.pdf                 | EWM Training Guides Base Plan      | "C:\Users\26318\Downloads\EWM-Training-Guides-Base-Plan.pdf" | 训练计划/基础期/周安排             | 本地 PDF（请补充来源页面与版权/引用要求）          | 22580.76 KB（23122701 B） |
| 04 | Level2꞉Chapter4꞉BasicTrainingMethodology_English.pdf | Basic Training Methodology (English) | "C:\Users\26318\Downloads\Level2꞉Chapter4꞉BasicTrainingMethodology_English.pdf" | 训练方法学/训练原则/周期             | 本地 PDF（请补充来源页面与版权/引用要求）          | 1017.29 KB（1041706 B） |
| 05 | jhse_Vol_8_N_II_350-366.pdf                        | JHSE Vol 8 No II 350-366           | "C:\Users\26318\Downloads\jhse_Vol_8_N_II_350-366.pdf"       | 运动科学/训练研究/论文               | 本地 PDF（请补充来源页面与版权/引用要求）          | 452.29 KB（463142 B） |
| 06 | 36b5639a13f6f78e00f1c2ca46b86e854898.pdf           | Paper (hash-named)                 | "C:\Users\26318\Downloads\36b5639a13f6f78e00f1c2ca46b86e854898.pdf" | 运动科学/待分类                    | 本地 PDF（请补充来源页面与版权/引用要求）          | 1602.31 KB（1640761 B） |
| 07 | Periodization for Massive Strength Gains.pdf       | Periodization for Massive Strength Gains | "C:\Users\26318\Downloads\Periodization for Massive Strength Gains.pdf" | 周期化/力量训练/负荷安排             | 本地 PDF（请补充来源页面与版权/引用要求）          | 224.76 KB（230150 B） |
| 08 | fphys-12-715044.pdf                                | Frontiers in Physiology 12:715044  | "C:\Users\26318\Downloads\fphys-12-715044.pdf"               | 运动生理/训练适应/论文               | 本地 PDF（请补充来源页面与版权/引用要求）          | 816.57 KB（836163 B） |
| 09 | -9787213062605.pdf                                 | Book (ISBN-like)                   | "C:\Users\26318\Downloads\-9787213062605.pdf"                | 跑步/训练/待分类                    | 本地 PDF（请补充来源页面与版权/引用要求）          | 1.40 KB（1436 B） |
| 10 | 10078-60-2017-v60-2017-28.pdf                       | 10078-60-2017-v60-2017-28           | "C:\Users\26318\Downloads\10078-60-2017-v60-2017-28.pdf"     | 运动科学/训练研究/论文               | 本地 PDF（请补充来源页面与版权/引用要求）          | 670.10 KB（686184 B） |
