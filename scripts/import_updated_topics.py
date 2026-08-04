# -*- coding: utf-8 -*-
"""Import the 2026-08-04 topic Word materials into blueprint topic JSON."""

import json
import re
import sqlite3
import sys
from collections import OrderedDict
from datetime import datetime, timezone
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sucai.extract_content import (
    DATA_ROOT,
    MEDIA_ROOT,
    attach_captions,
    extract_docx_blocks,
    process_images,
    split_sections,
)

DB_PATH = ROOT / "expo.db"


TOPICS = [
    {
        "id": "finance-commerce",
        "name": "财经商贸",
        "docx": Path("uploads/创新育人-财经商贸2026.8.4更新.docx"),
        "summary": "聚焦德商融合、数商兴农、赛商砺能、服商赋能，围绕电子商务、大数据与会计、现代物流管理等专业，展示财经商贸类人才培养、产教融合、技能竞赛和服务乡村振兴成果。",
        "stats": [
            {"label": "在校生", "value": "约1600人"},
            {"label": "省级项目", "value": "11项"},
            {"label": "技能竞赛", "value": "400余项"},
            {"label": "专业方向", "value": "电商/会计/物流"},
        ],
        "cover_index": 1,
    },
    {
        "id": "modern-agriculture",
        "name": "现代农业",
        "docx": Path("uploads/创新育人-现代农业(1).docx"),
        "summary": "面向山地特色农业、生态食品加工、茶叶与中草药产业、畜牧兽医和农产品质量检测，呈现农业工程系服务乡村振兴、产教融合和数智化农业人才培养成果。",
        "stats": [
            {"label": "专业教师", "value": "50人"},
            {"label": "在校生", "value": "1750人"},
            {"label": "实训设备", "value": "3000余万元"},
            {"label": "竞赛成果", "value": "100余项"},
        ],
        "cover_index": 1,
    },
]

MODULES = OrderedDict(
    [
        ("overview", {"title": "专题概况", "aliases": {"基本情况", "专题概况", "系部简介"}, "contentType": "article"}),
        ("majors", {"title": "专业群布局", "aliases": {"专业设置", "专业群布局", "专业群"}, "contentType": "article"}),
        ("training", {"title": "实训场景", "aliases": {"实训基地", "实训场景"}, "contentType": "scene"}),
        ("cooperation", {"title": "产教协同", "aliases": {"产教融合", "产教协同", "校企合作"}, "contentType": "activity"}),
        ("masters", {"title": "名师名匠", "aliases": {"名师名匠"}, "contentType": "person"}),
        ("alumni", {"title": "优秀校友", "aliases": {"优秀校友"}, "contentType": "person"}),
        ("students", {"title": "优秀学生", "aliases": {"优秀学生", "学生风采"}, "contentType": "person"}),
        ("achievements", {"title": "专题成果", "aliases": {"教学成果", "专题成果", "教学与创新成果"}, "contentType": "achievement"}),
        ("competitions", {"title": "技能大赛", "aliases": {"技能大赛"}, "contentType": "activity"}),
        ("honors", {"title": "荣誉资质", "aliases": {"荣誉资质"}, "contentType": "honor"}),
        ("media", {"title": "视频资源", "aliases": {"视频资源", "视频资料"}, "contentType": "video"}),
    ]
)

ALIAS_TO_ID = {alias: key for key, meta in MODULES.items() for alias in meta["aliases"]}
DROP_EXACT = {"无", "暂无", "补充人物照片", "补充大师工作室-大师、优秀校友", "补充系部对接产业领域"}
DROP_CONTAINS = ["../NULL", "图片下文字不全", "需进一步补充", "待补充"]
KEEP_SHORT_PREFIX = (
    "姓名：",
    "入学：",
    "毕业",
    "专业：",
    "座右铭：",
    "核心课程：",
    "就业方向：",
    "培养目标：",
    "职业面向：",
    "专业特色：",
)


def module_id_for_title(title):
    return ALIAS_TO_ID.get(str(title or "").strip(), "achievements")


