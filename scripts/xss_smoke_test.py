import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PORT = os.environ.get("XSS_SMOKE_PORT", "8767")


def request(url, method="GET", headers=None, body=None):
    req = urllib.request.Request(url, method=method, headers=headers or {}, data=body)
    return urllib.request.urlopen(req, timeout=5)


def json_body(payload):
    return json.dumps(payload, ensure_ascii=False).encode("utf-8")


def json_request(url, method="GET", headers=None, payload=None):
    body = json_body(payload) if payload is not None else None
    response = request(url, method=method, headers=headers or {}, body=body)
    return json.loads(response.read().decode("utf-8")), response


def main():
    with tempfile.TemporaryDirectory() as temp:
        temp_path = Path(temp)
        env = os.environ.copy()
        env.update(
            {
                "HOST": "127.0.0.1",
                "PORT": PORT,
                "DB_PATH": str(temp_path / "expo-xss.db"),
                "UPLOAD_DIR": str(temp_path / "uploads"),
                "ADMIN_PASSWORD": "xss-password",
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
                payload={"username": "admin", "password": "xss-password"},
            )
            cookie = login_response.headers.get("Set-Cookie", "").split(";", 1)[0]
            session, _ = json_request(f"http://127.0.0.1:{PORT}/api/session", headers={"Cookie": cookie})
            auth_headers = {
                "Content-Type": "application/json",
                "Cookie": cookie,
                "X-CSRF-Token": session["csrfToken"],
            }

            projects, _ = json_request(f"http://127.0.0.1:{PORT}/api/projects", headers={"Cookie": cookie})
            project_id = projects["projects"][0]["id"]
            payload = {
                "title": "XSS test",
                "body": (
                    '<p onclick="alert(1)">ok</p>'
                    '<script>alert(2)</script>'
                    '<img src="javascript:alert(3)" onerror="alert(4)" alt="x">'
                    '<a href="javascript:alert(5)">bad</a>'
                    '<a href="https://example.com/a">good</a>'
                ),
                "enabled": True,
            }
            code = "XSS-TEST"
            json_request(
                f"http://127.0.0.1:{PORT}/api/projects/{project_id}/pages/{urllib.parse.quote(code)}",
                method="PUT",
                headers=auth_headers,
                payload=payload,
            )
            page_data, _ = json_request(
                f"http://127.0.0.1:{PORT}/api/projects/{project_id}/pages/{urllib.parse.quote(code)}",
                headers={"Cookie": cookie},
            )
            body = page_data["page"]["body"].lower()
            forbidden = ["<script", "onclick", "onerror", "javascript:"]
            found = [item for item in forbidden if item in body]
            if found:
                raise RuntimeError(f"dangerous content survived: {found} in {body}")
            if 'href="https://example.com/a"' not in body:
                raise RuntimeError(f"safe link was not preserved: {body}")
            print("xss_sanitized=true")
            print(f"body={page_data['page']['body']}")
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()


if __name__ == "__main__":
    main()
