from langgraph_multi_agent import app

def main():
    try:
        # 生成工作流可视化图
        graph_image = app.get_graph().draw_mermaid_png()
        with open("workflow_graph.png", "wb") as f:
            f.write(graph_image)
        print("工作流图已保存为 workflow_graph.png")
    except Exception as e:
        print(f"生成工作流图时出错: {e}")
        # 如果网络/依赖问题导致png失败，回退保存mermaid代码
        try:
            mermaid_code = app.get_graph().draw_mermaid()
            with open("workflow_graph.mermaid", "w", encoding="utf-8") as f:
                f.write(mermaid_code)
            print("由于PNG生成失败，已回退保存Mermaid代码至 workflow_graph.mermaid")
        except Exception as e2:
            print(f"回退保存Mermaid也失败: {e2}")

if __name__ == "__main__":
    main()