import json
import hashlib
import mimetypes
import re
import shutil
import sqlite3
import zipfile
from datetime import datetime, timezone
from html import escape as html_escape
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "expo.db"
SOURCE_ROOT = ROOT / "uploads" / "资料"
IMPORT_ROOT = ROOT / "uploads" / "imported-materials"
CONVERTED_DOC_ROOT = ROOT / "output" / "doc-previews"

NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
}

PROJECT_DOCS = [
    ("modern-agriculture", "创新育人-现代农业(1).docx"),
    ("digital-tourism", "创新育人-数字文旅2026.7.25.docx"),
    ("smart-healthcare", "创新育人-智慧康养(合并版).docx"),
    ("finance-commerce", "创新育人-财经商贸2026.8.4更新.docx"),
    ("digital-intelligence", "创新育人-数智技术.docx"),
    ("smart-energy", "创新育人-智慧能源(1).docx"),
    ("smart-manufacturing", "创新育人-智能制造(1).docx"),
]

DEPARTMENT_DOCS = [
    ("smart-manufacturing", "工矿建筑系简介-修订版.docx", "工矿建筑系简介"),
    ("digital-intelligence", "电子信息工程系系部介绍(2).docx", "电子信息工程系系部介绍"),
    ("smart-healthcare", "医学护理系.docx", "医学护理系简介"),
    ("digital-tourism", "400字旅游管理系简介.docx", "旅游管理系简介"),
]

STANDALONE_MEDIA = [
    ("smart-healthcare", "医护系"),
    ("digital-tourism", "旅游管理系简介文字+图片/图片"),
]

VIDEO_MEDIA = [
    ("digital-tourism", "创新育人-数字文旅", "media"),
]

LEGACY_CONVERTED_DOCS = [
    ("finance-commerce", CONVERTED_DOC_ROOT / "创新育人-财经商贸2026_7_25更新.docx", None),
    ("finance-commerce", CONVERTED_DOC_ROOT / "改财政经济系_1_1.docx", "财政经济系简介（旧版补充）"),
]

MARKET_MODULE_CATEGORY = {
    "masters": "masters",
    "alumni": "alumni",
    "students": "students",
    "achievements": "teaching",
    "competitions": "competitions",
    "honors": "honors",
}

MARKET_CATEGORY_LABELS = {
    "masters": "名匠名师",
    "alumni": "优秀校友",
    "students": "优秀学生",
    "teaching": "教学科研",
    "competitions": "技能大赛",
    "honors": "荣誉资质",
}

MARKET_CATEGORY_COLORS = {
    "masters": "#7030A0",
    "alumni": "#0070C0",
    "students": "#30C0B4",
    "teaching": "#75BD42",
    "competitions": "#EFBB1F",
    "honors": "#FB9236",
}

MODULE_KEYWORDS = [
    ("systems", ("特色系统", "系统入口", "体验系统", "平台入口")),
    ("masters", ("名师名匠", "名师", "名匠", "教师团队", "专业带头人", "教授", "副教授", "研究员")),
    ("alumni", ("优秀校友", "校友", "毕业生", "就业典型")),
    ("students", ("优秀学生", "学生风采", "技能成才")),
    ("competitions", ("技能大赛", "竞赛", "比赛", "赛项", "获奖", "承办")),
    ("honors", ("荣誉资质", "荣誉", "证书", "奖项", "认定")),
    ("cooperation", ("产教融合", "产教协同", "校企合作", "订单班", "产业学院", "共同体", "企业")),
    ("training", ("实训基地", "实训室", "实训场景", "实训区", "工坊", "基地", "设备")),
    ("majors", ("专业设置", "专业群", "专业布局", "专业介绍", "培养目标", "就业方向")),
    ("achievements", ("教学成果", "创新成果", "专题成果", "成果", "案例", "课题项目", "社会服务")),
    ("media", ("视频资料", "视频资源", "宣传片", "媒体报道")),
]

CONTENT_TYPES = {
    "training": "scene",
    "cooperation": "activity",
    "masters": "person",
    "alumni": "person",
    "students": "person",
    "achievements": "achievement",
    "competitions": "activity",
    "honors": "honor",
    "media": "video",
    "systems": "article",
    "majors": "article",
    "overview": "article",
}

