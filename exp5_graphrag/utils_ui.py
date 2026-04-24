import urllib.parse
from datetime import date
from pathlib import Path
from core_state import BASE_DIR

GITHUB_STYLE = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Sans+SC:wght@400;500;700&display=swap');

/* 核心设计系统 - 深色模式标准化 */
:root {
    --primary-color: #165DFF;
    --primary-hover: #0E42D2;
    --primary-active: #0932B3;
    
    --bg-main: #121212;
    --bg-container: #1E1E1E;
    --bg-交互: #2D2D2D;
    --bg-border: #3D3D3D;
    
    --text-title: #FFFFFF;
    --text-body: #CCCCCC;
    --text-secondary: #888888;
    
    --success: #00B42A;
    --warning: #FF7D00;
    --error: #F53F3F;
    --info: #86909C;
    
    --radius-sm: 8px;
    --radius-lg: 12px;
}

/* PDF.js Viewer 样式扩展 */
.pdf-viewer-container {
    display: flex;
    flex-direction: column;
    height: 100%;
    background: #525659;
}

.pdf-toolbar {
    background: #323639;
    padding: 8px 16px;
    display: flex;
    align-items: center;
    gap: 12px;
    color: white;
    box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    z-index: 10;
}

.pdf-toolbar button {
    background: rgba(255,255,255,0.1);
    border: 1px solid rgba(255,255,255,0.2);
    color: white;
    padding: 4px 8px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 12px;
    display: flex;
    align-items: center;
    gap: 4px;
}

.pdf-toolbar button:hover {
    background: rgba(255,255,255,0.2);
}

.pdf-toolbar .page-info {
    font-size: 13px;
    font-family: monospace;
}

.pdf-canvas-wrapper {
    flex-grow: 1;
    overflow: auto;
    padding: 20px;
    display: flex;
    justify-content: center;
    background: #525659;
}

#pdf-render-canvas {
    box-shadow: 0 0 20px rgba(0,0,0,0.5);
    background: white;
    max-width: 100%;
}

.pdf-loading-overlay {
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(0,0,0,0.5);
    display: none;
    align-items: center;
    justify-content: center;
    z-index: 20;
}

.pdf-loading-overlay.active {
    display: flex;
}

/* 实验室报告风格 (Structured Report v2.0) */
.lab-report {
    background-color: var(--bg-container);
    border: 1px solid var(--bg-border);
    border-radius: var(--radius-lg);
    padding: 24px;
    margin: 16px 0;
    color: var(--text-body);
    font-size: 14px;
    line-height: 1.6;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}

.report-header {
    border-bottom: 2px solid var(--primary-color);
    padding-bottom: 16px;
    margin-bottom: 20px;
}

.report-title {
    font-size: 22px;
    font-weight: 700;
    color: var(--text-title);
    margin-bottom: 8px;
    letter-spacing: -0.02em;
}

.report-meta {
    font-size: 12px;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

.report-section {
    margin-bottom: 24px;
}

.section-title {
    font-size: 16px;
    font-weight: 600;
    color: var(--primary-color);
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.section-title::before {
    content: "";
    width: 4px;
    height: 16px;
    background: var(--primary-color);
    border-radius: 2px;
}

.findings-table {
    width: 100%;
    border-collapse: collapse;
    margin: 12px 0;
    border: 1px solid var(--bg-border);
    border-radius: var(--radius-sm);
    overflow: hidden;
}

.findings-table th {
    background: var(--bg-交互);
    color: var(--text-title);
    text-align: left;
    padding: 10px 14px;
    font-weight: 600;
    border-bottom: 1px solid var(--bg-border);
}

.findings-table td {
    padding: 10px 14px;
    border-bottom: 1px solid var(--bg-border);
    color: var(--text-body);
}

.findings-table tr:last-child td {
    border-bottom: none;
}

.audit-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 16px;
    margin-top: 12px;
}

.audit-item {
    background: var(--bg-交互);
    padding: 12px;
    border-radius: var(--radius-sm);
    border: 1px solid var(--bg-border);
}

.audit-label {
    font-size: 12px;
    color: var(--text-secondary);
    margin-bottom: 8px;
}

.progress-container {
    height: 6px;
    background: var(--bg-main);
    border-radius: 3px;
    overflow: hidden;
    margin-bottom: 8px;
}

.progress-bar {
    height: 100%;
    transition: width 0.6s ease;
}

.audit-value {
    font-weight: 700;
    font-size: 18px;
    text-align: right;
}

.evidence-tag {
    display: inline-flex;
    align-items: center;
    padding: 4px 10px;
    background: rgba(22, 93, 255, 0.1);
    border: 1px solid rgba(22, 93, 255, 0.2);
    border-radius: 4px;
    color: var(--primary-color);
    font-size: 12px;
    cursor: pointer;
    margin: 4px;
    transition: all 0.2s;
}

.evidence-tag:hover {
    background: var(--primary-color);
    color: white;
}

/* 性能优化：强制隔离重绘区域，防止 ResizeObserver 导致的递归更新 */
.chatbot-container, .reasoning-terminal, .mermaid-container {
    contain: layout style;
    will-change: transform;
    backface-visibility: hidden;
    transform: translateZ(0);
    overflow: hidden !important; /* 强制隐藏溢出，防止布局抖动 */
}

/* UI 锁定层：彻底防止生成期间的任何交互导致事件堆积 */
.ui-locked-overlay {
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(0,0,0,0.01); /* 几乎透明，但拦截所有点击 */
    z-index: 999999;
    cursor: wait;
    display: none;
    pointer-events: all !important;
}

.ui-locked-overlay.active {
    display: block;
}

.ui-locked-indicator {
    position: fixed;
    top: 12px;
    left: 50%;
    transform: translateX(-50%);
    background: var(--primary-color);
    color: white;
    padding: 6px 16px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    box-shadow: 0 4px 12px rgba(0,0,0,0.5);
    z-index: 1000000;
    display: none;
    align-items: center;
    gap: 8px;
}

.ui-locked-indicator.active {
    display: flex;
}

/* 消息气泡渲染优化：减少重排 */
.chatbot-container .message {
    contain: layout style paint;
    overflow-wrap: break-word;
}

/* 修复 Svelte effect_update_depth_exceeded 错误的全局补丁 */
#gradio-app {
    contain: layout style;
}

