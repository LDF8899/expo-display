import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PORT = os.environ.get("CSRF_SMOKE_PORT", "8770")


def request(url, method="GET", headers=None, payload=None):
    body = json.dumps(payload or {}, ensure_ascii=False).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, method=method, headers=headers or {}, data=body)
    return urllib.request.urlopen(req, timeout=5)


def json_request(url, method="GET", headers=None, payload=None):
    response = request(url, method=method, headers=headers, payload=payload)
    return json.loads(response.read().decode("utf-8")), response


def main():
    with tempfile.TemporaryDirectory() as temp:
        env = os.environ.copy()
        env.update(
            {
                "HOST": "127.0.0.1",
                "PORT": PORT,
                "DB_PATH": str(Path(temp) / "expo-csrf.db"),
                "UPLOAD_DIR": str(Path(temp) / "uploads"),
                "ADMIN_PASSWORD": "csrf-password",
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
            _, login_response = json_request(
                f"http://127.0.0.1:{PORT}/api/login",
                method="POST",
                headers={"Content-Type": "application/json"},
                payload={"username": "admin", "password": "csrf-password"},
            )
            cookie = login_response.headers.get("Set-Cookie", "").split(";", 1)[0]
            session, _ = json_request(f"http://127.0.0.1:{PORT}/api/session", headers={"Cookie": cookie})
            csrf_token = session["csrfToken"]

            try:
                request(
                    f"http://127.0.0.1:{PORT}/api/account/password",
                    method="POST",
                    headers={"Content-Type": "application/json", "Cookie": cookie},
                    payload={"oldPassword": "csrf-password", "newPassword": "csrf-password-2"},
                )
                raise RuntimeError("missing CSRF token was accepted")
            except urllib.error.HTTPError as exc:
                if exc.code != 403:
                    raise RuntimeError(f"expected 403 without CSRF token, got {exc.code}") from exc

            result, _ = json_request(
                f"http://127.0.0.1:{PORT}/api/account/password",
                method="POST",
                headers={"Content-Type": "application/json", "Cookie": cookie, "X-CSRF-Token": csrf_token},
                payload={"oldPassword": "csrf-password", "newPassword": "csrf-password-2"},
            )
            if not result.get("ok"):
                raise RuntimeError(f"CSRF-protected request failed: {result}")
            print("csrf_required=true")
            print("csrf_with_token_ok=true")
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()


if __name__ == "__main__":
    main()