BAD_TITLES = {
    "序号",
    "名称",
    "地点",
    "功能",
    "工位数（个）",
    "设备价值",
    "占地面积（平米）",
    "岗位群",
    "初始岗位",
    "发展岗位",
    "目标岗位",
}


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def slugify(text):
    text = re.sub(r"[^A-Za-z0-9]+", "-", text).strip("-").lower()
    return text or "item"


def json_text(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def normalize_text(text):
    text = re.sub(r"\s+", " ", str(text or "").replace("\u3000", " ")).strip()
    text = text.replace("【需进一步补充，逐项介绍重点实训基地/实训室，审核确认排序补充对应图片】", "")
    text = text.replace("需补充重点实训基地介绍、对应图片", "")
    text = text.replace("（如有，请补充）", "")
    text = text.replace("补充专业群对接产业领域", "")
    return text.strip()


def find_source(filename):
    matches = [p for p in SOURCE_ROOT.rglob(filename) if not p.name.startswith("~$")]
    if not matches:
        raise FileNotFoundError(filename)
    return matches[0]


def read_relationships(zf):
    rels = {}
    try:
        root = ET.fromstring(zf.read("word/_rels/document.xml.rels"))
    except KeyError:
        return rels
    for rel in root.findall("rel:Relationship", NS):
        rels[rel.attrib.get("Id")] = rel.attrib.get("Target", "")
    return rels


def docx_paragraphs(path):
    with zipfile.ZipFile(path) as zf:
        rels = read_relationships(zf)
        root = ET.fromstring(zf.read("word/document.xml"))
        paragraphs = []
        for para in root.findall(".//w:body/w:p", NS):
            text = normalize_text("".join(t.text or "" for t in para.findall(".//w:t", NS)))
            image_rel_ids = []
            for blip in para.findall(".//a:blip", NS):
                rid = blip.attrib.get(f"{{{NS['r']}}}embed")
                if rid and rid in rels:
                    target = rels[rid]
                    if target.startswith("media/"):
                        image_rel_ids.append("word/" + target)
            if text or image_rel_ids:
                paragraphs.append({"text": text, "images": image_rel_ids})
        media_names = [n for n in zf.namelist() if n.startswith("word/media/")]
    return paragraphs, media_names


def extract_docx_media(path, slug):
    out_dir = IMPORT_ROOT / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    media_map = {}
    with zipfile.ZipFile(path) as zf:
        for index, name in enumerate([n for n in zf.namelist() if n.startswith("word/media/")], start=1):
            ext = Path(name).suffix.lower() or ".bin"
            dest = out_dir / f"docx-img-{index:03d}{ext}"
            if not dest.exists():
                dest.write_bytes(zf.read(name))
            media_map[name] = "/" + dest.relative_to(ROOT).as_posix()
    return media_map


def all_docx_image_names(path):
    with zipfile.ZipFile(path) as zf:
        return [
            name for name in zf.namelist()
            if name.startswith("word/media/") and Path(name).suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
        ]


def docx_asset_pool(media_map, source_assets, title="配图"):
    pool = []
    for image_name, url in media_map.items():
        if Path(image_name).suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
            continue
        pool.append({
            "asset_id": source_assets.get(image_name),
            "role": "gallery",
            "title": title,
            "caption": title,
            "url": url,
            "image_name": image_name,
        })
    return pool


def fallback_assets(pool, index, title):
    if not pool:
        return []
    asset = dict(pool[(index - 1) % len(pool)])
    asset.update({"role": "cover", "title": title, "caption": title})
    asset.pop("image_name", None)
    return [asset]


def is_probable_title(text, next_text=""):
    text = normalize_text(text)
    if not text or text in BAD_TITLES:
        return False
    if len(text) > 46:
        return False
    if re.fullmatch(r"[0-9一二三四五六七八九十、.（）() ]+", text):
        return False
    if text.endswith(("：", ":")):
        return True
    if any(key in text for _, keys in MODULE_KEYWORDS for key in keys):
        return True
    if re.search(r"^[\u4e00-\u9fa5]{2,4}[，, ]", text):
        return True
    if re.search(r"^[\u4e00-\u9fa5]{2,4}\\s+(教授|副教授|研究员|博士|学生|老师)", text):
        return True
    if 2 <= len(text) <= 20 and re.search(r"[\u4e00-\u9fa5]", text) and len(next_text) >= 24:
        return True
    return False


def module_for(title, body):
    title_text = normalize_text(title)
    body_text = normalize_text(body)
    text = f"{title_text} {body_text}"
    if any(key in title_text for key in ("简介", "基本情况", "概况", "介绍")):
        return "overview"
    if any(key in title_text for key in ("大赛", "竞赛", "比赛", "赛项", "获奖")):
        return "competitions"
    if any(key in title_text for key in ("实训", "基地", "工坊", "实训室", "实训区", "模拟医院")):
        return "training"
    if (
        title_text.endswith("专业")
        or "专业（" in title_text
        or "专业(" in title_text
        or any(key in body_text[:180] for key in ("培养目标", "核心课程", "就业方向", "专业简介"))
    ):
        return "majors"
    if "优秀学生" in title_text or "学生风采" in title_text:
        return "students"
    if any(key in text for key in ("优秀校友", "校友", "毕业生", "毕业年份", "入学")):
        return "alumni"
    if any(key in text for key in ("优秀学生", "学生风采", "在校期间")) and not any(key in text for key in ("教师", "老师", "教授", "副教授")):
        return "students"
    if (
        re.fullmatch(r"[\u4e00-\u9fa5·]{2,6}", title_text)
        and any(key in body_text for key in ("教学", "教师", "指导学生", "科研", "辅导员", "课程", "课题", "专业带头人"))
    ):
        return "masters"
    if any(key in title_text for key in ("教师", "老师", "教授", "副教授", "研究员", "博士", "专业带头人", "名师", "名匠")):
        return "masters"
    if any(key in text for key in ("教授", "副教授", "研究员", "博士", "专业带头人", "名师", "名匠", "教师团队")):
        return "masters"
    if any(key in title_text for key in ("订单班", "校企合作", "产教融合", "共同体", "合作")):
        return "cooperation"
    if any(key in title_text for key in ("荣誉", "资质", "证书", "奖项", "认定")):
        return "honors"
    if any(key in title_text for key in ("成果", "案例", "项目", "社会服务")):
        return "achievements"
    for module, keys in MODULE_KEYWORDS:
        if any(key in text for key in keys):
            return module
    return "overview"


def polish_summary(title, body, project_name):
    sentences = re.split(r"(?<=[。！？!?])", normalize_text(body))
    first = normalize_text("".join(sentences[:2])) or normalize_text(body)[:180]
    if not first:
        first = f"{title}是{project_name}专题的重要展示内容。"
    if len(first) > 220:
        first = first[:220].rstrip("，。；、 ") + "。"
    return first


def body_blocks(paragraphs):
    blocks = []
    for para in paragraphs:
        text = normalize_text(para)
        if text:
            blocks.append({"type": "paragraph", "text": text})
    return blocks


def split_sections(paragraphs):
    text_items = [p for p in paragraphs if p["text"] or p["images"]]
    sections = []
    current = None
    for index, item in enumerate(text_items):
        text = item["text"]
        next_text = text_items[index + 1]["text"] if index + 1 < len(text_items) else ""
        starts_section = text and is_probable_title(text, next_text)
        if starts_section:
            if current:
                sections.append(current)
            current = {"title": text.rstrip("：:"), "paragraphs": [], "images": list(item["images"])}
        else:
            if current is None:
                current = {"title": "专题概况", "paragraphs": [], "images": []}
            if text:
                current["paragraphs"].append(text)
            current["images"].extend(item["images"])
    if current:
        sections.append(current)
    merged = []
    for section in sections:
        title = normalize_text(section["title"]).rstrip("：:")
        paras = [normalize_text(p) for p in section["paragraphs"] if normalize_text(p)]
        if title in BAD_TITLES or (not paras and not section["images"]):
            continue
        if merged and len(paras) <= 1 and len(title) <= 8 and title not in ("基本情况", "专业设置", "实训基地", "名师名匠", "优秀校友", "优秀学生"):
            merged[-1]["paragraphs"].append(title)
            merged[-1]["paragraphs"].extend(paras)
            merged[-1]["images"].extend(section["images"])
        else:
            merged.append({"title": title, "paragraphs": paras, "images": section["images"]})
    return merged


def choose_sections(sections, project_name):
    chosen = []
    seen = set()
    for section in sections:
        title = normalize_text(section["title"])
        body = "\n".join(section["paragraphs"])
        if not title or title in seen:
            continue
        if len(body) < 25 and not section["images"]:
            continue
        if "存在问题" in title or title == "建议":
            continue
        module = module_for(title, body)
        code_hint = slugify(f"{module}-{len(chosen)+1:03d}")
        chosen.append({
            "title": title[:80],
            "module": module,
            "content_type": CONTENT_TYPES.get(module, "article"),
            "summary": polish_summary(title, body, project_name),
            "paragraphs": section["paragraphs"][:10],
            "images": section["images"][:8],
            "code_hint": code_hint,
        })
        seen.add(title)
    return chosen[:80]


def register_asset(conn, owner, url, source_path, original_name):
    storage_key = url.removeprefix("/uploads/")
    row = conn.execute("SELECT id FROM assets WHERE storage_key = ? LIMIT 1", (storage_key,)).fetchone()
    mime = mimetypes.guess_type(original_name)[0] or "application/octet-stream"
    size = source_path.stat().st_size if source_path.exists() else 0
    now = now_iso()
    if row:
        if column_exists(conn, "assets", "updated_at"):
            conn.execute(
                "UPDATE assets SET original_filename = ?, url = ?, mime_type = ?, size_bytes = ?, updated_at = ? WHERE id = ?",
                (original_name, url, mime, size, now, row["id"]),
            )
        else:
            conn.execute(
                "UPDATE assets SET original_filename = ?, url = ?, mime_type = ?, size_bytes = ? WHERE id = ?",
                (original_name, url, mime, size, row["id"]),
            )
        return row["id"]
    cur = conn.execute(
        """
        INSERT INTO assets (owner_username, original_filename, storage_key, url, mime_type, size_bytes, backend, created_at)
        VALUES (?, ?, ?, ?, ?, ?, 'local', ?)
        """,
        (owner, original_name, storage_key, url, mime, size, now),
    )
    return cur.lastrowid


def column_exists(conn, table, column):
    return any(row["name"] == column for row in conn.execute(f"PRAGMA table_info({table})"))


def upsert_item(conn, project_id, code, module, content_type, title, summary, body, assets, sort_order, featured=False):
    now = now_iso()
    existing = conn.execute("SELECT id FROM content_items WHERE project_id = ? AND code = ? LIMIT 1", (project_id, code)).fetchone()
    meta = {"来源": "uploads/资料自动拆分导入", "拆分原则": "一件事或一个人物独立展示"}
    cover_asset_id = next((asset.get("asset_id") for asset in assets if asset.get("role") == "cover" and asset.get("asset_id")), None)
    values = (
        project_id,
        code,
        module,
        content_type,
        title[:255],
        "",
        summary[:1024],
        json_text(body),
        json_text(meta),
        cover_asset_id,
        sort_order,
        1 if featured else 0,
        1,
        "approved",
        "admin",
        "admin",
        "",
        now,
        now,
    )
    if existing:
        item_id = existing["id"]
        conn.execute(
            """
            UPDATE content_items SET module_key = ?, content_type = ?, title = ?, subtitle = ?,
                summary = ?, body_json = ?, meta_json = ?, cover_asset_id = ?, sort_order = ?,
                featured = ?, enabled = 1, review_status = 'approved', reviewed_by = 'admin',
                review_note = '', updated_at = ?
            WHERE id = ? AND project_id = ?
            """,
            (module, content_type, title[:255], "", summary[:1024], json_text(body), json_text(meta), cover_asset_id,
             sort_order, 1 if featured else 0, now, item_id, project_id),
        )
        conn.execute("DELETE FROM content_item_assets WHERE content_item_id = ?", (item_id,))
    else:
        cur = conn.execute(
            """
            INSERT INTO content_items (
                project_id, code, module_key, content_type, title, subtitle, summary, body_json,
                meta_json, cover_asset_id, sort_order, featured, enabled, review_status,
                submitted_by, reviewed_by, review_note, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            values,
        )
        item_id = cur.lastrowid
    for index, asset in enumerate(assets):
        conn.execute(
            """
            INSERT INTO content_item_assets (content_item_id, asset_id, role, title, caption, url, sort_order, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item_id,
                asset.get("asset_id"),
                asset.get("role", "gallery"),
                asset.get("title", ""),
                asset.get("caption", ""),
                asset.get("url", ""),
                index,
                now,
            ),
        )
    return item_id


def project_map(conn):
    rows = conn.execute("SELECT id, name, portal_slug FROM projects WHERE portal_type = 'topic'").fetchall()
    return {row["portal_slug"]: {"id": row["id"], "name": row["name"]} for row in rows}


def import_docx_path(conn, projects, portal_slug, path, title_override=None, code_prefix="MAT"):
    project = projects[portal_slug]
    doc_slug = f"{portal_slug}/{slugify(path.stem)}"
    paragraphs, _ = docx_paragraphs(path)
    media_map = extract_docx_media(path, doc_slug)
    source_assets = {}
    for media_name, url in media_map.items():
        asset_path = ROOT / url.lstrip("/")
        source_assets[media_name] = register_asset(conn, "admin", url, asset_path, Path(media_name).name)
    image_pool = docx_asset_pool(media_map, source_assets, project["name"])
    sections = choose_sections(split_sections(paragraphs), project["name"])
    if title_override:
        intro = []
        for p in paragraphs:
            if p["text"] and "存在问题" not in p["text"] and p["text"] != "建议":
                intro.append(p["text"])
            if len("".join(intro)) > 220:
                break
        sections.insert(0, {
            "title": title_override,
            "module": "overview",
            "content_type": "article",
            "summary": polish_summary(title_override, "\n".join(intro), project["name"]),
            "paragraphs": intro[:5],
            "images": [name for p in paragraphs for name in p["images"]][:4],
            "code_hint": "overview-department",
        })
    imported = 0
    for index, section in enumerate(sections, start=1):
        assets = []
        for img_index, image_name in enumerate(section["images"]):
            url = media_map.get(image_name)
            if not url:
                continue
            assets.append({
                "asset_id": source_assets.get(image_name),
                "role": "cover" if img_index == 0 else "gallery",
                "title": section["title"],
                "caption": section["title"],
                "url": url,
            })
        if not assets:
            assets = fallback_assets(image_pool, index, section["title"])
        source_key = slugify(path.stem).upper().replace("-", "_")[:36]
        code = f"{code_prefix}-{portal_slug.upper().replace('-', '_')}-{source_key}-{index:03d}"
        upsert_item(
            conn,
            project["id"],
            code,
            section["module"],
            section["content_type"],
            section["title"],
            section["summary"],
            body_blocks(section["paragraphs"]),
            assets,
            index * 10,
            featured=index == 1,
        )
        imported += 1
    return imported


def import_doc(conn, projects, portal_slug, filename, title_override=None, code_prefix="MAT"):
    return import_docx_path(conn, projects, portal_slug, find_source(filename), title_override, code_prefix)


def copy_media_file(conn, portal_slug, path, role="gallery", title="素材图片"):
    rel_key = path.relative_to(SOURCE_ROOT).as_posix()
    dest_dir = IMPORT_ROOT / portal_slug / "standalone"
    dest_dir.mkdir(parents=True, exist_ok=True)
    ext = path.suffix.lower()
    digest = hashlib.sha1(rel_key.encode("utf-8")).hexdigest()[:10]
    safe_name = f"{slugify(path.stem)[:40]}-{digest}{ext}"
    dest = dest_dir / safe_name
    if not dest.exists():
        shutil.copy2(path, dest)
    url = "/" + dest.relative_to(ROOT).as_posix()
    asset_id = register_asset(conn, "admin", url, dest, path.name)
    return {"asset_id": asset_id, "role": role, "title": title, "caption": path.stem, "url": url}


def import_standalone_media(conn, projects):
    imported = 0
    for portal_slug, folder_hint in STANDALONE_MEDIA:
        candidates = [p for p in SOURCE_ROOT.rglob("*") if p.is_file() and folder_hint.replace("/", "\\") in str(p.parent)]
        image_paths = [p for p in candidates if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}]
        for index, path in enumerate(image_paths, start=1):
            title = normalize_text(path.stem)
            asset = copy_media_file(conn, portal_slug, path, "cover", title)
            project = projects[portal_slug]
            code = f"MAT-{portal_slug.upper().replace('-', '_')}-MEDIA-{index:03d}"
            upsert_item(
                conn,
                project["id"],
                code,
                "achievements" if portal_slug != "smart-healthcare" else "training",
                "scene" if portal_slug == "smart-healthcare" else "achievement",
                title,
                f"{title}，作为{project['name']}专题的现场图片资料展示。",
                body_blocks([f"该图片资料来源于原始上传素材，展示{project['name']}相关教学、实训或产教融合场景。"]),
                [asset],
                900 + index,
            )
            imported += 1
    return imported