/* 导航与 Tab 锁定预防 */
.tabs {
    position: relative;
    z-index: 100;
}

/* 隐藏滚动条抖动 */
.gradio-container {
    scrollbar-gutter: stable;
}

/* 全局基础样式重置 */

.gradio-container {
    background-color: var(--bg-main) !important;
    font-family: 'Inter', 'Noto Sans SC', -apple-system, BlinkMacSystemFont, sans-serif !important;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

/* 强制所有文本颜色符合标准 */
* {
    color-scheme: dark;
}

h1, h2, h3, .title, strong { color: var(--text-title) !important; font-weight: 600; letter-spacing: -0.01em; }
p, span, td, div { color: var(--text-body); }

/* 容器与卡片 */
.github-container { 
    background-color: var(--bg-container) !important; 
    border: 1px solid var(--bg-border) !important; 
    border-radius: var(--radius-lg) !important; 
    padding: 16px; 
    margin-bottom: 16px; 
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    overflow: hidden;
}

.github-header { 
    background-color: var(--bg-交互) !important; 
    border-bottom: 1px solid var(--bg-border); 
    padding: 10px 16px; 
    margin: -16px -16px 16px -16px; 
    border-top-left-radius: var(--radius-lg); 
    border-top-right-radius: var(--radius-lg); 
    font-weight: 600; 
    font-size: 14px;
    display: flex; 
    align-items: center; 
    justify-content: space-between;
    color: var(--text-title) !important;
}

/* 导航栏样式优化 */
.header-nav {
    background-color: var(--bg-container) !important;
    border-bottom: 1px solid var(--bg-border);
    padding: 12px 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}

.repo-breadcrumb {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 18px;
    font-weight: 600;
}

.repo-badge {
    background-color: var(--bg-交互);
    color: var(--text-secondary);
    font-size: 12px;
    padding: 2px 8px;
    border: 1px solid var(--bg-border);
    border-radius: var(--radius-sm);
    font-weight: 500;
}

.mermaid-container {
    background-color: #ffffff !important;
    border: 2px solid var(--bg-border) !important;
    border-radius: var(--radius-lg) !important;
    padding: 10px !important;
    overflow: auto !important;
    min-height: 500px !important;
    width: 100% !important;
    display: block !important;
}

.mermaid-container * {
    color: #000 !important; /* 强制图表内部文本为深色 */
}

/* 消息气泡样式 (GitHub Style) */
.chatbot-container .message-row {
    display: flex;
    flex-direction: column;
    margin-bottom: 24px; /* 增加间距 */
    animation: fadeIn 0.4s ease-out;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
}

.chatbot-container .user {
    align-items: flex-end !important;
}

.chatbot-container .bot {
    align-items: flex-start !important;
}

.chatbot-container .message {
    border-radius: var(--radius-lg) !important;
    padding: 16px 20px !important; /* 默认恢复内边距 */
    font-size: 15px !important;
    line-height: 1.65 !important;
    max-width: 92% !important;
    border: 1px solid var(--bg-border) !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
    background-color: var(--bg-container) !important;
}

/* 教练计划卡片样式 (Coach Plan Card) - 覆盖默认内边距 */
.coach-plan-card {
    display: flex;
    flex-direction: column;
    width: 100%;
    margin: -16px -20px; /* 抵消父容器内边距，实现全铺满效果 */
}

.plan-header-mini {
    background: linear-gradient(90deg, var(--primary-color), var(--primary-hover));
    padding: 10px 18px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid rgba(255,255,255,0.1);
}

.plan-badge {
    font-size: 11px;
    font-weight: 800;
    color: white;
    letter-spacing: 1px;
    background: rgba(0,0,0,0.2);
    padding: 2px 8px;
    border-radius: 4px;
}

.plan-date {
    font-size: 12px;
    color: rgba(255,255,255,0.8);
    font-family: monospace;
}

.plan-content-wrapper {
    padding: 20px 24px;
}

/* Markdown 排版增强 - 移除冗余符号感，增强 UI 模块感 */
.chatbot-container .message p { margin-bottom: 12px; }
.chatbot-container .message p:last-child { margin-bottom: 0; }
.chatbot-container .message strong { color: var(--text-title); font-weight: 600; }
.chatbot-container .message em { color: var(--text-secondary); font-style: italic; }

/* 彻底美化标题：去掉 ## 符号感 */
.chatbot-container .message h1, 
.chatbot-container .message h2, 
.chatbot-container .message h3, 
.chatbot-container .message h4 {
    margin-top: 28px;
    margin-bottom: 16px;
    color: var(--text-title) !important;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 10px;
    border-bottom: none !important;
}

.chatbot-container .message h1::before, 
.chatbot-container .message h2::before {
    content: "";
    width: 4px;
    height: 18px;
    background: var(--primary-color);
    border-radius: 2px;
}

.chatbot-container .message h3::before {
    content: "●";
    color: var(--primary-color);
    font-size: 10px;
}

.chatbot-container .message h1 { font-size: 22px; border-bottom: 1px solid var(--bg-border) !important; padding-bottom: 8px; }
.chatbot-container .message h2 { font-size: 19px; }
.chatbot-container .message h3 { font-size: 16px; color: var(--primary-color) !important; }

/* 表格美化 - 让计划表看起来像专业仪表盘 */
.chatbot-container .message table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    margin: 16px 0;
    border: 1px solid var(--bg-border);
    border-radius: var(--radius-sm);
    overflow: hidden;
}

.chatbot-container .message th {
    background-color: var(--bg-交互);
    color: var(--text-title);
    font-weight: 600;
    text-align: left;
    padding: 12px 16px;
    border-bottom: 1px solid var(--bg-border);
}

.chatbot-container .message td {
    padding: 12px 16px;
    border-bottom: 1px solid var(--bg-border);
    font-size: 14px;
}

.chatbot-container .message tr:last-child td {
    border-bottom: none;
}

.chatbot-container .message tr:hover {
    background-color: rgba(255,255,255,0.02);
}

.chatbot-container .message code {
    background: rgba(255, 255, 255, 0.1);
    padding: 2px 6px;
    border-radius: 4px;
    font-family: 'Consolas', 'Monaco', monospace;
    font-size: 13.5px;
    color: #e6b450;
}

