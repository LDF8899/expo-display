import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PORT = os.environ.get("ADMIN_EMPTY_CONTENT_PORT", "8789")
ADMIN_PASSWORD = "Admin-Empty-Content-Password-2026"


def request(url, method="GET", headers=None, payload=None):
    body = json.dumps(payload or {}, ensure_ascii=False).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, method=method, headers=headers or {}, data=body)
    return urllib.request.urlopen(req, timeout=5)


def json_request(url, method="GET", headers=None, payload=None):
    response = request(url, method=method, headers=headers, payload=payload)
    return json.loads(response.read().decode("utf-8")), response


def login(base_url):
    _, response = json_request(
        f"{base_url}/api/login",
        method="POST",
        headers={"Content-Type": "application/json"},
        payload={"username": "admin", "password": ADMIN_PASSWORD},
    )
    cookie = response.headers.get("Set-Cookie", "").split(";", 1)[0]
    session, _ = json_request(f"{base_url}/api/session", headers={"Cookie": cookie})
    return {
        "headers": {
            "Content-Type": "application/json",
            "Cookie": cookie,
            "X-CSRF-Token": session["csrfToken"],
        }
    }


def main():
    with tempfile.TemporaryDirectory() as temp:
        temp_path = Path(temp)
        base_url = f"http://127.0.0.1:{PORT}"
        env = os.environ.copy()
        env.update(
            {
                "HOST": "127.0.0.1",
                "PORT": PORT,
                "DB_PATH": str(temp_path / "expo-empty-content.db"),
                "UPLOAD_DIR": str(temp_path / "uploads"),
                "ADMIN_PASSWORD": ADMIN_PASSWORD,
                "ASSET_STORAGE_BACKEND": "local",
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
            admin = login(base_url)
            projects, _ = json_request(f"{base_url}/api/projects", headers=admin["headers"])
            project_id = projects["projects"][0]["id"]
            forms, _ = json_request(f"{base_url}/api/projects/{project_id}/lowcode/forms", headers=admin["headers"])
            module_key = (forms["forms"][0].get("targetModuleKey") if forms["forms"] else "") or "service"

            page, _ = json_request(
                f"{base_url}/api/projects/{project_id}/pages/EMPTY-PAGE",
                method="PUT",
                headers=admin["headers"],
                payload={"title": "", "subtitle": "", "body": "", "enabled": True},
            )
            if page["page"]["title"] != "" or page["page"]["body"] != "":
                raise RuntimeError(f"empty page fields were not preserved: {page['page']}")

            item, _ = json_request(
                f"{base_url}/api/projects/{project_id}/content-items",
                method="POST",
                headers=admin["headers"],
                payload={
                    "moduleKey": module_key,
                    "contentType": "article",
                    "title": "",
                    "subtitle": "",
                    "summary": "",
                    "bodyJson": [],
                    "enabled": True,
                },
            )
            if item["item"]["title"] != "" or item["item"]["summary"] != "":
                raise RuntimeError(f"empty content item fields were not preserved: {item['item']}")

            form_id = forms["forms"][0]["id"]
            record, _ = json_request(
                f"{base_url}/api/projects/{project_id}/lowcode/forms/{form_id}/records",
                method="POST",
                headers=admin["headers"],
                payload={"data": {"title": "", "summary": "", "bodyText": ""}},
            )
            generated = record.get("item") or {}
            if generated.get("title") != "":
                raise RuntimeError(f"empty lowcode generated title was not preserved: {generated}")

            print("admin_empty_content_ok=true")
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()


if __name__ == "__main__":
    main()
