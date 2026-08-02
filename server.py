import base64
import csv
import hashlib
import hmac
import io
import json
import os
import re
import secrets
import threading
import time
import uuid
from http.cookies import SimpleCookie
from datetime import datetime, timezone
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse
from xml.sax.saxutils import escape as xml_escape

from db_backend import DBError, connect_database, database_backend, execute_mysql_schema
from html_sanitizer import sanitize_rich_html
from storage_backend import asset_storage, asset_storage_backend, storage_status


ROOT = Path(__file__).resolve().parent
STATIC_DIR = ROOT / "static"


def load_env_file(path=None):
    if not path and os.environ.get("DB_PATH") and "DATABASE_BACKEND" not in os.environ:
        return
    env_path = Path(path or os.environ.get("ENV_FILE") or ROOT / ".env")
    if not env_path.is_absolute():
        env_path = ROOT / env_path
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


load_env_file()


def env_bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def env_int(name, default):
    try:
        return int(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


def env_path(name, default):
    value = os.environ.get(name)
    path = Path(value) if value else Path(default)
    return path if path.is_absolute() else ROOT / path


UPLOAD_DIR = env_path("UPLOAD_DIR", "uploads")
DB_PATH = env_path("DB_PATH", "expo.db")
DATABASE_BACKEND = database_backend()
MYSQL_SCHEMA_PATH = env_path("MYSQL_SCHEMA_PATH", "database/mysql_schema.sql")
HOST = os.environ.get("HOST", "127.0.0.1")
PORT = env_int("PORT", 8000)
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "123456")
ADMIN_COOKIE = os.environ.get("ADMIN_COOKIE", "expo_admin_session")
ADMIN_SESSION_SECONDS = env_int("ADMIN_SESSION_SECONDS", 12 * 60 * 60)
CSRF_SECRET = os.environ.get("CSRF_SECRET", "")
PUBLIC_BASE_URL = os.environ.get("PUBLIC_BASE_URL", "").rstrip("/")
SESSION_COOKIE_SECURE = env_bool("SESSION_COOKIE_SECURE", PUBLIC_BASE_URL.startswith("https://"))
ALLOW_DEFAULT_ADMIN_PASSWORD = env_bool("ALLOW_DEFAULT_ADMIN_PASSWORD", False)
TRUST_PROXY_HEADERS = env_bool("TRUST_PROXY_HEADERS", False)
ALLOWED_ORIGINS = [
    origin.strip().rstrip("/")
    for origin in os.environ.get("ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
]
MAX_JSON_BYTES = env_int("MAX_JSON_BYTES", 8 * 1024 * 1024)
MAX_UPLOAD_BYTES = env_int("MAX_UPLOAD_BYTES", 5 * 1024 * 1024)
ALLOW_SVG_UPLOADS = env_bool("ALLOW_SVG_UPLOADS", False)
ASSET_KEY_PREFIX = os.environ.get("ASSET_KEY_PREFIX", "").strip().strip("/")
LOGIN_RATE_LIMIT = env_int("LOGIN_RATE_LIMIT", 10)
LOGIN_RATE_WINDOW_SECONDS = env_int("LOGIN_RATE_WINDOW_SECONDS", 5 * 60)
UPLOAD_RATE_LIMIT = env_int("UPLOAD_RATE_LIMIT", 120)
UPLOAD_RATE_WINDOW_SECONDS = env_int("UPLOAD_RATE_WINDOW_SECONDS", 60 * 60)
PASSWORD_MIN_LENGTH = env_int("PASSWORD_MIN_LENGTH", 10)
ALLOW_WEAK_USER_PASSWORDS = env_bool("ALLOW_WEAK_USER_PASSWORDS", False)
PASSWORD_ITERATIONS = 120000
LATEST_SCAN_SECONDS = 10
DEFAULT_PROJECT_NAME = "毕节职业技术学院"
DEFAULT_SAMPLE_CODE = "DEMO-10100043"
DEFAULT_PAGE_CATEGORY = "校园新闻"
DEFAULT_PAGE_SOURCE = "学校展示"
DEFAULT_DISPLAY_CONFIG = {
    "logoImageUrl": "",
    "schoolName": DEFAULT_PROJECT_NAME,
    "schoolMeta": "欢迎来到校园 · 同心特色校园文化",
    "badgeText": "欢迎到校",
    "summaryLabel": "WELCOME OVERVIEW",
    "summaryTitle": "从学校形象到展项内容，形成完整参观动线。",
    "summaryCopy": "新版欢迎页采用舞台式首屏：左侧大图沉浸、右侧轮播导览、顶部显示实时通道状态，更适合展会现场远距离观看。",
    "summaryTags": ["远距可读", "实时扫码", "项目部署"],
    "scanTitle": "扫描展项二维码",
    "scanCopy": "大屏将自动进入对应编号内容页，保留当前项目与扫码事件的实时联动。",
    "scanImageUrl": "",
    "sideTitle": "",
    "sideCopy": "",
    "brandColor": "#28539c",
    "brandDeepColor": "#20468b",
    "accent2": "#47b7ff",
    "slides": [
        {
            "label": "校园入口与主楼",
            "meta": "WELCOME 01",
            "title": "学校形象",
            "body": "用校门、主楼、展馆空间或学校标识作为第一视觉，让观众在远处就能识别当前展示主题。",
            "imageUrl": "",
            "visual": "gate",
        },
        {
            "label": "扫码内容导览",
            "meta": "WELCOME 02",
            "title": "成果导览",
            "body": "观众扫码后进入具体编号内容，系统继续保留项目、编号、来源和更新时间等关键上下文。",
            "imageUrl": "",
            "visual": "library",
        },
        {
            "label": "现场节奏",
            "meta": "WELCOME 03",
            "title": "现场节奏",
            "body": "自动轮播在无人操作时维持画面流动，人工控制按钮承担上一张与下一张浏览。",
            "imageUrl": "",
            "visual": "students",
        },
    ],
}

SSE_CLIENTS = set()
LAST_SCAN = None
RATE_LIMITS = {}
RATE_LIMIT_LOCK = threading.Lock()
WEAK_ONLINE_SECRETS = {
    "",
    "123456",
    "password",
    "admin",
    "change-this-password",
    "change-this-random-csrf-secret",
    "replace-admin-password",
    "replace-random-csrf-secret",
    "REPLACE_WITH_STRONG_ADMIN_PASSWORD",
    "REPLACE_WITH_RANDOM_CSRF_SECRET",
}
WEAK_USER_PASSWORDS = WEAK_ONLINE_SECRETS | {
    "000000",
    "111111",
    "654321",
    "qwerty",
    "abc123",
    "password123",
    "admin123",
    "teacher",
    "teacher123",
    "user",
    "user123",
    "test",
    "test123",
}

UPLOAD_MIME_EXTENSIONS = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/webp": ".webp",
}
if ALLOW_SVG_UPLOADS:
    UPLOAD_MIME_EXTENSIONS["image/svg+xml"] = ".svg"


class RequestRejected(Exception):
    pass

QR_L_CAPACITY = {
    1: (19, 7),
    2: (34, 10),
    3: (55, 15),
    4: (80, 20),
    5: (108, 26),
}

QR_ALIGNMENT = {
    1: [],
    2: [6, 18],
    3: [6, 22],
    4: [6, 26],
    5: [6, 30],
}

GF_EXP = [0] * 512
GF_LOG = [0] * 256


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def online_mode_enabled():
    return bool(
        PUBLIC_BASE_URL
        or HOST in {"0.0.0.0", "::"}
        or DATABASE_BACKEND == "mysql"
        or asset_storage_backend() != "local"
    )


def validate_runtime_config():
    if not online_mode_enabled():
        return
    if ADMIN_PASSWORD in WEAK_ONLINE_SECRETS and not ALLOW_DEFAULT_ADMIN_PASSWORD:
        raise RuntimeError(
            "线上模式下 ADMIN_PASSWORD 必须是强随机值；仅临时测试时可设置 ALLOW_DEFAULT_ADMIN_PASSWORD=1"
        )
    if CSRF_SECRET in WEAK_ONLINE_SECRETS:
        raise RuntimeError("线上模式下 CSRF_SECRET 必须是强随机值")


def csrf_secret():
    return (CSRF_SECRET or f"{ADMIN_PASSWORD}:{ADMIN_COOKIE}").encode("utf-8")


def csrf_token_for_session(token):
    if not token:
        return ""
    return hmac.new(csrf_secret(), str(token).encode("utf-8"), hashlib.sha256).hexdigest()


def validate_user_password(password, username="", display_name="", required=True):
    password = str(password or "").strip()
    if not password:
        if required:
            raise ValueError("password 不能为空")
        return ""
    if ALLOW_WEAK_USER_PASSWORDS:
        return password
    min_length = max(1, PASSWORD_MIN_LENGTH)
    if len(password) < min_length:
        raise ValueError(f"password 至少需要 {min_length} 个字符")
    lowered = password.lower()
    if lowered in {item.lower() for item in WEAK_USER_PASSWORDS}:
        raise ValueError("password 强度太弱")
    for label, value in (("username", username), ("displayName", display_name)):
        value = str(value or "").strip().lower()
        if value and lowered == value:
            raise ValueError(f"password 不能和 {label} 相同")
    groups = [
        bool(re.search(r"[a-z]", password)),
        bool(re.search(r"[A-Z]", password)),
        bool(re.search(r"\d", password)),
        bool(re.search(r"[^A-Za-z0-9]", password)),
    ]
    if sum(groups) < 2:
        raise ValueError("password 至少需要包含两类字符")
    return password


def rate_limit_retry_after(bucket, key, limit, window_seconds):
    if limit <= 0 or window_seconds <= 0:
        return 0
    now = time.time()
    store_key = f"{bucket}:{key}"
    with RATE_LIMIT_LOCK:
        events = [ts for ts in RATE_LIMITS.get(store_key, []) if ts > now - window_seconds]
        if len(events) >= limit:
            RATE_LIMITS[store_key] = events
            return max(1, int(window_seconds - (now - events[0])) + 1)
        events.append(now)
        RATE_LIMITS[store_key] = events
    return 0


def database_status():
    try:
        with db_connect() as conn:
            row = conn.execute("SELECT 1 AS ok").fetchone()
        return {"ok": bool(row), "backend": DATABASE_BACKEND}
    except Exception as exc:
        return {"ok": False, "backend": DATABASE_BACKEND, "error": str(exc)}


def ready_status():
    checks = {
        "database": database_status(),
        "storage": storage_status(UPLOAD_DIR),
        "runtime": {
            "ok": True,
            "onlineMode": online_mode_enabled(),
            "host": HOST,
            "publicBaseUrl": PUBLIC_BASE_URL,
            "secureCookie": SESSION_COOKIE_SECURE,
            "trustProxyHeaders": TRUST_PROXY_HEADERS,
        },
    }
    ok = all(item.get("ok") for item in checks.values())
    return {
        "ok": ok,
        "time": now_iso(),
        "checks": checks,
    }


def db_connect():
    return connect_database(DB_PATH)


def table_exists(conn, name):
    if DATABASE_BACKEND == "mysql":
        return bool(
            conn.execute(
                """
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = DATABASE() AND table_name = ?
                """,
                (name,),
            ).fetchone()
        )
    return bool(
        conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
            (name,),
        ).fetchone()
    )


def table_columns(conn, name):
    if not table_exists(conn, name):
        return []
    if DATABASE_BACKEND == "mysql":
        return [
            row["COLUMN_NAME"]
            for row in conn.execute(
                """
                SELECT COLUMN_NAME
                FROM information_schema.columns
                WHERE table_schema = DATABASE() AND table_name = ?
                ORDER BY ORDINAL_POSITION
                """,
                (name,),
            ).fetchall()
        ]
    return [row["name"] for row in conn.execute(f"PRAGMA table_info({name})")]


def drop_index_if_exists(conn, name):
    if DATABASE_BACKEND == "mysql":
        return
    conn.execute(f"DROP INDEX IF EXISTS {name}")


def upsert_admin_credentials(conn):
    if DATABASE_BACKEND == "mysql":
        conn.execute(
            """
            INSERT INTO admin_users (username, password_hash, updated_at)
            VALUES (?, ?, ?)
            ON DUPLICATE KEY UPDATE
                password_hash = VALUES(password_hash),
                updated_at = VALUES(updated_at)
            """,
            (ADMIN_USERNAME, hash_password(ADMIN_PASSWORD), now_iso()),
        )
        return
    conn.execute(
        """
        INSERT INTO admin_users (username, password_hash, updated_at)
        VALUES (?, ?, ?)
        ON CONFLICT(username) DO UPDATE SET
            password_hash = excluded.password_hash,
            updated_at = excluded.updated_at
        """,
        (ADMIN_USERNAME, hash_password(ADMIN_PASSWORD), now_iso()),
    )


def init_db():
    UPLOAD_DIR.mkdir(exist_ok=True)
    if DATABASE_BACKEND == "mysql":
        init_mysql_db()
        return
    with db_connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                display_name TEXT NOT NULL DEFAULT '',
                role TEXT NOT NULL DEFAULT 'teacher',
                department TEXT NOT NULL DEFAULT '',
                enabled INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS user_sessions (
                token TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                expires_at INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS admin_users (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS admin_sessions (
                token TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                expires_at INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                idle_kicker TEXT NOT NULL DEFAULT '学校简介',
                idle_title TEXT NOT NULL DEFAULT '欢迎来到毕节职业技术学院',
                idle_copy TEXT NOT NULL DEFAULT '毕节职业技术学院立足地方发展需求，围绕人才培养、技术技能教育、社会服务与校园文化建设，打造开放、务实、富有活力的学习共同体。',
                welcome_kicker TEXT NOT NULL DEFAULT 'Welcome',
                welcome_title TEXT NOT NULL DEFAULT '欢迎参观 {title}',
                welcome_subtitle TEXT NOT NULL DEFAULT '即将进入展示页面',
                default_image_url TEXT NOT NULL DEFAULT '/static/expo-stage.png',
                accent TEXT NOT NULL DEFAULT '#f59a13',
                display_config TEXT NOT NULL DEFAULT '{}',
                deployed INTEGER NOT NULL DEFAULT 0,
                content_deployed INTEGER NOT NULL DEFAULT 0,
                updated_at TEXT NOT NULL
            )
            """
        )
        migrate_projects_table(conn)
        ensure_default_project(conn)
        upgrade_legacy_default_project(conn)
        migrate_pages_table(conn)
        ensure_page_extra_columns(conn)
        ensure_unique_page_codes(conn)
        migrate_role_tables(conn)
        migrate_review_tables(conn)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL,
                raw_url TEXT NOT NULL,
                project_id INTEGER NOT NULL DEFAULT 0,
                result TEXT NOT NULL DEFAULT 'ok',
                detail TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL
            )
            """
        )
        migrate_scans_table(conn)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS admin_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL DEFAULT '',
                role TEXT NOT NULL DEFAULT '',
                action TEXT NOT NULL,
                target_type TEXT NOT NULL DEFAULT '',
                target_id TEXT NOT NULL DEFAULT '',
                target_label TEXT NOT NULL DEFAULT '',
                detail TEXT NOT NULL DEFAULT '',
                changes TEXT NOT NULL DEFAULT '',
                ip TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL
            )
            """
        )
        migrate_logs_table(conn)
        migrate_assets_table(conn)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_admin_logs_created_at ON admin_logs(created_at)")
        project_id = deployed_content_project_id(conn)
        existing = conn.execute(
            "SELECT code FROM pages WHERE code = ?",
            (DEFAULT_SAMPLE_CODE,),
        ).fetchone()
        if not existing:
            conn.execute(
                """
                INSERT INTO pages (project_id, code, title, subtitle, body, image_url, accent, enabled, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?)
                """,
                (
                    project_id,
                    DEFAULT_SAMPLE_CODE,
                    "欢迎来到成果展示",
                    "深圳先进技术研究院展会互动展示",
                    "这里可以放项目介绍、展品亮点、团队说明和现场引导文案。后台可以随时替换这些文字和图片。",
                    "/static/sample.svg",
                    "#0f766e",
                    now_iso(),
                ),
            )
        upsert_admin_credentials(conn)
        ensure_default_user(conn)
        ensure_legacy_versions(conn)


def init_mysql_db():
    with db_connect() as conn:
        execute_mysql_schema(conn, MYSQL_SCHEMA_PATH)
        upsert_admin_credentials(conn)
        ensure_default_user(conn)
        ensure_default_project(conn)
        project_id = deployed_content_project_id(conn)
        existing = conn.execute(
            "SELECT code FROM pages WHERE code = ?",
            (DEFAULT_SAMPLE_CODE,),
        ).fetchone()
        if not existing:
            conn.execute(
                """
                INSERT INTO pages (
                    project_id, code, title, subtitle, body, image_url, accent,
                    enabled, review_status, submitted_by, reviewed_by, review_note, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, 1, 'approved', ?, ?, '', ?)
                """,
                (
                    project_id,
                    DEFAULT_SAMPLE_CODE,
                    "欢迎来到成果展示",
                    "深圳先进技术研究院展会互动展示",
                    "这里可以放项目介绍、展品亮点、团队说明和现场引导文案。后台可以随时替换这些文字和图片。",
                    "/static/sample.svg",
                    "#0f766e",
                    ADMIN_USERNAME,
                    ADMIN_USERNAME,
                    now_iso(),
                ),
            )
        ensure_legacy_versions(conn)


def ensure_default_project(conn):
    if conn.execute("SELECT id FROM projects LIMIT 1").fetchone():
        if not conn.execute("SELECT id FROM projects WHERE deployed = 1 LIMIT 1").fetchone():
            first = conn.execute("SELECT id FROM projects ORDER BY id LIMIT 1").fetchone()
            conn.execute("UPDATE projects SET deployed = CASE WHEN id = ? THEN 1 ELSE 0 END", (first["id"],))
        if not conn.execute("SELECT id FROM projects WHERE content_deployed = 1 LIMIT 1").fetchone():
            first = conn.execute("SELECT id FROM projects WHERE deployed = 1 ORDER BY id LIMIT 1").fetchone()
            if not first:
                first = conn.execute("SELECT id FROM projects ORDER BY id LIMIT 1").fetchone()
            conn.execute("UPDATE projects SET content_deployed = CASE WHEN id = ? THEN 1 ELSE 0 END", (first["id"],))
        return

    conn.execute(
        """
        INSERT INTO projects (
            name, idle_kicker, idle_title, idle_copy, welcome_kicker,
            welcome_title, welcome_subtitle, default_image_url, accent, display_config,
            deployed, content_deployed, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 1, ?)
        """,
        (
            DEFAULT_PROJECT_NAME,
            "学校简介",
            "欢迎来到毕节职业技术学院",
            "毕节职业技术学院立足地方发展需求，围绕人才培养、技术技能教育、社会服务与校园文化建设，打造开放、务实、富有活力的学习共同体。",
            "Welcome",
            "欢迎参观 {title}",
            "即将进入展示页面",
            "/static/expo-stage.png",
            "#f59a13",
            display_config_json(DEFAULT_DISPLAY_CONFIG),
            now_iso(),
        ),
    )


def migrate_projects_table(conn):
    columns = set(table_columns(conn, "projects"))
    if "display_config" not in columns:
        conn.execute("ALTER TABLE projects ADD COLUMN display_config TEXT NOT NULL DEFAULT '{}'")
    if "content_deployed" not in columns:
        conn.execute("ALTER TABLE projects ADD COLUMN content_deployed INTEGER NOT NULL DEFAULT 0")
        conn.execute("UPDATE projects SET content_deployed = deployed")


def upgrade_legacy_default_project(conn):
    legacy = conn.execute(
        """
        SELECT id
        FROM projects
        WHERE name = ?
          AND idle_kicker = ?
          AND idle_title = ?
          AND idle_copy = ?
          AND accent = ?
        """,
        ("默认展会", "Achievement Expo", "成果展示互动屏", "请扫描展品二维码", "#0f766e"),
    ).fetchall()
    for row in legacy:
        conn.execute(
            """
            UPDATE projects SET
                name = ?,
                idle_kicker = ?,
                idle_title = ?,
                idle_copy = ?,
                accent = ?,
                display_config = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                DEFAULT_PROJECT_NAME,
                "学校简介",
                "欢迎来到毕节职业技术学院",
                DEFAULT_DISPLAY_CONFIG["summaryCopy"],
                "#f59a13",
                display_config_json(DEFAULT_DISPLAY_CONFIG),
                now_iso(),
                row["id"],
            ),
        )