.chatbot-container .message pre {
    background: #0A0A0A;
    padding: 12px;
    border-radius: var(--radius-sm);
    overflow-x: auto;
    border: 1px solid var(--bg-border);
    margin: 12px 0;
}

.chatbot-container .message pre code {
    background: transparent;
    padding: 0;
    color: var(--text-body);
}

.chatbot-container .message blockquote {
    border-left: 4px solid var(--primary-color);
    margin-left: 0;
    padding-left: 12px;
    color: var(--text-secondary);
    background: rgba(22, 93, 255, 0.05);
    padding: 10px 12px;
    border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
}

.chatbot-container .message ul, .chatbot-container .message ol {
    padding-left: 20px;
    margin-bottom: 12px;
}

.chatbot-container .message li {
    margin-bottom: 6px;
}

.chatbot-container .user > .message {
    background-color: var(--primary-color) !important;
    color: white !important;
    border-color: var(--primary-active) !important;
    border-bottom-right-radius: 4px !important;
    box-shadow: 0 4px 12px rgba(22, 93, 255, 0.2) !important;
}

.chatbot-container .bot > .message {
    background-color: var(--bg-交互) !important;
    color: var(--text-body) !important;
    border-color: var(--bg-border) !important;
    border-bottom-left-radius: 4px !important;
}

/* Toast 提示系统 */
#toast-container {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 9999;
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.toast {
    padding: 12px 20px;
    border-radius: var(--radius-sm);
    color: white;
    font-weight: 500;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    animation: slideIn 0.3s ease-out;
    display: flex;
    align-items: center;
    gap: 8px;
    min-width: 200px;
}

.toast-success { background-color: var(--success); }
.toast-error { background-color: var(--error); }
.toast-info { background-color: var(--info); }

@keyframes slideIn {
    from { transform: translateX(100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}

/* 状态组件 */
.github-flash-error { background-color: rgba(245, 63, 63, 0.1); color: var(--error); border: 1px solid var(--error); border-radius: var(--radius-sm); padding: 12px 16px; margin: 8px 0; }
.github-flash-warn { background-color: rgba(255, 125, 0, 0.1); color: var(--warning); border: 1px solid var(--warning); border-radius: var(--radius-sm); padding: 12px 16px; margin: 8px 0; }
.github-token-label { background-color: var(--bg-交互); color: var(--text-body); border-radius: 2em; padding: 2px 10px; font-size: 12px; font-weight: 500; border: 1px solid var(--bg-border); }

/* 日志终端样式 */
.reasoning-terminal { 
    background-color: #0A0A0A; 
    color: var(--text-body); 
    font-family: 'Consolas', 'Monaco', monospace; 
    padding: 16px; 
    border-radius: var(--radius-lg); 
    font-size: 13px; 
    line-height: 1.6; 
    overflow-x: auto;
    border: 1px solid var(--bg-border);
    min-height: 100px;
    position: relative;
}

.reasoning-terminal::before {
    content: "TERMINAL - PROCESS LOG";
    display: block;
    font-size: 10px;
    color: var(--text-secondary);
    margin-bottom: 10px;
    padding-bottom: 8px;
    border-bottom: 1px dashed var(--bg-border);
    letter-spacing: 1px;
}

.reasoning-terminal span {
    animation: typeIn 0.2s ease-out;
}

@keyframes typeIn {
    from { opacity: 0; transform: translateX(-4px); }
    to { opacity: 1; transform: translateX(0); }
}

/* Pipeline 进度条样式 (垂直步骤条) */
.pipeline-container {
    display: flex;
    flex-direction: column;
    gap: 0;
    padding: 10px 5px;
}

.pipeline-item {
    display: flex;
    align-items: flex-start;
    gap: 16px;
    position: relative;
    padding-bottom: 24px;
    transition: all 0.4s ease;
}

.pipeline-item:not(:last-child)::after {
    content: "";
    position: absolute;
    left: 9px;
    top: 24px;
    bottom: 0;
    width: 2px;
    background-color: var(--bg-border);
    transition: background-color 0.5s ease;
}

.pipeline-item.completed:not(:last-child)::after {
    background-color: var(--success);
}

.pipeline-item.active:not(:last-child)::after {
    background: linear-gradient(to bottom, var(--primary-color) 0%, var(--bg-border) 100%);
    background-size: 100% 200%;
    animation: flowDown 2s infinite linear;
}

@keyframes flowDown {
    0% { background-position: 0% -100%; }
    100% { background-position: 0% 100%; }
}

.pipeline-icon {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: var(--bg-main);
    border: 2px solid var(--bg-border);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1;
    margin-top: 2px;
    transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.pipeline-item.active .pipeline-icon {
    border-color: var(--primary-color);
    color: var(--primary-color);
    box-shadow: 0 0 12px rgba(22, 93, 255, 0.6), inset 0 0 4px rgba(22, 93, 255, 0.3);
    animation: activePulse 2s infinite;
    transform: scale(1.15);
}

@keyframes activePulse {
    0% { box-shadow: 0 0 0 0 rgba(22, 93, 255, 0.5), inset 0 0 4px rgba(22, 93, 255, 0.3); }
    70% { box-shadow: 0 0 0 12px rgba(22, 93, 255, 0), inset 0 0 4px rgba(22, 93, 255, 0); }
    100% { box-shadow: 0 0 0 0 rgba(22, 93, 255, 0), inset 0 0 4px rgba(22, 93, 255, 0.3); }
}

.pipeline-item.completed .pipeline-icon {
    border-color: var(--success);
    background: var(--success);
    color: white;
    transform: scale(1.05);
}

.pipeline-item.completed .pipeline-icon::after {
    content: "✓";
    font-size: 12px;
    font-weight: bold;
}

.pipeline-label {
    font-size: 14px;
    color: var(--text-secondary);
    font-weight: 400;
}

.pipeline-item.active .pipeline-label {
    color: var(--primary-color) !important;
    font-weight: 600;
}

.pipeline-item.completed .pipeline-label {
    color: var(--text-title) !important;
}

/* 输入框与按钮交互 */
#input-box textarea {
    background-color: var(--bg-交互) !important;
    border: 1px solid var(--bg-border) !important;
    border-radius: var(--radius-lg) !important;
    color: var(--text-title) !important;
    padding: 12px 16px !important;
}
#input-box textarea:focus {
    border-color: var(--primary-color) !important;
    box-shadow: 0 0 0 2px rgba(22, 93, 255, 0.2) !important;
}

.primary-btn {
    background-color: var(--primary-color) !important;
    color: white !important;
    border-radius: var(--radius-lg) !important;
    transition: all 0.2s;
    font-weight: 600 !important;
}
.primary-btn:hover { 
    background-color: var(--primary-hover) !important;
    transform: translateY(-1px);
}
.primary-btn:active { 
    background-color: var(--primary-active) !important;
    transform: translateY(0);
}

/* 表格样式增强 */
.table-row:hover {
    background-color: var(--bg-交互) !important;
}

.delete-btn:hover {
    color: var(--error) !important;
    background-color: rgba(245, 63, 63, 0.1) !important;
    border-radius: 4px;
}

/* 上传区 Hover 态 */
.gradio-container .upload-container:hover {
    border-color: var(--primary-color) !important;
    background-color: rgba(22, 93, 255, 0.05) !important;
}

/* 代码块输入框风格 */
.code-style-input textarea {
    font-family: 'Consolas', monospace !important;
    background-color: var(--bg-main) !important;
    font-size: 13px !important;
}

/* PDF 预览与侧边栏 */
.side-panel-container {
    gap: 16px;
    min-height: 700px;
}

#pdf-side-panel {
    display: none;
    width: 0;
    border: 1px solid var(--bg-border);
    border-radius: var(--radius-lg);
    background: var(--bg-container);
    overflow: hidden;
    flex-direction: column;
    transition: width 0.3s ease;
}

