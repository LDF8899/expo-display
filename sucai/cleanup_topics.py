# -*- coding: utf-8 -*-
"""清理专题 JSON: 合并重复章节、剔除占位/内部标注、去除冗余行。"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "static" / "blueprint" / "data" / "topics"

# 文档内部标注/占位模式（含图注中的左右图标注）
STRIP_PATTERNS = [
    (re.compile(r"[（(]\s*[左右上下]图\s*[）)]"), ""),
    (re.compile(r"^\s*系部简介[:：]\s*$"), ""),
    (re.compile(r"^\s*创新育人区[—\-–]?\s*$"), ""),
    (re.compile(r"[（(]注[:：][^）)]*[）)]"), ""),
    (re.compile(r"[（(]见视频[）)]"), ""),
    (re.compile(r"^\s*一段总结[^。]*。?"), ""),
    (re.compile(r"^\s*补充专业群对接产业领域\s*$"), ""),
]

DROP_PATTERNS = [
    re.compile(r"^补充[:：]"), re.compile(r"^【"), re.compile(r"待补充"),
    re.compile(r"^（?注[:：]"), re.compile(r"需进一步补充"),
    re.compile(r"确认专业介绍顺序"), re.compile(r"暂不按专业群分割"),
    re.compile(r"以系部为单位"), re.compile(r"^图片下文字不全"),
    re.compile(r"^一、存在问题"), re.compile(r"^二、建议"),
    re.compile(r"^三、参赛备战"), re.compile(r"^五、案例育人价值"),
    re.compile(r"^六、案例总结"),
]

# 空/无意义行
MEANINGLESS = re.compile(r"^[\s|、。，；：（）()0-9]+$")


def clean_text(t: str) -> str:
    for pat, rep in STRIP_PATTERNS:
        t = pat.sub(rep, t)
    t = t.strip()
    # 压缩连续空白
    t = re.sub(r"[ \t]+", " ", t)
    return t


def cleanup(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    sections = data["sections"]
    merged = []
    seen_ids = {}
    for sec in sections:
        blocks = []
        prev_text = None
        for b in sec["blocks"]:
            if b["type"] == "text":
                t = clean_text(b["content"])
                if not t or MEANINGLESS.match(t):
                    continue
                if any(p.search(t) for p in DROP_PATTERNS):
                    continue
                if t == prev_text:  # 相邻重复
                    continue
                prev_text = t
                blocks.append({"type": "text", "content": t})
            else:
                prev_text = None
                if b["type"] == "video":
                    blocks.append({k: v for k, v in b.items()})
                    continue
                cap = clean_text(b.get("caption", ""))
                if MEANINGLESS.match(cap) or any(p.search(cap) for p in DROP_PATTERNS):
                    cap = ""
                blocks.append({"type": "image", "src": b["src"], "caption": cap})
        if not blocks:
            continue
        sid = sec["id"]
        if sid in seen_ids:
            seen_ids[sid]["blocks"].extend(blocks)
        else:
            merged.append({"id": sid, "title": sec["title"], "blocks": blocks})
            seen_ids[sid] = merged[-1]
    data["sections"] = merged
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"cleaned {path.name}: {[s['id'] for s in merged]}")


if __name__ == "__main__":
    targets = sys.argv[1:] or [str(p) for p in DATA_DIR.glob("*.json")]
    for t in targets:
        cleanup(Path(t))