def deployed_project_id(conn=None):
    close_conn = conn is None
    conn = conn or db_connect()
    try:
        row = conn.execute("SELECT id FROM projects WHERE deployed = 1 ORDER BY id LIMIT 1").fetchone()
        if row:
            return row["id"]
        row = conn.execute("SELECT id FROM projects ORDER BY id LIMIT 1").fetchone()
        return row["id"] if row else None
    finally:
        if close_conn:
            conn.close()


def deployed_content_project_id(conn=None):
    close_conn = conn is None
    conn = conn or db_connect()
    try:
        row = conn.execute("SELECT id FROM projects WHERE content_deployed = 1 ORDER BY id LIMIT 1").fetchone()
        if row:
            return row["id"]
        return deployed_project_id(conn)
    finally:
        if close_conn:
            conn.close()


def migrate_pages_table(conn):
    desired = {
        "id",
        "project_id",
        "code",
        "title",
        "subtitle",
        "body",
        "image_url",
        "accent",
        "enabled",
        "updated_at",
    }
    project_id = deployed_content_project_id(conn)

    if not table_exists(conn, "pages"):
        create_pages_table(conn)
        return

    columns = set(table_columns(conn, "pages"))
    if desired.issubset(columns):
        return

    old_rows = conn.execute(
        """
        SELECT code, title, subtitle, body, image_url, accent, enabled, updated_at
        FROM pages
        """
    ).fetchall()
    conn.execute("ALTER TABLE pages RENAME TO pages_old")
    create_pages_table(conn)
    for row in old_rows:
        conn.execute(
            """
            INSERT OR REPLACE INTO pages (
                project_id, code, title, subtitle, body, image_url, accent, enabled, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                project_id,
                row["code"],
                row["title"],
                row["subtitle"],
                row["body"],
                row["image_url"],
                row["accent"],
                row["enabled"],
                row["updated_at"],
            ),
        )
    conn.execute("DROP TABLE pages_old")


def create_pages_table(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS pages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            code TEXT NOT NULL,
            category TEXT NOT NULL DEFAULT '校园新闻',
            source TEXT NOT NULL DEFAULT '学校展示',
            published_at TEXT NOT NULL DEFAULT '',
            title TEXT NOT NULL,
            subtitle TEXT NOT NULL DEFAULT '',
            body TEXT NOT NULL DEFAULT '',
            image_url TEXT NOT NULL DEFAULT '',
            accent TEXT NOT NULL DEFAULT '#0f766e',
            enabled INTEGER NOT NULL DEFAULT 1,
            updated_at TEXT NOT NULL,
            UNIQUE(project_id, code)
        )
        """
    )


def ensure_page_extra_columns(conn):
    columns = set(table_columns(conn, "pages"))
    if "category" not in columns:
        conn.execute(
            "ALTER TABLE pages ADD COLUMN category TEXT NOT NULL DEFAULT '校园新闻'"
        )
    if "source" not in columns:
        conn.execute(
            "ALTER TABLE pages ADD COLUMN source TEXT NOT NULL DEFAULT '学校展示'"
        )
    if "published_at" not in columns:
        conn.execute("ALTER TABLE pages ADD COLUMN published_at TEXT NOT NULL DEFAULT ''")


def ensure_unique_page_codes(conn):
    duplicates = conn.execute(
        """
        SELECT code, GROUP_CONCAT(id) AS ids
        FROM pages
        GROUP BY code
        HAVING COUNT(*) > 1
        """
    ).fetchall()
    for row in duplicates:
        ids = [int(page_id) for page_id in str(row["ids"]).split(",") if str(page_id).isdigit()]
        for index, page_id in enumerate(ids[1:], start=2):
            new_code = unique_page_code(conn, f"{row['code']}-{index}")
            conn.execute(
                "UPDATE pages SET code = ?, updated_at = ? WHERE id = ?",
                (new_code, now_iso(), page_id),
            )
    drop_index_if_exists(conn, "idx_pages_code_unique")


def unique_page_code(conn, preferred):
    base = str(preferred or "page").strip() or "page"
    code = base
    index = 2
    while conn.execute("SELECT id FROM pages WHERE code = ?", (code,)).fetchone():
        code = f"{base}-{index}"
        index += 1
    return code


def migrate_role_tables(conn):
    project_columns = set(table_columns(conn, "projects"))
    if "owner_username" not in project_columns:
        conn.execute("ALTER TABLE projects ADD COLUMN owner_username TEXT NOT NULL DEFAULT 'admin'")
    if "config_status" not in project_columns:
        conn.execute("ALTER TABLE projects ADD COLUMN config_status TEXT NOT NULL DEFAULT 'approved'")
    if "pending_config_version_id" not in project_columns:
        conn.execute("ALTER TABLE projects ADD COLUMN pending_config_version_id INTEGER")

    page_columns = set(table_columns(conn, "pages"))
    if "review_status" not in page_columns:
        conn.execute("ALTER TABLE pages ADD COLUMN review_status TEXT NOT NULL DEFAULT 'approved'")
    if "pending_version_id" not in page_columns:
        conn.execute("ALTER TABLE pages ADD COLUMN pending_version_id INTEGER")
    if "submitted_by" not in page_columns:
        conn.execute("ALTER TABLE pages ADD COLUMN submitted_by TEXT NOT NULL DEFAULT 'admin'")
    if "reviewed_by" not in page_columns:
        conn.execute("ALTER TABLE pages ADD COLUMN reviewed_by TEXT NOT NULL DEFAULT 'admin'")
    if "review_note" not in page_columns:
        conn.execute("ALTER TABLE pages ADD COLUMN review_note TEXT NOT NULL DEFAULT ''")


