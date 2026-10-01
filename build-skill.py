#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build-skill.py — 把 skills/<名字>/ 打包成 dist/<名字>.skill

用法：
    python build-skill.py                 # 打包 skills/ 下的全部 skill
    python build-skill.py daily-brief     # 只打包指定的一个

产物：
    dist/<名字>.skill   —— 本质是 zip，内含一层 <名字>/ 目录，可直接上传到扣子 / Kimi 网页版

出厂校验（不通过就报错退出）：
    1. 包内必须恰好一个 SKILL.md
    2. SKILL.md 的 frontmatter 必须含 name 和 description
    3. frontmatter 的 name 必须等于目录名
    4. description 不超过 1024 字符，name 不超过 64 字符
"""
import os
import re
import sys
import zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
SKILLS_DIR = os.path.join(ROOT, "skills")
DIST_DIR = os.path.join(ROOT, "dist")

EXCLUDE_DIRS = {".git", "__pycache__", ".venv", "node_modules", ".idea", ".vscode"}
EXCLUDE_FILES = {".DS_Store", "Thumbs.db", ".gitignore"}


def parse_frontmatter(text):
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    block = text[3:end]
    data = {}
    for line in block.splitlines():
        line = line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        m = re.match(r"^([A-Za-z0-9_-]+)\s*:\s*(.*)$", line)
        if m:
            key, val = m.group(1), m.group(2).strip()
            if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
                val = val[1:-1]
            data[key] = val
    return data


def collect_files(skill_dir):
    files = []
    for dirpath, dirnames, filenames in os.walk(skill_dir):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for fn in filenames:
            if fn in EXCLUDE_FILES:
                continue
            files.append(os.path.join(dirpath, fn))
    return files


def build_one(skill_name):
    skill_dir = os.path.join(SKILLS_DIR, skill_name)
    if not os.path.isdir(skill_dir):
        print("  [跳过] 找不到目录 skills/%s" % skill_name)
        return False

    skill_md = os.path.join(skill_dir, "SKILL.md")
    if not os.path.isfile(skill_md):
        print("  [失败] skills/%s 下没有 SKILL.md" % skill_name)
        return False

    files = collect_files(skill_dir)

    # 校验 1：恰好一个 SKILL.md
    skill_md_count = sum(1 for f in files if os.path.basename(f) == "SKILL.md")
    if skill_md_count != 1:
        print("  [失败] 包内 SKILL.md 数量为 %d，必须恰好 1 个" % skill_md_count)
        return False

    # 校验 2：frontmatter
    with open(skill_md, "r", encoding="utf-8") as fh:
        fm = parse_frontmatter(fh.read())
    if fm is None:
        print("  [失败] SKILL.md 缺少 YAML frontmatter（文件开头必须是 --- 包起来的一段）")
        return False
    if not fm.get("name") or not fm.get("description"):
        print("  [失败] frontmatter 必须同时包含 name 和 description")
        return False

    # 校验 3：name 必须等于目录名
    if fm["name"] != skill_name:
        print("  [失败] frontmatter 的 name=「%s」与目录名「%s」不一致" % (fm["name"], skill_name))
        return False

    # 校验 4：长度限制
    if len(fm["name"]) > 64:
        print("  [失败] name 超过 64 字符")
        return False
    if len(fm["description"]) > 1024:
        print("  [失败] description 超过 1024 字符（当前 %d）" % len(fm["description"]))
        return False

    os.makedirs(DIST_DIR, exist_ok=True)
    out_path = os.path.join(DIST_DIR, "%s.skill" % skill_name)
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in files:
            rel = os.path.relpath(path, SKILLS_DIR)
            zf.write(path, rel)

    size_kb = os.path.getsize(out_path) / 1024.0
    print("  [成功] dist/%s.skill  （%d 个文件，%.1f KB，SKILL.md 恰好 1 个）"
          % (skill_name, len(files), size_kb))
    return True


def main():
    if not os.path.isdir(SKILLS_DIR):
        print("找不到 skills/ 目录，请在仓库根目录运行本脚本")
        return 1

    if len(sys.argv) > 1:
        targets = sys.argv[1:]
    else:
        targets = sorted(
            d for d in os.listdir(SKILLS_DIR)
            if os.path.isdir(os.path.join(SKILLS_DIR, d))
        )

    if not targets:
        print("skills/ 下没有可打包的 skill")
        return 1

    print("开始打包，共 %d 个：" % len(targets))
    ok = 0
    for name in targets:
        if build_one(name):
            ok += 1

    print("\n完成：成功 %d / 共 %d" % (ok, len(targets)))
    print("产物在 dist/ 目录。上传到扣子或 Kimi 网页版即可安装。")
    return 0 if ok == len(targets) else 1


if __name__ == "__main__":
    sys.exit(main())
