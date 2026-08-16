import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PORT = os.environ.get("TEACHER_REDIRECT_PORT", "8794")


def request(url, method="GET", headers=None, payload=None):
    body = json.dumps(payload or {}, ensure_ascii=False).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, method=method, headers=headers or {}, data=body)
    return urllib.request.urlopen(req, timeout=5)


def json_request(url, method="GET", headers=None, payload=None):
    response = request(url, method=method, headers=headers, payload=payload)
    return json.loads(response.read().decode("utf-8")), response


def login(base_url, username, password):
    data, response = json_request(
        f"{base_url}/api/login",
        method="POST",
        headers={"Content-Type": "application/json"},
        payload={"username": username, "password": password},
    )
    cookie = response.headers.get("Set-Cookie", "").split(";", 1)[0]
    return data, cookie


def main():
    with tempfile.TemporaryDirectory() as temp:
        temp_path = Path(temp)
        base_url = f"http://127.0.0.1:{PORT}"
        admin_password = "Admin-Teacher-Redirect-Password-2026"
        env = os.environ.copy()
        env.update(
            {
                "HOST": "127.0.0.1",
                "PORT": PORT,
                "DB_PATH": str(temp_path / "expo-teacher-redirect.db"),
                "UPLOAD_DIR": str(temp_path / "uploads"),
                "ADMIN_PASSWORD": admin_password,
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
            admin_login, admin_cookie = login(base_url, "admin", admin_password)
            if admin_login.get("redirectUrl") != "/admin":
                raise RuntimeError(f"admin redirect mismatch: {admin_login}")
            session, _ = json_request(f"{base_url}/api/session", headers={"Cookie": admin_cookie})
            headers = {
                "Content-Type": "application/json",
                "Cookie": admin_cookie,
                "X-CSRF-Token": session["csrfToken"],
            }
            json_request(
                f"{base_url}/api/users",
                method="POST",
                headers=headers,
                payload={
                    "username": "redirectteacher",
                    "displayName": "Redirect Teacher",
                    "department": "Redirect",
                    "password": "Redirect-Teacher-Password-2026",
                    "role": "teacher",
                    "enabled": True,
                },
            )
            teacher_login, teacher_cookie = login(base_url, "redirectteacher", "Redirect-Teacher-Password-2026")
            if teacher_login.get("redirectUrl") != "/teacher?view=pages":
                raise RuntimeError(f"teacher redirect mismatch: {teacher_login}")
            html = request(f"{base_url}/teacher?view=pages", headers={"Cookie": teacher_cookie}).read().decode("utf-8")
            if 'id="nav"' not in html or "admin.js" not in html:
                raise RuntimeError("teacher pages view did not serve teacher shell")
            response = request(f"{base_url}/admin", headers={"Cookie": teacher_cookie})
            if not response.geturl().endswith("/teacher?view=pages"):
                raise RuntimeError(f"teacher /admin redirect mismatch: {response.geturl()}")
            print("teacher_login_redirect_ok=true")
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()


if __name__ == "__main__":
    main()