def migrate_review_tables(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS page_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            page_id INTEGER,
            project_id INTEGER NOT NULL,
            code TEXT NOT NULL,
            operation TEXT NOT NULL DEFAULT 'upsert',
            status TEXT NOT NULL DEFAULT 'pending',
            snapshot TEXT NOT NULL,
            submitted_by TEXT NOT NULL DEFAULT '',
            submitted_at TEXT NOT NULL,
            reviewed_by TEXT NOT NULL DEFAULT '',
            reviewed_at TEXT NOT NULL DEFAULT '',
            review_note TEXT NOT NULL DEFAULT '',
            changes TEXT NOT NULL DEFAULT ''
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS project_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            snapshot TEXT NOT NULL,
            submitted_by TEXT NOT NULL DEFAULT '',
            submitted_at TEXT NOT NULL,
            reviewed_by TEXT NOT NULL DEFAULT '',
            reviewed_at TEXT NOT NULL DEFAULT '',
            review_note TEXT NOT NULL DEFAULT '',
            changes TEXT NOT NULL DEFAULT ''
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS deployed_pages (
            project_id INTEGER NOT NULL,
            page_id INTEGER NOT NULL,
            updated_at TEXT NOT NULL,
            PRIMARY KEY(project_id, page_id)
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_page_versions_status ON page_versions(status, submitted_at)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_project_versions_status ON project_versions(status, submitted_at)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_page_versions_project ON page_versions(project_id, submitted_at)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_page_versions_page ON page_versions(page_id, submitted_at)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_project_versions_project ON project_versions(project_id, submitted_at)")


def migrate_scans_table(conn):
    columns = set(table_columns(conn, "scans"))
    if "project_id" not in columns:
        conn.execute("ALTER TABLE scans ADD COLUMN project_id INTEGER NOT NULL DEFAULT 0")
    if "result" not in columns:
        conn.execute("ALTER TABLE scans ADD COLUMN result TEXT NOT NULL DEFAULT 'ok'")
    if "detail" not in columns:
        conn.execute("ALTER TABLE scans ADD COLUMN detail TEXT NOT NULL DEFAULT ''")


def migrate_logs_table(conn):
    columns = set(table_columns(conn, "admin_logs"))
    if "role" not in columns:
        conn.execute("ALTER TABLE admin_logs ADD COLUMN role TEXT NOT NULL DEFAULT ''")
    if "changes" not in columns:
        conn.execute("ALTER TABLE admin_logs ADD COLUMN changes TEXT NOT NULL DEFAULT ''")


def migrate_assets_table(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_username TEXT NOT NULL DEFAULT '',
            original_filename TEXT NOT NULL DEFAULT '',
            storage_key TEXT NOT NULL,
            url TEXT NOT NULL,
            mime_type TEXT NOT NULL DEFAULT '',
            size_bytes INTEGER NOT NULL DEFAULT 0,
            backend TEXT NOT NULL DEFAULT 'local',
            created_at TEXT NOT NULL
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_assets_owner_created ON assets(owner_username, created_at)")


def ensure_default_user(conn):
    now = now_iso()
    legacy = conn.execute("SELECT password_hash FROM admin_users WHERE username = ?", (ADMIN_USERNAME,)).fetchone()
    password_hash = legacy["password_hash"] if legacy else hash_password(ADMIN_PASSWORD)
    if DATABASE_BACKEND == "mysql":
        conn.execute(
            """
            INSERT INTO users (username, password_hash, display_name, role, department, enabled, created_at, updated_at)
            VALUES (?, ?, ?, 'admin', '', 1, ?, ?)
            ON DUPLICATE KEY UPDATE
                password_hash = CASE WHEN role = 'admin' THEN password_hash ELSE VALUES(password_hash) END,
                display_name = CASE WHEN display_name = '' THEN VALUES(display_name) ELSE display_name END,
                role = 'admin',
                enabled = 1,
                updated_at = VALUES(updated_at)
            """,
            (ADMIN_USERNAME, password_hash, "Administrator", now, now),
        )
        conn.execute("UPDATE projects SET owner_username = ? WHERE owner_username = '' OR owner_username IS NULL", (ADMIN_USERNAME,))
        conn.execute("UPDATE pages SET submitted_by = ? WHERE submitted_by = '' OR submitted_by IS NULL", (ADMIN_USERNAME,))
        conn.execute("UPDATE pages SET reviewed_by = ? WHERE reviewed_by = '' OR reviewed_by IS NULL", (ADMIN_USERNAME,))
        return
    conn.execute(
        """
        INSERT INTO users (username, password_hash, display_name, role, department, enabled, created_at, updated_at)
        VALUES (?, ?, ?, 'admin', '', 1, ?, ?)
        ON CONFLICT(username) DO UPDATE SET
            password_hash = CASE WHEN users.role = 'admin' THEN users.password_hash ELSE excluded.password_hash END,
            display_name = CASE WHEN users.display_name = '' THEN excluded.display_name ELSE users.display_name END,
            role = 'admin',
            enabled = 1,
            updated_at = excluded.updated_at
        """,
        (ADMIN_USERNAME, password_hash, "Administrator", now, now),
    )
    conn.execute("UPDATE projects SET owner_username = 'admin' WHERE owner_username = '' OR owner_username IS NULL")
    conn.execute("UPDATE pages SET submitted_by = 'admin' WHERE submitted_by = '' OR submitted_by IS NULL")
    conn.execute("UPDATE pages SET reviewed_by = 'admin' WHERE reviewed_by = '' OR reviewed_by IS NULL")


def page_snapshot_from_row(row):
    return {
        "code": row["code"],
        "category": row["category"] if "category" in row.keys() else DEFAULT_PAGE_CATEGORY,
        "source": row["source"] if "source" in row.keys() else DEFAULT_PAGE_SOURCE,
        "publishedAt": row["published_at"] if "published_at" in row.keys() else "",
        "title": row["title"],
        "subtitle": row["subtitle"],
        "body": row["body"],
        "imageUrl": row["image_url"],
        "accent": row["accent"],
        "enabled": bool(row["enabled"]),
    }


def project_snapshot_from_row(row):
    return {
        "name": row["name"],
        "ownerUsername": row["owner_username"] if "owner_username" in row.keys() else ADMIN_USERNAME,
        "idleKicker": row["idle_kicker"],
        "idleTitle": row["idle_title"],
        "idleCopy": row["idle_copy"],
        "welcomeKicker": row["welcome_kicker"],
        "welcomeTitle": row["welcome_title"],
        "welcomeSubtitle": row["welcome_subtitle"],
        "defaultImageUrl": row["default_image_url"],
        "accent": row["accent"],
        "displayConfig": normalize_display_config(row["display_config"] if "display_config" in row.keys() else "{}"),
    }


def ensure_legacy_versions(conn):
    now = now_iso()
    rows = conn.execute("SELECT * FROM pages").fetchall()
    for row in rows:
        exists = conn.execute(
            "SELECT id FROM page_versions WHERE page_id = ? AND status = 'approved' LIMIT 1",
            (row["id"],),
        ).fetchone()
        if not exists:
            snapshot = page_snapshot_from_row(row)
            conn.execute(
                """
                INSERT INTO page_versions (
                    page_id, project_id, code, operation, status, snapshot,
                    submitted_by, submitted_at, reviewed_by, reviewed_at, changes
                )
                VALUES (?, ?, ?, 'upsert', 'approved', ?, 'admin', ?, 'admin', ?, 'legacy import')
                """,
                (row["id"], row["project_id"], row["code"], json.dumps(snapshot, ensure_ascii=False), now, now),
            )
    project_rows = conn.execute("SELECT * FROM projects").fetchall()
    for row in project_rows:
        exists = conn.execute(
            "SELECT id FROM project_versions WHERE project_id = ? AND status = 'approved' LIMIT 1",
            (row["id"],),
        ).fetchone()
        if not exists:
            snapshot = project_snapshot_from_row(row)
            conn.execute(
                """
                INSERT INTO project_versions (
                    project_id, status, snapshot, submitted_by, submitted_at,
                    reviewed_by, reviewed_at, changes
                )
                VALUES (?, 'approved', ?, 'admin', ?, 'admin', ?, 'legacy import')
                """,
                (row["id"], json.dumps(snapshot, ensure_ascii=False), now, now),
            )
    deployed = conn.execute("SELECT id FROM projects WHERE content_deployed = 1 ORDER BY id LIMIT 1").fetchone()
    if deployed and not conn.execute("SELECT 1 FROM deployed_pages LIMIT 1").fetchone():
        approved_pages = conn.execute(
            "SELECT id FROM pages WHERE project_id = ? AND review_status = 'approved' AND enabled = 1",
            (deployed["id"],),
        ).fetchall()
        for page in approved_pages:
            conn.execute(
                "INSERT OR IGNORE INTO deployed_pages (project_id, page_id, updated_at) VALUES (?, ?, ?)",
                (deployed["id"], page["id"], now),
            )


def hash_password(password, salt=None):
    salt = salt or secrets.token_bytes(16)
    derived = hashlib.pbkdf2_hmac(
        "sha256",
        str(password).encode("utf-8"),
        salt,
        PASSWORD_ITERATIONS,
    )
    return f"pbkdf2_sha256${PASSWORD_ITERATIONS}${salt.hex()}${derived.hex()}"


def verify_password(password, stored):
    try:
        algo, iterations, salt_hex, hash_hex = str(stored).split("$", 3)
        if algo != "pbkdf2_sha256":
            return False
        derived = hashlib.pbkdf2_hmac(
            "sha256",
            str(password).encode("utf-8"),
            bytes.fromhex(salt_hex),
            int(iterations),
        )
        return hmac.compare_digest(derived.hex(), hash_hex)
    except Exception:
        return False


def row_to_user(row):
    if not row:
        return None
    return {
        "username": row["username"],
        "displayName": row["display_name"] or row["username"],
        "role": row["role"],
        "department": row["department"],
        "enabled": bool(row["enabled"]),
        "createdAt": row["created_at"],
        "updatedAt": row["updated_at"],
    }


def get_user(username):
    if not username:
        return None
    with db_connect() as conn:
        row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    return row_to_user(row)


def list_users():
    with db_connect() as conn:
        rows = conn.execute(
            """
            SELECT u.*,
                   COUNT(DISTINCT p.id) AS project_count,
                   COUNT(DISTINCT pages.id) AS page_count
            FROM users u
            LEFT JOIN projects p ON p.owner_username = u.username
            LEFT JOIN pages ON pages.project_id = p.id
            GROUP BY u.username
            ORDER BY CASE u.role WHEN 'admin' THEN 0 ELSE 1 END, u.enabled DESC, u.username
            """
        ).fetchall()
    users = []
    for row in rows:
        user = row_to_user(row)
        user["projectCount"] = int(row["project_count"] or 0)
        user["pageCount"] = int(row["page_count"] or 0)
        users.append(user)
    return users


def upsert_user(data, actor="admin"):
    username = str(data.get("username", "")).strip()
    if not username:
        raise ValueError("username 不能为空")
    if not re.match(r"^[A-Za-z0-9_.-]{2,64}$", username):
        raise ValueError("username 只能使用字母、数字、点、短横线或下划线")
    role = str(data.get("role") or "teacher").strip()
    if role not in {"admin", "teacher"}:
        role = "teacher"
    display_name = str(data.get("displayName") or data.get("name") or username).strip()
    department = str(data.get("department") or "").strip()
    enabled = 1 if data.get("enabled", True) else 0
    password = str(data.get("password") or "").strip()
    now = now_iso()
    with db_connect() as conn:
        current = conn.execute("SELECT username FROM users WHERE username = ?", (username,)).fetchone()
        if current:
            password = validate_user_password(password, username, display_name, required=False)
            fields = [display_name, role, department, enabled, now, username]
            conn.execute(
                """
                UPDATE users SET display_name = ?, role = ?, department = ?,
                    enabled = ?, updated_at = ?
                WHERE username = ?
                """,
                fields,
            )
            if password:
                conn.execute(
                    "UPDATE users SET password_hash = ?, updated_at = ? WHERE username = ?",
                    (hash_password(password), now, username),
                )
        else:
            password = validate_user_password(password, username, display_name, required=True)
            conn.execute(
                """
                INSERT INTO users (
                    username, password_hash, display_name, role, department, enabled, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (username, hash_password(password), display_name, role, department, enabled, now, now),
            )
    return get_user(username)


def reset_user_password(username, password):
    password = validate_user_password(password, username, required=True)
    with db_connect() as conn:
        row = conn.execute("SELECT username FROM users WHERE username = ?", (username,)).fetchone()
        if not row:
            return None
        conn.execute(
            "UPDATE users SET password_hash = ?, updated_at = ? WHERE username = ?",
            (hash_password(password), now_iso(), username),
        )
    return get_user(username)


def set_user_enabled(username, enabled):
    if username == ADMIN_USERNAME and not enabled:
        raise ValueError("admin 账号不能被禁用")
    with db_connect() as conn:
        row = conn.execute("SELECT username FROM users WHERE username = ?", (username,)).fetchone()
        if not row:
            return None
        conn.execute(
            "UPDATE users SET enabled = ?, updated_at = ? WHERE username = ?",
            (1 if enabled else 0, now_iso(), username),
        )
    return get_user(username)


def change_password(username, old_password, new_password):
    new_password = validate_user_password(new_password, username, required=True)
    with db_connect() as conn:
        row = conn.execute("SELECT password_hash FROM users WHERE username = ?", (username,)).fetchone()
        if not row or not verify_password(old_password, row["password_hash"]):
            raise ValueError("当前 password 不正确")
        conn.execute(
            "UPDATE users SET password_hash = ?, updated_at = ? WHERE username = ?",
            (hash_password(new_password), now_iso(), username),
        )


def create_admin_session(username):
    token = secrets.token_urlsafe(32)
    expires_at = int(time.time()) + ADMIN_SESSION_SECONDS
    with db_connect() as conn:
        conn.execute(
            "INSERT INTO user_sessions (token, username, expires_at, created_at) VALUES (?, ?, ?, ?)",
            (token, username, expires_at, now_iso()),
        )
        conn.execute("DELETE FROM user_sessions WHERE expires_at <= ?", (int(time.time()),))
    return token


def get_session_user(token):
    if not token:
        return None
    now = int(time.time())
    with db_connect() as conn:
        row = conn.execute(
            """
            SELECT sessions.username, sessions.expires_at, users.*
            FROM user_sessions sessions
            JOIN users ON users.username = sessions.username
            WHERE sessions.token = ?
            """,
            (token,),
        ).fetchone()
        if not row:
            return None
        if int(row["expires_at"]) <= now:
            conn.execute("DELETE FROM user_sessions WHERE token = ?", (token,))
            return None
        if not bool(row["enabled"]):
            conn.execute("DELETE FROM user_sessions WHERE token = ?", (token,))
            return None
        return row_to_user(row)


def get_session_username(token):
    user = get_session_user(token)
    return user["username"] if user else None


def delete_admin_session(token):
    if not token:
        return
    with db_connect() as conn:
        conn.execute("DELETE FROM user_sessions WHERE token = ?", (token,))


def default_display_config():
    return json.loads(json.dumps(DEFAULT_DISPLAY_CONFIG, ensure_ascii=False))


def clean_config_text(value):
    return str(value or "").strip()


def normalize_text_list(value, fallback, max_items=8):
    if isinstance(value, list):
        items = [clean_config_text(item) for item in value]
    else:
        text = clean_config_text(value)
        items = re.split(r"[\n,，、]+", text) if text else []
    items = [item for item in items if item]
    return items[:max_items] if items else []


def normalize_display_config(value):
    if isinstance(value, str):
        try:
            value = json.loads(value or "{}")
        except json.JSONDecodeError:
            value = {}
    if not isinstance(value, dict):
        value = {}

    config = default_display_config()
    text_fields = (
        "logoImageUrl",
        "schoolName",
        "schoolMeta",
        "badgeText",
        "summaryLabel",
        "summaryTitle",
        "summaryCopy",
        "scanTitle",
        "scanCopy",
        "scanImageUrl",
        "sideTitle",
        "sideCopy",
        "brandColor",
        "brandDeepColor",
        "accent2",
    )
    for field in text_fields:
        if field in value:
            config[field] = clean_config_text(value.get(field))

    if "summaryTags" in value:
        config["summaryTags"] = normalize_text_list(
            value.get("summaryTags"),
            DEFAULT_DISPLAY_CONFIG["summaryTags"],
        )

    source_slides = value.get("slides")
    if not isinstance(source_slides, list):
        source_slides = []

    slides = []
    default_slides = DEFAULT_DISPLAY_CONFIG["slides"]
    slide_count = max(len(default_slides), min(len(source_slides), 6))
    for index in range(slide_count):
        fallback = dict(default_slides[index]) if index < len(default_slides) else {
            "label": f"轮播内容 {index + 1}",
            "meta": f"欢迎 {index + 1:02d}",
            "title": "校园内容",
            "body": "",
            "imageUrl": "",
            "visual": "gate",
        }
        source = source_slides[index] if index < len(source_slides) and isinstance(source_slides[index], dict) else {}
        slide = {}
        for field in ("label", "meta", "title", "body", "imageUrl", "visual"):
            slide[field] = clean_config_text(source.get(field, fallback.get(field, "")))
        slides.append(slide)
    config["slides"] = slides
    return config


def display_config_json(value):
    return json.dumps(normalize_display_config(value), ensure_ascii=False, separators=(",", ":"))


def row_to_project(row):
    if not row:
        return None
    display_config = row["display_config"] if "display_config" in row.keys() else "{}"
    content_deployed = row["content_deployed"] if "content_deployed" in row.keys() else row["deployed"]
    page_count = row["page_count"] if "page_count" in row.keys() else 0
    scan_count = row["scan_count"] if "scan_count" in row.keys() else 0
    pending_page_count = row["pending_page_count"] if "pending_page_count" in row.keys() else 0
    owner_username = row["owner_username"] if "owner_username" in row.keys() else ADMIN_USERNAME
    owner_display_name = row["owner_display_name"] if "owner_display_name" in row.keys() else owner_username
    owner_enabled = row["owner_enabled"] if "owner_enabled" in row.keys() else 1
    return {
        "id": row["id"],
        "name": row["name"],
        "ownerUsername": owner_username,
        "ownerDisplayName": owner_display_name or owner_username,
        "ownerEnabled": bool(owner_enabled),
        "idleKicker": row["idle_kicker"],
        "idleTitle": row["idle_title"],
        "idleCopy": row["idle_copy"],
        "welcomeKicker": row["welcome_kicker"],
        "welcomeTitle": row["welcome_title"],
        "welcomeSubtitle": row["welcome_subtitle"],
        "defaultImageUrl": row["default_image_url"],
        "accent": row["accent"],
        "displayConfig": normalize_display_config(display_config),
        "deployed": bool(row["deployed"]),
        "contentDeployed": bool(content_deployed),
        "configStatus": row["config_status"] if "config_status" in row.keys() else "approved",
        "pendingConfigVersionId": row["pending_config_version_id"] if "pending_config_version_id" in row.keys() else None,
        "pageCount": int(page_count or 0),
        "pendingPageCount": int(pending_page_count or 0),
        "scanCount": int(scan_count or 0),
        "updatedAt": row["updated_at"],
    }


def get_project(project_id):
    with db_connect() as conn:
        row = conn.execute(
            """
            SELECT p.*, users.display_name AS owner_display_name, users.enabled AS owner_enabled
            FROM projects p
            LEFT JOIN users ON users.username = p.owner_username
            WHERE p.id = ?
            """,
            (project_id,),
        ).fetchone()
    return row_to_project(row)


def project_accessible(project, user):
    if not project or not user:
        return False
    if user.get("role") == "admin":
        return True
    return project.get("ownerUsername") == user.get("username")


def get_deployed_project():
    with db_connect() as conn:
        row = conn.execute(
            """
            SELECT p.*, users.display_name AS owner_display_name, users.enabled AS owner_enabled
            FROM projects p
            LEFT JOIN users ON users.username = p.owner_username
            WHERE p.deployed = 1 AND COALESCE(users.enabled, 1) = 1
            ORDER BY p.id LIMIT 1
            """
        ).fetchone()
        if not row:
            row = conn.execute(
                """
                SELECT p.*, users.display_name AS owner_display_name, users.enabled AS owner_enabled
                FROM projects p
                LEFT JOIN users ON users.username = p.owner_username
                WHERE COALESCE(users.enabled, 1) = 1
                ORDER BY p.id LIMIT 1
                """
            ).fetchone()
    return row_to_project(row)


def get_deployed_content_project():
    with db_connect() as conn:
        row = conn.execute(
            """
            SELECT p.*, users.display_name AS owner_display_name, users.enabled AS owner_enabled
            FROM projects p
            LEFT JOIN users ON users.username = p.owner_username
            WHERE p.content_deployed = 1 AND COALESCE(users.enabled, 1) = 1
            ORDER BY p.id LIMIT 1
            """
        ).fetchone()
        if not row:
            row = conn.execute(
                """
                SELECT p.*, users.display_name AS owner_display_name, users.enabled AS owner_enabled
                FROM projects p
                LEFT JOIN users ON users.username = p.owner_username
                WHERE p.deployed = 1 AND COALESCE(users.enabled, 1) = 1
                ORDER BY p.id LIMIT 1
                """
            ).fetchone()
        if not row:
            row = conn.execute(
                """
                SELECT p.*, users.display_name AS owner_display_name, users.enabled AS owner_enabled
                FROM projects p
                LEFT JOIN users ON users.username = p.owner_username
                WHERE COALESCE(users.enabled, 1) = 1
                ORDER BY p.id LIMIT 1
                """
            ).fetchone()
    return row_to_project(row)


def list_projects(user=None):
    user = user or {"role": "admin"}
    owner_filter = ""
    params = []
    if user.get("role") != "admin":
        owner_filter = "WHERE p.owner_username = ?"
        params.append(user.get("username", ""))
    with db_connect() as conn:
        rows = conn.execute(
            f"""
            SELECT
                p.*,
                users.display_name AS owner_display_name,
                users.enabled AS owner_enabled,
                COUNT(DISTINCT pages.id) AS page_count,
                SUM(CASE WHEN pages.review_status IN ('pending','pending_delete','rejected') THEN 1 ELSE 0 END) AS pending_page_count,
                COUNT(DISTINCT scans.id) AS scan_count
            FROM projects p
            LEFT JOIN users ON users.username = p.owner_username
            LEFT JOIN pages ON pages.project_id = p.id
            LEFT JOIN scans ON scans.project_id = p.id
            {owner_filter}
            GROUP BY p.id
            ORDER BY p.deployed DESC, p.content_deployed DESC, p.updated_at DESC, p.id DESC
            """,
            params,
        ).fetchall()
    return [row_to_project(row) for row in rows]


def create_admin_log(action, target_type="", target_id="", target_label="", detail="", username="", role="", ip="", changes=""):
    try:
        with db_connect() as conn:
            conn.execute(
                """
                INSERT INTO admin_logs (
                    username, role, action, target_type, target_id, target_label, detail, changes, ip, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(username or ""),
                    str(role or ""),
                    str(action or ""),
                    str(target_type or ""),
                    str(target_id or ""),
                    str(target_label or ""),
                    str(detail or ""),
                    str(changes or ""),
                    str(ip or ""),
                    now_iso(),
                ),
            )
    except DBError as exc:
        print(f"admin log failed: {exc}")


def row_to_admin_log(row):
    return {
        "id": row["id"],
        "username": row["username"],
        "role": row["role"] if "role" in row.keys() else "",
        "action": row["action"],
        "targetType": row["target_type"],
        "targetId": row["target_id"],
        "targetLabel": row["target_label"],
        "detail": row["detail"],
        "changes": row["changes"] if "changes" in row.keys() else "",
        "ip": row["ip"],
        "createdAt": row["created_at"],
    }


def list_admin_logs(limit=80, username="", action="", date_from="", date_to=""):
    limit = max(1, min(int(limit or 80), 300))
    where = []
    params = []
    if username:
        where.append("username = ?")
        params.append(username)
    if action:
        where.append("action = ?")
        params.append(action)
    if date_from:
        where.append("created_at >= ?")
        params.append(date_from)
    if date_to:
        where.append("created_at <= ?")
        params.append(date_to)
    where_sql = f"WHERE {' AND '.join(where)}" if where else ""
    with db_connect() as conn:
        rows = conn.execute(
            f"""
            SELECT * FROM admin_logs
            {where_sql}
            ORDER BY created_at DESC, id DESC
            LIMIT ?
            """,
            (*params, limit),
        ).fetchall()
    return [row_to_admin_log(row) for row in rows]


def operations_summary(user=None):
    user = user or {"role": "admin", "username": ""}
    ready = ready_status()
    owner_join = ""
    owner_where = ""
    owner_params = []
    if user.get("role") != "admin":
        owner_join = "JOIN projects ON projects.id = pages.project_id"
        owner_where = "WHERE projects.owner_username = ?"
        owner_params.append(user.get("username", ""))
    with db_connect() as conn:
        deployed = conn.execute(
            """
            SELECT
                MAX(CASE WHEN deployed = 1 THEN id ELSE 0 END) AS welcome_id,
                MAX(CASE WHEN deployed = 1 THEN name ELSE '' END) AS welcome_name,
                MAX(CASE WHEN content_deployed = 1 THEN id ELSE 0 END) AS content_id,
                MAX(CASE WHEN content_deployed = 1 THEN name ELSE '' END) AS content_name
            FROM projects
            """
        ).fetchone()
        pending_pages = conn.execute(
            f"""
            SELECT COUNT(*) AS value
            FROM pages
            {owner_join}
            {owner_where + (' AND' if owner_where else 'WHERE')} pages.review_status IN ('pending','pending_delete')
            """,
            owner_params,
        ).fetchone()["value"]
        pending_projects = 0
        if user.get("role") == "admin":
            pending_projects = conn.execute(
                "SELECT COUNT(*) AS value FROM projects WHERE config_status = 'pending'"
            ).fetchone()["value"]
        asset_count = conn.execute(
            "SELECT COUNT(*) AS value FROM assets" if user.get("role") == "admin" else "SELECT COUNT(*) AS value FROM assets WHERE owner_username = ?",
            () if user.get("role") == "admin" else (user.get("username", ""),),
        ).fetchone()["value"]
        recent_errors = conn.execute(
            """
            SELECT * FROM admin_logs
            WHERE action IN ('deploy_content','review_reject','disable_user')
            ORDER BY created_at DESC, id DESC
            LIMIT 5
            """
        ).fetchall() if user.get("role") == "admin" else []
    return {
        "ready": ready,
        "deployed": {
            "welcomeProjectId": int(deployed["welcome_id"] or 0),
            "welcomeProjectName": deployed["welcome_name"] or "",
            "contentProjectId": int(deployed["content_id"] or 0),
            "contentProjectName": deployed["content_name"] or "",
        },
        "pending": {
            "pages": int(pending_pages or 0),
            "projects": int(pending_projects or 0),
        },
        "assets": {"count": int(asset_count or 0)},
        "recentErrors": [row_to_admin_log(row) for row in recent_errors],
        "config": online_config_audit() if user.get("role") == "admin" else {"ok": True, "errors": [], "warnings": []},
    }


def config_issue(level, code, message):
    return {"level": level, "code": code, "message": message}


def online_config_audit():
    errors = []
    warnings = []
    is_online = online_mode_enabled()
    public_base = PUBLIC_BASE_URL.strip()
    if not is_online:
        warnings.append(config_issue("warning", "local_mode", "当前仍是本地模式；公网部署前需要配置 PUBLIC_BASE_URL、MySQL 或对象存储。"))
    if not public_base:
        warnings.append(config_issue("warning", "public_base_url", "未配置 PUBLIC_BASE_URL，线上二维码、Cookie 和反代判断缺少公网基准地址。"))
    elif not public_base.startswith("https://"):
        warnings.append(config_issue("warning", "public_base_url_https", "PUBLIC_BASE_URL 不是 HTTPS；正式公网建议使用 HTTPS。"))
    if public_base.startswith("https://") and not SESSION_COOKIE_SECURE:
        errors.append(config_issue("error", "secure_cookie", "HTTPS 公网地址下 SESSION_COOKIE_SECURE 必须开启。"))
    if is_online and ADMIN_PASSWORD in WEAK_ONLINE_SECRETS:
        errors.append(config_issue("error", "admin_password", "线上模式不能使用默认或占位管理员密码。"))
    if is_online and CSRF_SECRET in WEAK_ONLINE_SECRETS:
        errors.append(config_issue("error", "csrf_secret", "线上模式必须配置强随机 CSRF_SECRET。"))
    if PASSWORD_MIN_LENGTH < 10:
        errors.append(config_issue("error", "password_min_length", "PASSWORD_MIN_LENGTH 不应低于 10。"))
    if ALLOW_WEAK_USER_PASSWORDS:
        errors.append(config_issue("error", "weak_user_passwords", "ALLOW_WEAK_USER_PASSWORDS 已开启，线上必须关闭。"))
    if DATABASE_BACKEND != "mysql":
        warnings.append(config_issue("warning", "database_backend", "当前数据库不是 MySQL；多人线上正式环境建议使用 MySQL。"))
    if asset_storage_backend() == "local":
        warnings.append(config_issue("warning", "asset_storage", "当前资源存储为本地 uploads；多实例或云部署建议使用对象存储。"))
    if ALLOW_SVG_UPLOADS:
        warnings.append(config_issue("warning", "svg_uploads", "SVG 上传已开启；线上建议关闭，避免脚本型 SVG 风险。"))
    if LOGIN_RATE_LIMIT <= 0:
        warnings.append(config_issue("warning", "login_rate_limit", "登录限流已关闭。"))
    if UPLOAD_RATE_LIMIT <= 0:
        warnings.append(config_issue("warning", "upload_rate_limit", "上传限流已关闭。"))
    if is_online and not TRUST_PROXY_HEADERS:
        warnings.append(config_issue("warning", "proxy_headers", "线上反代部署通常需要 TRUST_PROXY_HEADERS=1 以记录真实客户端 IP。"))
    return {
        "ok": not errors,
        "onlineMode": is_online,
        "errors": errors,
        "warnings": warnings,
    }


def acceptance_report(user):
    dashboard = admin_dashboard(user)
    operations = dashboard.get("operations", {})
    deployed = operations.get("deployed", {})
    content_project_id = int(deployed.get("contentProjectId") or 0)
    content_check = deploy_content_check(content_project_id) if content_project_id else {
        "ok": False,
        "projectId": 0,
        "pageIds": [],
        "errors": ["内容项目尚未部署"],
        "warnings": [],
        "eligiblePageIds": [],
    }
    reviews = list_reviews("pending")
    return {
        "ok": bool(operations.get("ready", {}).get("ok")) and bool(operations.get("config", {}).get("ok")) and bool(content_check.get("ok")),
        "generatedAt": now_iso(),
        "generatedBy": user.get("username", ""),
        "summary": dashboard.get("summary", {}),
        "ready": operations.get("ready", {}),
        "config": operations.get("config", {}),
        "deployed": deployed,
        "deployCheck": content_check,
        "pending": {
            "pages": len(reviews.get("pages", [])),
            "projects": len(reviews.get("projects", [])),
        },
        "assets": operations.get("assets", {}),
        "recentErrors": operations.get("recentErrors", []),
    }


def row_to_asset(row):
    if not row:
        return None
    return {
        "id": row["id"],
        "ownerUsername": row["owner_username"],
        "originalFilename": row["original_filename"],
        "storageKey": row["storage_key"],
        "url": row["url"],
        "mimeType": row["mime_type"],
        "sizeBytes": int(row["size_bytes"] or 0),
        "backend": row["backend"],
        "createdAt": row["created_at"],
    }


def list_assets(user, limit=80):
    try:
        limit = int(limit or 80)
    except (TypeError, ValueError):
        limit = 80
    limit = max(1, min(limit, 200))
    where = ""
    params = []
    if user.get("role") != "admin":
        where = "WHERE owner_username = ?"
        params.append(user.get("username", ""))
    with db_connect() as conn:
        rows = conn.execute(
            f"""
            SELECT *
            FROM assets
            {where}
            ORDER BY created_at DESC, id DESC
            LIMIT ?
            """,
            (*params, limit),
        ).fetchall()
    return [row_to_asset(row) for row in rows]


def get_asset(asset_id):
    with db_connect() as conn:
        row = conn.execute("SELECT * FROM assets WHERE id = ?", (asset_id,)).fetchone()
    return row_to_asset(row)


def asset_accessible(asset, user):
    if not asset or not user:
        return False
    if user.get("role") == "admin":
        return True
    return asset.get("ownerUsername") == user.get("username")


def create_asset_record(user, original_filename, storage_key, url, mime_type, size_bytes):
    with db_connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO assets (
                owner_username, original_filename, storage_key, url,
                mime_type, size_bytes, backend, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user.get("username", ""),
                str(original_filename or "")[:255],
                storage_key,
                url,
                mime_type,
                int(size_bytes or 0),
                asset_storage_backend(),
                now_iso(),
            ),
        )
        asset_id = cursor.lastrowid
    return get_asset(asset_id)


def asset_usage_summary(url):
    empty = {"projects": 0, "pages": 0, "pendingPageVersions": 0, "pendingProjectVersions": 0, "total": 0}
    if not url:
        return empty
    pattern = f"%{url}%"
    with db_connect() as conn:
        projects = conn.execute(
            """
            SELECT COUNT(*) AS value
            FROM projects
            WHERE default_image_url = ? OR display_config LIKE ?
            """,
            (url, pattern),
        ).fetchone()["value"]
        pages = conn.execute(
            """
            SELECT COUNT(*) AS value
            FROM pages
            WHERE image_url = ? OR body LIKE ?
            """,
            (url, pattern),
        ).fetchone()["value"]
        page_versions = conn.execute(
            """
            SELECT COUNT(*) AS value
            FROM page_versions
            WHERE status = 'pending' AND snapshot LIKE ?
            """,
            (pattern,),
        ).fetchone()["value"]
        project_versions = conn.execute(
            """
            SELECT COUNT(*) AS value
            FROM project_versions
            WHERE status = 'pending' AND snapshot LIKE ?
            """,
            (pattern,),
        ).fetchone()["value"]
    summary = {
        "projects": int(projects or 0),
        "pages": int(pages or 0),
        "pendingPageVersions": int(page_versions or 0),
        "pendingProjectVersions": int(project_versions or 0),
    }
    summary["total"] = sum(summary.values())
    return summary


def asset_usage_message(summary):
    parts = []
    if summary.get("projects"):
        parts.append(f"{summary['projects']} 个项目")
    if summary.get("pages"):
        parts.append(f"{summary['pages']} 个展示页")
    if summary.get("pendingPageVersions"):
        parts.append(f"{summary['pendingPageVersions']} 个待审核页面草稿")
    if summary.get("pendingProjectVersions"):
        parts.append(f"{summary['pendingProjectVersions']} 个待审核项目草稿")
    return "资源正在被使用：" + "，".join(parts) if parts else "资源正在被使用"


def delete_asset(asset_id, user):
    asset = get_asset(asset_id)
    if not asset or not asset_accessible(asset, user):
        return None
    usage = asset_usage_summary(asset["url"])
    if usage["total"]:
        raise ValueError(asset_usage_message(usage))
    asset_storage(UPLOAD_DIR).delete(asset["storageKey"])
    with db_connect() as conn:
        conn.execute("DELETE FROM assets WHERE id = ?", (asset_id,))
    return asset


def admin_dashboard(user=None):
    user = user or {"role": "admin", "username": ""}
    owner_where = ""
    owner_params = []
    scan_owner_where = ""
    scan_owner_params = []
    if user.get("role") != "admin":
        owner_where = "WHERE projects.owner_username = ?"
        owner_params.append(user.get("username", ""))
        scan_owner_where = "WHERE projects.owner_username = ?"
        scan_owner_params.append(user.get("username", ""))
    with db_connect() as conn:
        project_count = conn.execute(f"SELECT COUNT(*) AS value FROM projects {owner_where}", owner_params).fetchone()["value"]
        page_count = conn.execute(
            f"SELECT COUNT(*) AS value FROM pages JOIN projects ON projects.id = pages.project_id {owner_where}",
            owner_params,
        ).fetchone()["value"]
        enabled_page_count = conn.execute(
            f"""
            SELECT COUNT(*) AS value
            FROM pages JOIN projects ON projects.id = pages.project_id
            {owner_where + (' AND' if owner_where else 'WHERE')} pages.enabled = 1 AND pages.review_status = 'approved'
            """,
            owner_params,
        ).fetchone()["value"]
        pending_count = conn.execute(
            f"""
            SELECT COUNT(*) AS value
            FROM pages JOIN projects ON projects.id = pages.project_id
            {owner_where + (' AND' if owner_where else 'WHERE')} pages.review_status IN ('pending','pending_delete')
            """,
            owner_params,
        ).fetchone()["value"]
        rejected_count = conn.execute(
            f"""
            SELECT COUNT(*) AS value
            FROM pages JOIN projects ON projects.id = pages.project_id
            {owner_where + (' AND' if owner_where else 'WHERE')} pages.review_status = 'rejected'
            """,
            owner_params,
        ).fetchone()["value"]
        if user.get("role") == "admin":
            scan_count = conn.execute("SELECT COUNT(*) AS value FROM scans").fetchone()["value"]
            today_scan_count = conn.execute(
                "SELECT COUNT(*) AS value FROM scans WHERE substr(created_at, 1, 10) = ?",
                (now_iso()[:10],),
            ).fetchone()["value"]
        else:
            scan_count = conn.execute(
                """
                SELECT COUNT(*) AS value
                FROM scans
                JOIN projects ON projects.id = scans.project_id
                WHERE projects.owner_username = ?
                """,
                scan_owner_params,
            ).fetchone()["value"]
            today_scan_count = conn.execute(
                """
                SELECT COUNT(*) AS value
                FROM scans
                JOIN projects ON projects.id = scans.project_id
                WHERE projects.owner_username = ? AND substr(scans.created_at, 1, 10) = ?
                """,
                (*scan_owner_params, now_iso()[:10]),
            ).fetchone()["value"]
        deployed = conn.execute(
            f"""
            SELECT
                MAX(CASE WHEN deployed = 1 THEN name ELSE '' END) AS welcome_name,
                MAX(CASE WHEN content_deployed = 1 THEN name ELSE '' END) AS content_name
            FROM projects
            {owner_where}
            """,
            owner_params,
        ).fetchone()
        categories = conn.execute(
            f"""
            SELECT category, COUNT(*) AS count
            FROM pages JOIN projects ON projects.id = pages.project_id
            {owner_where}
            GROUP BY category
            ORDER BY count DESC, category
            LIMIT 8
            """,
            owner_params,
        ).fetchall()
        recent_scans = conn.execute(
            f"""
            SELECT scans.id, scans.code, scans.raw_url, scans.created_at, pages.title, projects.name AS project_name
            FROM scans
            LEFT JOIN projects ON projects.id = scans.project_id
            LEFT JOIN pages ON pages.project_id = scans.project_id AND pages.code = scans.code
            {scan_owner_where}
            ORDER BY scans.created_at DESC, scans.id DESC
            LIMIT 8
            """,
            scan_owner_params,
        ).fetchall()
        recent_projects = conn.execute(
            f"""
            SELECT p.*, users.display_name AS owner_display_name, users.enabled AS owner_enabled,
                   COUNT(pages.id) AS page_count, 0 AS scan_count, 0 AS pending_page_count
            FROM projects p
            LEFT JOIN users ON users.username = p.owner_username
            LEFT JOIN pages ON pages.project_id = p.id
            {owner_where.replace('projects.', 'p.')}
            GROUP BY p.id
            ORDER BY p.updated_at DESC, p.id DESC
            LIMIT 6
            """,
            owner_params,
        ).fetchall()

    return {
        "summary": {
            "projects": int(project_count or 0),
            "pages": int(page_count or 0),
            "enabledPages": int(enabled_page_count or 0),
            "pendingPages": int(pending_count or 0),
            "rejectedPages": int(rejected_count or 0),
            "scans": int(scan_count or 0),
            "todayScans": int(today_scan_count or 0),
            "welcomeDeployed": deployed["welcome_name"] or "",
            "contentDeployed": deployed["content_name"] or "",
            "clients": len(SSE_CLIENTS),
        },
        "categories": [{"name": row["category"] or "未分类", "count": row["count"]} for row in categories],
        "recentScans": [
            {
                "id": row["id"],
                "code": row["code"],
                "url": row["raw_url"],
                "title": row["title"] or "",
                "projectName": row["project_name"] or "",
                "createdAt": row["created_at"],
            }
            for row in recent_scans
        ],
        "recentProjects": [row_to_project(row) for row in recent_projects],
        "logs": list_admin_logs(8) if user.get("role") == "admin" else list_admin_logs(8, username=user.get("username", "")),
        "operations": operations_summary(user),
    }


def upsert_project(project_id, data):
    current = get_project(project_id) if project_id else None
    current = current or {}

    def field(name, default=""):
        if name in data:
            return str(data.get(name) or "").strip()
        return str(current.get(name, default) or "").strip()

    project = {
        "name": field("name", "新的学校大屏项目") or "新的学校大屏项目",
        "idle_kicker": field("idleKicker", "学校简介"),
        "idle_title": field("idleTitle", "欢迎来到毕节职业技术学院"),
        "idle_copy": field("idleCopy", DEFAULT_DISPLAY_CONFIG["summaryCopy"]),
        "welcome_kicker": field("welcomeKicker", "Welcome"),
        "welcome_title": field("welcomeTitle", "欢迎参观 {title}"),
        "welcome_subtitle": field("welcomeSubtitle", "即将进入展示页面"),
        "default_image_url": field("defaultImageUrl", "/static/expo-stage.png") or "/static/expo-stage.png",
        "accent": field("accent", "#f59a13") or "#f59a13",
        "display_config": display_config_json(
            data.get("displayConfig") if "displayConfig" in data else current.get("displayConfig", {})
        ),
        "updated_at": now_iso(),
    }

    with db_connect() as conn:
        if project_id:
            conn.execute(
                """
                UPDATE projects SET
                    name = ?, idle_kicker = ?, idle_title = ?, idle_copy = ?,
                    welcome_kicker = ?, welcome_title = ?, welcome_subtitle = ?,
                    default_image_url = ?, accent = ?, display_config = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    project["name"],
                    project["idle_kicker"],
                    project["idle_title"],
                    project["idle_copy"],
                    project["welcome_kicker"],
                    project["welcome_title"],
                    project["welcome_subtitle"],
                    project["default_image_url"],
                    project["accent"],
                    project["display_config"],
                    project["updated_at"],
                    project_id,
                ),
            )
        else:
            cursor = conn.execute(
                """
                INSERT INTO projects (
                    name, idle_kicker, idle_title, idle_copy, welcome_kicker,
                    welcome_title, welcome_subtitle, default_image_url, accent, display_config, deployed, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?)
                """,
                (
                    project["name"],
                    project["idle_kicker"],
                    project["idle_title"],
                    project["idle_copy"],
                    project["welcome_kicker"],
                    project["welcome_title"],
                    project["welcome_subtitle"],
                    project["default_image_url"],
                    project["accent"],
                    project["display_config"],
                    project["updated_at"],
                ),
            )
            project_id = cursor.lastrowid
    return get_project(project_id)


def summarize_changes(before, after):
    before = before or {}
    after = after or {}
    changed = []
    for key in sorted(set(before.keys()) | set(after.keys())):
        if before.get(key) != after.get(key):
            changed.append(key)
    return ",".join(changed[:30])


REVIEW_FIELD_LABELS = {
    "name": "项目名称",
    "ownerUsername": "归属账号",
    "idleKicker": "欢迎页小标题",
    "idleTitle": "欢迎页标题",
    "idleCopy": "欢迎页简介",
    "welcomeKicker": "进入页小标题",
    "welcomeTitle": "进入页标题",
    "welcomeSubtitle": "进入页副标题",
    "defaultImageUrl": "默认图片",
    "accent": "主题色",
    "displayConfig": "展示配置",
    "code": "编号",
    "category": "栏目",
    "source": "来源",
    "publishedAt": "发布日期",
    "title": "标题",
    "subtitle": "副标题",
    "body": "正文",
    "imageUrl": "图片",
    "enabled": "启用状态",
}


def review_value(value):
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    if isinstance(value, bool):
        return "是" if value else "否"
    return "" if value is None else str(value)


def review_diffs(before, after):
    before = before or {}
    after = after or {}
    keys = [key for key in REVIEW_FIELD_LABELS if key in before or key in after]
    keys.extend(sorted((set(before.keys()) | set(after.keys())) - set(keys)))
    diffs = []
    for key in keys:
        before_value = review_value(before.get(key))
        after_value = review_value(after.get(key))
        diffs.append(
            {
                "field": key,
                "label": REVIEW_FIELD_LABELS.get(key, key),
                "before": before_value,
                "after": after_value,
                "changed": before_value != after_value,
            }
        )
    return diffs


def project_public_payload(project):
    return {
        "name": project.get("name", ""),
        "ownerUsername": project.get("ownerUsername", ADMIN_USERNAME),
        "idleKicker": project.get("idleKicker", ""),
        "idleTitle": project.get("idleTitle", ""),
        "idleCopy": project.get("idleCopy", ""),
        "welcomeKicker": project.get("welcomeKicker", "Welcome"),
        "welcomeTitle": project.get("welcomeTitle", "Welcome to {title}"),
        "welcomeSubtitle": project.get("welcomeSubtitle", ""),
        "defaultImageUrl": project.get("defaultImageUrl", ""),
        "accent": project.get("accent", "#f59a13"),
        "displayConfig": project.get("displayConfig", {}),
    }


def page_public_payload(page):
    page = page or {}
    return {
        "code": page.get("code", ""),
        "category": page.get("category", DEFAULT_PAGE_CATEGORY),
        "source": page.get("source", DEFAULT_PAGE_SOURCE),
        "publishedAt": page.get("publishedAt", ""),
        "title": page.get("title", ""),
        "subtitle": page.get("subtitle", ""),
        "body": page.get("body", ""),
        "imageUrl": page.get("imageUrl", ""),
        "accent": page.get("accent", "#0f766e"),
        "enabled": bool(page.get("enabled", True)),
    }


def project_payload_from_data(data, current=None):
    current = current or {}

    def field(name, default=""):
        if name in data:
            return str(data.get(name) or "").strip()
        return str(current.get(name, default) or "").strip()

    display_config = data.get("displayConfig") if "displayConfig" in data else current.get("displayConfig", {})
    return {
        "name": field("name", "New display project") or "New display project",
        "owner_username": field("ownerUsername", current.get("ownerUsername", ADMIN_USERNAME)) or ADMIN_USERNAME,
        "idle_kicker": field("idleKicker", "School intro"),
        "idle_title": field("idleTitle", DEFAULT_PROJECT_NAME),
        "idle_copy": field("idleCopy", DEFAULT_DISPLAY_CONFIG["summaryCopy"]),
        "welcome_kicker": field("welcomeKicker", "Welcome"),
        "welcome_title": field("welcomeTitle", "Welcome to {title}"),
        "welcome_subtitle": field("welcomeSubtitle", "Opening display page"),
        "default_image_url": field("defaultImageUrl", "/static/expo-stage.png") or "/static/expo-stage.png",
        "accent": field("accent", "#f59a13") or "#f59a13",
        "display_config": display_config_json(display_config),
        "updated_at": now_iso(),
    }


def project_payload_to_public(payload):
    return {
        "name": payload["name"],
        "ownerUsername": payload["owner_username"],
        "idleKicker": payload["idle_kicker"],
        "idleTitle": payload["idle_title"],
        "idleCopy": payload["idle_copy"],
        "welcomeKicker": payload["welcome_kicker"],
        "welcomeTitle": payload["welcome_title"],
        "welcomeSubtitle": payload["welcome_subtitle"],
        "defaultImageUrl": payload["default_image_url"],
        "accent": payload["accent"],
        "displayConfig": normalize_display_config(payload["display_config"]),
    }


def save_project(project_id, data, actor=None):
    actor = actor or {"username": ADMIN_USERNAME}
    current = get_project(project_id) if project_id else None
    current = current or {}
    payload = project_payload_from_data(data, current)
    before = project_public_payload(current)
    after = project_payload_to_public(payload)
    with db_connect() as conn:
        if project_id:
            conn.execute(
                """
                UPDATE projects SET
                    name = ?, owner_username = ?, idle_kicker = ?, idle_title = ?, idle_copy = ?,
                    welcome_kicker = ?, welcome_title = ?, welcome_subtitle = ?,
                    default_image_url = ?, accent = ?, display_config = ?,
                    config_status = 'approved', pending_config_version_id = NULL, updated_at = ?
                WHERE id = ?
                """,
                (
                    payload["name"],
                    payload["owner_username"],
                    payload["idle_kicker"],
                    payload["idle_title"],
                    payload["idle_copy"],
                    payload["welcome_kicker"],
                    payload["welcome_title"],
                    payload["welcome_subtitle"],
                    payload["default_image_url"],
                    payload["accent"],
                    payload["display_config"],
                    payload["updated_at"],
                    project_id,
                ),
            )
        else:
            cursor = conn.execute(
                """
                INSERT INTO projects (
                    name, owner_username, idle_kicker, idle_title, idle_copy, welcome_kicker,
                    welcome_title, welcome_subtitle, default_image_url, accent, display_config,
                    deployed, content_deployed, config_status, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, 'approved', ?)
                """,
                (
                    payload["name"],
                    payload["owner_username"],
                    payload["idle_kicker"],
                    payload["idle_title"],
                    payload["idle_copy"],
                    payload["welcome_kicker"],
                    payload["welcome_title"],
                    payload["welcome_subtitle"],
                    payload["default_image_url"],
                    payload["accent"],
                    payload["display_config"],
                    payload["updated_at"],
                ),
            )
            project_id = cursor.lastrowid
        conn.execute(
            """
            INSERT INTO project_versions (
                project_id, status, snapshot, submitted_by, submitted_at,
                reviewed_by, reviewed_at, changes
            )
            VALUES (?, 'approved', ?, ?, ?, ?, ?, ?)
            """,
            (
                project_id,
                json.dumps(after, ensure_ascii=False),
                actor.get("username", ADMIN_USERNAME),
                now_iso(),
                actor.get("username", ADMIN_USERNAME),
                now_iso(),
                summarize_changes(before, after),
            ),
        )
    return get_project(project_id)


def submit_project_config(project_id, data, user):
    project = get_project(project_id)
    if not project:
        return None
    before = project_public_payload(project)
    payload = project_payload_from_data(data, project)
    proposed = project_payload_to_public(payload)
    proposed["ownerUsername"] = project.get("ownerUsername", ADMIN_USERNAME)
    changes = summarize_changes(before, proposed)
    with db_connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO project_versions (
                project_id, status, snapshot, submitted_by, submitted_at, changes
            )
            VALUES (?, 'pending', ?, ?, ?, ?)
            """,
            (project_id, json.dumps(proposed, ensure_ascii=False), user["username"], now_iso(), changes),
        )
        version_id = cursor.lastrowid
        conn.execute(
            "UPDATE projects SET config_status = 'pending', pending_config_version_id = ?, updated_at = ? WHERE id = ?",
            (version_id, now_iso(), project_id),
        )
    return get_project(project_id)


def deploy_project_check(project_id):
    result = {"ok": True, "projectId": project_id, "errors": [], "warnings": []}
    with db_connect() as conn:
        row = conn.execute("SELECT id, config_status FROM projects WHERE id = ?", (project_id,)).fetchone()
    if not row:
        result["ok"] = False
        result["errors"].append("项目不存在")
    elif row["config_status"] == "pending":
        result["ok"] = False
        result["errors"].append("项目配置正在等待审核")
    return result


def deploy_project(project_id):
    check = deploy_project_check(project_id)
    if not check["ok"]:
        raise ValueError("; ".join(check["errors"]))
    with db_connect() as conn:
        conn.execute("UPDATE projects SET deployed = CASE WHEN id = ? THEN 1 ELSE 0 END", (project_id,))
    return get_project(project_id)


def upload_url_to_key(url):
    url = str(url or "").strip()
    if not url:
        return ""
    parsed = urlparse(url)
    path = parsed.path if parsed.scheme else url
    if path.startswith("/uploads/"):
        return path.removeprefix("/uploads/").lstrip("/")
    public_base = os.environ.get("ASSET_PUBLIC_BASE_URL", "").strip().rstrip("/")
    if public_base and url.startswith(public_base + "/"):
        return url.removeprefix(public_base + "/").lstrip("/")
    return ""


def local_upload_missing(url):
    if asset_storage_backend() != "local":
        return False
    key = upload_url_to_key(url)
    if not key:
        return False
    target = (UPLOAD_DIR / key).resolve()
    root = UPLOAD_DIR.resolve()
    if root not in target.parents and target != root:
        return True
    return not target.exists()


def referenced_urls_from_text(text):
    text = str(text or "")
    urls = set(re.findall(r"""(?:src|href)=["']([^"']+)["']""", text, flags=re.I))
    urls.update(re.findall(r"""(?<![\w/])(/uploads/[^\s"'<>),]+)""", text))
    return urls


def page_asset_urls(page):
    urls = set()
    if page.get("imageUrl"):
        urls.add(page["imageUrl"])
    urls.update(referenced_urls_from_text(page.get("body", "")))
    return urls


def deploy_content_check(project_id, page_ids=None):
    result = {
        "ok": True,
        "projectId": project_id,
        "pageIds": [],
        "errors": [],
        "warnings": [],
        "eligiblePageIds": [],
    }
    with db_connect() as conn:
        project = conn.execute("SELECT id, config_status FROM projects WHERE id = ?", (project_id,)).fetchone()
        if not project:
            result["ok"] = False
            result["errors"].append("项目不存在")
            return result
        if project["config_status"] == "pending":
            result["warnings"].append("项目配置有待审核版本")

        eligible_rows = conn.execute(
            "SELECT id FROM pages WHERE project_id = ? AND review_status = 'approved' AND enabled = 1 ORDER BY id",
            (project_id,),
        ).fetchall()
        eligible_ids = [int(row["id"]) for row in eligible_rows]
        result["eligiblePageIds"] = eligible_ids

        pending_count = conn.execute(
            """
            SELECT COUNT(*) AS value
            FROM pages
            WHERE project_id = ? AND review_status IN ('pending','pending_delete')
            """,
            (project_id,),
        ).fetchone()["value"]
        if int(pending_count or 0):
            result["warnings"].append(f"{int(pending_count)} 个页面仍在等待审核")

        if page_ids is None:
            selected_ids = eligible_ids
        else:
            selected_ids = [int(page_id) for page_id in page_ids if str(page_id).isdigit()]
        result["pageIds"] = selected_ids
        if not selected_ids:
            result["errors"].append("未选择可部署页面")
        for page_id in selected_ids:
            row = conn.execute(
                """
                SELECT id, code, title, body, image_url, enabled, review_status
                FROM pages
                WHERE id = ? AND project_id = ?
                """,
                (page_id, project_id),
            ).fetchone()
            if not row:
                result["errors"].append(f"page {page_id} 不属于当前项目")
                continue
            if row["review_status"] != "approved" or not bool(row["enabled"]):
                result["errors"].append(f"page {row['code']} 未通过审核或未启用")
                continue
            page = {"body": row["body"], "imageUrl": row["image_url"]}
            for url in sorted(page_asset_urls(page)):
                if local_upload_missing(url):
                    result["errors"].append(f"page {row['code']} 缺少资源：{url}")
    result["ok"] = not result["errors"]
    return result


def deploy_content_project(project_id, page_ids=None):
    check = deploy_content_check(project_id, page_ids)
    if not check["ok"]:
        raise ValueError("; ".join(check["errors"]))
    with db_connect() as conn:
        exists = conn.execute("SELECT id FROM projects WHERE id = ?", (project_id,)).fetchone()
        if not exists:
            return None
        if page_ids is None:
            rows = conn.execute(
                "SELECT id FROM pages WHERE project_id = ? AND review_status = 'approved' AND enabled = 1",
                (project_id,),
            ).fetchall()
            page_ids = [row["id"] for row in rows]
        page_ids = [int(page_id) for page_id in page_ids if str(page_id).isdigit()]
        conn.execute("UPDATE projects SET content_deployed = CASE WHEN id = ? THEN 1 ELSE 0 END", (project_id,))
        conn.execute("DELETE FROM deployed_pages")
        for page_id in page_ids:
            row = conn.execute(
                """
                SELECT id FROM pages
                WHERE id = ? AND project_id = ? AND review_status = 'approved' AND enabled = 1
                """,
                (page_id, project_id),
            ).fetchone()
            if row:
                conn.execute(
                    "INSERT OR IGNORE INTO deployed_pages (project_id, page_id, updated_at) VALUES (?, ?, ?)",
                    (project_id, page_id, now_iso()),
                )
    return get_project(project_id)


def delete_project(project_id):
    with db_connect() as conn:
        row = conn.execute("SELECT id, deployed, content_deployed FROM projects WHERE id = ?", (project_id,)).fetchone()
        if not row:
            return False
        conn.execute("DELETE FROM deployed_pages WHERE project_id = ?", (project_id,))
        conn.execute("DELETE FROM pages WHERE project_id = ?", (project_id,))
        conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))

        if int(row["deployed"]) == 1 and not conn.execute("SELECT id FROM projects WHERE deployed = 1 LIMIT 1").fetchone():
            fallback = conn.execute("SELECT id FROM projects ORDER BY updated_at DESC, id DESC LIMIT 1").fetchone()
            if fallback:
                conn.execute("UPDATE projects SET deployed = CASE WHEN id = ? THEN 1 ELSE 0 END", (fallback["id"],))

        if int(row["content_deployed"]) == 1 and not conn.execute(
            "SELECT id FROM projects WHERE content_deployed = 1 LIMIT 1"
        ).fetchone():
            fallback = conn.execute("SELECT id FROM projects ORDER BY updated_at DESC, id DESC LIMIT 1").fetchone()
            if fallback:
                conn.execute(
                    "UPDATE projects SET content_deployed = CASE WHEN id = ? THEN 1 ELSE 0 END",
                    (fallback["id"],),
                )
    return True


