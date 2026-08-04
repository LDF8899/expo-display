import os
import re
import sqlite3
from pathlib import Path
from urllib.parse import unquote, urlparse


try:
    import pymysql

    DBError = (sqlite3.Error, pymysql.MySQLError)
except ImportError:
    pymysql = None
    DBError = sqlite3.Error


def database_backend():
    return os.environ.get("DATABASE_BACKEND", "sqlite").strip().lower() or "sqlite"


def mysql_config_from_env():
    url = os.environ.get("DATABASE_URL", "").strip()
    if url:
        parsed = urlparse(url)
        if parsed.scheme not in {"mysql", "mysql+pymysql"}:
            raise RuntimeError("DATABASE_URL 只支持 mysql:// 或 mysql+pymysql://")
        return {
            "host": parsed.hostname or "127.0.0.1",
            "port": parsed.port or 3306,
            "user": unquote(parsed.username or ""),
            "password": unquote(parsed.password or ""),
            "database": parsed.path.lstrip("/"),
            "charset": "utf8mb4",
        }
    return {
        "host": os.environ.get("MYSQL_HOST", "127.0.0.1"),
        "port": int(os.environ.get("MYSQL_PORT", "3306")),
        "user": os.environ.get("MYSQL_USER", "root"),
        "password": os.environ.get("MYSQL_PASSWORD", ""),
        "database": os.environ.get("MYSQL_DATABASE", "expo_display"),
        "charset": os.environ.get("MYSQL_CHARSET", "utf8mb4"),
    }


def connect_database(sqlite_path):
    backend = database_backend()
    if backend == "sqlite":
        conn = sqlite3.connect(sqlite_path)
        conn.row_factory = sqlite3.Row
        return conn
    if backend == "mysql":
        return MySQLConnection(mysql_config_from_env())
    raise RuntimeError(f"不支持的 DATABASE_BACKEND：{backend}")


def translate_mysql_sql(sql):
    normalized = sql.strip()
    normalized = re.sub(r"\bINSERT\s+OR\s+IGNORE\s+INTO\b", "INSERT IGNORE INTO", normalized, flags=re.I)
    normalized = re.sub(r"\bINSERT\s+OR\s+REPLACE\s+INTO\b", "REPLACE INTO", normalized, flags=re.I)
    return _replace_placeholders(normalized)


def _replace_placeholders(sql):
    parts = []
    quote = ""
    escape = False
    for char in sql:
        if quote:
            parts.append(char)
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == quote:
                quote = ""
            continue
        if char in {"'", '"'}:
            quote = char
            parts.append(char)
            continue
        parts.append("%s" if char == "?" else char)
    return "".join(parts)


class MySQLResult:
    def __init__(self, cursor):
        self._cursor = cursor
        self.lastrowid = cursor.lastrowid
        self.rowcount = cursor.rowcount

    def fetchone(self):
        return self._cursor.fetchone()

    def fetchall(self):
        return self._cursor.fetchall()


class MySQLConnection:
    def __init__(self, config):
        try:
            import pymysql
            from pymysql.cursors import DictCursor
        except ImportError as exc:
            raise RuntimeError("DATABASE_BACKEND=mysql 时需要安装 PyMySQL") from exc

        self._pymysql = pymysql
        self._conn = pymysql.connect(
            host=config["host"],
            port=config["port"],
            user=config["user"],
            password=config["password"],
            database=config["database"],
            charset=config["charset"],
            cursorclass=DictCursor,
            autocommit=False,
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type:
            self._conn.rollback()
        else:
            self._conn.commit()
        self._conn.close()
        return False

    def execute(self, sql, params=()):
        cursor = self._conn.cursor()
        cursor.execute(translate_mysql_sql(sql), params or ())
        return MySQLResult(cursor)

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        self._conn.close()


def execute_mysql_schema(conn, schema_path, include_database=False):
    text = Path(schema_path).read_text(encoding="utf-8")
    for statement in split_sql_statements(text):
        head = statement.lstrip().upper()
        if not include_database and (head.startswith("CREATE DATABASE") or head.startswith("USE ")):
            continue
        conn.execute(statement)


def split_sql_statements(text):
    statements = []
    current = []
    quote = ""
    escape = False
    for char in text:
        if quote:
            current.append(char)
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == quote:
                quote = ""
            continue
        if char in {"'", '"', "`"}:
            quote = char
            current.append(char)
            continue
        if char == ";":
            statement = "".join(current).strip()
            if statement:
                statements.append(statement)
            current = []
            continue
        current.append(char)
    statement = "".join(current).strip()
    if statement:
        statements.append(statement)
    return statements