def import_videos(conn, projects):
    imported = 0
    for portal_slug, folder_hint, module in VIDEO_MEDIA:
        candidates = [p for p in SOURCE_ROOT.rglob("*.mp4") if folder_hint in str(p.parent)]
        for index, path in enumerate(candidates, start=1):
            project = projects[portal_slug]
            asset = copy_media_file(conn, portal_slug, path, "video", path.stem)
            code = f"MAT-{portal_slug.upper().replace('-', '_')}-VIDEO-{index:03d}"
            upsert_item(
                conn,
                project["id"],
                code,
                module,
                "video",
                f"{project['name']}视频资料 {index}",
                f"{project['name']}专题视频资料，可用于前台视频资源展示。",
                body_blocks([f"该视频来源于上传资料目录，作为{project['name']}专题的视频素材单独展示。"]),
                [asset],
                1000 + index,
            )
            imported += 1
    return imported


def plain_text_from_body_json(body_json):
    try:
        blocks = json.loads(body_json or "[]")
    except json.JSONDecodeError:
        return ""
    parts = []
    for block in blocks:
        if isinstance(block, str):
            parts.append(block)
        elif isinstance(block, dict):
            parts.append(str(block.get("text") or block.get("content") or block.get("html") or ""))
    text = re.sub(r"<[^>]+>", " ", "\n".join(parts))
    return normalize_text(text)


