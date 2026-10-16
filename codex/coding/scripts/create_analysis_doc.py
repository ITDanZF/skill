#!/usr/bin/env python3
"""Create a temporary Chinese coding-analysis Markdown file and best-effort open it in VS Code."""

from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = value.strip("-")
    return value or "coding-analysis"


def temp_root(workspace: Path) -> Path:
    base = Path(tempfile.gettempdir()) / "codex-coding-analysis"
    workspace_key = slugify(str(workspace.resolve()).replace(":", ""))[-80:]
    return base / workspace_key


def cleanup_expired(root: Path, now: dt.datetime, days: int) -> None:
    if not root.exists():
        return
    cutoff = now - dt.timedelta(days=days)
    for path in root.glob("*.md"):
        try:
            modified = dt.datetime.fromtimestamp(path.stat().st_mtime)
        except OSError:
            continue
        if modified < cutoff:
            try:
                path.unlink()
            except OSError:
                pass


def default_content(workspace: Path, title: str, now: dt.datetime, expires: dt.datetime) -> str:
    return f"""# 代码变更分析

- 生成时间：{now.isoformat(timespec='seconds')}
- 过期时间：{expires.isoformat(timespec='seconds')}
- 工作区：{workspace}
- 任务：{title}
- 状态：等待用户阅读与确认

## 1. 需求摘要

## 2. 已确认需求

## 3. 待确认问题

待确认问题必须同时在对话框中提出，并提供 2-4 个选项。本文档只作为记录。

## 4. 工程与模块分析

## 5. 当前行为

## 6. 根因分析

## 7. 现有代码规范评估

## 8. 建议修改方案

## 9. 涉及文件

| 文件 | 读取/修改/新增 | 原因 | 风险 |
| --- | --- | --- | --- |

## 10. 影响范围

## 11. 兜底与错误处理策略

## 12. 可选方案

## 13. 推荐方案

## 14. Todo List

- [ ] 用户阅读本分析文档。
- [ ] 在对话框中回答待确认问题。
- [ ] 用户确认选择的方案。
- [ ] 执行已批准的代码修改。
- [ ] 运行约定的快速验证。
- [ ] 汇报最终结果和剩余风险。

## 15. 验证计划

## 16. 审批检查点

在用户明确批准本方案前，不应修改源代码。需要确认的问题必须在对话框中提出，不能只写在本文档里。
"""


def open_vscode(path: Path) -> str:
    code = shutil.which("code.cmd") or shutil.which("code")
    if not code:
        return "未在 PATH 中找到 VS Code 命令 'code'。"
    try:
        subprocess.Popen([code, "--reuse-window", str(path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except OSError as exc:
        return f"打开 VS Code 失败：{exc}"
    return "已尝试用 VS Code 打开。"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", default=os.getcwd(), help="Workspace path for this analysis.")
    parser.add_argument("--title", default="coding-analysis", help="Short task title for the filename and report metadata.")
    parser.add_argument("--content-file", help="Optional Markdown content file to copy into the temporary report.")
    parser.add_argument("--ttl-days", type=int, default=3, help="Temporary report lifetime in days.")
    parser.add_argument("--no-open", action="store_true", help="Create the report without opening VS Code.")
    args = parser.parse_args()

    workspace = Path(args.workspace).expanduser().resolve()
    now = dt.datetime.now()
    expires = now + dt.timedelta(days=args.ttl_days)
    root = temp_root(workspace)
    root.mkdir(parents=True, exist_ok=True)
    cleanup_expired(root, now, args.ttl_days)

    filename = f"{now.strftime('%Y%m%d-%H%M%S')}-{slugify(args.title)}.md"
    output = root / filename

    if args.content_file:
        content = Path(args.content_file).read_text(encoding="utf-8")
    else:
        content = default_content(workspace, args.title, now, expires)

    output.write_text(content, encoding="utf-8")

    status = "已创建，未打开 VS Code。"
    if not args.no_open:
        status = open_vscode(output)

    print(f"REPORT_PATH={output}")
    print(f"OPEN_STATUS={status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())