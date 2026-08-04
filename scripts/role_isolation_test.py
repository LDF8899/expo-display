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
PORT = os.environ.get("ROLE_ISOLATION_PORT", "8774")


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


def create_teacher(base_url, admin, username, password):
    result, _ = json_request(
        f"{base_url}/api/users",
        method="POST",
        headers=admin["headers"],
        payload={
            "username": username,
            "displayName": username.title(),
            "department": "Isolation",
            "password": password,
            "role": "teacher",
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


def create_page(base_url, admin, project_id, code, title):
    result, _ = json_request(
        f"{base_url}/api/projects/{project_id}/pages/{urllib.parse.quote(code)}",
        method="PUT",
        headers=admin["headers"],
        payload={
            "category": "Isolation",
            "source": "Role Test",
            "publishedAt": "2026-07-18",
            "title": title,
            "body": "<p>role isolation</p>",
            "enabled": True,
        },
    )
    return result["page"]


def insert_scan(db_path, code, project_id, created_at):
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO scans (code, raw_url, project_id, result, detail, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (code, f"/display?project={project_id}&code={code}", project_id, "ok", "role isolation", created_at),
        )


def assert_teacher_isolated(base_url, teacher, own_project_id, own_project_name, other_project_id):
    projects, _ = json_request(f"{base_url}/api/projects", headers={"Cookie": teacher["cookie"]})
    visible_ids = {item["id"] for item in projects["projects"]}
    if visible_ids != {own_project_id}:
        raise RuntimeError(f"teacher project list leaked: {projects}")

    expect_status(404, f"{base_url}/api/projects/{other_project_id}", headers={"Cookie": teacher["cookie"]})
    expect_status(
        404,
        f"{base_url}/api/projects/{other_project_id}/pages/SHARED-CODE",
        method="PUT",
        headers=teacher["headers"],
        payload={"title": "forbidden", "body": "<p>forbidden</p>", "enabled": True},
    )

    dashboard, _ = json_request(f"{base_url}/api/admin/dashboard", headers={"Cookie": teacher["cookie"]})
    data = dashboard["dashboard"]
    if data["summary"]["scans"] != 1 or data["summary"]["todayScans"] != 1:
        raise RuntimeError(f"teacher scan counts leaked: {data['summary']}")
    recent_projects = {item["projectName"] for item in data["recentScans"]}
    if recent_projects != {own_project_name}:
        raise RuntimeError(f"teacher recent scans leaked: {data['recentScans']}")
    log_users = {item["username"] for item in data["logs"]}
    if log_users and log_users != {own_project_name.lower().replace(' ', '')}:
        raise RuntimeError(f"teacher dashboard logs leaked: {data['logs']}")


def main():
    with tempfile.TemporaryDirectory() as temp:
        temp_path = Path(temp)
        db_path = temp_path / "expo-role-isolation.db"
        base_url = f"http://127.0.0.1:{PORT}"
        env = os.environ.copy()
        env.update(
            {
                "HOST": "127.0.0.1",
                "PORT": PORT,
                "DB_PATH": str(db_path),
                "UPLOAD_DIR": str(temp_path / "uploads"),
                "ADMIN_PASSWORD": "Admin-Role-Isolation-2026",
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
            admin = login(base_url, "admin", "Admin-Role-Isolation-2026")
            create_teacher(base_url, admin, "teacherone", "Teacher-One-Password-2026")
            create_teacher(base_url, admin, "teachertwo", "Teacher-Two-Password-2026")
            project_one = create_project(base_url, admin, "teacherone", "teacherone")
            project_two = create_project(base_url, admin, "teachertwo", "teachertwo")
            create_page(base_url, admin, project_one["id"], "SHARED-CODE", "Teacher One Page")
            create_page(base_url, admin, project_two["id"], "SHARED-CODE", "Teacher Two Page")
            today = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime())
            insert_scan(db_path, "SHARED-CODE", project_one["id"], today)
            insert_scan(db_path, "SHARED-CODE", project_two["id"], today)

            teacher_one = login(base_url, "teacherone", "Teacher-One-Password-2026")
            teacher_two = login(base_url, "teachertwo", "Teacher-Two-Password-2026")
            assert_teacher_isolated(base_url, teacher_one, project_one["id"], "teacherone", project_two["id"])
            assert_teacher_isolated(base_url, teacher_two, project_two["id"], "teachertwo", project_one["id"])

            admin_dashboard, _ = json_request(f"{base_url}/api/admin/dashboard", headers={"Cookie": admin["cookie"]})
            if admin_dashboard["dashboard"]["summary"]["scans"] != 2:
                raise RuntimeError(f"admin should see all scans: {admin_dashboard['dashboard']['summary']}")
            print("role_isolation_ok=true")
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()


if __name__ == "__main__":
    main()