def delete_page(project_id, code):
    with db_connect() as conn:
        cursor = conn.execute("DELETE FROM pages WHERE project_id = ? AND code = ?", (project_id, code))
        return cursor.rowcount > 0


def copy_project(project_id, data=None):
    source = get_project(project_id)
    if not source:
        return None

    data = data if isinstance(data, dict) else {}
    name = str(data.get("name") or "").strip() or f"{source['name']} 复制"
    copied = upsert_project(
        None,
        {
            "name": name,
            "idleKicker": source.get("idleKicker", ""),
            "idleTitle": source.get("idleTitle", ""),
            "idleCopy": source.get("idleCopy", ""),
            "welcomeKicker": source.get("welcomeKicker", "Welcome"),
            "welcomeTitle": source.get("welcomeTitle", "欢迎参观 {title}"),
            "welcomeSubtitle": source.get("welcomeSubtitle", "即将进入展示页面"),
            "defaultImageUrl": source.get("defaultImageUrl", "/static/expo-stage.png"),
            "accent": source.get("accent", "#f59a13"),
            "displayConfig": source.get("displayConfig", {}),
        },
    )
    if not copied:
        return None

    with db_connect() as conn:
        rows = conn.execute(
            "SELECT * FROM pages WHERE project_id = ? ORDER BY updated_at DESC, id DESC",
            (project_id,),
        ).fetchall()
        for row in rows:
            code = unique_page_code(conn, row["code"])
            conn.execute(
                """
                INSERT INTO pages (
                    project_id, code, category, source, published_at,
                    title, subtitle, body, image_url, accent, enabled, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    copied["id"],
                    code,
                    row["category"] if "category" in row.keys() else DEFAULT_PAGE_CATEGORY,
                    row["source"] if "source" in row.keys() else DEFAULT_PAGE_SOURCE,
                    row["published_at"] if "published_at" in row.keys() else "",
                    row["title"],
                    row["subtitle"],
                    row["body"],
                    row["image_url"],
                    row["accent"],
                    row["enabled"],
                    now_iso(),
                ),
            )

    return copied


def row_to_page(row):
    if not row:
        return None
    page = {
        "id": row["id"],
        "projectId": row["project_id"],
        "code": row["code"],
        "category": row["category"] if "category" in row.keys() else DEFAULT_PAGE_CATEGORY,
        "source": row["source"] if "source" in row.keys() else DEFAULT_PAGE_SOURCE,
        "publishedAt": row["published_at"] if "published_at" in row.keys() else "",
        "title": row["title"],
        "subtitle": row["subtitle"],
        "body": row["body"],
        "imageUrl": row["image_url"],
        "accent": row["accent"],
        "enabled": bool(row["enabled"]),
        "reviewStatus": row["review_status"] if "review_status" in row.keys() else "approved",
        "pendingVersionId": row["pending_version_id"] if "pending_version_id" in row.keys() else None,
        "submittedBy": row["submitted_by"] if "submitted_by" in row.keys() else "",
        "reviewedBy": row["reviewed_by"] if "reviewed_by" in row.keys() else "",
        "reviewNote": row["review_note"] if "review_note" in row.keys() else "",
        "qrAvailable": bool(row["enabled"]) and (row["review_status"] if "review_status" in row.keys() else "approved") == "approved",
        "updatedAt": row["updated_at"],
    }
    draft = None
    if "draft_snapshot" in row.keys() and row["draft_snapshot"]:
        try:
            draft = json.loads(row["draft_snapshot"])
        except json.JSONDecodeError:
            draft = None
    if draft:
        page["draft"] = draft
        if page["reviewStatus"] in {"pending", "pending_delete", "rejected"}:
            for key in ("code", "category", "source", "publishedAt", "title", "subtitle", "body", "imageUrl", "accent", "enabled"):
                if key in draft:
                    page[key] = draft[key]
            page["deleteRequested"] = page["reviewStatus"] == "pending_delete"
    page["published"] = {
        "code": row["code"],
        "category": row["category"] if "category" in row.keys() else DEFAULT_PAGE_CATEGORY,
        "source": row["source"] if "source" in row.keys() else DEFAULT_PAGE_SOURCE,
        "publishedAt": row["published_at"] if "published_at" in row.keys() else "",
        "title": row["title"],
        "subtitle": row["subtitle"],
        "body": row["body"],
        "imageUrl": row["image_url"],
        "accent": row["accent"],
        "enabled": bool(row["enabled"]),
    }
    return page


def get_page(project_id, code):
    with db_connect() as conn:
        row = conn.execute(
            """
            SELECT pages.*, pending.snapshot AS draft_snapshot
            FROM pages
            LEFT JOIN page_versions pending ON pending.id = pages.pending_version_id
            WHERE pages.project_id = ? AND pages.code = ?
            """,
            (project_id, code),
        ).fetchone()
    return row_to_page(row)


def get_page_by_id(page_id):
    with db_connect() as conn:
        row = conn.execute(
            """
            SELECT pages.*, pending.snapshot AS draft_snapshot
            FROM pages
            LEFT JOIN page_versions pending ON pending.id = pages.pending_version_id
            WHERE pages.id = ?
            """,
            (page_id,),
        ).fetchone()
    return row_to_page(row)


def get_page_by_code(code):
    with db_connect() as conn:
        row = conn.execute(
            """
            SELECT pages.*, pending.snapshot AS draft_snapshot
            FROM pages
            LEFT JOIN page_versions pending ON pending.id = pages.pending_version_id
            WHERE pages.code = ? ORDER BY pages.project_id, pages.id LIMIT 1
            """,
            (code,),
        ).fetchone()
    return row_to_page(row)


def page_code_conflict(project_id, code, exclude_page_id=None):
    with db_connect() as conn:
        if exclude_page_id:
            row = conn.execute(
                "SELECT id, project_id, title FROM pages WHERE project_id = ? AND code = ? AND id != ? LIMIT 1",
                (project_id, code, exclude_page_id),
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT id, project_id, title FROM pages WHERE project_id = ? AND code = ? LIMIT 1",
                (project_id, code),
            ).fetchone()
    return dict(row) if row else None


def list_pages(project_id):
    with db_connect() as conn:
        rows = conn.execute(
            """
            SELECT pages.*, pending.snapshot AS draft_snapshot
            FROM pages
            LEFT JOIN page_versions pending ON pending.id = pages.pending_version_id
            WHERE pages.project_id = ?
            ORDER BY pages.updated_at DESC
            """,
            (project_id,),
        ).fetchall()
    return [row_to_page(row) for row in rows]


def upsert_page(project_id, code, data):
    code = str(code or "").strip()
    if not code:
        raise ValueError("code 不能为空")

    previous_code = str(data.get("previousCode") or data.get("oldCode") or "").strip()
    current = get_page(project_id, code)
    if not current and previous_code and previous_code != code:
        current = get_page(project_id, previous_code)
    current = current or {}
    current_id = current.get("id")
    conflict = page_code_conflict(project_id, code, current_id)
    if conflict:
        raise ValueError(f"编号 {code} 已被其他展示页使用")

    def field(name, default=""):
        if name in data:
            return str(data.get(name) or "").strip()
        return str(current.get(name, default) or "").strip()

    if "enabled" in data:
        enabled = 1 if data.get("enabled") else 0
    else:
        enabled = 1 if current.get("enabled", True) else 0

    page = {
        "category": field("category", DEFAULT_PAGE_CATEGORY) or DEFAULT_PAGE_CATEGORY,
        "source": field("source", DEFAULT_PAGE_SOURCE) or DEFAULT_PAGE_SOURCE,
        "published_at": field("publishedAt", field("published_at")),
        "title": field("title", "未命名展示页") or "未命名展示页",
        "subtitle": field("subtitle"),
        "body": sanitize_rich_html(field("body")),
        "image_url": field("imageUrl"),
        "accent": field("accent", "#0f766e") or "#0f766e",
        "enabled": enabled,
        "updated_at": now_iso(),
    }
    with db_connect() as conn:
        if current_id:
            conn.execute(
                """
                UPDATE pages SET
                    code = ?, category = ?, source = ?, published_at = ?,
                    title = ?, subtitle = ?, body = ?, image_url = ?,
                    accent = ?, enabled = ?, updated_at = ?
                WHERE id = ? AND project_id = ?
                """,
                (
                    code,
                    page["category"],
                    page["source"],
                    page["published_at"],
                    page["title"],
                    page["subtitle"],
                    page["body"],
                    page["image_url"],
                    page["accent"],
                    page["enabled"],
                    page["updated_at"],
                    current_id,
                    project_id,
                ),
            )
        else:
            cursor = conn.execute(
                """
                INSERT INTO pages (
                    project_id, code, category, source, published_at,
                    title, subtitle, body, image_url, accent, enabled, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    project_id,
                    code,
                    page["category"],
                    page["source"],
                    page["published_at"],
                    page["title"],
                    page["subtitle"],
                    page["body"],
                    page["image_url"],
                    page["accent"],
                    page["enabled"],
                    page["updated_at"],
                ),
            )
            current_id = cursor.lastrowid
    return get_page_by_id(current_id)


