***

name: hf-model-manager
description: Hugging Face 模型下载与验证工具。当用户提到下载 Hugging Face 模型、使用 Hugging Face 链接、模型缺失、或需要安装深度学习模型（如 Marker, Surya, Transformers 模型）时触发。本技能提供镜像加速、断点续传、手动搬运校验等功能。
--------------------------------------------------------------------------------------------------------------------------------------------------------------

# 本技能专门用于在受限网络环境下高效、可靠地下载和验证 Hugging Face 模型，封装了我们在处理 Marker、Surya 等深度学习模型时积累的全套实战经验。

***

## 核心功能

1. **智能镜像加速**：自动检测网络环境，国内网络默认使用 `https://hf-mirror.com` 镜像站，大幅提升下载速度，无需用户手动配置。
2. **断点续传支持**：自动开启 `resume_download`，支持中断后继续下载，避免大文件下载失败需要从头重来。
3. **自动文件搬运**：自动检测用户手动下载到 `Downloads` 文件夹的模型文件，自动搬运到标准缓存目录，省去用户手动移动的麻烦。
4. **标准化目录管理**：自动创建符合 Hugging Face 规范的目录结构，统一缓存路径，避免乱存乱放导致的重复下载。
5. **双层完整性校验**：通过文件 hash 校验 + 可选的模型加载测试，确保下载的模型完整可用，杜绝坏文件。

***

## 触发场景

当遇到以下情况时，本技能会自动触发：

1. 检测到项目依赖的 HF 模型本地缺失时（比如代码要加载模型但找不到）。
2. 用户输入 HF 模型 ID / 仓库链接时（比如用户说 "帮我下载 vikhyatk/moondream2"）。
3. 用户提到要下载模型、安装模型，或者做 OCR/LLM 等需要模型的任务时。
4. 检测到之前的模型下载失败 / 文件不完整时，自动触发断点续传。

***

## 交互规则 (核心指令)

1. **强制三方案原则**：在执行任何实质性的下载或配置变更前，必须提供至少三个备选方案（如：自动下载、手动搬运、忽略或降级方案），让用户进行选择。
2. **单次单任务**：每次交互仅处理一个模型的下载或一个阶段的任务，避免多任务混乱。
3. **状态透明**：每下载完一个模型或移动完一个文件，必须汇报当前的目录大小和剩余任务，让用户随时掌握进度。

***

## 完整性校验机制

本技能采用分层校验，兼顾速度和可靠性：

1. **第一层：强制文件 Hash 校验**
   1. 使用 Hugging Face 官方的 sha256 hash 校验每个文件的完整性
   2. 比单纯检查文件存在靠谱得多，能快速发现损坏的下载文件
2. **第二层：可选模型加载测试**
   1. 默认开启轻量加载测试，只加载模型配置和权重头验证
   2. 支持用户手动开启完整加载测试（类似我们之前的 `test_marker.py`），跑最小推理用例，彻底验证模型可用

***

## 使用指南

### 1. 自动下载

使用内置脚本 `manage_hf.py` 进行自动下载：

```
python .trae/skills/hf-model-manager/scripts/manage_hf.py --repo "vikp/surya_det3" --cache "path/to/cache"
```

### 2. 手动搬运并校验

如果用户已经手动下载了文件到 `Downloads`：

```
python .trae/skills/hf-model-manager/scripts/manage_hf.py --repo "vikp/surya_det3" --cache "path/to/cache" --move "model.safetensors"
```

### 3. 环境配置建议

- 始终自动设置环境变量：
  - <br />
  ```
  os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
  os.environ["HF_HOME"] = cache_dir
  ```
- 对于 Windows 环境，优先将缓存路径重定向至项目本地目录，避免 `AppData\Local` 权限问题。

***

## 故障排除 (实战经验总结)
- **代理干扰导致的“假死”**：如果终端卡在 `Attempt 1 of 3` 或报 `ProxyError`，说明环境中有失效代理。必须在脚本中强制清理：
  ```python
  for var in ["HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"]:
      if var in os.environ: del os.environ[var]
  ```
- **深度离线强制**：即使模型已下载，Marker/Surya 仍会尝试联网检查 `manifest.json`。必须设置：
  ```python
  os.environ["MARKER_OFFLINE"] = "1"
  os.environ["SURYA_OFFLINE"] = "1"
  os.environ["HF_HUB_OFFLINE"] = "1"
  ```
- **权限错误 (WinError 5)**：通过在脚本开头设置 `os.environ["HF_HOME"]` 到非系统受限目录解决，避免系统盘权限限制。
- **UTF-8 编码问题**：在脚本开头使用 `sys.stdout.reconfigure(encoding='utf-8')` 处理特殊字符，避免中文文件名报错。

