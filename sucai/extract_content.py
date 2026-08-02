# -*- coding: utf-8 -*-
"""按 DESIGN.md 结构把素材 docx 提取为 JSON + 三档 WebP 媒体。

用法: python sucai/extract_content.py <kind> <id> <name> <docx路径> [--cover 图片序号]
  kind: departments | topics
输出: static/blueprint/data/<kind>/<id>.json
媒体: uploads/blueprint/<kind>/<id>/images/imgNN.webp (大图, <=1920)
      uploads/blueprint/<kind>/<id>/images/imgNN_1280.webp
      uploads/blueprint/<kind>/<id>/images/imgNN_640.webp
      uploads/blueprint/<kind>/<id>/cover.webp (代表图)
"""
import json
import re
import sys
from pathlib import Path
from zipfile import ZipFile

import xml.etree.ElementTree as ET
from PIL import Image

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
V_NS = "urn:schemas-microsoft-com:vml"

ROOT = Path(__file__).resolve().parents[1]
MEDIA_ROOT = ROOT / "uploads" / "blueprint"
DATA_ROOT = ROOT / "static" / "blueprint" / "data"

# 章节标题词表（按素材文档实际出现顺序）
SECTION_TITLES = [
    "基本情况", "系部简介", "专业设置", "专业群", "师资队伍", "实训基地",
    "产教融合校企合作", "产教融合", "校企合作", "产业学院", "订单班",
    "教学成果", "教学与创新成果", "名师名匠", "优秀校友", "优秀学生",
    "学生风采", "技能大赛", "荣誉资质", "视频资料", "视频资源",
]

# 工程占位/内部注释模式（正式页面必须剔除）
PLACEHOLDER_PATTERNS = [
    re.compile(r"^（?注[:：]"), re.compile(r"^\(注[:：]"),
    re.compile(r"^补充[:：]"), re.compile(r"^【需进一步补充"),
    re.compile(r"待补充"), re.compile(r"需进一步补充"), re.compile(r"（见视频）"),
    re.compile(r"^一段总结"), re.compile(r"^补充专业群对接"),
    re.compile(r"^【"), re.compile(r"确认专业介绍顺序"),
    re.compile(r"暂不按专业群分割"), re.compile(r"以系部为单位"),
    re.compile(r"^一、存在问题"), re.compile(r"^二、建议"),
    re.compile(r"^图片下文字不全"),
]

SECTION_ALIASES = {
    "系部简介": "基本情况", "教学与创新成果": "教学成果",
    "产教融合校企合作": "产教融合", "视频资源": "视频资料",
    "学生风采": "优秀学生", "专业群": "专业设置",
}

SECTION_IDS = {
    "基本情况": "overview", "专业设置": "majors", "实训基地": "training",
    "产教融合": "cooperation", "教学成果": "achievements",
    "技能大赛": "competitions", "荣誉资质": "honors", "名师名匠": "masters",
    "优秀校友": "alumni", "优秀学生": "students", "视频资料": "media",
    "师资队伍": "faculty", "订单班": "orders", "产业学院": "industry-school",
}


def strip_ns(tag):
    return tag.split("}")[-1]


def extract_docx_blocks(docx_path: Path):
    """返回有序块流: [("text", str) | ("image", rId)]"""
    blocks = []
    with ZipFile(str(docx_path)) as z:
        names = set(z.namelist())
        rels = {}
        if "word/_rels/document.xml.rels" in names:
            rels_xml = z.read("word/_rels/document.xml.rels")
            root = ET.fromstring(rels_xml)
            for rel in root:
                rels[rel.get("Id")] = rel.get("Target")
        doc_xml = z.read("word/document.xml")
        root = ET.fromstring(doc_xml)
        body = root.find(f"{{{W_NS}}}body")
        for child in body:
            tag = strip_ns(child.tag)
            if tag == "p":
                # 收集该段内图片 (a:blip 与 VML v:imagedata 两种引用)
                images = []
                for blip in child.iter(f"{{{A_NS}}}blip"):
                    rid = blip.get(f"{{{R_NS}}}embed")
                    if rid and rid in rels:
                        images.append(rels[rid])
                for im in child.iter(f"{{{V_NS}}}imagedata"):
                    rid = im.get(f"{{{R_NS}}}id")
                    if rid and rid in rels:
                        images.append(rels[rid])
                texts = [t.text or "" for t in child.iter(f"{{{W_NS}}}t")]
                text = "".join(texts).strip()
                if images:
                    for img in images:
                        blocks.append(("image", img))
                if text:
                    blocks.append(("text", text))
            elif tag == "tbl":
                rows = []
                for tr in child.iter(f"{{{W_NS}}}tr"):
                    cells = []
                    for tc in tr.findall(f"{{{W_NS}}}tc"):
                        cell_text = "".join(
                            t.text or "" for t in tc.iter(f"{{{W_NS}}}t")
                        ).strip()
                        if cell_text:
                            cells.append(cell_text)
                    if cells:
                        rows.append(" / ".join(cells))
                if rows:
                    blocks.append(("text", "\n".join(rows)))
    return blocks, rels


