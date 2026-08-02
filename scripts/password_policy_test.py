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
PORT = os.environ.get("PASSWORD_POLICY_PORT", "8773")


def request(url, method="GET", headers=None, payload=None):
    body = json.dumps(payload or {}, ensure_ascii=False).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, method=method, headers=headers or {}, data=body)
    return urllib.request.urlopen(req, timeout=5)


def json_request(url, method="GET", headers=None, payload=None):
    response = request(url, method=method, headers=headers, payload=payload)
    return json.loads(response.read().decode("utf-8")), response


def expect_status(code, url, method="GET", headers=None, payload=None):
    try:
        request(url, method=method, headers=headers, payload=payload)
    except urllib.error.HTTPError as exc:
        if exc.code == code:
            return
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"expected {code}, got {exc.code}: {body}") from exc
    raise RuntimeError(f"expected {code}, request succeeded")


def login(base_url, username, password):
    _, response = json_request(
        f"{base_url}/api/login",
        method="POST",
        headers={"Content-Type": "application/json"},
        payload={"username": username, "password": password},
    )
    cookie = response.headers.get("Set-Cookie", "").split(";", 1)[0]
    session, _ = json_request(f"{base_url}/api/session", headers={"Cookie": cookie})
    return {
        "cookie": cookie,
        "headers": {
            "Content-Type": "application/json",
            "Cookie": cookie,
            "X-CSRF-Token": session["csrfToken"],
        },
    }


def main():
    with tempfile.TemporaryDirectory() as temp:
        base_url = f"http://127.0.0.1:{PORT}"
        env = os.environ.copy()
        env.update(
            {
                "HOST": "127.0.0.1",
                "PORT": PORT,
                "PUBLIC_BASE_URL": base_url,
                "DB_PATH": str(Path(temp) / "expo-password-policy.db"),
                "UPLOAD_DIR": str(Path(temp) / "uploads"),
                "ADMIN_PASSWORD": "Admin-Policy-Password-2026",
                "CSRF_SECRET": "password-policy-csrf-secret-2026-0123456789",
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
            admin = login(base_url, "admin", "Admin-Policy-Password-2026")

            weak_user = {
                "username": "weakteacher",
                "displayName": "Weak Teacher",
                "department": "Policy",
                "password": "123456",
                "role": "teacher",
                "enabled": True,
            }
            expect_status(400, f"{base_url}/api/users", method="POST", headers=admin["headers"], payload=weak_user)

            missing_password = dict(weak_user)
            missing_password["username"] = "nopassword"
            missing_password["password"] = ""
            expect_status(400, f"{base_url}/api/users", method="POST", headers=admin["headers"], payload=missing_password)

            strong_password = "Teacher-Policy-Password-2026"
            strong_user = dict(weak_user)
            strong_user["username"] = "policyteacher"
            strong_user["password"] = strong_password
            created, _ = json_request(
                f"{base_url}/api/users",
                method="POST",
                headers=admin["headers"],
                payload=strong_user,
            )
            if created["user"]["username"] != "policyteacher":
                raise RuntimeError(f"strong password user create failed: {created}")

            expect_status(
                400,
                f"{base_url}/api/users/policyteacher/reset-password",
                method="POST",
                headers=admin["headers"],
                payload={"password": "password"},
            )
            reset_password = "Teacher-Policy-Reset-2026"
            json_request(
                f"{base_url}/api/users/policyteacher/reset-password",
                method="POST",
                headers=admin["headers"],
                payload={"password": reset_password},
            )

            teacher = login(base_url, "policyteacher", reset_password)
            expect_status(
                400,
                f"{base_url}/api/account/password",
                method="POST",
                headers=teacher["headers"],
                payload={"oldPassword": reset_password, "newPassword": "123456"},
            )

            print("password_policy_ok=true")
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()


if __name__ == "__main__":
    main()