def compact_text(text):
    return re.sub(r"\s+", " ", str(text or "")).strip()


def is_drop_text(text):
    text = compact_text(text)
    if not text or text in DROP_EXACT:
        return True
    return any(part in text for part in DROP_CONTAINS)


def caption_candidate(text):
    text = compact_text(text)
    if not text or len(text) > 48:
        return False
    if text.startswith(KEEP_SHORT_PREFIX):
        return False
    if text in DROP_EXACT:
        return False
    if re.match(r"^[一二三四五六七八九十]+[、.]", text):
        return False
    return not (text.endswith("：") or text.endswith(":"))


def clean_blocks(blocks):
    cleaned = []
    for block in blocks:
        if block.get("type") == "text":
            text = compact_text(block.get("content", ""))
            if not is_drop_text(text):
                cleaned.append({"type": "text", "content": text})
        elif block.get("type") == "image" and block.get("src"):
            src = str(block.get("src") or "")
            if "NULL" in src.upper():
                continue
            item = {"type": "image", "src": src}
            caption = compact_text(block.get("caption", ""))
            if caption and not is_drop_text(caption):
                item["caption"] = caption
            cleaned.append(item)
        elif block.get("type") == "video" and (block.get("src") or block.get("poster")):
            cleaned.append(block)

    out = []
    i = 0
    while i < len(cleaned):
        block = dict(cleaned[i])
        if block.get("type") == "image":
            if not block.get("caption") and out and out[-1].get("type") == "text" and caption_candidate(out[-1].get("content")):
                block["caption"] = out[-1]["content"]
            if (
                not block.get("caption")
                and i + 1 < len(cleaned)
                and cleaned[i + 1].get("type") == "text"
                and caption_candidate(cleaned[i + 1].get("content"))
            ):
                block["caption"] = cleaned[i + 1]["content"]
                i += 1
        out.append(block)
        i += 1
    return out


def build_topic(config):
    blocks, _ = extract_docx_blocks(config["docx"])
    raw_sections = split_sections(blocks)
    media_dir = MEDIA_ROOT / "topics" / config["id"] / "images"
    media_dir.mkdir(parents=True, exist_ok=True)
    merged = OrderedDict(
        (
            key,
            {
                "id": key,
                "title": meta["title"],
                "contentType": meta["contentType"],
                "blocks": [],
            },
        )
        for key, meta in MODULES.items()
    )
    counter = [0]
    cover_url = ""

    for raw in raw_sections:
        module_id = module_id_for_title(raw.get("title"))
        processed, section_cover = process_images(
            config["docx"],
            raw.get("blocks", []),
            media_dir,
            counter,
            config.get("cover_index", 1) if not cover_url else 999999,
        )
        processed = clean_blocks(attach_captions(processed))
        if processed:
            if merged[module_id]["blocks"]:
                merged[module_id]["blocks"].append({"type": "text", "content": MODULES[module_id]["title"] + "补充资料"})
            merged[module_id]["blocks"].extend(processed)
        if not cover_url and section_cover:
            cover_url = section_cover

    if not cover_url:
        for section in merged.values():
            for block in section["blocks"]:
                if block.get("type") == "image":
                    cover_url = block["src"]
                    break
            if cover_url:
                break

    sections = []
    for key, section in merged.items():
        if not section["blocks"]:
            continue
        section["backendUpdatedAt"] = "2026-08-04"
        section["backendPageCode"] = f"{config['id']}-{key}"
        sections.append(section)

    return {
        "id": config["id"],
        "type": "topic",
        "name": config["name"],
        "summary": config["summary"],
        "cover": cover_url,
        "stats": config["stats"],
        "sections": sections,
    }


def block_image_url(blocks):
    for block in blocks:
        if block.get("type") == "image" and block.get("src"):
            return block["src"]
        if block.get("type") == "video" and (block.get("poster") or block.get("src")):
            return block.get("poster") or block.get("src")
    return ""