def split_sections(blocks):
    """按标题词切分章节, 返回 [{"title":..., "blocks":[...]}]"""
    sections = []
    current = None
    for kind, payload in blocks:
        if kind == "text" and payload in SECTION_TITLES:
            title = SECTION_ALIASES.get(payload, payload)
            current = {"title": title, "blocks": []}
            sections.append(current)
            continue
        if current is None:
            continue  # 标题前的导语丢弃(通常重复系部简介)
        if kind == "text":
            if any(p.search(payload) for p in PLACEHOLDER_PATTERNS):
                continue
            if payload in SECTION_TITLES:
                continue
            current["blocks"].append({"type": "text", "content": payload})
        else:
            current["blocks"].append({"type": "image", "src": payload})
    # 无章节标题的文档（简短简介）：全部归入"基本情况"
    if not sections:
        title = "基本情况"
        current = {"title": title, "blocks": []}
        sections.append(current)
        for kind, payload in blocks:
            if kind == "text":
                if any(p.search(payload) for p in PLACEHOLDER_PATTERNS):
                    continue
                if payload in SECTION_TITLES:
                    continue
                current["blocks"].append({"type": "text", "content": payload})
            else:
                current["blocks"].append({"type": "image", "src": payload})
    return sections


def process_images(docx_path: Path, blocks, out_dir: Path, counter, cover_index=1):
    """把块流中的图片落盘为三档 WebP, 返回 (新块流, cover_url)"""
    url_map = {}
    cover_url = None
    rel_prefix = out_dir.relative_to(MEDIA_ROOT).as_posix()
    with ZipFile(str(docx_path)) as z:
        for b in blocks:
            if b["type"] != "image":
                continue
            counter[0] += 1
            idx = counter[0]
            target = b["src"].replace("\\", "/").lstrip("/")
            # rels target 形如 media/image1.jpeg, 兼容 word/media/ 前缀
            if not target.startswith("word/"):
                target = "word/" + target
            try:
                raw = z.read(target)
            except KeyError:
                continue
            img = Image.open(io_bytes(raw))
            img = img.convert("RGB")
            w, h = img.size
            stem = f"img{idx:02d}"
            sizes = {}
            for label, max_w in (("", 1920), ("_1280", 1280), ("_640", 640)):
                if w <= max_w and label:
                    continue
                tw = min(w, max_w)
                th = max(1, round(h * tw / w))
                thumb = img if (tw == w) else img.resize((tw, th), Image.LANCZOS)
                fn = out_dir / f"{stem}{label}.webp"
                thumb.save(fn, "WEBP", quality=82, method=4)
                sizes[label] = fn
            if not sizes:
                fn = out_dir / f"{stem}.webp"
                img.save(fn, "WEBP", quality=82, method=4)
            url = f"/uploads/blueprint/{rel_prefix}/{stem}.webp"
            url_map[b["src"]] = url
            if idx == cover_index:
                cover_url = url
    new_blocks = []
    for b in blocks:
        if b["type"] == "image":
            url = url_map.get(b["src"])
            if url:
                new_blocks.append({**b, "src": url})
        else:
            new_blocks.append(b)
    return new_blocks, cover_url


def io_bytes(data):
    import io
    return io.BytesIO(data)


def attach_captions(blocks):
    """为图片块附加图注: 取前一个短文本块(<40字, 非数字行)"""
    out = []
    prev_text = None
    for b in blocks:
        if b["type"] == "image":
            caption = ""
            if prev_text and len(prev_text) <= 40 and not re.fullmatch(r"[\d\s|，。、（）()]+", prev_text):
                caption = prev_text
            b["caption"] = caption
            out.append(b)
        else:
            prev_text = b["content"]
            out.append(b)
    return out


def main():
    if len(sys.argv) < 5:
        print(__doc__)
        sys.exit(2)
    kind, pid, name, docx = sys.argv[1], sys.argv[2], sys.argv[3], Path(sys.argv[4])
    cover_index = 1
    if "--cover" in sys.argv:
        cover_index = int(sys.argv[sys.argv.index("--cover") + 1])

    blocks, _rels = extract_docx_blocks(docx)
    sections = split_sections(blocks)

    media_dir = MEDIA_ROOT / kind / pid / "images"
    media_dir.mkdir(parents=True, exist_ok=True)
    new_blocks_by_sec = []
    cover_url = None
    counter = [0]
    for sec in sections:
        nb, cv = process_images(docx, sec["blocks"], media_dir, counter, cover_index if sec is sections[0] else 999)
        nb = attach_captions(nb)
        if not cover_url and cv:
            cover_url = cv
        new_blocks_by_sec.append({**sec, "blocks": nb})

    # 剔除空章节
    new_blocks_by_sec = [s for s in new_blocks_by_sec if s["blocks"]]
    # 视频资料章节若无视频素材则剔除
    new_blocks_by_sec = [
        s for s in new_blocks_by_sec
        if not (s["title"] == "视频资料" and not any(
            b["type"] == "video" for b in s["blocks"]))
    ]
    # cover 兜底: 全文第一张图
    if not cover_url:
        for sec in new_blocks_by_sec:
            for b in sec["blocks"]:
                if b["type"] == "image":
                    cover_url = b["src"]
                    break
            if cover_url:
                break

    data = {
        "id": pid, "type": kind.rstrip("s"), "name": name, "summary": "",
        "cover": cover_url or "", "stats": [],
        "sections": [
            {"id": SECTION_IDS.get(s["title"], "section"), "title": s["title"],
             "blocks": s["blocks"]}
            for s in new_blocks_by_sec
        ],
    }
    out = DATA_ROOT / kind / f"{pid}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"written {out}")
    print(f"sections: {[s['id'] for s in data['sections']]}")
    print(f"cover: {cover_url}")


if __name__ == "__main__":
    main()
