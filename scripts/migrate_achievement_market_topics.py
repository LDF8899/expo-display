from __future__ import annotations

import argparse
import shutil
import sqlite3
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path


TOPIC_MARKERS = {
    "MODERN-AGRICULTURE": "modern-agriculture",
    "DIGITAL-TOURISM": "digital-tourism",
    "SMART-HEALTHCARE": "smart-healthcare",
    "FINANCE-COMMERCE": "finance-commerce",
    "DIGITAL-INTELLIGENCE": "digital-intelligence",
    "SMART-ENERGY": "smart-energy",
    "SMART-MANUFACTURING": "smart-manufacturing",
}


def topic_from_code(code: str) -> str:
    upper_code = (code or "").upper()
    matches = [slug for marker, slug in TOPIC_MARKERS.items() if marker in upper_code]
    if len(matches) != 1:
        return ""
    return matches[0]


def rows_by_topic(rows):
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["target_slug"]].append(row)
    return grouped


def print_summary(rows):
    for slug, topic_rows in sorted(rows_by_topic(rows).items()):
        categories = defaultdict(int)
        for row in topic_rows:
            categories[row["category_key"]] += 1
        category_text = ", ".join(f"{key}:{count}" for key, count in sorted(categories.items()))
        print(f"- {slug}: {len(topic_rows)} ({category_text})")


def main() -> int:
    parser = argparse.ArgumentParser(description="Move achievement-market pages into topic projects by code marker.")
    parser.add_argument("--db", default=str(Path(__file__).resolve().parents[1] / "expo.db"))
    parser.add_argument("--apply", action="store_true", help="write changes; omit for dry run")
    parser.add_argument("--no-backup", action="store_true", help="skip database backup when applying")
    args = parser.parse_args()

    db_path = Path(args.db).resolve()
    if not db_path.exists():
        print(f"Database not found: {db_path}", file=sys.stderr)
        return 2

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    projects = {
        row["portal_slug"]: row
        for row in conn.execute(
            """
            SELECT id, name, portal_slug
            FROM projects
            WHERE portal_type = 'topic'
            """
        ).fetchall()
    }
    missing_topics = [slug for slug in TOPIC_MARKERS.values() if slug not in projects]
    if missing_topics:
        print("Missing topic projects: " + ", ".join(missing_topics), file=sys.stderr)
        return 2

    source_rows = conn.execute(
        """
        SELECT ami.id AS item_id, ami.project_id AS item_project_id, ami.category_key,
               ami.page_id, pages.project_id AS page_project_id, pages.code, pages.title
        FROM achievement_market_items ami
        JOIN pages ON pages.id = ami.page_id
        ORDER BY pages.code
        """
    ).fetchall()

    assignments = []
    unmatched = []
    ambiguous = []
    for row in source_rows:
        upper_code = (row["code"] or "").upper()
        matches = [slug for marker, slug in TOPIC_MARKERS.items() if marker in upper_code]
        if not matches:
            unmatched.append(row)
            continue
        if len(matches) > 1:
            ambiguous.append((row, matches))
            continue
        slug = matches[0]
        target = projects[slug]
        assignments.append(
            {
                "item_id": row["item_id"],
                "page_id": row["page_id"],
                "code": row["code"],
                "title": row["title"],
                "category_key": row["category_key"],
                "target_slug": slug,
                "target_project_id": int(target["id"]),
                "target_project_name": target["name"],
                "item_project_id": int(row["item_project_id"]),
                "page_project_id": int(row["page_project_id"]),
            }
        )

    if unmatched or ambiguous:
        if unmatched:
            print(f"Unmatched records: {len(unmatched)}", file=sys.stderr)
            for row in unmatched[:20]:
                print(f"  {row['code']} {row['title']}", file=sys.stderr)
        if ambiguous:
            print(f"Ambiguous records: {len(ambiguous)}", file=sys.stderr)
            for row, matches in ambiguous[:20]:
                print(f"  {row['code']} -> {', '.join(matches)}", file=sys.stderr)
        return 2

    conflicts = []
    for row in assignments:
        conflict = conn.execute(
            """
            SELECT id, code
            FROM pages
            WHERE project_id = ?
              AND code = ?
              AND id <> ?
            LIMIT 1
            """,
            (row["target_project_id"], row["code"], row["page_id"]),
        ).fetchone()
        if conflict:
            conflicts.append((row, conflict))
    if conflicts:
        print(f"Target code conflicts: {len(conflicts)}", file=sys.stderr)
        for row, conflict in conflicts[:20]:
            print(f"  {row['code']} -> page {conflict['id']}", file=sys.stderr)
        return 2

    print(f"Achievement-market records: {len(source_rows)}")
    print_summary(assignments)

    if not args.apply:
        print("Dry run only. Re-run with --apply to write changes.")
        return 0

    backup_path = None
    if not args.no_backup:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_path = db_path.with_name(f"{db_path.stem}.before-topic-market-{timestamp}{db_path.suffix}")
        shutil.copy2(db_path, backup_path)
        print(f"Backup: {backup_path}")

    now = datetime.now().isoformat(timespec="seconds")
    target_project_ids = sorted({row["target_project_id"] for row in assignments})

    with conn:
        for row in assignments:
            conn.execute(
                "UPDATE pages SET project_id = ?, updated_at = ? WHERE id = ?",
                (row["target_project_id"], now, row["page_id"]),
            )
            conn.execute(
                "UPDATE achievement_market_items SET project_id = ?, updated_at = ? WHERE id = ?",
                (row["target_project_id"], now, row["item_id"]),
            )
            conn.execute(
                "UPDATE page_versions SET project_id = ? WHERE page_id = ?",
                (row["target_project_id"], row["page_id"]),
            )
            deployed = conn.execute(
                "SELECT updated_at FROM deployed_pages WHERE page_id = ? ORDER BY updated_at DESC LIMIT 1",
                (row["page_id"],),
            ).fetchone()
            conn.execute("DELETE FROM deployed_pages WHERE page_id = ?", (row["page_id"],))
            if deployed:
                conn.execute(
                    "INSERT OR IGNORE INTO deployed_pages (project_id, page_id, updated_at) VALUES (?, ?, ?)",
                    (row["target_project_id"], row["page_id"], deployed["updated_at"] or now),
                )

        if target_project_ids:
            placeholders = ",".join("?" for _ in target_project_ids)
            conn.execute(
                f"""
                UPDATE projects
                SET content_deployed = 1,
                    content_deployed_at = CASE
                        WHEN COALESCE(content_deployed_at, '') = '' THEN ?
                        ELSE content_deployed_at
                    END
                WHERE id IN ({placeholders})
                """,
                [now, *target_project_ids],
            )

            school_rows = conn.execute(
                """
                SELECT projects.id
                FROM projects
                WHERE projects.portal_type = 'school'
                  AND NOT EXISTS (
                    SELECT 1 FROM deployed_pages WHERE deployed_pages.project_id = projects.id
                  )
                """
            ).fetchall()
            for row in school_rows:
                conn.execute("UPDATE projects SET content_deployed = 0 WHERE id = ?", (row["id"],))

    print("Applied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