#pdf-side-panel.open {
    display: flex;
    width: 45%;
}

.panel-header {
    padding: 12px 16px;
    background: var(--bg-交互);
    border-bottom: 1px solid var(--bg-border);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

@keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(22, 93, 255, 0.4); }
    70% { box-shadow: 0 0 0 10px rgba(22, 93, 255, 0); }
    100% { box-shadow: 0 0 0 0 rgba(22, 93, 255, 0); }
}

.spinner {
    width: 12px;
    height: 12px;
    border: 2px solid transparent;
    border-top-color: currentColor;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}
"""

PDF_VIEWER_JS = """
function initPdfViewer() {
    console.log("Initializing High-Fidelity PDF.js Viewer...");
    
    // 初始化 PDF.js
    if (typeof pdfjsLib === 'undefined') {
        const script = document.createElement('script');
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js';
        script.onload = () => {
            pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
        };
        document.head.appendChild(script);
    }

    // 修复 Svelte/Gradio 的 ResizeObserver 递归循环错误
    window.addEventListener('error', e => {
        if (e.message === 'ResizeObserver loop limit exceeded' || e.message.includes('effect_update_depth_exceeded')) {
            const resizeObserverErrDiv = document.getElementById('resize-observer-err');
            if (!resizeObserverErrDiv) {
                console.warn("Caught Svelte recursion error, suppressing to prevent UI freeze.");
                e.stopImmediatePropagation();
            }
        }
    });

    window.addEventListener('unhandledrejection', e => {
        if (e.reason && (e.reason.message === 'ResizeObserver loop limit exceeded' || e.reason.message?.includes('effect_update_depth_exceeded'))) {
            e.stopImmediatePropagation();
        }
    });

    // 全局 UI 锁定控制器
    window.toggleUILock = function(locked) {
        if (!document.getElementById("ui-lock-overlay")) {
            const overlay = document.createElement("div");
            overlay.id = "ui-lock-overlay";
            overlay.className = "ui-locked-overlay";
            document.body.appendChild(overlay);
            
            const indicator = document.createElement("div");
            indicator.id = "ui-lock-indicator";
            indicator.className = "ui-locked-indicator";
            indicator.innerHTML = `<div class="spinner"></div><span>AI is generating, interaction limited...</span>`;
            document.body.appendChild(indicator);
        }
        
        const overlay = document.getElementById("ui-lock-overlay");
        const indicator = document.getElementById("ui-lock-indicator");
        
        if (locked) {
            overlay.classList.add("active");
            indicator.classList.add("active");
            console.log("UI LOCKED: AI Processing Started");
        } else {
            overlay.classList.remove("active");
            indicator.classList.remove("active");
            console.log("UI UNLOCKED: AI Processing Completed");
        }
    };

    let pdfDoc = null,
        pageNum = 1,
        pageRendering = false,
        pageNumPending = null,
        scale = 1.5,
        canvas = null,
        ctx = null;

    function renderPage(num) {
        pageRendering = true;
        document.querySelector('.pdf-loading-overlay')?.classList.add('active');

        pdfDoc.getPage(num).then((page) => {
            const viewport = page.getViewport({ scale: scale });
            canvas.height = viewport.height;
            canvas.width = viewport.width;

            const renderContext = {
                canvasContext: ctx,
                viewport: viewport
            };
            const renderTask = page.render(renderContext);

            renderTask.promise.then(() => {
                pageRendering = false;
                document.querySelector('.pdf-loading-overlay')?.classList.remove('active');
                if (pageNumPending !== null) {
                    renderPage(pageNumPending);
                    pageNumPending = null;
                }
            });
        });

        document.getElementById('page_num').textContent = num;
    }

    function queueRenderPage(num) {
        if (pageRendering) {
            pageNumPending = num;
        } else {
            renderPage(num);
        }
    }

    function onPrevPage() {
        if (pageNum <= 1) return;
        pageNum--;
        queueRenderPage(pageNum);
    }

    function onNextPage() {
        if (pageNum >= pdfDoc.numPages) return;
        pageNum++;
        queueRenderPage(pageNum);
    }

    function onZoomIn() {
        scale += 0.2;
        renderPage(pageNum);
    }

    function onZoomOut() {
        if (scale <= 0.5) return;
        scale -= 0.2;
        renderPage(pageNum);
    }

    // 初始化 Toast 容器
    if (!document.getElementById("toast-container")) {
        const toastContainer = document.createElement("div");
        toastContainer.id = "toast-container";
        document.body.appendChild(toastContainer);
    }

    window.showToast = function(message, type = "info") {
        const container = document.getElementById("toast-container");
        const toast = document.createElement("div");
        toast.className = `toast toast-${type}`;
        let icon = type === "success" ? "✅ " : (type === "error" ? "❌ " : "ℹ️ ");
        toast.innerHTML = `<span>${icon}${message}</span>`;
        container.appendChild(toast);
        setTimeout(() => {
            toast.style.opacity = "0";
            toast.style.transform = "translateX(100%)";
            toast.style.transition = "all 0.3s ease";
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    };

    const checkExist = setInterval(function() {
        const workspaceRow = document.querySelector('.side-panel-container');
        if (workspaceRow) {
            clearInterval(checkExist);
            
            if (!document.getElementById("pdf-side-panel")) {
                const panelHtml = `
                    <div id="pdf-side-panel">
                        <div class="panel-header">
                            <span style="font-weight:600; font-size:12px; color:var(--text-title);">DOCUMENT PREVIEW (PDF.js)</span>
                            <span id="panel-close" style="cursor:pointer; font-size:18px; color:var(--text-title);">&times;</span>
                        </div>
                        <div class="pdf-viewer-container">
                            <div class="pdf-toolbar">
                                <button id="prev_page">Prev</button>
                                <button id="next_page">Next</button>
                                <span class="page-info">Page: <span id="page_num"></span> / <span id="page_count"></span></span>
                                <button id="zoom_out">-</button>
                                <button id="zoom_in">+</button>
                                <button id="download_pdf">Open Raw</button>
                            </div>
                            <div class="pdf-canvas-wrapper">
                                <div class="pdf-loading-overlay"><div class="spinner"></div></div>
                                <canvas id="pdf-render-canvas"></canvas>
                            </div>
                        </div>
                    </div>
                `;
                workspaceRow.insertAdjacentHTML('beforeend', panelHtml);
                
                document.getElementById("panel-close").onclick = () => {
                    document.getElementById("pdf-side-panel").classList.remove("open");
                };

                canvas = document.getElementById('pdf-render-canvas');
                ctx = canvas.getContext('2d');

                document.getElementById('prev_page').onclick = onPrevPage;
                document.getElementById('next_page').onclick = onNextPage;
                document.getElementById('zoom_in').onclick = onZoomIn;
                document.getElementById('zoom_out').onclick = onZoomOut;
            }
        }
    }, 500);

    // 全局点击拦截
    if (!window.pdfLinkHandlerBound) {
        document.addEventListener('click', function(e) {
            let target = e.target.closest('.pdf-link');
            let isMarkdownLink = false;
            
            if (!target) {
                target = e.target.closest('a');
                if (target && target.href && (target.href.includes('/pdf_docs/') || target.getAttribute('href')?.startsWith('/pdf_docs/'))) {
                    isMarkdownLink = true;
                } else {
                    target = null;
                }
            }

            if (target) {
                e.preventDefault();
                let src = "";
                let page = 1;

                if (isMarkdownLink) {
                    const href = target.getAttribute('href') || target.href;
                    const fileMatch = href.match(/(\/pdf_docs\/)([^#?]+)/);
                    if (fileMatch) {
                        src = fileMatch[1] + fileMatch[2];
                        const pageMatch = href.match(/#page=(\d+)/);
                        if (pageMatch) page = parseInt(pageMatch[1]);
                    }
                } else {
                    src = target.getAttribute('data-src');
                    page = parseInt(target.getAttribute('data-page') || "1");
                }
                
                if (!src) return;

                try {
                    const parts = src.split('/');
                    const filename = parts.pop();
                    src = parts.join('/') + '/' + encodeURIComponent(decodeURIComponent(filename));
                } catch(e) { console.error("URL encoding error:", e); }

                console.log("PDF Viewer fetching:", src, "at page:", page);

                const panel = document.getElementById("pdf-side-panel");
                if (panel) {
                    panel.classList.add("open");
                    pageNum = page;
                    
                    document.getElementById('download_pdf').onclick = () => window.open(src, '_blank');

                    pdfjsLib.getDocument(src).promise.then((pdfDoc_) => {
                        pdfDoc = pdfDoc_;
                        document.getElementById('page_count').textContent = pdfDoc.numPages;
                        renderPage(pageNum);
                        if (window.showToast) window.showToast("PDF Loaded Successfully", "success");
                    }).catch(err => {
                        console.error("PDF.js load error:", err);
                        if (window.showToast) window.showToast("Failed to load PDF: " + err.message, "error");
                    });
                }
            }
        }, false); // 修改为冒泡阶段，减少对 Gradio 内部事件的干扰
        window.pdfLinkHandlerBound = true;
    }

    window.deleteFile = function(filePath) {
        if (confirm("Are you sure you want to delete this file?")) {
            const deleteInput = document.querySelector('#delete-file-input textarea');
            const deleteBtn = document.querySelector('#delete-file-btn');
            if (deleteInput && deleteBtn) {
                deleteInput.value = filePath;
                deleteInput.dispatchEvent(new Event('input', { bubbles: true }));
                setTimeout(() => deleteBtn.click(), 100);
            }
        }
    };

    window.askQuestion = function(text) {
        const input = document.querySelector('#input-box textarea');
        const sendBtn = document.querySelector('.primary-btn');
        if (input && sendBtn) {
            input.value = text;
            input.dispatchEvent(new Event('input', { bubbles: true }));
            setTimeout(() => sendBtn.click(), 100);
        }
    };

    // 新增：Mermaid 节点点击交互
    if (!window.mermaidClickHandlerBound) {
        let lastClickTime = 0;
        document.addEventListener('click', function(e) {
            // 节流处理，防止高频触发
            const now = Date.now();
            if (now - lastClickTime < 500) return;
            
            const node = e.target.closest('.node') || e.target.closest('.cluster');
            if (node) {
                lastClickTime = now;
                const label = node.querySelector('.nodeLabel') || node.querySelector('text');
                if (label) {
                    const entityName = label.textContent.trim();
                    console.log("Mermaid Node Clicked:", entityName);
                    
                    // 自动切换到 Graph Explorer 标签页并执行搜索
                    const tabs = document.querySelectorAll('.tabs button');
                    for (let tab of tabs) {
                        if (tab.textContent.includes('Graph Explorer')) {
                            tab.click();
                            setTimeout(() => {
                                const searchInput = document.querySelector('#tab_graph input[type="text"]');
                                const searchBtn = document.querySelector('#tab_graph button.primary');
                                if (searchInput && searchBtn) {
                                    searchInput.value = entityName;
                                    searchInput.dispatchEvent(new Event('input', { bubbles: true }));
                                    searchBtn.click();
                                }
                            }, 300);
                            break;
                        }
                    }
                }
            }
        }, false); // 修改为冒泡阶段
        window.mermaidClickHandlerBound = true;
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPdfViewer);
} else {
    initPdfViewer();
}
"""

class UIHelper:
    @staticmethod
    def generate_pipeline_html(active_node=None):
        steps = [
            ("router", "Router"),
            ("profiler", "User Profile"),
            ("entity_extraction", "KG Extraction"),
            ("coach", "Plan Generation"),
            ("therapist", "Safety Review"),
            ("auditor", "Final Auditor")
        ]
        
        normalized_active = active_node
        if active_node in ["planner", "executor", "adaptive_coach"]:
            normalized_active = "coach"
        elif active_node == "nutritionist":
            normalized_active = "therapist" 
        elif active_node == "formatter":
            normalized_active = "auditor" 
            
        active_idx = len(steps) # 默认都不 active
        for i, (node_id, _) in enumerate(steps):
            if node_id == normalized_active:
                active_idx = i
                break
        
        html = '<div class="pipeline-container">'
        for i, (node_id, label) in enumerate(steps):
            status_class = ""
            icon_content = ""
            
            if i < active_idx:
                status_class = "completed"
                icon_content = '<svg height="12" viewBox="0 0 16 16" width="12" style="fill: white;"><path d="M13.78 4.22a.75.75 0 0 1 0 1.06l-7.25 7.25a.75.75 0 0 1-1.06 0L2.22 9.28a.75.75 0 0 1 1.06-1.06L6 10.94l6.72-6.72a.75.75 0 0 1 1.06 0Z"></path></svg>'
            elif i == active_idx:
                status_class = "active"
                icon_content = '<div class="spinner"></div>'
            else:
                status_class = "pending"
                icon_content = ""
                
            html += f"""
            <div class="pipeline-item {status_class}">
                <div class="pipeline-icon">{icon_content}</div>
                <div class="pipeline-label">{label}</div>
            </div>
            """
        html += '</div>'
        return html

    @staticmethod
    def generate_token_html(tokens, roi_score=0):
        p = tokens.get("Prompt", 0)
        c = tokens.get("Completion", 0)
        t = tokens.get("Total", 0)
        
        roi_val = 0
        if t > 0:
            roi_val = (roi_score / t) * 1000
            
        roi_color = "var(--success)" if roi_val > 50 else "var(--warning)" if roi_val > 20 else "var(--error)"
        
        return f"""<div style='display: flex; gap: 8px; flex-wrap: wrap; margin-top: 12px;'>
<div class='github-token-label' title='Prompt Tokens'>P: {p}</div>
<div class='github-token-label' title='Completion Tokens'>C: {c}</div>
<div class='github-token-label' style='background-color: var(--bg-交互); border-color: var(--primary-color); color: var(--text-title); font-weight: 600;' title='Total Tokens'>Total: {t}</div>
<div class='github-token-label' style='background-color: {roi_color}22; border-color: {roi_color}; color: {roi_color}; font-weight: 700;' title='Token ROI (Score/1k Tokens)'>ROI: {roi_val:.1f}</div>
</div>"""

    @staticmethod
    def render_structured_report(structured_report, final_report):
        if not structured_report:
            # 改进：在包装前，对 final_report 进行预处理，确保 Markdown 渲染不会带入原始符号
            # 我们通过 CSS 伪元素来美化，但如果渲染器有问题，我们可以手动替换一些明显的符号
            clean_report = final_report
            if clean_report:
                # 移除开头的 ## 或 ###，因为卡片已经有了标题感
                import re
                clean_report = re.sub(r'^#+\s+.*?\n', '', clean_report, flags=re.MULTILINE)
                
            return f"""<div class="coach-plan-card">
<div class="plan-header-mini">
    <div class="plan-badge">AI COACH PLAN</div>
    <div class="plan-date">{date.today().strftime('%Y-%m-%d')}</div>
</div>
<div class="plan-content-wrapper">

{clean_report}

</div>
</div>"""
        
        meta = structured_report.get("report_metadata", {})
        html = f"""<div class="lab-report">
<div class="report-header">
<div class="report-title">{meta.get('title', 'Professional Analysis Report')}</div>
<div class="report-meta">Version: {meta.get('version', '2.0')} | Protocol: JSON v2.0</div>
</div>"""
        
        framework = structured_report.get("analysis_framework", {})
        if framework:
            entities = framework.get('key_entities', [])
            entity_badges = "".join([f'<span class="repo-badge" style="margin-right:4px; color:var(--primary-color)">{e}</span>' for e in entities])
            
            graph_ctx = framework.get('graph_context', '')
            graph_html = ""
            if graph_ctx:
                graph_html = f"""<div style="margin-top:12px; padding:10px; background:rgba(0,188,212,0.05); border:1px solid rgba(0,188,212,0.2); border-radius:var(--radius-sm); font-size:12px;">
<div style="color:#00bcd4; font-weight:600; margin-bottom:4px; display:flex; align-items:center; gap:4px;">
<svg height="12" viewBox="0 0 16 16" width="12" style="fill:currentColor;"><path d="M1.75 1A1.75 1.75 0 0 0 0 2.75v10.5C0 14.216.784 15 1.75 15h12.5A1.75 1.75 0 0 0 16 13.25v-8.5A1.75 1.75 0 0 0 14.25 3h-5.71l-.745-1.117A1.75 1.75 0 0 0 6.31 1H1.75Z"></path></svg>
KG Traversal Path
</div>
<div style="white-space:pre-wrap;">{graph_ctx}</div>
</div>"""
            
            html += f"""<div class="report-section">
<div class="section-title">Analysis Framework</div>
<div style="background:var(--bg-交互); padding:12px; border-radius:var(--radius-sm); border:1px solid var(--bg-border);">
<div style="margin-bottom:8px;"><strong>Query:</strong> {framework.get('query', '')}</div>
<div><strong>Key Entities:</strong> {entity_badges}</div>
{graph_html}
</div>
</div>"""
        
        steps = structured_report.get("execution_steps", [])
        if steps:
            html += '<div class="report-section"><div class="section-title">Execution Steps & Findings</div>'
            for step in steps:
                html += f"""<div style="margin-bottom:16px; border-left:2px solid var(--bg-border); padding-left:16px;">
<div style="font-weight:600; color:var(--text-title); margin-bottom:4px;">{step.get('task_id', 'TASK')}: {step.get('objective', '')}</div>"""
                
                findings = step.get("findings", {})
                if findings:
                    html += '<table class="findings-table"><thead><tr><th>Parameter</th><th>Value</th></tr></thead><tbody>'
                    for k, v in findings.items():
                        html += f'<tr><td>{k}</td><td>{v}</td></tr>'
                    html += '</tbody></table>'
                
                mechanisms = step.get("mechanisms", [])
                if mechanisms:
                    mech_items = "".join([f"<li><strong>{m.get('factor', '')}</strong>: {m.get('effect', '')}</li>" for m in mechanisms])
                    html += f'<div style="font-size:13px; color:var(--text-secondary); margin:8px 0;"><ul>{mech_items}</ul></div>'
                
                if step.get("conclusion"):
                    html += f'<div style="font-style:italic; color:var(--success); font-size:13px;">Conclusion: {step.get("conclusion")}</div>'
                
                html += '</div>'
            html += '</div>'
        
        audit = structured_report.get("audit_block", {})
        if audit:
            scores = audit.get("scores", {})
            html += '<div class="report-section"><div class="section-title">Audit & Verification</div><div class="audit-grid">'
            for label, score in scores.items():
                color = "var(--success)" if score >= 80 else "var(--warning)" if score >= 60 else "var(--error)"
                html += f"""<div class="audit-item">
<div class="audit-label">{label.upper()}</div>
<div class="progress-container">
<div class="progress-bar" style="width: {score}%; background-color: {color};"></div>
</div>
<div class="audit-value" style="color: {color};">{score}%</div>
</div>"""
            html += '</div>'
            html += f"""<div style="margin-top:12px; padding:12px; background:rgba(0,180,42,0.05); border:1px solid rgba(0,180,42,0.2); border-radius:var(--radius-sm);">
<div style="display:flex; align-items:center; gap:8px; margin-bottom:4px;">
<span class="repo-badge" style="background:var(--success); color:white; border:none;">{audit.get('verdict', 'PASS')}</span>
<strong style="color:var(--text-title)">Audit Summary</strong>
</div>
<div style="font-size:13px;">{audit.get('summary', '')}</div>
</div></div>"""
            
        evidence = structured_report.get("evidence_base", [])
        if evidence:
            html += '<div class="report-section"><div class="section-title">Evidence Base (Interactive)</div><div style="display:flex; flex-wrap:wrap; gap:8px;">'
            for ev in evidence:
                doc = ev.get("document", "")
                pages = ev.get("pages", [1])
                
                doc_dir = ""
                if (BASE_DIR / "uploaded_docs" / doc).exists():
                    doc_dir = "uploaded_docs"
                elif (BASE_DIR / "domain_docs" / doc).exists():
                    doc_dir = "domain_docs"
                
                encoded_doc = urllib.parse.quote(doc, safe='')
                if doc_dir:
                    rel_path = f"/pdf_docs/{doc_dir}/{encoded_doc}"
                else:
                    rel_path = f"/pdf_docs/domain_docs/{encoded_doc}" 
                
                for p in pages:
                    html += f'<span class="pdf-link evidence-tag" data-src="{rel_path}" data-page="{p}">📄 {doc} (P.{p})</span>'
            html += '</div></div>'
            
        html += "</div>"
        return html

    @staticmethod
    def render_reasoning_flow_md(entities: list, graph_ctx: str) -> str:
        """渲染结构化推理流 Markdown (替代 Mermaid)"""
        if not entities:
            return "> 🔍 **未识别到核心实体，执行通用检索**"
            
        # 1. 实体识别部分
        entity_str = " | ".join([f"`{e}`" for e in entities])
        md = f"### 🧩 逻辑推理链\n\n**1. 核心实体提取**\n> {entity_str}\n\n"
        
        # 2. 知识关联部分
        if graph_ctx:
            # 将 graph_ctx 中的列表项转换为更美观的展示
            lines = graph_ctx.split("\n")
            # 兼容处理：如果第一行是标题，则跳过
            start_idx = 1 if lines and "关联逻辑" in lines[0] else 0
            
            md += "**2. 知识图谱关联分析**\n"
            found_rel = False
            for line in lines[start_idx:]:
                if line.strip():
                    # 尝试美化关系箭头：将 --(rel)--> 转换为 ➔ *rel* ➔
                    clean_line = line.strip().lstrip("- ").replace("--(", " ➔ *").replace(")--", "* ➔ ")
                    md += f"- {clean_line}\n"
                    found_rel = True
            
            if not found_rel:
                md += "- 💡 发现独立实体，正在检索相关文档分片...\n"
        else:
            md += "**2. 知识图谱关联分析**\n- ⚠️ 未在本地图谱中发现直接关联，已切换至全局语义检索。\n"
            
        md += "\n---\n"
        return md

    @staticmethod
    def render_reasoning_flow_md(entities: list, graph_ctx: str) -> str:
        """渲染结构化推理流 Markdown (替代 Mermaid)"""
        if not entities:
            return "> 🔍 **未识别到核心实体，执行通用检索**"
            
        # 1. 实体识别部分
        entity_str = " | ".join([f"`{e}`" for e in entities])
        md = f"### 🧩 逻辑推理链\n\n**1. 核心实体提取**\n> {entity_str}\n\n"
        
        # 2. 知识关联部分
        if graph_ctx:
            # 将 graph_ctx 中的列表项转换为更美观的展示
            lines = graph_ctx.split("\n")
            # 兼容处理：如果第一行是标题，则跳过
            start_idx = 1 if lines and "关联逻辑" in lines[0] else 0
            
            md += "**2. 知识图谱关联分析**\n"
            found_rel = False
            for line in lines[start_idx:]:
                if line.strip():
                    # 尝试美化关系箭头：将 --(rel)--> 转换为 ➔ *rel* ➔
                    clean_line = line.strip().lstrip("- ").replace("--(", " ➔ *").replace(")--", "* ➔ ")
                    md += f"- {clean_line}\n"
                    found_rel = True
            
            if not found_rel:
                md += "- 💡 发现独立实体，正在检索相关文档分片...\n"
        else:
            md += "**2. 知识图谱关联分析**\n- ⚠️ 未在本地图谱中发现直接关联，已切换至全局语义检索。\n"
            
        md += "\n---\n"
        return md

    @staticmethod
    def generate_token_md(tokens, roi_score=0):
        p = tokens.get("Prompt", 0)
        c = tokens.get("Completion", 0)
        t = tokens.get("Total", 0)
        
        roi_val = 0
        if t > 0:
            roi_val = (roi_score / t) * 1000
            
        roi_emoji = "✅" if roi_val > 50 else "⚠️" if roi_val > 20 else "❌"
        
        return f"""**📊 资源消耗统计 (Markdown 版)**
| 类型 | 数量 (Tokens) |
| :--- | :--- |
| 📥 Prompt | {p} |
| 📤 Completion | {c} |
| 💎 **Total** | **{t}** |
| {roi_emoji} **Token ROI** | **{roi_val:.1f}** (Score/1k) |
"""

    @staticmethod
    def render_build_summary_md(meta):
        """生成用户友好的知识库构建摘要 (Markdown)"""
        if not meta:
            return "### ❌ 构建失败\n未能获取到构建元数据。"
        
        total_chunks = meta.get("chunks", 0)
        files = meta.get("files", [])
        
        # 统计成功和失败
        success_files = [f for f in files if "error" not in f]
        error_files = [f for f in files if "error" in f]
        
        md = "### ✅ 知识库索引构建完成\n\n"
        md += f"- **总分片数 (Chunks)**: `{total_chunks}`\n"
        md += f"- **成功处理文件**: `{len(success_files)}` 个\n"
        if error_files:
            md += f"- **异常文件**: `{len(error_files)}` 个\n"
        
        md += "\n#### 📄 处理详情 (File Stats)\n\n"
        md += "| 文件名 | 页数 | 分片数 | 状态 |\n"
        md += "| :--- | :--- | :--- | :--- |\n"
        
        # 为了简洁，如果文件太多，只展示前 15 个
        display_files = files[:15]
        for f in display_files:
            name = f.get("source_file", "未知")
            pages = f.get("pages", 0)
            chunks = f.get("chunks", 0)
            status = "✅ 成功" if "error" not in f else f"❌ 失败: {f['error']}"
            md += f"| `{name}` | {pages} | {chunks} | {status} |\n"
            
        if len(files) > 15:
            md += f"| ... | ... | ... | *(还有 {len(files)-15} 个文件未列出)* |\n"
            
        md += "\n> **提示**: 向量数据库 (ChromaDB) 已在后台自动加载并持久化。您可以开始提问了。"
        return md

    @staticmethod
    def dict_to_md(data, title="Metadata"):
        if not data:
            return ""
        
        md = f"### 📄 {title}\n\n"
        
        import json
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                md += f"- **{k}**:\n```json\n{json.dumps(v, indent=2, ensure_ascii=False)}\n```\n"
            else:
                md += f"- **{k}**: {v}\n"
        
        return md

    @staticmethod
    def render_structured_report_md(structured_report, final_report):
        if not structured_report:
            return f"### 📄 Final Analysis Report\n\n{final_report}"
            
        meta = structured_report.get("report_metadata", {})
        md = f"# {meta.get('title', 'Professional Analysis Report')}\n"
        md += f"> Version: {meta.get('version', '2.0')} | Protocol: JSON v2.0\n\n"
        
        framework = structured_report.get("analysis_framework", {})
        if framework:
            md += "## 🔬 Analysis Framework\n"
            md += f"- **Query:** {framework.get('query', '')}\n"
            entities = framework.get('key_entities', [])
            md += f"- **Key Entities:** {', '.join([f'`{e}`' for e in entities])}\n"
            graph_ctx = framework.get('graph_context', '')
            if graph_ctx:
                md += f"- **KG Traversal Path:**\n```text\n{graph_ctx}\n```\n"
            md += "\n"
            
        steps = structured_report.get("execution_steps", [])
        if steps:
            md += "## 🚀 Execution Steps & Findings\n"
            for step in steps:
                md += f"### {step.get('task_id', 'TASK')}: {step.get('objective', '')}\n"
                findings = step.get("findings", {})
                if findings:
                    md += "| Parameter | Value |\n| :--- | :--- |\n"
                    for k, v in findings.items():
                        md += f"| {k} | {v} |\n"
                    md += "\n"
                
                mechanisms = step.get("mechanisms", [])
                if mechanisms:
                    md += "**Key Mechanisms:**\n"
                    for m in mechanisms:
                        md += f"- **{m.get('factor', '')}**: {m.get('effect', '')}\n"
                    md += "\n"
                
                if step.get("conclusion"):
                    md += f"**Conclusion:** *{step.get('conclusion')}*\n\n"
            
        audit = structured_report.get("audit_block", {})
        if audit:
            md += "## 🛡️ Audit & Verification\n"
            scores = audit.get("scores", {})
            for label, score in scores.items():
                emoji = "✅" if score >= 80 else "⚠️" if score >= 60 else "❌"
                md += f"- **{label.upper()}:** {emoji} {score}%\n"
            md += f"\n> **Verdict:** {audit.get('verdict', 'PASS')}\n"
            md += f"> **Summary:** {audit.get('summary', '')}\n\n"
            
        evidence = structured_report.get("evidence_base", [])
        if evidence:
            md += "## 📚 Evidence Base\n"
            for ev in evidence:
                doc = ev.get("document", "")
                pages = ev.get("pages", [1])
                for p in pages:
                    md += f"- 📄 `{doc}` (Page {p})\n"
                    
        return md

    @staticmethod
    def render_guided_questions(questions):
        if not questions:
            return ""
        html = '<div style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; margin-bottom: 16px;">'
        html += '<div style="width: 100%; font-size: 12px; color: var(--text-secondary); margin-bottom: 4px;">💡 您可能还想问：</div>'
        for q in questions:
            q_esc = q.replace("'", "\\'")
            html += f'<div class="repo-badge" style="cursor: pointer; background: var(--bg-交互); border-color: var(--primary-color); color: var(--text-title); padding: 4px 12px;" onclick="window.askQuestion(\'{q_esc}\')">{q}</div>'
        html += '</div>'
        return html