def blocks_to_html(blocks):
    parts = []
    for block in blocks:
        if block.get("type") == "text":
            text = compact_text(block.get("content", ""))
            if text:
                parts.append(f"<p>{escape(text)}</p>")
        elif block.get("type") == "image" and block.get("src"):
            src = escape(block["src"], quote=True)
            caption = compact_text(block.get("caption", ""))
            alt = escape(caption or "专题图片", quote=True)
            figcaption = f"<figcaption>{escape(caption)}</figcaption>" if caption else ""
            parts.append(f'<figure><img src="{src}" alt="{alt}" />{figcaption}</figure>')
        elif block.get("type") == "video" and block.get("src"):
            src = escape(block["src"], quote=True)
            title = escape(compact_text(block.get("title", "视频资源")), quote=True)
            parts.append(f'<video controls src="{src}" title="{title}"></video>')
    return "\n".join(parts)


def blocks_to_body_json(blocks):
    body = []
    for block in blocks:
        if block.get("type") == "text":
            text = compact_text(block.get("content", ""))
            if text:
                body.append({"type": "paragraph", "text": text})
    return body


def section_assets(section):
    assets = []
    for block in section.get("blocks", []):
        if block.get("type") == "image" and block.get("src"):
            role = "certificate" if section["id"] == "honors" else "gallery"
            if not assets:
                role = "cover"
            assets.append(
                {
                    "url": block["src"],
                    "caption": compact_text(block.get("caption", "")),
                    "role": role,
                }
            )
        elif block.get("type") == "video" and block.get("src"):
            assets.append(
                {
                    "url": block["src"],
                    "caption": compact_text(block.get("title", "")),
                    "role": "video",
                }
            )
    return assets