def html_from_body_json(body_json, fallback):
    text = plain_text_from_body_json(body_json) or normalize_text(fallback)
    paragraphs = [part.strip() for part in re.split(r"\n+|(?<=。)", text) if part.strip()]
    return "".join(f"<p>{html_escape(part)}</p>" for part in paragraphs[:8])


def first_item_image(conn, content_item_id):
    row = conn.execute(
        """
        SELECT url, asset_id
        FROM content_item_assets
        WHERE content_item_id = ? AND url <> ''
        ORDER BY CASE role WHEN 'cover' THEN 0 WHEN 'gallery' THEN 1 WHEN 'image' THEN 2 ELSE 3 END, sort_order, id
        LIMIT 1
        """,
        (content_item_id,),
    ).fetchone()
    return row["url"] if row else ""


def upsert_market_page(conn, school_project_id, code, title, subtitle, body, image_url, category_key, source, sort_order):
    now = now_iso()
    category = MARKET_CATEGORY_LABELS.get(category_key, "教学科研")
    color = MARKET_CATEGORY_COLORS.get(category_key, "#75BD42")
    existing = conn.execute("SELECT id FROM pages WHERE project_id = ? AND code = ? LIMIT 1", (school_project_id, code)).fetchone()
    if existing:
        page_id = existing["id"]
        conn.execute(
            """
            UPDATE pages SET category = ?, source = ?, published_at = ?, title = ?, subtitle = ?,
                body = ?, image_url = ?, content_type = ?, accent = ?, enabled = 1,
                review_status = 'approved', reviewed_by = 'admin', review_note = '', updated_at = ?
            WHERE id = ? AND project_id = ?
            """,
            (category, source, now[:10], title[:255], subtitle[:512], body, image_url,
             "person" if category_key in {"masters", "alumni", "students"} else ("activity" if category_key == "competitions" else "achievement"),
             color, now, page_id, school_project_id),
        )
    else:
        cur = conn.execute(
            """
            INSERT INTO pages (
                project_id, code, category, source, published_at, title, subtitle, body,
                image_url, image_transform_json, content_type, accent, enabled, updated_at,
                review_status, pending_version_id, submitted_by, reviewed_by, review_note
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, '{}', ?, ?, 1, ?, 'approved', NULL, 'admin', 'admin', '')
            """,
            (
                school_project_id, code, category, source, now[:10], title[:255], subtitle[:512], body,
                image_url, "person" if category_key in {"masters", "alumni", "students"} else ("activity" if category_key == "competitions" else "achievement"),
                color, now,
            ),
        )
        page_id = cur.lastrowid
    snapshot = {
        "code": code,
        "category": category,
        "source": source,
        "publishedAt": now[:10],
        "title": title[:255],
        "subtitle": subtitle[:512],
        "body": body,
        "imageUrl": image_url,
        "contentType": "person" if category_key in {"masters", "alumni", "students"} else ("activity" if category_key == "competitions" else "achievement"),
        "accent": color,
        "enabled": True,
    }
    conn.execute(
        """
        INSERT INTO page_versions (
            page_id, project_id, code, operation, status, snapshot,
            submitted_by, submitted_at, reviewed_by, reviewed_at, changes
        )
        VALUES (?, ?, ?, 'upsert', 'approved', ?, 'admin', ?, 'admin', ?, 'materials-market-sync')
        """,
        (page_id, school_project_id, code, json_text(snapshot), now, now),
    )
    row = conn.execute("SELECT id FROM achievement_market_items WHERE page_id = ? LIMIT 1", (page_id,)).fetchone()
    if row:
        conn.execute(
            """
            UPDATE achievement_market_items
            SET category_key = ?, intro = ?, sort_order = ?, enabled = 1, updated_at = ?
            WHERE id = ?
            """,
            (category_key, subtitle[:240], sort_order, now, row["id"]),
        )
    else:
        conn.execute(
            """
            INSERT INTO achievement_market_items (project_id, page_id, category_key, intro, sort_order, enabled, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, 1, ?, ?)
            """,
            (school_project_id, page_id, category_key, subtitle[:240], sort_order, now, now),
        )
    return page_id


