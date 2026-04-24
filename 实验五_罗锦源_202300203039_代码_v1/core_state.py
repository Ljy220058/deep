import asyncio
import os
import socket
from pathlib import Path

# 全局路径常量
BASE_DIR = Path(__file__).parent.resolve()
DEFAULT_VECTOR_DIR = BASE_DIR / "vector_kb"
UPLOAD_DOCS_DIR = BASE_DIR / "uploaded_docs"
USER_VECTOR_DIR = BASE_DIR / "vector_kb_user"

# 全局知识图谱高亮词
DEFAULT_HIGHLIGHTS = [
    "gradual increment", "maximal values are reached", "lifestyles",
    "quality and efficiency of the training process and competitive performance",
    "prevention programs", "into the training process and competition schedules"
]

# 共享全局状态 (避免循环引用)
class GlobalState:
    def __init__(self):
        self.chunks = []
        self.kb_chunks_len = 0

global_state = GlobalState()

async def check_ollama_status():
    """检查 Ollama 服务是否在线"""
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    host = ollama_url.split("//")[-1].split(":")[0]
    port = int(ollama_url.split(":")[-1])
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout=2.0)
        writer.close()
        await writer.wait_closed()
        return True
    except:
        return False

def pick_free_port(host: str, preferred_port: int | None, max_tries: int = 50) -> int:
    """自动寻找空闲端口"""
    if preferred_port is None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, 0))
            return int(s.getsockname()[1])
    start = int(preferred_port)
    for port in range(start, start + int(max_tries)):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind((host, int(port)))
                return int(port)
        except OSError:
            continue
    raise OSError(f"Cannot find empty port in range: {start}-{start + int(max_tries) - 1}")
