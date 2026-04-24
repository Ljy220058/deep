import argparse
import json
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(r"c:\Users\26318\Documents\trae_projects\ollama_pro\实验五_罗锦源_202300203039_代码_v1\graphrag_project")
PLAN_PATH = PROJECT_ROOT / "output" / "query_experiment_plan.json"
RESULT_PATH = PROJECT_ROOT / "output" / "query_experiment_results.json"

EXPERIMENTS = [
    {
        "name": "global_theme_overview",
        "method": "global",
        "query": "What are the major themes across the corpus about endurance training, nutrition, and performance improvement?",
        "response_type": "List of 5-8 points",
        "purpose": "适合做主题概览，观察跨文档汇总能力"
    },
    {
        "name": "local_fact_lookup",
        "method": "local",
        "query": "What are the reported effects of HIIT and MICT on running economy and VO2max?",
        "response_type": "Bullet list",
        "purpose": "适合做具体事实查询，观察局部证据检索能力"
    }
]


def build_command(experiment):
    return " ".join(
        [
            "python -m graphrag query",
            "--root .",
            f"--method {experiment['method']}",
            f'--query "{experiment["query"]}"',
            f'--response-type "{experiment["response_type"]}"',
        ]
    )


def collect_index_summary():
    output_dir = PROJECT_ROOT / "output"
    return {
        "entities": len(pd.read_parquet(output_dir / "entities.parquet")),
        "relationships": len(pd.read_parquet(output_dir / "relationships.parquet")),
        "communities": len(pd.read_parquet(output_dir / "communities.parquet")),
        "community_reports": len(pd.read_parquet(output_dir / "community_reports.parquet")),
    }


def build_plan():
    index_summary = collect_index_summary()
    experiments = []
    for experiment in EXPERIMENTS:
        experiments.append(
            {
                **experiment,
                "command": build_command(experiment),
                "comparison_focus": "global 更适合跨文档主题归纳；local 更适合围绕具体实体和事实追问",
                "evaluation_dimensions": [
                    "回答粒度",
                    "跨文档综合能力",
                    "具体事实命中率",
                    "是否贴近知识图谱中的实体关系",
                ],
            }
        )
    plan = {
        "project_root": str(PROJECT_ROOT),
        "index_summary": index_summary,
        "experiments": experiments,
    }
    PLAN_PATH.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    return plan


def run_query(experiment):
    return {
        "name": experiment["name"],
        "method": experiment["method"],
        "query": experiment["query"],
        "response_type": experiment["response_type"],
        "purpose": experiment["purpose"],
        "command": build_command(experiment),
    }


def summarize_plan(plan):
    print("GraphRAG 查询实验设计")
    print(f"项目目录: {plan['project_root']}")
    print(
        "索引概况: "
        f"{plan['index_summary']['entities']} 个实体, "
        f"{plan['index_summary']['relationships']} 条关系, "
        f"{plan['index_summary']['communities']} 个社区, "
        f"{plan['index_summary']['community_reports']} 份社区报告"
    )
    for experiment in plan["experiments"]:
        print(f"\n=== {experiment['name']} ===")
        print(f"查询模式: {experiment['method']}")
        print(f"目的: {experiment['purpose']}")
        print(f"问题: {experiment['query']}")
        print(f"命令: {experiment['command']}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()

    plan = build_plan()
    summarize_plan(plan)
    print(f"\n实验设计已保存到: {PLAN_PATH}")

    if args.execute:
        results = [run_query(experiment) for experiment in EXPERIMENTS]
        RESULT_PATH.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"命令清单已保存到: {RESULT_PATH}")


if __name__ == "__main__":
    main()
(f"命令清单已保存到: {RESULT_PATH}")


if __name__ == "__main__":
    main()