def page_payload_from_data(data, current=None):
    current = current or {}

    def field(name, default=""):
        if name in data:
            return str(data.get(name) or "").strip()
        return str(current.get(name, default) or "").strip()

    enabled = data.get("enabled", current.get("enabled", True))
    return {
        "code": field("code", current.get("code", "")),
        "category": field("category", DEFAULT_PAGE_CATEGORY) or DEFAULT_PAGE_CATEGORY,
        "source": field("source", DEFAULT_PAGE_SOURCE) or DEFAULT_PAGE_SOURCE,
        "publishedAt": field("publishedAt", current.get("publishedAt", "")),
        "title": field("title", "Untitled page") or "Untitled page",
        "subtitle": field("subtitle"),
        "body": sanitize_rich_html(field("body")),
        "imageUrl": field("imageUrl"),
        "accent": field("accent", "#0f766e") or "#0f766e",
        "enabled": bool(enabled),
    }


def write_page_snapshot(conn, project_id, code, snapshot, current_id=None, actor=None, status="approved", operation="upsert"):
    actor = actor or {"username": ADMIN_USERNAME}
    changes = summarize_changes(page_snapshot_from_row(conn.execute("SELECT * FROM pages WHERE id = ?", (current_id,)).fetchone()) if current_id else {}, snapshot)
    cursor = conn.execute(
        """
        INSERT INTO page_versions (
            page_id, project_id, code, operation, status, snapshot,
            submitted_by, submitted_at, reviewed_by, reviewed_at, changes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            current_id,
            project_id,
            code,
            operation,
            status,
            json.dumps(snapshot, ensure_ascii=False),
            actor.get("username", ADMIN_USERNAME),
            now_iso(),
            actor.get("username", ADMIN_USERNAME) if status == "approved" else "",
            now_iso() if status == "approved" else "",
            changes,
        ),
    )
    return cursor.lastrowid


def apply_page_snapshot(conn, project_id, page_id, snapshot, actor=None):
    actor = actor or {"username": ADMIN_USERNAME}
    now = now_iso()
    if page_id:
        conn.execute(
            """
            UPDATE pages SET
                code = ?, category = ?, source = ?, published_at = ?,
                title = ?, subtitle = ?, body = ?, image_url = ?, accent = ?,
                enabled = ?, review_status = 'approved', pending_version_id = NULL,
                reviewed_by = ?, review_note = '', updated_at = ?
            WHERE id = ? AND project_id = ?
            """,
            (
                snapshot["code"],
                snapshot["category"],
                snapshot["source"],
                snapshot["publishedAt"],
                snapshot["title"],
                snapshot["subtitle"],
                snapshot["body"],
                snapshot["imageUrl"],
                snapshot["accent"],
                1 if snapshot.get("enabled", True) else 0,
                actor.get("username", ADMIN_USERNAME),
                now,
                page_id,
                project_id,
            ),
        )
        return page_id
    cursor = conn.execute(
        """
        INSERT INTO pages (
            project_id, code, category, source, published_at, title, subtitle,
            body, image_url, accent, enabled, review_status, submitted_by,
            reviewed_by, review_note, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'approved', ?, ?, '', ?)
        """,
        (
            project_id,
            snapshot["code"],
            snapshot["category"],
            snapshot["source"],
            snapshot["publishedAt"],
            snapshot["title"],
            snapshot["subtitle"],
            snapshot["body"],
            snapshot["imageUrl"],
            snapshot["accent"],
            1 if snapshot.get("enabled", True) else 0,
            actor.get("username", ADMIN_USERNAME),
            actor.get("username", ADMIN_USERNAME),
            now,
        ),
    )
    return cursor.lastrowid


def save_page(project_id, code, data, actor, approve_now=False):
    code = str(code or "").strip()
    if not code:
        raise ValueError("code 不能为空")
    previous_code = str(data.get("previousCode") or data.get("oldCode") or "").strip()
    current = get_page(project_id, code)
    if not current and previous_code and previous_code != code:
        current = get_page(project_id, previous_code)
    current = current or {}
    current_id = current.get("id")
    conflict = page_code_conflict(project_id, code, current_id)
    if conflict:
        raise ValueError(f"code {code} 已被当前项目中的其他展示页使用")
    snapshot = page_payload_from_data({**data, "code": code}, current)
    with db_connect() as conn:
        if approve_now:
            page_id = apply_page_snapshot(conn, project_id, current_id, snapshot, actor)
            version_id = write_page_snapshot(conn, project_id, snapshot["code"], snapshot, page_id, actor, "approved", "upsert")
            conn.execute("UPDATE page_versions SET page_id = ? WHERE id = ?", (page_id, version_id))
        else:
            if current_id:
                page_id = current_id
            else:
                cursor = conn.execute(
                    """
                    INSERT INTO pages (
                        project_id, code, category, source, published_at, title, subtitle,
                        body, image_url, accent, enabled, review_status, submitted_by,
                        reviewed_by, review_note, updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 'pending', ?, '', '', ?)
                    """,
                    (
                        project_id,
                        snapshot["code"],
                        snapshot["category"],
                        snapshot["source"],
                        snapshot["publishedAt"],
                        snapshot["title"],
                        snapshot["subtitle"],
                        snapshot["body"],
                        snapshot["imageUrl"],
                        snapshot["accent"],
                        actor.get("username", ""),
                        now_iso(),
                    ),
                )
                page_id = cursor.lastrowid
            version_id = write_page_snapshot(conn, project_id, snapshot["code"], snapshot, page_id, actor, "pending", "upsert")
            conn.execute(
                """
                UPDATE pages SET review_status = 'pending', pending_version_id = ?,
                    submitted_by = ?, review_note = '', updated_at = ?
                WHERE id = ?
                """,
                (version_id, actor.get("username", ""), now_iso(), page_id),
            )
    return get_page(project_id, snapshot["code"])


def request_delete_page(project_id, code, actor, approve_now=False):
    page = get_page(project_id, code)
    if not page:
        return False
    snapshot = page.get("published", page)
    with db_connect() as conn:
        if approve_now:
            conn.execute("DELETE FROM deployed_pages WHERE page_id = ?", (page["id"],))
            conn.execute(
                "UPDATE pages SET enabled = 0, review_status = 'deleted', pending_version_id = NULL, updated_at = ? WHERE id = ?",
                (now_iso(), page["id"]),
            )
            write_page_snapshot(conn, project_id, code, snapshot, page["id"], actor, "approved", "delete")
        else:
            version_id = write_page_snapshot(conn, project_id, code, snapshot, page["id"], actor, "pending", "delete")
            conn.execute(
                """
                UPDATE pages SET review_status = 'pending_delete', pending_version_id = ?,
                    submitted_by = ?, review_note = '', updated_at = ?
                WHERE id = ?
                """,
                (version_id, actor.get("username", ""), now_iso(), page["id"]),
            )
    return True


def row_to_page_version(row):
    if not row:
        return None
    try:
        snapshot = json.loads(row["snapshot"] or "{}")
    except json.JSONDecodeError:
        snapshot = {}
    current_page = get_page_by_id(row["page_id"]) if row["page_id"] else None
    current = page_public_payload(current_page.get("published") if current_page else None) if current_page else {}
    return {
        "id": row["id"],
        "pageId": row["page_id"],
        "projectId": row["project_id"],
        "projectName": row["project_name"] if "project_name" in row.keys() else "",
        "code": row["code"],
        "operation": row["operation"],
        "status": row["status"],
        "snapshot": snapshot,
        "current": current,
        "diffs": review_diffs(current, snapshot),
        "previewUrl": f"/display?project={row['project_id']}&code={snapshot.get('code') or row['code']}&preview=review&reviewVersion={row['id']}",
        "submittedBy": row["submitted_by"],
        "submittedAt": row["submitted_at"],
        "reviewedBy": row["reviewed_by"],
        "reviewedAt": row["reviewed_at"],
        "reviewNote": row["review_note"],
        "changes": row["changes"],
    }


def row_to_project_version(row):
    if not row:
        return None
    try:
        snapshot = json.loads(row["snapshot"] or "{}")
    except json.JSONDecodeError:
        snapshot = {}
    current_project = get_project(row["project_id"])
    current = project_public_payload(current_project) if current_project else {}
    return {
        "id": row["id"],
        "projectId": row["project_id"],
        "projectName": row["project_name"] if "project_name" in row.keys() else "",
        "status": row["status"],
        "snapshot": snapshot,
        "current": current,
        "diffs": review_diffs(current, snapshot),
        "submittedBy": row["submitted_by"],
        "submittedAt": row["submitted_at"],
        "reviewedBy": row["reviewed_by"],
        "reviewedAt": row["reviewed_at"],
        "reviewNote": row["review_note"],
        "changes": row["changes"],
    }


def list_reviews(status="pending"):
    with db_connect() as conn:
        page_rows = conn.execute(
            """
            SELECT page_versions.*, projects.name AS project_name
            FROM page_versions
            JOIN projects ON projects.id = page_versions.project_id
            WHERE page_versions.status = ?
            ORDER BY page_versions.submitted_at DESC, page_versions.id DESC
            """,
            (status,),
        ).fetchall()
        project_rows = conn.execute(
            """
            SELECT project_versions.*, projects.name AS project_name
            FROM project_versions
            JOIN projects ON projects.id = project_versions.project_id
            WHERE project_versions.status = ?
            ORDER BY project_versions.submitted_at DESC, project_versions.id DESC
            """,
            (status,),
        ).fetchall()
    return {
        "pages": [row_to_page_version(row) for row in page_rows],
        "projects": [row_to_project_version(row) for row in project_rows],
    }


def list_project_versions(project_id):
    with db_connect() as conn:
        rows = conn.execute(
            """
            SELECT project_versions.*, projects.name AS project_name
            FROM project_versions
            JOIN projects ON projects.id = project_versions.project_id
            WHERE project_versions.project_id = ?
            ORDER BY project_versions.submitted_at DESC, project_versions.id DESC
            """,
            (project_id,),
        ).fetchall()
    return [row_to_project_version(row) for row in rows]


def list_page_versions(project_id, code):
    page = get_page(project_id, code)
    page_id = page["id"] if page else 0
    with db_connect() as conn:
        rows = conn.execute(
            """
            SELECT page_versions.*, projects.name AS project_name
            FROM page_versions
            JOIN projects ON projects.id = page_versions.project_id
            WHERE page_versions.project_id = ?
              AND (page_versions.page_id = ? OR page_versions.code = ?)
            ORDER BY page_versions.submitted_at DESC, page_versions.id DESC
            """,
            (project_id, page_id, code),
        ).fetchall()
    return [row_to_page_version(row) for row in rows]


def approve_page_version(version_id, actor, note=""):
    with db_connect() as conn:
        row = conn.execute("SELECT * FROM page_versions WHERE id = ?", (version_id,)).fetchone()
        if not row:
            return None
        version = row_to_page_version(row)
        snapshot = version["snapshot"]
        if version["operation"] == "delete":
            conn.execute("DELETE FROM deployed_pages WHERE page_id = ?", (version["pageId"],))
            conn.execute(
                """
                UPDATE pages SET enabled = 0, review_status = 'deleted', pending_version_id = NULL,
                    reviewed_by = ?, review_note = ?, updated_at = ?
                WHERE id = ?
                """,
                (actor["username"], note, now_iso(), version["pageId"]),
            )
        else:
            page_id = apply_page_snapshot(conn, version["projectId"], version["pageId"], snapshot, actor)
            conn.execute("UPDATE page_versions SET page_id = ? WHERE id = ?", (page_id, version_id))
        conn.execute(
            """
            UPDATE page_versions SET status = 'approved', reviewed_by = ?,
                reviewed_at = ?, review_note = ?
            WHERE id = ?
            """,
            (actor["username"], now_iso(), note, version_id),
        )
    return get_page_by_id(version["pageId"]) if version["pageId"] else None


def reject_page_version(version_id, actor, note=""):
    with db_connect() as conn:
        row = conn.execute("SELECT * FROM page_versions WHERE id = ?", (version_id,)).fetchone()
        if not row:
            return None
        conn.execute(
            """
            UPDATE page_versions SET status = 'rejected', reviewed_by = ?,
                reviewed_at = ?, review_note = ?
            WHERE id = ?
            """,
            (actor["username"], now_iso(), note, version_id),
        )
        conn.execute(
            """
            UPDATE pages SET review_status = 'rejected', review_note = ?,
                reviewed_by = ?, updated_at = ?
            WHERE pending_version_id = ?
            """,
            (note, actor["username"], now_iso(), version_id),
        )
    return row_to_page_version(row)


def approve_project_version(version_id, actor, note=""):
    with db_connect() as conn:
        row = conn.execute("SELECT * FROM project_versions WHERE id = ?", (version_id,)).fetchone()
        if not row:
            return None
        version = row_to_project_version(row)
        snapshot = version["snapshot"]
        payload = project_payload_from_data(snapshot, get_project(version["projectId"]))
        conn.execute(
            """
            UPDATE projects SET
                name = ?, idle_kicker = ?, idle_title = ?, idle_copy = ?,
                welcome_kicker = ?, welcome_title = ?, welcome_subtitle = ?,
                default_image_url = ?, accent = ?, display_config = ?,
                config_status = 'approved', pending_config_version_id = NULL, updated_at = ?
            WHERE id = ?
            """,
            (
                payload["name"],
                payload["idle_kicker"],
                payload["idle_title"],
                payload["idle_copy"],
                payload["welcome_kicker"],
                payload["welcome_title"],
                payload["welcome_subtitle"],
                payload["default_image_url"],
                payload["accent"],
                payload["display_config"],
                now_iso(),
                version["projectId"],
            ),
        )
        conn.execute(
            """
            UPDATE project_versions SET status = 'approved', reviewed_by = ?,
                reviewed_at = ?, review_note = ?
            WHERE id = ?
            """,
            (actor["username"], now_iso(), note, version_id),
        )
    return get_project(version["projectId"])


def reject_project_version(version_id, actor, note=""):
    with db_connect() as conn:
        row = conn.execute("SELECT * FROM project_versions WHERE id = ?", (version_id,)).fetchone()
        if not row:
            return None
        version = row_to_project_version(row)
        conn.execute(
            """
            UPDATE project_versions SET status = 'rejected', reviewed_by = ?,
                reviewed_at = ?, review_note = ?
            WHERE id = ?
            """,
            (actor["username"], now_iso(), note, version_id),
        )
        conn.execute(
            """
            UPDATE projects SET config_status = 'rejected', updated_at = ?
            WHERE pending_config_version_id = ?
            """,
            (now_iso(), version_id),
        )
    return version


def get_display_project(project_id):
    with db_connect() as conn:
        row = conn.execute(
            """
            SELECT p.*, users.display_name AS owner_display_name, users.enabled AS owner_enabled
            FROM projects p
            LEFT JOIN users ON users.username = p.owner_username
            WHERE p.id = ? AND COALESCE(users.enabled, 1) = 1
            """,
            (project_id,),
        ).fetchone()
    return row_to_project(row)


def get_display_page(project_id, code, require_deployed=False):
    with db_connect() as conn:
        sql = """
            SELECT pages.*, NULL AS draft_snapshot
            FROM pages
            JOIN projects ON projects.id = pages.project_id
            LEFT JOIN users ON users.username = projects.owner_username
        """
        params = [project_id, code]
        where = """
            WHERE pages.project_id = ?
              AND pages.code = ?
              AND pages.review_status = 'approved'
              AND pages.enabled = 1
              AND COALESCE(users.enabled, 1) = 1
        """
        if require_deployed:
            sql += " JOIN deployed_pages ON deployed_pages.page_id = pages.id AND deployed_pages.project_id = pages.project_id "
            where += " AND projects.content_deployed = 1"
        row = conn.execute(sql + where, params).fetchone()
    return row_to_page(row)


def scan_code_candidates(code):
    text = str(code or "").strip()
    if not text:
        return []
    candidates = [text]
    if re.fullmatch(r"\d{5,}", text):
        candidates.append(f"DEMO-{text}")
    if text.upper().startswith("DEMO-") and len(text) > 5:
        candidates.append(text[5:])
    unique = []
    for candidate in candidates:
        if candidate and candidate not in unique:
            unique.append(candidate)
    return unique


def find_deployed_display_page(project_id, code):
    for candidate in scan_code_candidates(code):
        page = get_display_page(project_id, candidate, require_deployed=True)
        if page:
            return candidate, page
    return str(code or "").strip(), None


def validated_latest_scan():
    global LAST_SCAN
    scan = LAST_SCAN
    if not scan:
        return None
    try:
        received_at = datetime.fromisoformat(str(scan.get("receivedAt", "")).replace("Z", "+00:00"))
        if (datetime.now(timezone.utc) - received_at).total_seconds() > LATEST_SCAN_SECONDS:
            LAST_SCAN = None
            return None
    except Exception:
        LAST_SCAN = None
        return None
    if scan.get("external"):
        return scan
    project = get_deployed_content_project()
    code = str(scan.get("code") or "")
    project_id = (scan.get("project") or {}).get("id")
    if not project or (project_id and int(project_id) != int(project["id"])):
        LAST_SCAN = None
        return None
    matched_code, page = find_deployed_display_page(project["id"], code)
    if not page:
        LAST_SCAN = None
        return None
    code = matched_code
    scan["code"] = code
    scan["project"] = project
    scan["page"] = page
    scan["localDisplayUrl"] = f"/display?project={project['id']}&code={code}"
    scan["displayUrl"] = scan["localDisplayUrl"]
    return scan


def deployed_page_ids(project_id):
    with db_connect() as conn:
        rows = conn.execute("SELECT page_id FROM deployed_pages WHERE project_id = ?", (project_id,)).fetchall()
    return [row["page_id"] for row in rows]


def extract_code(value):
    text = str(value or "").strip()
    if not text:
        return ""

    parsed = urlparse(text)
    haystack = " ".join([parsed.path, parsed.params, parsed.query, parsed.fragment, text])

    match = re.search(r"activePage/([A-Za-z0-9_-]+)", haystack)
    if match:
        return match.group(1)

    numeric = re.findall(r"\d{5,}", haystack)
    if numeric:
        return numeric[-1]

    return text[-64:]


def normalize_scan_url(value):
    text = str(value or "").strip()
    markdown_match = re.search(r"\((https?://[^)\s]+)\)", text)
    if markdown_match:
        text = markdown_match.group(1)

    inline_match = re.search(r"https?://[^\s\"'<>]+", text)
    if inline_match:
        text = inline_match.group(0)

    parsed = urlparse(text)
    if parsed.scheme not in ("http", "https"):
        return None
    return text


def extract_scan_target(value):
    text = unquote(str(value or "").strip())
    parsed = urlparse(text)
    query = parse_qs(parsed.query)
    if parsed.fragment:
        fragment = parsed.fragment
        if "?" in fragment:
            fragment = fragment.split("?", 1)[1]
        fragment_query = parse_qs(fragment)
        for key, values in fragment_query.items():
            query.setdefault(key, values)

    def first_value(*names):
        for name in names:
            values = query.get(name)
            if values and str(values[0]).strip():
                return str(values[0]).strip()
        return ""

    project_text = first_value("project", "projectId", "pid")
    code = first_value("code", "page", "pageCode")
    project_id = int(project_text) if project_text.isdigit() else None
    if code:
        return project_id, code[-64:]

    haystack = " ".join([parsed.path, parsed.params, parsed.query, parsed.fragment, text])
    match = re.search(r"activePage/([A-Za-z0-9_-]+)", haystack)
    if match:
        return project_id, match.group(1)

    numeric = re.findall(r"\d{5,}", haystack)
    if numeric:
        return project_id, numeric[-1]

    return project_id, text[-64:] if text else ""


def is_admin_display_url(value):
    parsed = urlparse(str(value or "").strip())
    host = parsed.netloc.lower()
    query = parse_qs(parsed.query)
    source = (query.get("source") or [""])[0]
    path = parsed.path.rstrip("/") or "/"
    local_hosts = {"", "127.0.0.1", "localhost", f"127.0.0.1:{PORT}", f"localhost:{PORT}"}
    return (
        source == "expo-admin"
        or (path == "/display" and (not host or host in local_hosts))
    )


def is_external_url(value):
    parsed = urlparse(str(value or "").strip())
    if parsed.scheme not in ("http", "https"):
        return False
    return not is_admin_display_url(value)


def init_qr_field():
    value = 1
    for i in range(255):
        GF_EXP[i] = value
        GF_LOG[value] = i
        value <<= 1
        if value & 0x100:
            value ^= 0x11D
    for i in range(255, 512):
        GF_EXP[i] = GF_EXP[i - 255]


def qr_mul(left, right):
    if not left or not right:
        return 0
    return GF_EXP[GF_LOG[left] + GF_LOG[right]]


def qr_generator_poly(degree):
    poly = [1]
    for i in range(degree):
        next_poly = [0] * (len(poly) + 1)
        for j, coefficient in enumerate(poly):
            next_poly[j] ^= coefficient
            next_poly[j + 1] ^= qr_mul(coefficient, GF_EXP[i])
        poly = next_poly
    return poly


def qr_rs_remainder(data, degree):
    generator = qr_generator_poly(degree)
    result = [0] * degree
    for byte in data:
        factor = byte ^ result.pop(0)
        result.append(0)
        for i in range(degree):
            result[i] ^= qr_mul(generator[i + 1], factor)
    return result


def append_bits(target, value, length):
    for i in range(length - 1, -1, -1):
        target.append((value >> i) & 1)


def qr_format_bits(mask):
    data = (0b01 << 3) | mask
    value = data << 10
    generator = 0x537
    for i in range(14, 9, -1):
        if (value >> i) & 1:
            value ^= generator << (i - 10)
    return ((data << 10) | value) ^ 0x5412


def make_qr_matrix(text):
    if not GF_EXP[0]:
        init_qr_field()

    payload = str(text or "").encode("utf-8")
    if not payload:
        raise ValueError("二维码内容不能为空")

    version = None
    data_codewords = ecc_codewords = 0
    bit_length = 4 + 8 + len(payload) * 8
    for candidate, (data_count, ecc_count) in QR_L_CAPACITY.items():
        if bit_length <= data_count * 8:
            version = candidate
            data_codewords = data_count
            ecc_codewords = ecc_count
            break
    if version is None:
        raise ValueError("二维码内容太长")

    bits = []
    append_bits(bits, 0b0100, 4)
    append_bits(bits, len(payload), 8)
    for byte in payload:
        append_bits(bits, byte, 8)

    capacity_bits = data_codewords * 8
    append_bits(bits, 0, min(4, capacity_bits - len(bits)))
    while len(bits) % 8:
        bits.append(0)

    data = []
    for i in range(0, len(bits), 8):
        byte = 0
        for bit in bits[i : i + 8]:
            byte = (byte << 1) | bit
        data.append(byte)

    pad = 0xEC
    while len(data) < data_codewords:
        data.append(pad)
        pad ^= 0xEC ^ 0x11

    codewords = data + qr_rs_remainder(data, ecc_codewords)
    stream = []
    for byte in codewords:
        append_bits(stream, byte, 8)

    size = version * 4 + 17
    modules = [[False for _ in range(size)] for _ in range(size)]
    reserved = [[False for _ in range(size)] for _ in range(size)]

    def set_module(row, col, dark, reserve=True):
        if 0 <= row < size and 0 <= col < size:
            modules[row][col] = bool(dark)
            if reserve:
                reserved[row][col] = True

    def draw_finder(row, col):
        for dy in range(-1, 8):
            for dx in range(-1, 8):
                rr = row + dy
                cc = col + dx
                dark = (
                    0 <= dx <= 6
                    and 0 <= dy <= 6
                    and (dx in (0, 6) or dy in (0, 6) or (2 <= dx <= 4 and 2 <= dy <= 4))
                )
                set_module(rr, cc, dark)

    draw_finder(0, 0)
    draw_finder(0, size - 7)
    draw_finder(size - 7, 0)

    for i in range(8, size - 8):
        dark = i % 2 == 0
        set_module(6, i, dark)
        set_module(i, 6, dark)

    positions = QR_ALIGNMENT[version]
    for row in positions:
        for col in positions:
            if reserved[row][col]:
                continue
            for dy in range(-2, 3):
                for dx in range(-2, 3):
                    distance = max(abs(dx), abs(dy))
                    set_module(row + dy, col + dx, distance == 2 or distance == 0)

    for i in range(9):
        if i != 6:
            set_module(8, i, False)
            set_module(i, 8, False)
    for i in range(8):
        set_module(8, size - 1 - i, False)
    for i in range(7):
        set_module(size - 1 - i, 8, False)
    set_module(version * 4 + 9, 8, True)

    bit_index = 0
    upward = True
    col = size - 1
    while col > 0:
        if col == 6:
            col -= 1
        rows = range(size - 1, -1, -1) if upward else range(size)
        for row in rows:
            for cc in (col, col - 1):
                if reserved[row][cc]:
                    continue
                bit = stream[bit_index] if bit_index < len(stream) else 0
                bit_index += 1
                set_module(row, cc, bool(bit) ^ ((row + cc) % 2 == 0), False)
        upward = not upward
        col -= 2

    fmt = qr_format_bits(0)
    for i in range(15):
        bit = (fmt >> i) & 1
        if i < 6:
            set_module(i, 8, bit)
        elif i < 8:
            set_module(i + 1, 8, bit)
        else:
            set_module(size - 15 + i, 8, bit)

        if i < 8:
            set_module(8, size - i - 1, bit)
        elif i < 9:
            set_module(8, 8 - 1, bit)
        else:
            set_module(8, 15 - i - 1, bit)
    set_module(size - 8, 8, True)
    return modules


def qr_svg(text):
    modules = make_qr_matrix(text)
    border = 4
    size = len(modules) + border * 2
    parts = []
    for row, line in enumerate(modules):
        for col, dark in enumerate(line):
            if dark:
                parts.append(f"M{col + border},{row + border}h1v1h-1z")
    title = xml_escape(str(text or ""))
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" '
        f'width="512" height="512" role="img" aria-label="QR code">'
        f"<title>{title}</title>"
        f'<rect width="{size}" height="{size}" fill="#fff"/>'
        f'<path d="{" ".join(parts)}" fill="#000"/>'
        "</svg>"
    )


def broadcast_scan(scan):
    payload = f"event: scan\ndata: {json.dumps(scan, ensure_ascii=False)}\n\n".encode("utf-8")
    dead = []
    for client in list(SSE_CLIENTS):
        try:
            client.write(payload)
            client.flush()
        except Exception:
            dead.append(client)
    for client in dead:
        SSE_CLIENTS.discard(client)


def content_type_for(path):
    suffix = path.suffix.lower()
    return {
        ".html": "text/html; charset=utf-8",
        ".css": "text/css; charset=utf-8",
        ".js": "application/javascript; charset=utf-8",
        ".svg": "image/svg+xml",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
    }.get(suffix, "application/octet-stream")


def is_relative_to(path, root):
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


class ExpoHandler(BaseHTTPRequestHandler):
    server_version = "ExpoDisplay/0.1"

    def handle(self):
        try:
            super().handle()
        except RequestRejected:
            pass
        except (BrokenPipeError, ConnectionAbortedError, ConnectionResetError):
            pass

    def log_message(self, fmt, *args):
        print("[%s] %s" % (self.log_date_time_string(), fmt % args))

    def cors_origin(self):
        origin = self.headers.get("Origin", "").rstrip("/")
        if not origin or not ALLOWED_ORIGINS:
            return ""
        if "*" in ALLOWED_ORIGINS:
            return origin if self.headers.get("Cookie") else "*"
        return origin if origin in ALLOWED_ORIGINS else ""

    def send_cors_headers(self):
        origin = self.cors_origin()
        if not origin:
            return
        self.send_header("Access-Control-Allow-Origin", origin)
        self.send_header("Vary", "Origin")
        if origin != "*":
            self.send_header("Access-Control-Allow-Credentials", "true")

    def send_security_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "same-origin")
        self.send_header("X-Frame-Options", "SAMEORIGIN")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: http: https:; "
            "connect-src 'self' http: https:; "
            "font-src 'self' data:; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "frame-ancestors 'self'",
        )

    def send_json(self, status, payload, extra_headers=None):
        body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_security_headers()
        self.send_cors_headers()
        for name, value in (extra_headers or {}).items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)

    def send_redirect(self, location):
        self.send_response(302)
        self.send_header("Location", location)
        self.end_headers()

    def read_json(self, max_bytes=MAX_JSON_BYTES):
        length = int(self.headers.get("Content-Length", "0"))
        if length > max_bytes:
            self.send_json(413, {"ok": False, "error": "请求内容太大"})
            raise RequestRejected()
        raw = self.rfile.read(length).decode("utf-8") if length else ""
        if not raw.strip():
            return {}
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"url": raw.strip()}

    def cookie_value(self, name):
        cookie = SimpleCookie()
        cookie.load(self.headers.get("Cookie", ""))
        if name not in cookie:
            return ""
        return cookie[name].value

    def current_admin(self):
        user = self.current_user()
        return user["username"] if user and user.get("role") == "admin" else None

    def current_user(self):
        return get_session_user(self.cookie_value(ADMIN_COOKIE))

    def require_auth(self):
        user = self.current_user()
        if user:
            return user
        self.send_json(401, {"ok": False, "error": "请先登录"})
        return None

    def require_admin(self):
        user = self.current_user()
        if user and user.get("role") == "admin":
            return user
        self.send_json(401, {"ok": False, "error": "需要管理员权限"})
        return None

    def csrf_exempt(self, path):
        return path in {"/api/login", "/api/scan", "/api/scans"}

    def require_csrf(self, path):
        if self.command not in {"POST", "PUT", "DELETE"} or self.csrf_exempt(path):
            return True
        token = self.cookie_value(ADMIN_COOKIE)
        expected = csrf_token_for_session(token)
        provided = self.headers.get("X-CSRF-Token", "")
        if expected and hmac.compare_digest(provided, expected):
            return True
        self.send_json(403, {"ok": False, "error": "登录状态已失效，请刷新页面后重试"})
        return False

    def admin_username(self):
        user = self.current_user()
        return user["username"] if user else ""

    def user_role(self):
        user = self.current_user()
        return user.get("role", "") if user else ""

    def client_ip(self):
        if TRUST_PROXY_HEADERS:
            forwarded = self.headers.get("X-Forwarded-For", "")
            if forwarded:
                first = forwarded.split(",", 1)[0].strip()
                if first:
                    return first
            real_ip = self.headers.get("X-Real-IP", "").strip()
            if real_ip:
                return real_ip
        return self.client_address[0] if self.client_address else ""

    def log_admin(self, action, target_type="", target_id="", target_label="", detail="", changes=""):
        user = self.current_user() or {}
        create_admin_log(
            action,
            target_type=target_type,
            target_id=target_id,
            target_label=target_label,
            detail=detail,
            username=user.get("username", self.admin_username()),
            role=user.get("role", self.user_role()),
            ip=self.client_ip(),
            changes=changes,
        )

    def session_cookie_header(self, token):
        secure = "; Secure" if SESSION_COOKIE_SECURE else ""
        return (
            f"{ADMIN_COOKIE}={token}; Path=/; HttpOnly; SameSite=Lax; "
            f"Max-Age={ADMIN_SESSION_SECONDS}{secure}"
        )

    def clear_session_cookie_header(self):
        secure = "; Secure" if SESSION_COOKIE_SECURE else ""
        return f"{ADMIN_COOKIE}=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0{secure}"

    def serve_file(self, path):
        try:
            resolved = path.resolve()
            allowed_roots = (STATIC_DIR.resolve(), UPLOAD_DIR.resolve())
            if not any(is_relative_to(resolved, root) for root in allowed_roots):
                self.send_error(403)
                return
            body = resolved.read_bytes()
        except FileNotFoundError:
            self.send_error(404)
            return

        self.send_response(200)
        self.send_header("Content-Type", content_type_for(resolved))
        if resolved.suffix.lower() in {".html", ".css", ".js"}:
            self.send_header("Cache-Control", "no-store, max-age=0")
        self.send_header("Content-Length", str(len(body)))
        self.send_security_headers()
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_cors_headers()
        self.send_header("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-CSRF-Token")
        self.send_security_headers()
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = unquote(parsed.path)

        if path == "/":
            self.send_response(302)
            self.send_header("Location", "/display")
            self.end_headers()
            return

        if path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return

        if path == "/display":
            self.serve_file(STATIC_DIR / "display.html")
            return

        # 系部数字展厅（DESIGN.md）：一级页与二级页共用入口
        if (
            path == "/departments"
            or path.startswith("/departments/")
            or path == "/topics"
            or path.startswith("/topics/")
        ):
            self.serve_file(STATIC_DIR / "blueprint" / "index.html")
            return

        if path == "/login":
            user = self.current_user()
            if user:
                self.send_redirect("/admin" if user.get("role") == "admin" else "/teacher?view=pages")
                return
            self.serve_file(STATIC_DIR / "login.html")
            return

        if path == "/admin":
            user = self.current_user()
            if not user:
                self.send_redirect("/login")
                return
            if user.get("role") != "admin":
                self.send_redirect("/teacher?view=pages")
                return
            self.serve_file(STATIC_DIR / "admin.html")
            return

        if path == "/teacher":
            user = self.current_user()
            if not user:
                self.send_redirect("/login")
                return
            if user.get("role") == "admin":
                self.send_redirect("/admin")
                return
            self.serve_file(STATIC_DIR / "admin.html")
            return

        if path == "/api/health":
            self.send_json(200, {"ok": True, "clients": len(SSE_CLIENTS), "time": now_iso()})
            return

        if path == "/api/ready":
            status = ready_status()
            self.send_json(200 if status["ok"] else 503, status)
            return

        if path == "/api/session":
            user = self.current_user()
            permissions = []
            if user:
                permissions = ["admin"] if user["role"] == "admin" else ["teacher"]
            token = self.cookie_value(ADMIN_COOKIE)
            self.send_json(
                200,
                {
                    "ok": True,
                    "authenticated": bool(user),
                    "user": user,
                    "permissions": permissions,
                    "username": user["username"] if user else "",
                    "csrfToken": csrf_token_for_session(token) if user else "",
                },
            )
            return

        if path == "/api/admin/dashboard":
            user = self.require_auth()
            if not user:
                return
            self.send_json(200, {"ok": True, "dashboard": admin_dashboard(user)})
            return

        if path == "/api/admin/logs":
            if not self.require_admin():
                return
            limit = parse_qs(parsed.query).get("limit", ["80"])[0]
            query = parse_qs(parsed.query)
            self.send_json(
                200,
                {
                    "ok": True,
                    "logs": list_admin_logs(
                        limit,
                        username=(query.get("username") or [""])[0],
                        action=(query.get("action") or [""])[0],
                        date_from=(query.get("from") or [""])[0],
                        date_to=(query.get("to") or [""])[0],
                    ),
                },
            )
            return

        if path == "/api/admin/acceptance-report.json":
            user = self.require_admin()
            if not user:
                return
            self.send_json(
                200,
                {"ok": True, "report": acceptance_report(user)},
                {"Content-Disposition": 'attachment; filename="expo-acceptance-report.json"'},
            )
            return

        if path == "/api/admin/logs.csv":
            if not self.require_admin():
                return
            query = parse_qs(parsed.query)
            rows = list_admin_logs(
                300,
                username=(query.get("username") or [""])[0],
                action=(query.get("action") or [""])[0],
                date_from=(query.get("from") or [""])[0],
                date_to=(query.get("to") or [""])[0],
            )
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=["createdAt", "username", "role", "action", "targetType", "targetId", "targetLabel", "detail", "changes", "ip"], extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)
            body = output.getvalue().encode("utf-8-sig")
            self.send_response(200)
            self.send_header("Content-Type", "text/csv; charset=utf-8")
            self.send_header("Content-Disposition", 'attachment; filename="admin-logs.csv"')
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if path == "/api/display/project":
            project = get_deployed_project()
            self.send_json(200, {"ok": True, "project": project})
            return

        if path == "/api/display/latest":
            self.send_json(200, {"ok": True, "scan": validated_latest_scan()})
            return

        if path.startswith("/api/display/projects/"):
            parts = path.strip("/").split("/")
            if len(parts) == 4 and parts[0] == "api" and parts[1] == "display" and parts[2] == "projects":
                project_id = int(parts[3]) if parts[3].isdigit() else 0
                project = get_display_project(project_id)
                if not project:
                    self.send_json(404, {"ok": False, "error": "项目不存在"})
                    return
                self.send_json(200, {"ok": True, "project": project})
                return
            if len(parts) == 6 and parts[0] == "api" and parts[1] == "display" and parts[2] == "projects" and parts[4] == "pages":
                project_id = int(parts[3]) if parts[3].isdigit() else 0
                code = parts[5]
                project = get_display_project(project_id)
                page = get_display_page(project_id, code, require_deployed=False) if project else None
                if not project or not page:
                    self.send_json(404, {"ok": False, "error": "页面不存在"})
                    return
                self.send_json(200, {"ok": True, "project": project, "page": page})
                return

        if path == "/api/qr-public":
            # 公开二维码（无需登录），供大屏展示页使用；data 限长防滥用
            data = parse_qs(parsed.query).get("data", [""])[0]
            if len(data) > 512:
                self.send_json(400, {"ok": False, "error": "二维码内容过长"})
                return
            try:
                body = qr_svg(data).encode("utf-8")
            except ValueError as exc:
                self.send_json(400, {"ok": False, "error": str(exc)})
                return
            self.send_response(200)
            self.send_header("Content-Type", "image/svg+xml; charset=utf-8")
            self.send_header("Content-Disposition", 'inline; filename="display-qr.svg"')
            self.send_header("Content-Length", str(len(body)))
            self.send_security_headers()
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(body)
            return

        if path == "/api/qr":
            if not self.require_auth():
                return
            data = parse_qs(parsed.query).get("data", [""])[0]
            try:
                body = qr_svg(data).encode("utf-8")
            except ValueError as exc:
                self.send_json(400, {"ok": False, "error": str(exc)})
                return
            self.send_response(200)
            self.send_header("Content-Type", "image/svg+xml; charset=utf-8")
            self.send_header("Content-Disposition", 'inline; filename="display-qr.svg"')
            self.send_header("Content-Length", str(len(body)))
            self.send_security_headers()
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(body)
            return

        if path == "/api/users":
            if not self.require_admin():
                return
            self.send_json(200, {"ok": True, "users": list_users()})
            return

        if path == "/api/assets":
            user = self.require_auth()
            if not user:
                return
            limit = (parse_qs(parsed.query).get("limit") or ["80"])[0]
            self.send_json(200, {"ok": True, "assets": list_assets(user, limit)})
            return

        if path == "/api/reviews":
            if not self.require_admin():
                return
            status = (parse_qs(parsed.query).get("status") or ["pending"])[0]
            self.send_json(200, {"ok": True, "reviews": list_reviews(status)})
            return

        if path.startswith("/api/reviews/pages/") and path.endswith("/preview"):
            if not self.require_admin():
                return
            parts = path.strip("/").split("/")
            if len(parts) == 5 and parts[0] == "api" and parts[1] == "reviews" and parts[2] == "pages":
                version_id = int(parts[3]) if parts[3].isdigit() else 0
                with db_connect() as conn:
                    row = conn.execute(
                        """
                        SELECT page_versions.*, projects.name AS project_name
                        FROM page_versions
                        JOIN projects ON projects.id = page_versions.project_id
                        WHERE page_versions.id = ?
                        """,
                        (version_id,),
                    ).fetchone()
                version = row_to_page_version(row) if row else None
                project = get_project(version["projectId"]) if version else None
                if not version or not project:
                    self.send_json(404, {"ok": False, "error": "审核记录不存在"})
                    return
                page = {**version["snapshot"], "projectId": version["projectId"], "reviewStatus": version["status"], "qrAvailable": False}
                self.send_json(200, {"ok": True, "project": project, "page": page, "review": version})
                return

        if path.startswith("/api/deploy/content/"):
            if not self.require_admin():
                return
            project_id_text = path.rsplit("/", 1)[-1]
            project_id = int(project_id_text) if project_id_text.isdigit() else 0
            self.send_json(200, {"ok": True, "pageIds": deployed_page_ids(project_id)})
            return

        if path.startswith("/api/deploy/check/"):
            if not self.require_admin():
                return
            project_id_text = path.rsplit("/", 1)[-1]
            project_id = int(project_id_text) if project_id_text.isdigit() else 0
            self.send_json(200, {"ok": True, "check": deploy_content_check(project_id)})
            return

        if path == "/api/projects":
            user = self.require_auth()
            if not user:
                return
            self.send_json(
                200,
                {
                    "ok": True,
                    "projects": list_projects(user),
                    "deployedProjectId": (get_deployed_project() or {}).get("id"),
                    "deployedContentProjectId": (get_deployed_content_project() or {}).get("id"),
                },
            )
            return

        if path.startswith("/api/projects/"):
            user = self.require_auth()
            if not user:
                return
            parts = path.strip("/").split("/")
            if len(parts) == 3 and parts[0] == "api" and parts[1] == "projects":
                project_id = int(parts[2]) if parts[2].isdigit() else 0
                project = get_project(project_id)
                if not project or not project_accessible(project, user):
                    self.send_json(404, {"ok": False, "error": "项目不存在"})
                    return
                self.send_json(200, {"ok": True, "project": project})
                return
            if len(parts) == 4 and parts[0] == "api" and parts[1] == "projects" and parts[3] == "versions":
                project_id = int(parts[2]) if parts[2].isdigit() else 0
                project = get_project(project_id)
                if not project or not project_accessible(project, user):
                    self.send_json(404, {"ok": False, "error": "项目不存在"})
                    return
                self.send_json(200, {"ok": True, "project": project, "versions": list_project_versions(project_id)})
                return
            if len(parts) == 4 and parts[0] == "api" and parts[1] == "projects" and parts[3] == "pages":
                project_id = int(parts[2]) if parts[2].isdigit() else 0
                project = get_project(project_id)
                if not project or not project_accessible(project, user):
                    self.send_json(404, {"ok": False, "error": "项目不存在"})
                    return
                self.send_json(200, {"ok": True, "pages": list_pages(project_id)})
                return
            if len(parts) == 5 and parts[0] == "api" and parts[1] == "projects" and parts[3] == "pages":
                project_id = int(parts[2]) if parts[2].isdigit() else 0
                code = parts[4]
                project = get_project(project_id)
                if not project or not project_accessible(project, user):
                    self.send_json(404, {"ok": False, "error": "项目不存在"})
                    return
                page = get_page(project_id, code)
                if not page:
                    self.send_json(404, {"ok": False, "error": "页面不存在"})
                    return
                self.send_json(200, {"ok": True, "page": page})
                return
            if len(parts) == 6 and parts[0] == "api" and parts[1] == "projects" and parts[3] == "pages" and parts[5] == "versions":
                project_id = int(parts[2]) if parts[2].isdigit() else 0
                code = parts[4]
                project = get_project(project_id)
                if not project or not project_accessible(project, user):
                    self.send_json(404, {"ok": False, "error": "项目不存在"})
                    return
                self.send_json(200, {"ok": True, "project": project, "versions": list_page_versions(project_id, code)})
                return

        if path == "/api/pages":
            project = get_deployed_content_project()
            pages = []
            if project:
                pages = [
                    page for page in list_pages(project["id"])
                    if page.get("qrAvailable") and page.get("id") in deployed_page_ids(project["id"])
                ]
            self.send_json(200, {"ok": True, "project": project, "pages": pages})
            return

        if path.startswith("/api/pages/"):
            code = path.rsplit("/", 1)[-1]
            project = get_deployed_content_project()
            page = get_display_page(project["id"], code, require_deployed=True) if project else None
            if not page:
                self.send_json(404, {"ok": False, "error": "页面不存在"})
                return
            self.send_json(200, {"ok": True, "project": project, "page": page})
            return

        if path == "/api/display/events":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream; charset=utf-8")
            self.send_header("Cache-Control", "no-cache, no-transform")
            self.send_header("Connection", "keep-alive")
            self.send_security_headers()
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(b": connected\n\n")
            self.wfile.flush()
            SSE_CLIENTS.add(self.wfile)
            try:
                while True:
                    time.sleep(15)
                    self.wfile.write(b": keepalive\n\n")
                    self.wfile.flush()
            except Exception:
                SSE_CLIENTS.discard(self.wfile)
            return

        if path.startswith("/static/"):
            self.serve_file(STATIC_DIR / path.removeprefix("/static/"))
            return

        if path.startswith("/uploads/"):
            self.serve_file(UPLOAD_DIR / path.removeprefix("/uploads/"))
            return

        self.send_error(404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
        if not self.require_csrf(path):
            return

        if path == "/api/login":
            data = self.read_json()
            username = str(data.get("username", "")).strip()
            password = str(data.get("password", ""))
            retry_after = rate_limit_retry_after(
                "login",
                f"{self.client_ip()}:{username.lower()}",
                LOGIN_RATE_LIMIT,
                LOGIN_RATE_WINDOW_SECONDS,
            )
            if retry_after:
                self.send_json(
                    429,
                    {"ok": False, "error": "登录尝试过多，请稍后再试"},
                    {"Retry-After": str(retry_after)},
                )
                return
            with db_connect() as conn:
                row = conn.execute(
                    "SELECT password_hash, enabled FROM users WHERE username = ?",
                    (username,),
                ).fetchone()
            if not row or not bool(row["enabled"]) or not verify_password(password, row["password_hash"]):
                self.send_json(401, {"ok": False, "error": "用户名或密码错误"})
                return
            token = create_admin_session(username)
            user = get_user(username)
            redirect_url = "/admin" if user["role"] == "admin" else "/teacher?view=pages"
            create_admin_log("login", "user", username, username, "login", username=username, role=user["role"], ip=self.client_ip())
            self.send_json(
                200,
                {"ok": True, "username": username, "user": user, "redirectUrl": redirect_url},
                {"Set-Cookie": self.session_cookie_header(token)},
            )
            return
        if path == "/api/logout":
            user = self.current_user() or {}
            username = user.get("username", "")
            delete_admin_session(self.cookie_value(ADMIN_COOKIE))
            create_admin_log("logout", "user", username, username, "logout", username=username, role=user.get("role", ""), ip=self.client_ip())
            self.send_json(
                200,
                {"ok": True},
                {"Set-Cookie": self.clear_session_cookie_header()},
            )
            return

        if path == "/api/account/password":
            user = self.require_auth()
            if not user:
                return
            data = self.read_json()
            try:
                change_password(user["username"], str(data.get("oldPassword", "")), str(data.get("newPassword", "")))
            except ValueError as exc:
                self.send_json(400, {"ok": False, "error": str(exc)})
                return
            self.log_admin("change_password", "user", user["username"], user["displayName"], "password changed")
            self.send_json(200, {"ok": True})
            return

        if path == "/api/users":
            actor = self.require_admin()
            if not actor:
                return
            data = self.read_json()
            try:
                user = upsert_user(data, actor["username"])
            except ValueError as exc:
                self.send_json(400, {"ok": False, "error": str(exc)})
                return
            self.log_admin("save_user", "user", user["username"], user["displayName"], "save user", changes="profile,password" if data.get("password") else "profile")
            self.send_json(200, {"ok": True, "user": user})
            return

        if path == "/api/users/import-csv":
            actor = self.require_admin()
            if not actor:
                return
            data = self.read_json()
            text_csv = str(data.get("csv") or "")
            result = {"created": 0, "updated": 0, "projects": 0, "errors": []}
            reader = csv.DictReader(io.StringIO(text_csv))
            for line_no, row in enumerate(reader, start=2):
                try:
                    username = str(row.get("username") or "").strip()
                    if not username:
                        raise ValueError("username 不能为空")
                    existed = get_user(username)
                    user = upsert_user({"username": username, "displayName": row.get("name") or row.get("displayName") or username, "password": row.get("password"), "department": row.get("department") or "", "role": "teacher", "enabled": True}, actor["username"])
                    result["updated" if existed else "created"] += 1
                    projects_text = str(row.get("projects") or "").strip()
                    for name in [item.strip() for item in re.split(r"[;；]", projects_text) if item.strip()]:
                        save_project(None, {"name": name, "ownerUsername": user["username"]}, actor)
                        result["projects"] += 1
                except Exception as exc:
                    result["errors"].append({"line": line_no, "error": str(exc)})
            self.log_admin("import_users", "user", "", "CSV import", json.dumps(result, ensure_ascii=False))
            self.send_json(200, {"ok": True, "result": result})
            return

        if path.startswith("/api/users/"):
            actor = self.require_admin()
            if not actor:
                return
            parts = path.strip("/").split("/")
            if len(parts) == 4 and parts[0] == "api" and parts[1] == "users":
                username = parts[2]
                action = parts[3]
                data = self.read_json()
                try:
                    if action == "reset-password":
                        user = reset_user_password(username, data.get("password"))
                        log_action = "reset_password"
                    elif action == "disable":
                        user = set_user_enabled(username, False)
                        log_action = "disable_user"
                    elif action == "enable":
                        user = set_user_enabled(username, True)
                        log_action = "enable_user"
                    else:
                        user = None
                        log_action = ""
                except ValueError as exc:
                    self.send_json(400, {"ok": False, "error": str(exc)})
                    return
                if not user:
                    self.send_json(404, {"ok": False, "error": "用户不存在"})
                    return
                self.log_admin(log_action, "user", user["username"], user["displayName"], log_action)
                self.send_json(200, {"ok": True, "user": user})
                return

        if path == "/api/deploy/content":
            actor = self.require_admin()
            if not actor:
                return
            data = self.read_json()
            project_id = int(data.get("projectId") or 0)
            page_ids = data.get("pageIds")
            try:
                project = deploy_content_project(project_id, page_ids if isinstance(page_ids, list) else None)
            except ValueError as exc:
                self.send_json(400, {"ok": False, "error": str(exc), "check": deploy_content_check(project_id, page_ids if isinstance(page_ids, list) else None)})
                return
            if not project:
                self.send_json(404, {"ok": False, "error": "项目不存在"})
                return
            self.log_admin("deploy_content", "project", project["id"], project["name"], "deploy selected pages", changes="pageIds")
            self.send_json(200, {"ok": True, "project": project, "pageIds": deployed_page_ids(project_id)})
            return

        if path.startswith("/api/reviews/"):
            actor = self.require_admin()
            if not actor:
                return
            parts = path.strip("/").split("/")
            data = self.read_json()
            note = str(data.get("note") or "")
            if len(parts) == 5 and parts[0] == "api" and parts[1] == "reviews":
                review_type = parts[2]
                version_id = int(parts[3]) if parts[3].isdigit() else 0
                action = parts[4]
                if review_type == "pages" and action == "approve":
                    item = approve_page_version(version_id, actor, note)
                elif review_type == "pages" and action == "reject":
                    item = reject_page_version(version_id, actor, note)
                elif review_type == "projects" and action == "approve":
                    item = approve_project_version(version_id, actor, note)
                elif review_type == "projects" and action == "reject":
                    item = reject_project_version(version_id, actor, note)
                else:
                    item = None
                if not item:
                    self.send_json(404, {"ok": False, "error": "审核记录不存在"})
                    return
                self.log_admin(f"review_{action}", review_type[:-1], version_id, str(version_id), note)
                self.send_json(200, {"ok": True, "item": item})
                return
        if path == "/api/projects":
            actor = self.require_admin()
            if not actor:
                return
            project = save_project(None, self.read_json(), actor)
            self.log_admin("create_project", "project", project["id"], project["name"], "新建项目")
            self.send_json(200, {"ok": True, "project": project})
            return

        if path.startswith("/api/projects/"):
            actor = self.require_admin()
            if not actor:
                return
            parts = path.strip("/").split("/")
            if len(parts) == 4 and parts[0] == "api" and parts[1] == "projects" and parts[3] == "copy":
                project_id = int(parts[2]) if parts[2].isdigit() else 0
                project = copy_project(project_id, self.read_json())
                if not project:
                    self.send_json(404, {"ok": False, "error": "项目不存在"})
                    return
                self.log_admin("copy_project", "project", project["id"], project["name"], f"复制来源项目 {project_id}")
                self.send_json(200, {"ok": True, "project": project})
                return
            if len(parts) == 4 and parts[0] == "api" and parts[1] == "projects" and parts[3] == "deploy":
                project_id = int(parts[2]) if parts[2].isdigit() else 0
                try:
                    project = deploy_project(project_id)
                except ValueError as exc:
                    self.send_json(400, {"ok": False, "error": str(exc), "check": deploy_project_check(project_id)})
                    return
                if not project:
                    self.send_json(404, {"ok": False, "error": "项目不存在"})
                    return
                self.log_admin("deploy_welcome", "project", project["id"], project["name"], "部署欢迎页")
                self.send_json(200, {"ok": True, "project": project})
                return
            if len(parts) == 4 and parts[0] == "api" and parts[1] == "projects" and parts[3] == "deploy-content":
                project_id = int(parts[2]) if parts[2].isdigit() else 0
                try:
                    project = deploy_content_project(project_id)
                except ValueError as exc:
                    self.send_json(400, {"ok": False, "error": str(exc), "check": deploy_content_check(project_id)})
                    return
                if not project:
                    self.send_json(404, {"ok": False, "error": "项目不存在"})
                    return
                self.log_admin("deploy_content", "project", project["id"], project["name"], "部署展示项目内容")
                self.send_json(200, {"ok": True, "project": project})
                return

        if path in ("/api/scan", "/api/scans"):
            global LAST_SCAN
            data = self.read_json()
            original_url = str(data.get("url", "")).strip()
            raw_url = normalize_scan_url(original_url)

            # 系部数字展厅联动（DESIGN.md 第 13 节）：
            # 扫码内容指向 /departments/<id> 或 /topics/<id>（二维码生成的是绝对 URL，需按 path 匹配），
            # 命中后广播相对路径给展厅大屏
            parsed_scan_url = urlparse(original_url)
            if parsed_scan_url.scheme in ("http", "https"):
                bp_path = parsed_scan_url.path
                bp_query = parsed_scan_url.query
            else:
                bp_path = original_url.split("?", 1)[0]
                bp_query = original_url.split("?", 1)[1] if "?" in original_url else ""
            bp_match = re.match(r"^/(?:departments|topics)/([a-z0-9-]+)$", bp_path)
            if bp_match:
                bp_section = re.search(r"(?:^|&)section=([a-z0-9-]+)", bp_query)
                bp_display_url = bp_path + (f"?section={bp_section.group(1)}" if bp_section else "")
                scan = {
                    "url": bp_display_url,
                    "originalUrl": original_url,
                    "displayUrl": bp_display_url,
                    "localDisplayUrl": bp_display_url,
                    "code": bp_match.group(1),
                    "project": None,
                    "page": None,
                    "external": True,
                    "result": "ok",
                    "detail": "blueprint",
                    "receivedAt": now_iso(),
                }
                LAST_SCAN = scan
                with db_connect() as conn:
                    conn.execute(
                        "INSERT INTO scans (code, raw_url, project_id, result, detail, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                        (scan["code"], original_url, 0, "ok", "blueprint", scan["receivedAt"]),
                    )
                if self.current_user():
                    self.log_admin("simulate_scan", "page", scan["code"], scan["code"], original_url, changes="blueprint")
                try:
                    broadcast_scan(scan)
                except Exception:
                    SSE_CLIENTS.clear()
                self.send_json(200, {"ok": True, "scan": scan, "clients": len(SSE_CLIENTS)})
                return

            project_id, code = extract_scan_target(raw_url or original_url)
            if not code:
                self.send_json(400, {"ok": False, "error": "扫码内容无效"})
                return

            scanned_url = raw_url or original_url
            external_link = is_external_url(scanned_url)
            project = None
            page = None
            local_display_url = ""
            result = "ok"
            detail = ""
            project = get_deployed_content_project()
            if project and (not project_id or int(project_id) == int(project["id"])):
                matched_code, page = find_deployed_display_page(project["id"], code)
                if page:
                    code = matched_code
                    external_link = False
                    local_display_url = f"/display?project={project['id']}&code={code}"
                elif not external_link:
                    result = "not_available"
                    detail = "页面未通过审核、未勾选部署或账号已禁用"
            elif not external_link:
                result = "not_deployed"
                detail = "内容未部署到当前大屏"
                project = None
            target_display_url = scanned_url if external_link else local_display_url
            scan = {
                "url": scanned_url,
                "originalUrl": original_url,
                "displayUrl": target_display_url,
                "localDisplayUrl": local_display_url,
                "code": code,
                "project": project,
                "page": page,
                "external": external_link,
                "result": result,
                "detail": detail,
                "receivedAt": now_iso(),
            }
            LAST_SCAN = scan
            with db_connect() as conn:
                conn.execute(
                    "INSERT INTO scans (code, raw_url, project_id, result, detail, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (code, raw_url or original_url, project["id"] if project else 0, result, detail, scan["receivedAt"]),
                )
            if self.current_user():
                self.log_admin("simulate_scan", "page", code, code, scanned_url, changes=result)
            if result == "ok":
                try:
                    broadcast_scan(scan)
                except Exception:
                    SSE_CLIENTS.clear()
            self.send_json(200, {"ok": True, "scan": scan, "clients": len(SSE_CLIENTS)})
            return
        if path == "/api/assets":
            user = self.require_auth()
            if not user:
                return
            retry_after = rate_limit_retry_after(
                "upload",
                f"{user.get('username', '')}:{self.client_ip()}",
                UPLOAD_RATE_LIMIT,
                UPLOAD_RATE_WINDOW_SECONDS,
            )
            if retry_after:
                self.send_json(
                    429,
                    {"ok": False, "error": "上传过于频繁，请稍后再试"},
                    {"Retry-After": str(retry_after)},
                )
                return
            data = self.read_json(max_bytes=max(MAX_JSON_BYTES, int(MAX_UPLOAD_BYTES * 1.5) + 1024))
            data_url = str(data.get("dataUrl", ""))
            filename = str(data.get("filename", "upload")).strip()
            match = re.match(r"data:(image/[a-zA-Z0-9.+-]+);base64,(.+)", data_url)
            if not match:
                self.send_json(400, {"ok": False, "error": "图片数据无效"})
                return

            mime, encoded = match.groups()
            ext = UPLOAD_MIME_EXTENSIONS.get(mime)
            if not ext:
                self.send_json(415, {"ok": False, "error": "不支持的图片类型"})
                return
            safe_name = f"{uuid.uuid4().hex}{ext}"
            storage_key = f"{ASSET_KEY_PREFIX}/{safe_name}" if ASSET_KEY_PREFIX else safe_name
            try:
                payload = base64.b64decode(encoded, validate=True)
                if len(payload) > MAX_UPLOAD_BYTES:
                    self.send_json(413, {"ok": False, "error": "上传图片太大"})
                    return
                url = asset_storage(UPLOAD_DIR).save(storage_key, payload, mime)
                asset = create_asset_record(user, filename, storage_key, url, mime, len(payload))
            except Exception as exc:
                self.send_json(400, {"ok": False, "error": str(exc)})
                return

            self.log_admin(
                "upload_asset",
                "asset",
                storage_key,
                filename,
                f"{mime} -> {url} ({asset_storage_backend()})",
            )
            self.send_json(200, {"ok": True, "url": url, "asset": asset})
            return

        self.send_error(404)

    def do_PUT(self):
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
        if not self.require_csrf(path):
            return

        if path.startswith("/api/projects/"):
            user = self.require_auth()
            if not user:
                return
            parts = path.strip("/").split("/")
            if len(parts) == 3 and parts[0] == "api" and parts[1] == "projects":
                project_id = int(parts[2]) if parts[2].isdigit() else 0
                project = get_project(project_id)
                if not project or not project_accessible(project, user):
                    self.send_json(404, {"ok": False, "error": "项目不存在"})
                    return
                if user["role"] == "admin":
                    project = save_project(project_id, self.read_json(), user)
                    self.log_admin("update_project", "project", project["id"], project["name"], "update project", changes="config")
                else:
                    project = submit_project_config(project_id, self.read_json(), user)
                    self.log_admin("submit_project_config", "project", project["id"], project["name"], "submit project config", changes="config")
                self.send_json(200, {"ok": True, "project": project})
                return
            if len(parts) == 5 and parts[0] == "api" and parts[1] == "projects" and parts[3] == "pages":
                project_id = int(parts[2]) if parts[2].isdigit() else 0
                code = parts[4].strip()
                if not code:
                    self.send_json(400, {"ok": False, "error": "code 不能为空"})
                    return
                project = get_project(project_id)
                if not project or not project_accessible(project, user):
                    self.send_json(404, {"ok": False, "error": "项目不存在"})
                    return
                try:
                    page = save_page(project_id, code, self.read_json(), user, approve_now=user["role"] == "admin")
                except ValueError as exc:
                    self.send_json(409, {"ok": False, "error": str(exc)})
                    return
                self.log_admin("save_page" if user["role"] == "admin" else "submit_page", "page", page["code"], page["title"], f"project {project_id}", changes="content")
                self.send_json(200, {"ok": True, "page": page})
                return

        if path.startswith("/api/pages/"):
            user = self.require_auth()
            if not user:
                return
            code = path.rsplit("/", 1)[-1].strip()
            if not code:
                self.send_json(400, {"ok": False, "error": "code 不能为空"})
                return
            project = get_deployed_content_project()
            if not project or not project_accessible(project, user):
                self.send_json(500, {"ok": False, "error": "当前没有已部署的内容项目"})
                return
            try:
                page = save_page(project["id"], code, self.read_json(), user, approve_now=user["role"] == "admin")
            except ValueError as exc:
                self.send_json(409, {"ok": False, "error": str(exc)})
                return
            self.log_admin("save_page" if user["role"] == "admin" else "submit_page", "page", page["code"], page["title"], f"project {project['id']}", changes="content")
            self.send_json(200, {"ok": True, "page": page})
            return
        self.send_error(404)
    def do_DELETE(self):
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
        if not self.require_csrf(path):
            return

        if path.startswith("/api/projects/"):
            user = self.require_auth()
            if not user:
                return
            parts = path.strip("/").split("/")
            if len(parts) == 3 and parts[0] == "api" and parts[1] == "projects":
                if user["role"] != "admin":
                    self.send_json(403, {"ok": False, "error": "没有权限执行此操作"})
                    return
                project_id = int(parts[2]) if parts[2].isdigit() else 0
                project = get_project(project_id)
                if not delete_project(project_id):
                    self.send_json(404, {"ok": False, "error": "项目不存在"})
                    return
                self.log_admin("delete_project", "project", project_id, project["name"] if project else "", "delete project")
                self.send_json(200, {"ok": True})
                return
            if len(parts) == 5 and parts[0] == "api" and parts[1] == "projects" and parts[3] == "pages":
                project_id = int(parts[2]) if parts[2].isdigit() else 0
                code = parts[4].strip()
                project = get_project(project_id)
                if not project or not project_accessible(project, user):
                    self.send_json(404, {"ok": False, "error": "项目不存在"})
                    return
                ok = request_delete_page(project_id, code, user, approve_now=user["role"] == "admin")
                if not ok:
                    self.send_json(404, {"ok": False, "error": "页面不存在"})
                    return
                self.log_admin("delete_page" if user["role"] == "admin" else "request_delete_page", "page", code, code, f"project {project_id}")
                self.send_json(200, {"ok": True})
                return

        if path.startswith("/api/assets/"):
            user = self.require_auth()
            if not user:
                return
            asset_id_text = path.rsplit("/", 1)[-1]
            asset_id = int(asset_id_text) if asset_id_text.isdigit() else 0
            try:
                asset = delete_asset(asset_id, user)
            except Exception as exc:
                self.send_json(400, {"ok": False, "error": str(exc)})
                return
            if not asset:
                self.send_json(404, {"ok": False, "error": "资源不存在"})
                return
            self.log_admin("delete_asset", "asset", asset["id"], asset["originalFilename"], asset["url"])
            self.send_json(200, {"ok": True, "asset": asset})
            return

        self.send_error(404)

def main():
    validate_runtime_config()
    init_db()
    server = ThreadingHTTPServer((HOST, PORT), ExpoHandler)
    print(f"Expo display server running at http://{HOST}:{PORT}")
    print(f"Display: http://{HOST}:{PORT}/display")
    print(f"Admin:   http://{HOST}:{PORT}/admin")
    server.serve_forever()


if __name__ == "__main__":
    main()
