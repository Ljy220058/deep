import os
import urllib.parse
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import gradio as gr
import uvicorn
import warnings

warnings.filterwarnings("ignore", category=UserWarning, message=".*The parameters have been moved from the Blocks constructor.*")

from core_state import BASE_DIR, pick_free_port, UPLOAD_DOCS_DIR
from utils_ui import GITHUB_STYLE, PDF_VIEWER_JS
from module_kb import KBModule
from module_research import ResearchModule
from module_training import TrainingModule

# ==========================================
# FastAPI & Static Files Setup
# ==========================================
app = FastAPI()

# 静态路由: 解决文件名含有特殊字符导致的无法访问问题
@app.get("/pdf_docs/{dir_name}/{file_name:path}")
async def serve_pdf(dir_name: str, file_name: str):
    import urllib.parse
    from fastapi.responses import FileResponse
    from fastapi import HTTPException
    
    file_name = urllib.parse.unquote(file_name)
    
    if dir_name == "uploaded_docs":
        target_dir = UPLOAD_DOCS_DIR
    elif dir_name == "domain_docs":
        target_dir = BASE_DIR / "domain_docs"
    else:
        raise HTTPException(status_code=404, detail="Directory not found")
        
    file_path = target_dir / file_name
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail=f"File not found: {file_name}")
        
    return FileResponse(
        path=file_path, 
        media_type="application/pdf" if file_path.suffix.lower() == ".pdf" else "text/plain",
        headers={"Accept-Ranges": "bytes"}
    )

# ==========================================
# Gradio UI 组装
# ==========================================
kb_module = KBModule()
research_module = ResearchModule()
training_module = TrainingModule()

with gr.Blocks(title="GraphRAG Copilot v2.0", css=GITHUB_STYLE) as demo:
    gr.HTML(f"<script>{PDF_VIEWER_JS}</script>")
    
    # Header Navigation
    gr.HTML("""
    <div class="header-nav">
        <div class="repo-breadcrumb">
            <svg height="24" viewBox="0 0 16 16" width="24" style="fill: var(--text-title);"><path d="M2 2.5A2.5 2.5 0 0 1 4.5 0h8.75a.75.75 0 0 1 .75.75v12.5a.75.75 0 0 1-.75.75h-2.5a.75.75 0 0 1 0-1.5h1.75v-2h-8a1 1 0 0 0-.714 1.7.75.75 0 1 1-1.072 1.05A2.495 2.495 0 0 1 2 11.5Zm10.5-1h-8a1 1 0 0 0-1 1v6.708A2.486 2.486 0 0 1 4.5 9h8ZM5 12.25a.25.25 0 0 1 .25-.25h3.5a.25.25 0 0 1 .25.25v3.25a.25.25 0 0 1-.4.2l-1.45-1.087a.249.249 0 0 0-.3 0L5.4 15.7a.25.25 0 0 1-.4-.2Z"></path></svg>
            <span style="color: var(--primary-color);">trae_projects</span> 
            <span style="color: var(--text-secondary);">/</span> 
            <span>ollama_pro</span>
            <span class="repo-badge" style="margin-left: 8px;">Private</span>
        </div>
        <div style="display: flex; gap: 12px; align-items: center;">
            <div style="font-size: 13px; color: var(--text-secondary); display: flex; align-items: center; gap: 4px;">
                <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: var(--success);"></span>
                Ollama Engine Active
            </div>
            <a href="https://github.com" target="_blank" style="text-decoration: none;">
                <span class="repo-badge" style="cursor: pointer; display: flex; align-items: center; gap: 4px;">
                    <svg height="14" viewBox="0 0 16 16" width="14" style="fill: currentColor;"><path d="M8 0c4.42 0 8 3.58 8 8a8.013 8.013 0 0 1-5.45 7.59c-.4.08-.55-.17-.55-.38 0-.27.01-1.13.01-2.2 0-.75-.25-1.23-.54-1.48 1.78-.2 3.65-.88 3.65-3.95 0-.88-.31-1.59-.82-2.15.08-.2.36-1.02-.08-2.12 0 0-.67-.22-2.2.82-.64-.18-1.32-.27-2-.27-.68 0-1.36.09-2 .27-1.53-1.03-2.2-.82-2.2-.82-.44 1.1-.16 1.92-.08 2.12-.51.56-.82 1.28-.82 2.15 0 3.06 1.86 3.75 3.64 3.95-.23.2-.44.55-.51 1.07-.46.21-1.61.55-2.33-.66-.15-.24-.6-.83-1.23-.82-.67.01-.27.38.01.53.34.19.73.9.82 1.13.16.45.68 1.31 2.69.94 0 .67.01 1.3.01 1.49 0 .21-.15.46-.55.38A7.995 7.995 0 0 1 0 8c0-4.42 3.58-8 8-8Z"></path></svg>
                    Star
                </span>
            </a>
        </div>
    </div>
    """)

    with gr.Tabs() as tabs:
        training_module.build_ui()
        research_module.build_ui()
        kb_module.build_ui()
        
    # ==========================================
    # 跨模块事件绑定
    # ==========================================
    
    # 从图谱构建到探索的交互
    kb_module.graph_build_btn.click(
        research_module.build_graph_ui, 
        outputs=[kb_module.kb_status, training_module.mermaid_output]
    ).then(
        lambda: f"```mermaid\n{graph_engine.generate_mermaid()}\n```",
        outputs=[research_module.mermaid_explorer]
    )
    
    # 初始加载用户画像数据
    demo.load(
        training_module.load_profile_to_ui,
        outputs=[
            training_module.profile_level, training_module.profile_mileage, training_module.profile_goal, training_module.profile_injury, training_module.profile_memory,
            training_module.profile_lthr, training_module.profile_tpace, training_module.pb_800, training_module.pb_1500, training_module.pb_5k, training_module.pb_10k, training_module.pb_half, training_module.pb_full,
            training_module.profile_race_date, training_module.profile_duration,
            training_module.z1_pace, training_module.z2_pace, training_module.z3_pace, training_module.z4_pace, training_module.z5_pace
        ]
    )

demo = demo.queue()
app = gr.mount_gradio_app(app, demo, path="/")

if __name__ == "__main__":
    from core_state import check_ollama_status, DEFAULT_VECTOR_DIR
    from workflow_engine import set_kb_data
    from build_vector_kb import load_vector_kb, retrieve
    import sys
    
    # 初始加载全局知识库
    print("正在加载本地全局知识库 (Hybrid: TF-IDF + BM25)...")
    try:
        chunks, vectorizer, matrix, bm25 = load_vector_kb(DEFAULT_VECTOR_DIR)
        set_kb_data(chunks, vectorizer, matrix, retrieve, bm25=bm25)
        from core_state import global_state
        global_state.chunks = chunks
        global_state.kb_chunks_len = len(chunks)
        print("全局知识库加载成功！")
    except Exception as e:
        print(f"全局知识库加载失败: {e}")
        set_kb_data([], None, None, retrieve)

    port = pick_free_port("127.0.0.1", preferred_port=8000)
    print(f"=========================================")
    print(f"Starting server at http://localhost:{port}")
    print(f"=========================================")
    try:
        with open("uvicorn_log.txt", "w") as f:
            f.write("Starting uvicorn...\n")
        uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")
        with open("uvicorn_log.txt", "a") as f:
            f.write("Uvicorn exited normally.\n")
    except Exception as e:
        with open("uvicorn_log.txt", "a") as f:
            f.write(f"Uvicorn crashed: {e}\n")