def cleanup_previous_market_import(conn):
    rows = conn.execute("SELECT id FROM pages WHERE code LIKE 'AM-MAT-%'").fetchall()
    page_ids = [row["id"] for row in rows]
    for page_id in page_ids:
        conn.execute("DELETE FROM achievement_market_items WHERE page_id = ?", (page_id,))
        conn.execute("DELETE FROM deployed_pages WHERE page_id = ?", (page_id,))
    conn.execute("DELETE FROM pages WHERE code LIKE 'AM-MAT-%'")
    return len(page_ids)


def sync_market_from_content_items(conn):
    school = conn.execute("SELECT id FROM projects WHERE portal_type = 'school' ORDER BY id LIMIT 1").fetchone()
    if not school:
        return 0
    school_project_id = int(school["id"])
    cleanup_previous_market_import(conn)
    rows = conn.execute(
        """
        SELECT ci.*, p.name AS project_name, p.portal_slug
        FROM content_items ci
        JOIN projects p ON p.id = ci.project_id
        WHERE ci.code LIKE 'MAT-%'
          AND ci.enabled = 1
          AND ci.review_status = 'approved'
          AND ci.module_key IN ('masters', 'alumni', 'students', 'achievements', 'competitions', 'honors')
        ORDER BY p.id, ci.module_key, ci.sort_order, ci.id
        """
    ).fetchall()
    imported = 0
    per_category_counts = {key: 0 for key in set(MARKET_MODULE_CATEGORY.values())}
    for row in rows:
        category_key = MARKET_MODULE_CATEGORY.get(row["module_key"])
        if not category_key:
            continue
        per_category_counts[category_key] = per_category_counts.get(category_key, 0) + 1
        title = row["title"]
        source = f"{row['project_name']}专题"
        subtitle = row["summary"] or f"{source}成果展示"
        body = html_from_body_json(row["body_json"], subtitle)
        image_url = first_item_image(conn, row["id"])
        code_seed = row["code"].replace("MAT-", "").replace("MAT_DEPT-", "")
        code = f"AM-MAT-{category_key.upper()}-{slugify(code_seed).upper()[:54]}"
        upsert_market_page(
            conn,
            school_project_id,
            code,
            title,
            subtitle,
            body,
            image_url,
            category_key,
            source,
            per_category_counts[category_key] * 10,
        )
        imported += 1
    now = now_iso()
    carousel = [
        row["image_url"] for row in conn.execute(
            """
            SELECT image_url
            FROM pages
            WHERE project_id = ? AND code LIKE 'AM-MAT-%' AND image_url <> ''
            ORDER BY updated_at DESC, id DESC
            LIMIT 8
            """,
            (school_project_id,),
        ).fetchall()
    ]
    welcome_image = carousel[0] if carousel else ""
    conn.execute(
        """
        INSERT OR REPLACE INTO achievement_market_config (
            id, welcome_title, welcome_subtitle, welcome_intro, welcome_image_url,
            welcome_carousel_json, welcome_note, updated_at
        )
        VALUES (1, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "成果超市",
            "校园成果集中展示",
            "集中呈现名匠名师、优秀校友、优秀学生、教学科研、技能大赛与荣誉资质等成果项目，扫码即可进入单项展示。",
            welcome_image,
            json_text(carousel),
            "由上传资料自动整理，可在后台继续编辑每个成果项目。",
            now,
        ),
    )
    conn.execute(
        """
        UPDATE projects
        SET content_deployed = CASE WHEN id = ? THEN 1 ELSE content_deployed END,
            content_deployed_at = CASE WHEN id = ? THEN ? ELSE content_deployed_at END
        """,
        (school_project_id, school_project_id, now),
    )
    conn.execute("DELETE FROM deployed_pages")
    page_rows = conn.execute(
        "SELECT id FROM pages WHERE project_id = ? AND code LIKE 'AM-MAT-%' AND enabled = 1 ORDER BY id",
        (school_project_id,),
    ).fetchall()
    for page in page_rows:
        conn.execute(
            "INSERT OR IGNORE INTO deployed_pages (project_id, page_id, updated_at) VALUES (?, ?, ?)",
            (school_project_id, page["id"], now),
        )
    return imported


def fill_missing_content_assets(conn):
    rows = conn.execute(
        """
        SELECT ci.id, ci.title, p.portal_slug
        FROM content_items ci
        JOIN projects p ON p.id = ci.project_id
        WHERE ci.code LIKE 'MAT-%'
          AND NOT EXISTS (SELECT 1 FROM content_item_assets cia WHERE cia.content_item_id = ci.id)
        ORDER BY ci.project_id, ci.sort_order, ci.id
        """
    ).fetchall()
    filled = 0
    now = now_iso()
    for row in rows:
        asset = conn.execute(
            """
            SELECT cia.asset_id, cia.url
            FROM content_item_assets cia
            JOIN content_items ci ON ci.id = cia.content_item_id
            JOIN projects p ON p.id = ci.project_id
            WHERE p.portal_slug = ? AND cia.url <> ''
            ORDER BY CASE cia.role WHEN 'cover' THEN 0 WHEN 'gallery' THEN 1 ELSE 2 END, cia.id
            LIMIT 1
            """,
            (row["portal_slug"],),
        ).fetchone()
        if not asset:
            continue
        conn.execute(
            """
            INSERT INTO content_item_assets (content_item_id, asset_id, role, title, caption, url, sort_order, created_at)
            VALUES (?, ?, 'cover', ?, ?, ?, 0, ?)
            """,
            (row["id"], asset["asset_id"], row["title"], row["title"], asset["url"], now),
        )
        conn.execute("UPDATE content_items SET cover_asset_id = ?, updated_at = ? WHERE id = ?", (asset["asset_id"], now, row["id"]))
        filled += 1
    return filled


def cleanup_previous_import(conn):
    rows = conn.execute("SELECT id FROM content_items WHERE code LIKE 'MAT-%'").fetchall()
    ids = [row["id"] for row in rows]
    for item_id in ids:
        conn.execute("DELETE FROM content_item_assets WHERE content_item_id = ?", (item_id,))
    conn.execute("DELETE FROM content_items WHERE code LIKE 'MAT-%'")
    return len(ids)


def main():
    if not DB_PATH.exists():
        raise SystemExit(f"Database not found: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    with conn:
        removed = cleanup_previous_import(conn)
        if removed:
            print(f"removed {removed} previous MAT imported items")
        projects = project_map(conn)
        total = 0
        for portal_slug, filename in PROJECT_DOCS:
            if portal_slug not in projects:
                print(f"skip missing project {portal_slug}")
                continue
            count = import_doc(conn, projects, portal_slug, filename)
            total += count
            print(f"imported {count:3d} items from {filename}")
        for portal_slug, filename, title in DEPARTMENT_DOCS:
            if portal_slug not in projects:
                continue
            try:
                count = import_doc(conn, projects, portal_slug, filename, title_override=title, code_prefix="MAT-DEPT")
                total += count
                print(f"imported {count:3d} department items from {filename}")
            except FileNotFoundError:
                print(f"skip missing department doc {filename}")
        for portal_slug, path, title in LEGACY_CONVERTED_DOCS:
            if portal_slug not in projects or not path.exists():
                print(f"skip missing converted legacy doc {path}")
                continue
            count = import_docx_path(conn, projects, portal_slug, path, title_override=title, code_prefix="MAT-LEGACY")
            total += count
            print(f"imported {count:3d} legacy doc items from {path.name}")
        media_count = import_standalone_media(conn, projects)
        video_count = import_videos(conn, projects)
        total += media_count + video_count
        filled_count = fill_missing_content_assets(conn)
        market_count = sync_market_from_content_items(conn)
        print(f"imported {media_count:3d} standalone image items")
        print(f"imported {video_count:3d} video items")
        print(f"filled   {filled_count:3d} content items with fallback cover images")
        print(f"synced   {market_count:3d} achievement market items")
        print(f"total imported/updated {total} content items")


if __name__ == "__main__":
    main()
