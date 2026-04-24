import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import os

def main():
    output_dir = r"c:\Users\26318\Documents\trae_projects\ollama_pro\实验五_罗锦源_202300203039_代码_v1\graphrag_project\output"
    entities_path = os.path.join(output_dir, "entities.parquet")
    relationships_path = os.path.join(output_dir, "relationships.parquet")
    
    if not os.path.exists(entities_path) or not os.path.exists(relationships_path):
        print("实体或关系数据不存在，请确认 GraphRAG 索引是否已成功生成数据。")
        return

    # 1. 加载数据
    print("加载实体和关系数据...")
    entities_df = pd.read_parquet(entities_path)
    relationships_df = pd.read_parquet(relationships_path)
    
    print(f"共加载了 {len(entities_df)} 个实体, {len(relationships_df)} 条关系。")

    # 2. 构建 NetworkX 图
    print("构建 NetworkX 图...")
    G = nx.Graph()
    
    # 添加节点
    for _, row in entities_df.iterrows():
        G.add_node(row['title'], type=row.get('type', 'Unknown'), description=row.get('description', ''))
        
    # 添加边
    for _, row in relationships_df.iterrows():
        # 如果存在 weight 字段，可以作为边的权重
        weight = row.get('weight', 1.0)
        G.add_edge(row['source'], row['target'], weight=weight, description=row.get('description', ''))
        
    print(f"图构建完成：{G.number_of_nodes()} 个节点, {G.number_of_edges()} 条边。")

    # 3. 计算节点重要性并选择前30个节点
    print("计算节点重要性 (Degree Centrality)...")
    centrality = nx.degree_centrality(G)
    
    # 按中心性排序，取前30
    sorted_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
    top_30_nodes = [node for node, cent in sorted_nodes[:30]]
    
    print("\n--- 最重要的前30个节点 ---")
    for i, (node, cent) in enumerate(sorted_nodes[:30], 1):
        print(f"{i}. {node} (中心性: {cent:.4f})")
        
    # 4. 可视化子图
    print("\n可视化前30个节点及其关联边...")
    subgraph = G.subgraph(top_30_nodes)
    
    plt.figure(figsize=(12, 12))
    pos = nx.spring_layout(subgraph, seed=42)
    
    # 绘制节点
    nx.draw_networkx_nodes(subgraph, pos, node_size=500, node_color='skyblue', alpha=0.8)
    
    # 绘制边
    nx.draw_networkx_edges(subgraph, pos, width=1.0, alpha=0.5, edge_color='gray')
    
    # 绘制标签
    nx.draw_networkx_labels(subgraph, pos, font_size=10, font_family='sans-serif')
    
    plt.title("GraphRAG Knowledge Graph - Top 30 Important Nodes")
    plt.axis('off')
    
    save_path = os.path.join(output_dir, "graph_visualization.png")
    plt.savefig(save_path, bbox_inches='tight', dpi=300)
    print(f"\n可视化图片已保存至: {save_path}")

if __name__ == "__main__":
    main()
