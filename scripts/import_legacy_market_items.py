import argparse
import os
import shutil
import sqlite3
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from db_backend import connect_database


DEFAULT_SOURCE_DB = ROOT / "database" / "expo-latest.db"
DEFAULT_SOURCE_UPLOADS = ROOT / "backup-before-reset-20260810-165734" / "uploads"
DEFAULT_CODES = ("BJ-SERVICE", "BJ-INTL", "BJ-GRAD", "BJ-TEACHER", "DEMO-10100043")

CATEGORY_MAP = {
    "BJ-TEACHER": "masters",
    "BJ-GRAD": "alumni",
    "BJ-SERVICE": "innovation",
    "BJ-INTL": "innovation",
    "DEMO-10100043": "innovation",
}

SORT_ORDER = {
    "BJ-TEACHER": 10,
    "BJ-GRAD": 20,
    "BJ-SERVICE": 30,
    "BJ-INTL": 40,
    "DEMO-10100043": 90,
}


def load_env(path):
    env_path = Path(path)
    if not env_path.is_absolute():
        env_path = ROOT / env_path
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def sqlite_row(conn, sql, params=()):
    row = conn.execute(sql, params).fetchone()
    return dict(row) if row else None


def sqlite_rows(conn, sql, params=()):
    return [dict(row) for row in conn.execute(sql, params).fetchall()]


def copy_legacy_uploads(source_uploads, target_uploads):
    copied = []
    if not source_uploads.exists():
        return copied
    target_uploads.mkdir(parents=True, exist_ok=True)
    for name in ("bijie-samples",):
        source = source_uploads / name
        target = target_uploads / name
        if source.exists() and source.is_dir():
            shutil.copytree(source, target, dirs_exist_ok=True)
            copied.append(str(target.relative_to(ROOT)))
    for name in (
        "4fcaa6e34b5f40c7a7e2b58947b9de1c.jpg",
        "acc2be26d71f4981b3c1f125390266a8.png",
        "fad5544323334f97a45f6afcf1eac08c.jpg",
    ):
        source = source_uploads / name
        target = target_uploads / name
        if source.exists() and not target.exists():
            shutil.copy2(source, target)
            copied.append(str(target.relative_to(ROOT)))
    return copied


