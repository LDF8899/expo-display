import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PORT = os.environ.get("DEPLOY_PRECHECK_PORT", "8777")


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
        body = exc.read().decode("utf-8", errors="replace")
        if exc.code == code:
            return json.loads(body)
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


def create_teacher(base_url, admin):
    json_request(
        f"{base_url}/api/users",
        method="POST",
        headers=admin["headers"],
        payload={
            "username": "deployteacher",
            "displayName": "Deploy Teacher",
            "department": "Deploy",
            "password": "Deploy-Teacher-Password-2026",
            "role": "teacher",
            "enabled": True,
        },
    )


def save_page(base_url, session, project_id, code, title, image_url=""):
    result, _ = json_request(
        f"{base_url}/api/projects/{project_id}/pages/{urllib.parse.quote(code)}",
        method="PUT",
        headers=session["headers"],
        payload={
            "category": "Deploy",
            "source": "Precheck Test",
            "publishedAt": "2026-07-18",
            "title": title,
            "body": "<p>deploy precheck</p>",
            "imageUrl": image_url,
            "enabled": True,
        },
    )
    return result["page"]


def main():
    with tempfile.TemporaryDirectory() as temp:
        temp_path = Path(temp)
        base_url = f"http://127.0.0.1:{PORT}"
        env = os.environ.copy()
        env.update(
            {
                "HOST": "127.0.0.1",
                "PORT": PORT,
                "DB_PATH": str(temp_path / "expo-deploy-precheck.db"),
                "UPLOAD_DIR": str(temp_path / "uploads"),
                "ADMIN_PASSWORD": "Admin-Deploy-Precheck-Password-2026",
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
            admin = login(base_url, "admin", "Admin-Deploy-Precheck-Password-2026")
            create_teacher(base_url, admin)
            teacher = login(base_url, "deployteacher", "Deploy-Teacher-Password-2026")

            project_result, _ = json_request(
                f"{base_url}/api/projects",
                method="POST",
                headers=admin["headers"],
                payload={"name": "Deploy Precheck Project", "ownerUsername": "deployteacher"},
            )
            project_id = project_result["project"]["id"]
            good = save_page(base_url, admin, project_id, "DEPLOY-GOOD", "Good Page")
            stable = save_page(base_url, admin, project_id, "DEPLOY-STABLE", "Stable Page")
            missing = save_page(base_url, admin, project_id, "DEPLOY-MISSING", "Missing Asset Page", "/uploads/missing.png")

            empty_error = expect_status(
                400,
                f"{base_url}/api/deploy/content",
                method="POST",
                headers=admin["headers"],
                payload={"projectId": project_id, "pageIds": []},
            )
            if "未选择可部署页面" not in empty_error.get("error", ""):
                raise RuntimeError(f"empty selection was not blocked: {empty_error}")

            missing_error = expect_status(
                400,
                f"{base_url}/api/deploy/content",
                method="POST",
                headers=admin["headers"],
                payload={"projectId": project_id, "pageIds": [missing["id"]]},
            )
            if "缺少资源" not in missing_error.get("error", ""):
                raise RuntimeError(f"missing asset was not blocked: {missing_error}")

            save_page(base_url, teacher, project_id, "DEPLOY-GOOD", "Good Page Draft")
            check, _ = json_request(f"{base_url}/api/deploy/check/{project_id}", headers={"Cookie": admin["cookie"]})
            warnings = check["check"]["warnings"]
            if not any("等待审核" in item for item in warnings):
                raise RuntimeError(f"pending warning missing: {check}")

            deployed, _ = json_request(
                f"{base_url}/api/deploy/content",
                method="POST",
                headers=admin["headers"],
                payload={"projectId": project_id, "pageIds": [stable["id"]]},
            )
            if stable["id"] not in deployed["pageIds"]:
                raise RuntimeError(f"valid deploy failed: {deployed}")

            json_request(
                f"{base_url}/api/projects/{project_id}",
                method="PUT",
                headers=teacher["headers"],
                payload={"name": "Pending Config Name"},
            )
            welcome_error = expect_status(
                400,
                f"{base_url}/api/projects/{project_id}/deploy",
                method="POST",
                headers=admin["headers"],
                payload={},
            )
            if "等待审核" not in welcome_error.get("error", ""):
                raise RuntimeError(f"pending config deploy was not blocked: {welcome_error}")

            print("deploy_precheck_ok=true")
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()


if __name__ == "__main__":
    main()
