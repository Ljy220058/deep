---
name: git-workflow-guardrails
description: 处理 GitHub 提交和推送时的常见错误（如 index.lock、嵌套仓库、分支不匹配、远程仓库未找到等）。当用户要求“提交到仓库”、“同步到 GitHub”或遇到 Git 报错时，请务必调用此技能以确保操作的原子性和成功率。
---

# Git 工作流护栏 (Git Workflow Guardrails)

本技能旨在通过标准化的诊断和修复流程，解决在 Trae 环境中进行 Git 提交和推送时最常见的障碍。

## 1. 核心诊断与修复流程

### 场景 A：Git 锁文件冲突 (index.lock)
**症状**：报错 `fatal: Unable to create '.../.git/index.lock': File exists.`
**操作**：
1. 强制停止所有残留的 Git 进程：`Get-Process git -ErrorAction SilentlyContinue | Stop-Process -Force`
2. 手动删除锁文件：`if (Test-Path .git/index.lock) { Remove-Item -Force .git/index.lock }`
3. 重新执行 Git 命令。

### 场景 B：嵌套 Git 仓库 (Embedded Repository)
**症状**：`git add` 警告 `adding embedded git repository`，且在远程仓库中该子目录显示为不可点击的“灰字”或“提交哈希”。
**操作**：
1. 检查子目录是否存在 `.git`：`Get-ChildItem -Path <subdir> -Force -Filter .git*`
2. 如果存在，彻底删除子目录的 Git 元数据：`Remove-Item -Recurse -Force <subdir>/.git`
3. 清除暂存区缓存：`git rm -r --cached <subdir>`
4. 重新添加并提交：`git add <subdir>/; git commit -m "..."`

### 场景 C：分支名不匹配 (Refspec Master/Main)
**症状**：`error: src refspec master does not match any` 或 `failed to push some refs`
**操作**：
1. 检查本地分支：`git branch`
2. 如果本地是 `master` 而远程是 `main`（或反之），明确指定映射关系：`git push origin master:main`
3. 或者统一本地分支名：`git branch -M master` (或 main)

### 场景 D：远程仓库不可达 (Repository Not Found)
**症状**：`fatal: repository '...' not found`
**操作**：
1. 检查配置：`git remote -v`
2. 确认 URL 是否正确。如果 URL 有误或需要更新，使用：`git remote set-url origin <new_url>`
3. 如果是权限或仓库不存在问题，建议通过 `WebSearch` 确认正确的仓库 URL。

## 2. 推荐的“鲁棒型”推送命令
在需要确保覆盖且同步到远程时，建议使用复合命令：
```powershell
# 1. 清理潜在锁 -> 2. 添加 -> 3. 提交 -> 4. 强制推送并建立追踪
if (Test-Path .git/index.lock) { Remove-Item -Force .git/index.lock }; git add .; git commit -m "feat: your message"; git push -u origin master --force
```

## 3. 验证准则
- **原子性**：每次修改关键逻辑后，必须立即进行 Git 提交。
- **验证**：推送后，建议运行 `git ls-remote origin` 或 `git log origin/master -n 1` 确认远程端已更新。
- **扁平化**：严禁在未说明的情况下将子项目作为 Submodule 提交，除非用户明确要求。默认应通过删除子目录 `.git` 的方式实现目录扁平化提交。
