import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PORT = os.environ.get("OPERATIONS_CONFIG_AUDIT_PORT", "8779")


def request(url, method="GET", headers=None, payload=None):
    body = json.dumps(payload or {}, ensure_ascii=False).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, method=method, headers=headers or {}, data=body)
    return urllib.request.urlopen(req, timeout=5)


def json_request(url, method="GET", headers=None, payload=None):
    response = request(url, method=method, headers=headers, payload=payload)
    return json.loads(response.read().decode("utf-8")), response


def login(base_url, password):
    _, response = json_request(
        f"{base_url}/api/login",
        method="POST",
        headers={"Content-Type": "application/json"},
        payload={"username": "admin", "password": password},
    )
    cookie = response.headers.get("Set-Cookie", "").split(";", 1)[0]
    return cookie


def main():
    with tempfile.TemporaryDirectory() as temp:
        base_url = f"http://127.0.0.1:{PORT}"
        admin_password = "Admin-Config-Audit-Password-2026"
        env = os.environ.copy()
        env.update(
            {
                "HOST": "127.0.0.1",
                "PORT": PORT,
                "PUBLIC_BASE_URL": base_url,
                "DB_PATH": str(Path(temp) / "expo-config-audit.db"),
                "UPLOAD_DIR": str(Path(temp) / "uploads"),
                "ADMIN_PASSWORD": admin_password,
                "CSRF_SECRET": "config-audit-csrf-secret-2026-0123456789",
                "PASSWORD_MIN_LENGTH": "6",
                "ALLOW_WEAK_USER_PASSWORDS": "1",
                "LOGIN_RATE_LIMIT": "0",
                "UPLOAD_RATE_LIMIT": "0",
            }
        )
        process = subprocess.Popen(
            [sys.executable, "server.py"],
            cwd=ROOT,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        try:
            time.sleep(2)
            cookie = login(base_url, admin_password)
            dashboard, _ = json_request(f"{base_url}/api/admin/dashboard", headers={"Cookie": cookie})
            config = dashboard["dashboard"]["operations"]["config"]
            error_codes = {item["code"] for item in config["errors"]}
            warning_codes = {item["code"] for item in config["warnings"]}
            required_errors = {"password_min_length", "weak_user_passwords"}
            required_warnings = {"database_backend", "asset_storage", "login_rate_limit", "upload_rate_limit", "proxy_headers", "public_base_url_https"}
            if config["ok"]:
                raise RuntimeError(f"config audit should not be ok: {config}")
            if not required_errors.issubset(error_codes):
                raise RuntimeError(f"missing config audit errors: {config}")
            if not required_warnings.issubset(warning_codes):
                raise RuntimeError(f"missing config audit warnings: {config}")
            print("operations_config_audit_ok=true")
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()


if __name__ == "__main__":
    main()