def upsert_project(mysql_conn, project):
    existing = mysql_conn.execute(
        """
        SELECT id FROM projects
        WHERE portal_type = ? AND portal_slug = ? AND name = ?
        ORDER BY id
        LIMIT 1
        """,
        (project.get("portal_type") or "school", project.get("portal_slug") or "", project["name"]),
    ).fetchone()
    values = (
        project["name"],
        project.get("portal_type") or "school",
        project.get("portal_slug") or "",
        project.get("idle_kicker") or "学校简介",
        project.get("idle_title") or project["name"],
        project.get("idle_copy") or "",
        project.get("welcome_kicker") or "Welcome",
        project.get("welcome_title") or "欢迎参观 {title}",
        project.get("welcome_subtitle") or "即将进入展示页面",
        project.get("default_image_url") or "/static/expo-stage.png",
        project.get("accent") or "#49c5b6",
        project.get("display_config") or "{}",
        1 if project.get("deployed") else 0,
        1,
        project.get("updated_at") or "",
        project.get("updated_at") or "",
        "admin",
        project.get("config_status") or "approved",
        project.get("updated_at") or "",
    )
    if existing:
        project_id = existing["id"]
        mysql_conn.execute(
            """
            UPDATE projects SET
                name = ?, portal_type = ?, portal_slug = ?,
                idle_kicker = ?, idle_title = ?, idle_copy = ?,
                welcome_kicker = ?, welcome_title = ?, welcome_subtitle = ?,
                default_image_url = ?, accent = ?, display_config = ?,
                deployed = ?, content_deployed = ?,
                deployed_at = CASE WHEN deployed_at = '' THEN ? ELSE deployed_at END,
                content_deployed_at = ?,
                owner_username = ?, config_status = ?, updated_at = ?
            WHERE id = ?
            """,
            (*values, project_id),
        )
        return int(project_id), "updated"

    result = mysql_conn.execute(
        """
        INSERT INTO projects (
            name, portal_type, portal_slug,
            idle_kicker, idle_title, idle_copy,
            welcome_kicker, welcome_title, welcome_subtitle,
            default_image_url, accent, display_config,
            deployed, content_deployed, deployed_at, content_deployed_at,
            owner_username, config_status, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        values,
    )
    return int(result.lastrowid), "created"


def upsert_page(mysql_conn, project_id, page):
    existing = mysql_conn.execute(
        "SELECT id FROM pages WHERE project_id = ? AND code = ? LIMIT 1",
        (project_id, page["code"]),
    ).fetchone()
    values = (
        project_id,
        page["code"],
        page.get("category") or "成果展示",
        page.get("source") or "毕节职业技术学院",
        page.get("published_at") or "",
        page["title"],
        page.get("subtitle") or "",
        page.get("body") or "",
        page.get("image_url") or "",
        page.get("content_type") or "article",
        page.get("accent") or "#0f766e",
        1,
        "approved",
        None,
        "admin",
        "admin",
        "",
        page.get("updated_at") or "",
    )
    if existing:
        page_id = existing["id"]
        mysql_conn.execute(
            """
            UPDATE pages SET
                category = ?, source = ?, published_at = ?, title = ?, subtitle = ?,
                body = ?, image_url = ?, content_type = ?, accent = ?,
                enabled = ?, review_status = ?, pending_version_id = ?,
                submitted_by = ?, reviewed_by = ?, review_note = ?, updated_at = ?
            WHERE id = ?
            """,
            (*values[2:], page_id),
        )
        return int(page_id), "updated"

    result = mysql_conn.execute(
        """
        INSERT INTO pages (
            project_id, code, category, source, published_at, title, subtitle,
            body, image_url, content_type, accent, enabled, review_status,
            pending_version_id, submitted_by, reviewed_by, review_note, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        values,
    )
    return int(result.lastrowid), "created"


def intro_for_page(page):
    return (page.get("subtitle") or page.get("title") or "")[:240]


def upsert_market_item(mysql_conn, project_id, page_id, page):
    code = page["code"]
    category_key = CATEGORY_MAP.get(code, "innovation")
    now = page.get("updated_at") or ""
    mysql_conn.execute(
        """
        INSERT INTO achievement_market_items (
            project_id, page_id, category_key, intro, sort_order,
            enabled, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, 1, ?, ?)
        ON DUPLICATE KEY UPDATE
            project_id = VALUES(project_id),
            category_key = VALUES(category_key),
            intro = VALUES(intro),
            sort_order = VALUES(sort_order),
            enabled = 1,
            updated_at = VALUES(updated_at)
        """,
        (project_id, page_id, category_key, intro_for_page(page), SORT_ORDER.get(code, 100), now, now),
    )


def sync_deployment(mysql_conn, project_id, page_ids):
    now = page_ids[0][1].get("updated_at") if page_ids else ""
    mysql_conn.execute(
        """
        UPDATE projects
        SET content_deployed = CASE WHEN id = ? THEN 1 ELSE 0 END,
            content_deployed_at = CASE WHEN id = ? THEN ? ELSE content_deployed_at END
        """,
        (project_id, project_id, now),
    )
    for page_id, page in page_ids:
        mysql_conn.execute(
            """
            INSERT INTO deployed_pages (project_id, page_id, updated_at)
            VALUES (?, ?, ?)
            ON DUPLICATE KEY UPDATE updated_at = VALUES(updated_at)
            """,
            (project_id, page_id, page.get("updated_at") or now),
        )


def import_legacy_market_items(source_db, source_uploads, target_uploads, codes):
    sqlite_conn = sqlite3.connect(source_db)
    sqlite_conn.row_factory = sqlite3.Row
    try:
        project = sqlite_row(sqlite_conn, "SELECT * FROM projects WHERE id = ?", (15,))
        if not project:
            raise RuntimeError("旧库中没有找到 project id=15")
        placeholders = ",".join("?" for _ in codes)
        pages = sqlite_rows(
            sqlite_conn,
            f"""
            SELECT *
            FROM pages
            WHERE project_id = ? AND code IN ({placeholders})
            ORDER BY id
            """,
            (project["id"], *codes),
        )
    finally:
        sqlite_conn.close()

    if not pages:
        raise RuntimeError("旧库中没有找到可导入的扫码展示页")

    copied = copy_legacy_uploads(source_uploads, target_uploads)
    with connect_database(ROOT / "expo.db") as mysql_conn:
        project_id, project_status = upsert_project(mysql_conn, project)
        imported_pages = []
        for page in pages:
            page_id, page_status = upsert_page(mysql_conn, project_id, page)
            upsert_market_item(mysql_conn, project_id, page_id, page)
            imported_pages.append((page_id, page))
            print(f"{page_status}: page {page['code']} -> {page_id}")
        sync_deployment(mysql_conn, project_id, imported_pages)

    print(f"{project_status}: project {project['name']} -> {project_id}")
    print(f"market_items: {len(imported_pages)}")
    if copied:
        print("copied_uploads:")
        for path in copied:
            print(f"  {path}")
    return project_id, imported_pages


def main():
    parser = argparse.ArgumentParser(description="Import legacy scanner display pages into Achievement Market.")
    parser.add_argument("--env", default=".env.local-runtime", help="runtime env file")
    parser.add_argument("--source-db", default=str(DEFAULT_SOURCE_DB), help="legacy SQLite database")
    parser.add_argument("--source-uploads", default=str(DEFAULT_SOURCE_UPLOADS), help="legacy uploads directory")
    parser.add_argument("--target-uploads", default=str(ROOT / "uploads"), help="current uploads directory")
    parser.add_argument("--codes", nargs="*", default=list(DEFAULT_CODES), help="page codes to import")
    args = parser.parse_args()

    load_env(args.env)
    os.environ["DATABASE_BACKEND"] = "mysql"
    import_legacy_market_items(
        Path(args.source_db),
        Path(args.source_uploads),
        Path(args.target_uploads),
        tuple(args.codes),
    )


if __name__ == "__main__":
    main()
