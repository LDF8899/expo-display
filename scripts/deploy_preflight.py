import argparse
import importlib.util
import json
import os
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backup_common import ROOT, load_env_file
from db_backend import connect_database, database_backend
from storage_backend import asset_storage_backend, storage_status


WEAK_VALUES = {
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
    "REPLACE_WITH_DB_PASSWORD",
    "REPLACE_WITH_ROOT_PASSWORD",
}


def check(name, ok, detail=None):
    return {"name": name, "ok": bool(ok), "detail": detail or ""}


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


def online_mode():
    return bool(
        os.environ.get("PUBLIC_BASE_URL", "").strip()
        or os.environ.get("HOST", "127.0.0.1") in {"0.0.0.0", "::"}
        or database_backend() == "mysql"
        or asset_storage_backend() != "local"
    )


def database_check(enabled):
    backend = database_backend()
    if backend == "sqlite":
        path = Path(os.environ.get("DB_PATH", ROOT / "expo.db"))
        if enabled:
            path.parent.mkdir(parents=True, exist_ok=True)
            with connect_database(path) as conn:
                conn.execute("SELECT 1 AS ok").fetchone()
        return check("database", True, f"sqlite:{path}")
    if backend == "mysql":
        missing = [
            name
            for name in ("MYSQL_HOST", "MYSQL_USER", "MYSQL_PASSWORD", "MYSQL_DATABASE")
            if not os.environ.get(name, "").strip()
        ]
        if missing:
            return check("database", False, f"missing {', '.join(missing)}")
        if enabled:
            with connect_database(ROOT / "expo.db") as conn:
                conn.execute("SELECT 1 AS ok").fetchone()
        return check("database", True, "mysql" + (" connected" if enabled else " configured"))
    return check("database", False, f"unsupported backend {backend}")


def main():
    parser = argparse.ArgumentParser(description="Validate online deployment configuration before starting the service.")
    parser.add_argument("--env-file", default="", help="optional .env file to load")
    parser.add_argument("--check-db", action="store_true", help="also connect to the configured database")
    args = parser.parse_args()

    load_env_file(args.env_file)
    schema_path = Path(os.environ.get("MYSQL_SCHEMA_PATH", ROOT / "database" / "mysql_schema.sql"))
    upload_dir = Path(os.environ.get("UPLOAD_DIR", ROOT / "uploads"))
    is_online = online_mode()

    checks = [
        check("schema", schema_path.exists(), str(schema_path)),
        check("admin_password", not (is_online and os.environ.get("ADMIN_PASSWORD", "123456") in WEAK_VALUES)),
        check("csrf_secret", not (is_online and os.environ.get("CSRF_SECRET", "") in WEAK_VALUES)),
        check("password_min_length", not (is_online and env_int("PASSWORD_MIN_LENGTH", 10) < 10)),
        check("weak_user_passwords", not (is_online and env_bool("ALLOW_WEAK_USER_PASSWORDS", False))),
        check("mysql_password", not (database_backend() == "mysql" and os.environ.get("MYSQL_PASSWORD", "") in WEAK_VALUES)),
        check("mysql_root_password", not (database_backend() == "mysql" and os.environ.get("MYSQL_ROOT_PASSWORD", "unused") in WEAK_VALUES)),
        check("pymysql", database_backend() != "mysql" or importlib.util.find_spec("pymysql") is not None),
        check("boto3", asset_storage_backend() != "s3" or importlib.util.find_spec("boto3") is not None),
        check("mysqldump", database_backend() != "mysql" or shutil.which("mysqldump") is not None or shutil.which("docker") is not None),
    ]
    checks.append(database_check(args.check_db))
    try:
        status = storage_status(upload_dir)
        checks.append(check("storage", status.get("ok"), json.dumps(status, ensure_ascii=False)))
    except Exception as exc:
        checks.append(check("storage", False, str(exc)))

    ok = all(item["ok"] for item in checks)
    result = {
        "ok": ok,
        "onlineMode": is_online,
        "databaseBackend": database_backend(),
        "assetStorageBackend": asset_storage_backend(),
        "checks": checks,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