def table_exists(conn, name):
    return bool(conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name = ?", (name,)).fetchone())


def table_columns(conn, name):
    return {row[1] for row in conn.execute(f"PRAGMA table_info({name})")}


def upsert_page(conn, project_id, section, now, sort_order):
    code = section["backendPageCode"]
    image_url = block_image_url(section.get("blocks", []))
    body = blocks_to_html(section.get("blocks", []))
    row = conn.execute("SELECT id FROM pages WHERE project_id = ? AND code = ?", (project_id, code)).fetchone()
    values = (
        section["title"],
        "",
        body,
        image_url,
        "#f59a13",
        1,
        now,
        section["title"],
        "创新育人专题",
        "2026-08-04",
        section["contentType"],
        "approved",
        None,
        "admin",
        "admin",
        "",
    )
    if row:
        conn.execute(
            """
            UPDATE pages SET title = ?, subtitle = ?, body = ?, image_url = ?, accent = ?,
                enabled = ?, updated_at = ?, category = ?, source = ?, published_at = ?,
                content_type = ?, review_status = ?, pending_version_id = ?,
                submitted_by = ?, reviewed_by = ?, review_note = ?
            WHERE id = ?
            """,
            (*values, row["id"]),
        )
        return row["id"]
    cursor = conn.execute(
        """
        INSERT INTO pages (
            project_id, code, title, subtitle, body, image_url, accent, enabled,
            updated_at, category, source, published_at, content_type, review_status,
            pending_version_id, submitted_by, reviewed_by, review_note
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (project_id, code, *values),
    )
    return cursor.lastrowid


def upsert_content_item(conn, project_id, page_id, section, now, sort_order, source_doc):
    if not table_exists(conn, "content_items"):
        return
    columns = table_columns(conn, "content_items")
    required = {"project_id", "page_id", "code", "module_key", "content_type", "title", "body_json", "meta_json"}
    if not required.issubset(columns):
        return

    code = section["backendPageCode"]
    texts = [compact_text(b.get("content", "")) for b in section.get("blocks", []) if b.get("type") == "text"]
    summary = texts[0][:360] if texts else ""
    body_json = json.dumps(blocks_to_body_json(section.get("blocks", [])), ensure_ascii=False)
    meta_json = json.dumps({"sourceDoc": source_doc, "updatedAt": "2026-08-04"}, ensure_ascii=False)
    row = conn.execute("SELECT id FROM content_items WHERE project_id = ? AND code = ?", (project_id, code)).fetchone()
    values = (
        project_id,
        page_id,
        code,
        section["id"],
        section["contentType"],
        section["title"],
        "",
        summary,
        body_json,
        meta_json,
        None,
        sort_order,
        1 if section["id"] in {"overview", "achievements"} else 0,
        1,
        "approved",
        None,
        "admin",
        "admin",
        "",
        now,
    )
    if row:
        conn.execute(
            """
            UPDATE content_items SET project_id = ?, page_id = ?, code = ?, module_key = ?,
                content_type = ?, title = ?, subtitle = ?, summary = ?, body_json = ?,
                meta_json = ?, cover_asset_id = ?, sort_order = ?, featured = ?, enabled = ?,
                review_status = ?, pending_version_id = ?, submitted_by = ?, reviewed_by = ?,
                review_note = ?, updated_at = ?
            WHERE id = ?
            """,
            (*values, row["id"]),
        )
        item_id = row["id"]
    else:
        cursor = conn.execute(
            """
            INSERT INTO content_items (
                project_id, page_id, code, module_key, content_type, title, subtitle, summary,
                body_json, meta_json, cover_asset_id, sort_order, featured, enabled,
                review_status, pending_version_id, submitted_by, reviewed_by, review_note,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (*values, now),
        )
        item_id = cursor.lastrowid

    if table_exists(conn, "content_item_assets"):
        conn.execute("DELETE FROM content_item_assets WHERE content_item_id = ?", (item_id,))
        for index, asset in enumerate(section_assets(section)):
            conn.execute(
                """
                INSERT INTO content_item_assets (
                    content_item_id, asset_id, role, title, caption, url, sort_order, created_at
                ) VALUES (?, NULL, ?, ?, ?, ?, ?, ?)
                """,
                (item_id, asset["role"], asset["caption"], asset["caption"], asset["url"], index, now),
            )


def sync_topic_to_database(data, source_doc):
    if not DB_PATH.exists():
        print(f"database_missing={DB_PATH}")
        return
    now = datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        project = conn.execute(
            "SELECT id FROM projects WHERE portal_type = 'topic' AND portal_slug = ?",
            (data["id"],),
        ).fetchone()
        if not project:
            print(f"database_project_missing={data['id']}")
            return
        project_id = project["id"]
        conn.execute(
            """
            UPDATE projects SET name = ?, idle_title = ?, idle_copy = ?,
                default_image_url = ?, updated_at = ?
            WHERE id = ?
            """,
            (data["name"], data["name"], data["summary"], data["cover"], now, project_id),
        )
        conn.execute(
            "UPDATE pages SET enabled = 0, review_status = 'deleted', updated_at = ? WHERE project_id = ?",
            (now, project_id),
        )
        if table_exists(conn, "content_items"):
            conn.execute(
                "UPDATE content_items SET enabled = 0, review_status = 'deleted', updated_at = ? WHERE project_id = ?",
                (now, project_id),
            )
        for index, section in enumerate(data["sections"]):
            page_id = upsert_page(conn, project_id, section, now, index)
            upsert_content_item(conn, project_id, page_id, section, now, index, source_doc)
        conn.commit()
    print(f"database_synced={data['id']} project_id={project_id} sections={len(data['sections'])}")


def main():
    for config in TOPICS:
        data = build_topic(config)
        out = DATA_ROOT / "topics" / f"{config['id']}.json"
        out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        sync_topic_to_database(data, config["docx"].name)
        total_images = sum(1 for sec in data["sections"] for block in sec["blocks"] if block.get("type") == "image")
        total_texts = sum(1 for sec in data["sections"] for block in sec["blocks"] if block.get("type") == "text")
        print(f"updated {out}: sections={len(data['sections'])} texts={total_texts} images={total_images} cover={data['cover']}")
        print("section_ids=" + ",".join(sec["id"] for sec in data["sections"]))


if __name__ == "__main__":
    main()
