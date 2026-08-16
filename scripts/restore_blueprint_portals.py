import os
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

os.environ.setdefault("ENV_FILE", str(ROOT / ".env.local-runtime"))

import server


DEFAULT_BLUEPRINT_ZIP = ROOT / "backup-before-reset-20260810-165734" / "static-blueprint-data.zip"


def load_zip_json(zip_path, portal_type, portal_slug):
    if not zip_path.exists():
        return None
    folder = "topics" if server.normalize_portal_type(portal_type) == "topic" else "departments"
    wanted = f"{folder}/{server.normalize_portal_slug(portal_slug)}.json"
    with zipfile.ZipFile(zip_path) as archive:
        names = {name.replace("\\", "/"): name for name in archive.namelist()}
        name = names.get(wanted)
        if not name:
            return None
        return server.json.loads(archive.read(name).decode("utf-8-sig"))


def install_zip_blueprint_loader(zip_path):
    original_loader = server.load_blueprint_json

    def load_blueprint_json(portal_type, portal_slug):
        data = load_zip_json(zip_path, portal_type, portal_slug)
        if data and data.get("sections"):
            return data
        return original_loader(portal_type, portal_slug)

    server.load_blueprint_json = load_blueprint_json


def main():
    if DEFAULT_BLUEPRINT_ZIP.exists():
        install_zip_blueprint_loader(DEFAULT_BLUEPRINT_ZIP)

    with server.db_connect() as conn:
        before_projects = conn.execute("SELECT COUNT(*) AS value FROM projects").fetchone()["value"]
        before_pages = conn.execute("SELECT COUNT(*) AS value FROM pages").fetchone()["value"]
        before_items = conn.execute("SELECT COUNT(*) AS value FROM content_items").fetchone()["value"]

        server.ensure_blueprint_portal_projects(conn)
        server.ensure_blueprint_pages(conn)
        server.ensure_blueprint_content_items(conn)
        server.ensure_special_experience_links(conn)

        after_projects = conn.execute("SELECT COUNT(*) AS value FROM projects").fetchone()["value"]
        after_pages = conn.execute("SELECT COUNT(*) AS value FROM pages").fetchone()["value"]
        after_items = conn.execute("SELECT COUNT(*) AS value FROM content_items").fetchone()["value"]
        portals = conn.execute(
            """
            SELECT id, name, portal_type, portal_slug
            FROM projects
            ORDER BY
              CASE portal_type WHEN 'school' THEN 0 WHEN 'department' THEN 1 ELSE 2 END,
              id
            """
        ).fetchall()

    print(f"projects: {before_projects} -> {after_projects}")
    print(f"pages: {before_pages} -> {after_pages}")
    print(f"content_items: {before_items} -> {after_items}")
    for portal in portals:
        slug = portal["portal_slug"] or "-"
        print(f"{portal['id']}: {portal['name']} [{portal['portal_type']}/{slug}]")


if __name__ == "__main__":
    main()
