import argparse
import os
import sqlite3
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from db_backend import connect_database, execute_mysql_schema

DEFAULT_SQLITE_DB = ROOT / "expo.db"
DEFAULT_SCHEMA = ROOT / "database" / "mysql_schema.sql"

TABLES = [
    "users",
    "admin_users",
    "projects",
    "pages",
    "page_versions",
    "project_versions",
    "deployed_pages",
    "scans",
    "admin_logs",
    "assets",
    "user_sessions",
    "admin_sessions",
]

TRUNCATE_ORDER = [
    "deployed_pages",
    "page_versions",
    "project_versions",
    "pages",
    "scans",
    "projects",
    "user_sessions",
    "admin_sessions",
    "admin_users",
    "users",
    "admin_logs",
    "assets",
]


def sqlite_rows(path, table):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        exists = conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
            (table,),
        ).fetchone()
        if not exists:
            return [], []
        columns = [row["name"] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()]
        rows = [dict(row) for row in conn.execute(f"SELECT * FROM {table}").fetchall()]
        return columns, rows
    finally:
        conn.close()


def insert_rows(conn, table, columns, rows):
    if not rows:
        return 0
    column_sql = ", ".join(f"`{column}`" for column in columns)
    placeholders = ", ".join("?" for _ in columns)
    sql = f"INSERT INTO `{table}` ({column_sql}) VALUES ({placeholders})"
    for row in rows:
        conn.execute(sql, tuple(row.get(column) for column in columns))
    return len(rows)


def truncate_destination(conn):
    conn.execute("SET FOREIGN_KEY_CHECKS = 0")
    try:
        for table in TRUNCATE_ORDER:
            conn.execute(f"DELETE FROM `{table}`")
            conn.execute(f"ALTER TABLE `{table}` AUTO_INCREMENT = 1")
    finally:
        conn.execute("SET FOREIGN_KEY_CHECKS = 1")


def main():
    parser = argparse.ArgumentParser(description="Migrate local expo.db data into MySQL.")
    parser.add_argument("--sqlite-db", default=str(DEFAULT_SQLITE_DB), help="source SQLite database path")
    parser.add_argument("--schema", default=str(DEFAULT_SCHEMA), help="MySQL schema SQL path")
    parser.add_argument("--truncate", action="store_true", help="truncate destination tables before import")
    args = parser.parse_args()

    sqlite_path = Path(args.sqlite_db)
    if not sqlite_path.exists():
        raise SystemExit(f"SQLite database not found: {sqlite_path}")

    os.environ["DATABASE_BACKEND"] = "mysql"
    with connect_database(sqlite_path) as conn:
        execute_mysql_schema(conn, args.schema)
        if args.truncate:
            truncate_destination(conn)

        total = 0
        for table in TABLES:
            columns, rows = sqlite_rows(sqlite_path, table)
            count = insert_rows(conn, table, columns, rows)
            total += count
            print(f"{table}: {count}")
        print(f"total: {total}")


if __name__ == "__main__":
    main()
