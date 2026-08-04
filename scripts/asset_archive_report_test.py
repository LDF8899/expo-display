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
PORT = os.environ.get("ASSET_ARCHIVE_REPORT_PORT", "8783")


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


def create_user(base_url, admin, username, password, department, role):
    result, _ = json_request(
        f"{base_url}/api/users",
        method="POST",
        headers=admin["headers"],
        payload={
            "username": username,
            "displayName": username.title(),
            "department": department,
            "password": password,
            "role": role,
            "enabled": True,
        },
    )
    return result["user"]


def create_project(base_url, admin, owner, name):
    result, _ = json_request(
        f"{base_url}/api/projects",
        method="POST",
        headers=admin["headers"],
        payload={"name": name, "ownerUsername": owner},
    )
    return result["project"]


def create_content_item(base_url, admin, project_id):
    result, _ = json_request(
        f"{base_url}/api/projects/{project_id}/content-items",
        method="POST",
        headers=admin["headers"],
        payload={
            "moduleKey": "overview",
            "contentType": "article",
            "title": "素材归档结构化资料",
            "summary": "用于验证结构化资料素材归档。",
            "body": "这是一条用于验证素材归档报告的结构化资料正文。",
            "enabled": True,
            "assets": [
                {
                    "url": "/uploads/archive-content.jpg",
                    "caption": "结构化资料图片",
                    "role": "cover",
                }
            ],
        },
    )
    return result["item"]


def submit_lowcode_record(base_url, admin, project_id):
    forms, _ = json_request(f"{base_url}/api/projects/{project_id}/lowcode/forms", headers={"Cookie": admin["cookie"]})
    form = forms["forms"][0]
    result, _ = json_request(
        f"{base_url}/api/projects/{project_id}/lowcode/forms/{form['id']}/records",
        method="POST",
        headers=admin["headers"],
        payload={
            "data": {
                "title": "素材归档模板填报",
                "summary": "用于验证模板填报素材归档。",
                "bodyText": "这是一条用于验证模板填报素材归档的正文。",
                "assets": [
                    {
                        "url": "/uploads/archive-lowcode.pdf",
                        "caption": "模板填报附件",
                        "role": "attachment",
                    }
                ],
            }
        },
    )
    return result["record"]


def main():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp:
        temp_path = Path(temp)
        db_path = temp_path / "expo-asset-archive-report.db"
        base_url = f"http://127.0.0.1:{PORT}"
        env = os.environ.copy()
        env.update(
            {
                "HOST": "127.0.0.1",
                "PORT": PORT,
                "DB_PATH": str(db_path),
                "UPLOAD_DIR": str(temp_path / "uploads"),
                "ADMIN_PASSWORD": "Admin-Asset-Archive-2026",
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
            admin = login(base_url, "admin", "Admin-Asset-Archive-2026")
            create_user(base_url, admin, "archiveteacher", "Archive-Teacher-2026", "财经商贸", "teacher")
            create_user(base_url, admin, "otherteacher", "Other-Archive-2026", "现代农业", "teacher")
            create_user(base_url, admin, "archivedept", "Archive-Dept-2026", "财经商贸", "department_admin")
            project = create_project(base_url, admin, "archiveteacher", "财经商贸素材归档门户")
            other_project = create_project(base_url, admin, "otherteacher", "现代农业素材归档门户")
            create_content_item(base_url, admin, project["id"])
            submit_lowcode_record(base_url, admin, project["id"])

            archive_data, _ = json_request(
                f"{base_url}/api/projects/{project['id']}/asset-archive",
                headers={"Cookie": admin["cookie"]},
            )
            report = archive_data["report"]
            urls = {entry["url"] for entry in report["entries"]}
            sources = {entry["source"] for entry in report["entries"]}
            if "/uploads/archive-content.jpg" not in urls or "/uploads/archive-lowcode.pdf" not in urls:
                raise RuntimeError(f"archive urls missing: {report}")
            if not {"结构化资料", "模板填报"}.issubset(sources):
                raise RuntimeError(f"archive sources missing: {report}")
            if report["byKind"].get("IMAGE", 0) < 1 or report["byKind"].get("FILE", 0) < 1:
                raise RuntimeError(f"archive kind counts wrong: {report}")

            dept_admin = login(base_url, "archivedept", "Archive-Dept-2026")
            scoped_data, _ = json_request(
                f"{base_url}/api/projects/{project['id']}/asset-archive",
                headers={"Cookie": dept_admin["cookie"]},
            )
            if not scoped_data["report"]["entries"]:
                raise RuntimeError(f"department admin archive unexpectedly empty: {scoped_data}")
            expect_status(
                404,
                f"{base_url}/api/projects/{other_project['id']}/asset-archive",
                headers={"Cookie": dept_admin["cookie"]},
            )
            print("asset_archive_report_ok=true")
        finally:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()


if __name__ == "__main__":
    main()
