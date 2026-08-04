import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PORT = os.environ.get("DEPARTMENT_ADMIN_SCOPE_PORT", "8781")


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
        "session": session,
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


def submit_page(base_url, teacher, project_id, code, title):
    result, _ = json_request(
        f"{base_url}/api/projects/{project_id}/pages/{urllib.parse.quote(code)}",
        method="PUT",
        headers=teacher["headers"],
        payload={
            "category": "Department Scope",
            "source": "Scope Test",
            "publishedAt": "2026-08-04",
            "title": title,
            "body": "<p>department admin scope</p>",
            "enabled": True,
        },
    )
    return result["page"]


def submit_lowcode_record(base_url, teacher, project_id):
    forms, _ = json_request(f"{base_url}/api/projects/{project_id}/lowcode/forms", headers={"Cookie": teacher["cookie"]})
    form = forms["forms"][0]
    result, _ = json_request(
        f"{base_url}/api/projects/{project_id}/lowcode/forms/{form['id']}/records",
        method="POST",
        headers=teacher["headers"],
        payload={
            "data": {
                "title": "模板填报待审资料",
                "summary": "这是一条通过资料采集模板提交的待审核资料。",
                "bodyText": "用于验证审核列表可以追溯到低代码原始填报记录。",
            }
        },
    )
    return result["record"]


def visible_review_project_ids(reviews):
    ids = set()
    for key in ("pages", "projects", "contentItems"):
        for item in reviews.get(key, []):
            ids.add(item["projectId"])
    return ids


def insert_asset(db_path, owner):
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO assets (
                owner_username, original_filename, storage_key, url,
                mime_type, size_bytes, backend, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (owner, f"{owner}.jpg", f"{owner}.jpg", f"/uploads/{owner}.jpg", "image/jpeg", 128, "local", "2026-08-04T00:00:00+00:00"),
        )


def main():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp:
        temp_path = Path(temp)
        db_path = temp_path / "expo-department-admin-scope.db"
        base_url = f"http://127.0.0.1:{PORT}"
        env = os.environ.copy()
        env.update(
            {
                "HOST": "127.0.0.1",
                "PORT": PORT,
                "DB_PATH": str(db_path),
                "UPLOAD_DIR": str(temp_path / "uploads"),
                "ADMIN_PASSWORD": "Admin-Department-Scope-2026",
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
            admin = login(base_url, "admin", "Admin-Department-Scope-2026")
            create_user(base_url, admin, "deptboss", "Dept-Boss-Password-2026", "财经商贸", "department_admin")
            create_user(base_url, admin, "bizteacher", "Biz-Teacher-Password-2026", "财经商贸", "teacher")
            create_user(base_url, admin, "agriteacher", "Agri-Teacher-Password-2026", "现代农业", "teacher")

            biz_project = create_project(base_url, admin, "bizteacher", "财经商贸专题")
            agri_project = create_project(base_url, admin, "agriteacher", "现代农业专题")

            biz_teacher = login(base_url, "bizteacher", "Biz-Teacher-Password-2026")
            agri_teacher = login(base_url, "agriteacher", "Agri-Teacher-Password-2026")
            submit_page(base_url, biz_teacher, biz_project["id"], "SCOPE-BIZ", "财经商贸待审")
            submit_page(base_url, agri_teacher, agri_project["id"], "SCOPE-AGRI", "现代农业待审")
            lowcode_record = submit_lowcode_record(base_url, biz_teacher, biz_project["id"])

            insert_asset(db_path, "bizteacher")
            insert_asset(db_path, "agriteacher")

            dept_admin = login(base_url, "deptboss", "Dept-Boss-Password-2026")
            if "department_admin" not in dept_admin["session"].get("permissions", []):
                raise RuntimeError(f"department admin permission missing: {dept_admin['session']}")

            projects, _ = json_request(f"{base_url}/api/projects", headers={"Cookie": dept_admin["cookie"]})
            visible_projects = {item["id"] for item in projects["projects"]}
            if visible_projects != {biz_project["id"]}:
                raise RuntimeError(f"department admin project scope leaked: {projects}")

            reviews, _ = json_request(f"{base_url}/api/reviews?status=pending", headers={"Cookie": dept_admin["cookie"]})
            visible_reviews = visible_review_project_ids(reviews["reviews"])
            if visible_reviews != {biz_project["id"]}:
                raise RuntimeError(f"department admin review scope leaked: {reviews}")
            lowcode_reviews = [
                item for item in reviews["reviews"]["contentItems"]
                if item.get("lowcodeRecord") and item["lowcodeRecord"].get("recordId") == lowcode_record["id"]
            ]
            if len(lowcode_reviews) != 1:
                raise RuntimeError(f"lowcode review source missing: {reviews}")
            detail, _ = json_request(
                f"{base_url}/api/lowcode/records/{lowcode_record['id']}",
                headers={"Cookie": dept_admin["cookie"]},
            )
            if detail["record"]["id"] != lowcode_record["id"] or detail["record"]["submittedBy"] != "bizteacher":
                raise RuntimeError(f"lowcode detail mismatch: {detail}")

            admin_reviews, _ = json_request(f"{base_url}/api/reviews?status=pending", headers={"Cookie": admin["cookie"]})
            all_pages = admin_reviews["reviews"]["pages"]
            biz_version = next(item for item in all_pages if item["projectId"] == biz_project["id"])["id"]
            agri_version = next(item for item in all_pages if item["projectId"] == agri_project["id"])["id"]

            expect_status(
                404,
                f"{base_url}/api/reviews/pages/{agri_version}/approve",
                method="POST",
                headers=dept_admin["headers"],
                payload={"note": "should not pass"},
            )
            json_request(
                f"{base_url}/api/reviews/pages/{biz_version}/approve",
                method="POST",
                headers=dept_admin["headers"],
                payload={"note": "department approved"},
            )

            assets, _ = json_request(f"{base_url}/api/assets", headers={"Cookie": dept_admin["cookie"]})
            asset_owners = {item["ownerUsername"] for item in assets["assets"]}
            if asset_owners != {"bizteacher"}:
                raise RuntimeError(f"department admin asset scope leaked: {assets}")

            expect_status(401, f"{base_url}/api/users", headers={"Cookie": dept_admin["cookie"]})
            expect_status(401, f"{base_url}/api/admin/logs", headers={"Cookie": dept_admin["cookie"]})
            expect_status(401, f"{base_url}/api/deploy/check/{biz_project['id']}", headers={"Cookie": dept_admin["cookie"]})
            print("department_admin_scope_ok=true")
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()


if __name__ == "__main__":
    main()
