# -*- coding: utf-8 -*-
"""校验 blueprint 数据: JSON 合法性、章节 id 唯一、图片/视频引用存在、无占位文案。"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "static" / "blueprint" / "data"
UPLOAD_DIR = ROOT / "uploads"

PLACEHOLDER = re.compile(r"补充[:：]|需进一步|待放|【|（注[:：]|待补充|暂不按|以系部为单位|一、存在问题|二、建议")

errors = []
ok = 0
for kind in ("departments", "topics"):
    for json_path in sorted((DATA_DIR / kind).glob("*.json")):
        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"{json_path}: JSON 解析失败 {exc}")
            continue
        if not data.get("id") or not data.get("name"):
            errors.append(f"{json_path}: 缺 id/name")
        if not data.get("summary"):
            errors.append(f"{json_path}: 缺 summary")
        if not data.get("cover"):
            errors.append(f"{json_path}: 缺 cover")
        cover_file = UPLOAD_DIR / data["cover"].replace("/uploads/", "").replace("/", "\\")
        if not cover_file.exists():
            errors.append(f"{json_path}: cover 文件不存在 {data['cover']}")
        sec_ids = []
        img_count = text_count = video_count = 0
        for sec in data.get("sections", []):
            sid = sec.get("id")
            if sid in sec_ids:
                errors.append(f"{json_path}: 重复章节 {sid}")
            sec_ids.append(sid)
            for b in sec.get("blocks", []):
                if b["type"] == "image":
                    img_count += 1
                    f = UPLOAD_DIR / b["src"].replace("/uploads/", "").replace("/", "\\")
                    if not f.exists():
                        errors.append(f"{json_path}: 图片不存在 {b['src']}")
                elif b["type"] == "video":
                    video_count += 1
                    f = UPLOAD_DIR / b["src"].replace("/uploads/", "").replace("/", "\\")
                    if not f.exists():
                        errors.append(f"{json_path}: 视频不存在 {b['src']}")
                elif b["type"] == "text":
                    text_count += 1
                    if PLACEHOLDER.search(b["content"]):
                        errors.append(f"{json_path}: 残留占位文案: {b['content'][:40]}")
                else:
                    errors.append(f"{json_path}: 未知块类型 {b.get('type')}")
        if not sec_ids:
            errors.append(f"{json_path}: 无章节")
        ok += 1
        print(f"OK {json_path.name}: {len(sec_ids)}章 {text_count}文本 {img_count}图 {video_count}视频")

print(f"\nchecked {ok} files, errors: {len(errors)}")
for e in errors[:30]:
    print(" -", e)
sys.exit(1 if errors else 0)
