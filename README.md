# Ollama DeepSeek 7B vs 14B 对比程序

这个仓库提供一个简单的对比脚本：对同一套用例，分别调用多个 Ollama 模型，采集耗时与 token 指标，并生成 Markdown/JSON 报告。

## 前置条件

- 本机或远端已启动 Ollama 服务（默认 `http://localhost:11434`）
- 已 `ollama pull` 并安装你要对比的模型（例如 deepseek 7b/14b）

## 快速开始

1) 查看 Ollama 已安装模型（可选）

```bash
python ollama_compare.py --host http://localhost:11434 --list-models
```

2) 运行对比

把 `--models` 替换成你本机真实的模型名称（以 `ollama list`/`--list-models` 为准），例如：

```bash
python ollama_compare.py ^
  --host http://localhost:11434 ^
  --models deepseek-r1:7b deepseek-r1:14b ^
  --suite suites/deepseek_7b_vs_14b.json ^
  --out results
```

运行结束会在控制台输出报告路径（`results/compare_YYYYMMDD_HHMMSS.md`），同时保存原始 JSON（同名 `.json`）。

3) 只检查套件是否可跑（不发请求）

```bash
python ollama_compare.py --models deepseek:7b deepseek:14b --suite suites/deepseek_7b_vs_14b.json --dry-run
```

## 你可以对比什么

- 指令遵循：是否满足“只输出 JSON/只输出 SQL/不超过 N 句”等约束
- 结构化输出：JSON 是否可解析
- 准确性：简单算术/规则性检查（regex/contains）
- 性能：每条用例的总耗时、prompt token、生成 token、生成 tps（根据 Ollama 返回的 eval_duration 估算）

## Prompt 策略对比（Zero-shot / Few-shot / CoT）

使用固定问题对比不同提示策略的表现：

```bash
python prompt_strategy_compare.py --model deepseek-r1:7b
```

可自定义问题与参数：

```bash
python prompt_strategy_compare.py --model deepseek-r1:7b --question "一个班有30人，其中20人会英语，15人会法语，5人两种都会。请问至少会一门语言的人数是多少？" --num_predict 256
```

## 自定义用例套件

用例文件是 JSON，结构示例见 [deepseek_7b_vs_14b.json](file:///C:/Users/26318/Documents/trae_projects/ollama_pro/suites/deepseek_7b_vs_14b.json)。

每个 case 支持：

- `id`, `title`, `prompt`, 可选 `system`
- `checks`: 支持类型
  - `contains` / `not_contains`
  - `regex`
  - `json`（允许把 JSON 放在 ``` 代码块里）
  - `min_words` / `max_words`
  - `max_sentences`
  - `codeblock`（可指定 `language`）

