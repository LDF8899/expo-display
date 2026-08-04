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
PORT = os.environ.get("ONLINE_WORKFLOW_PORT", "8772")


def request(url, method="GET", headers=None, payload=None):
    body = json.dumps(payload or {}, ensure_ascii=False).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, method=method, headers=headers or {}, data=body)
    return urllib.request.urlopen(req, timeout=5)


def json_request(url, method="GET", headers=None, payload=None):
    response = request(url, method=method, headers=headers, payload=payload)
    return json.loads(response.read().decode("utf-8")), response


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
        "csrf": session["csrfToken"],
        "headers": {
            "Content-Type": "application/json",
            "Cookie": cookie,
            "X-CSRF-Token": session["csrfToken"],
        },
    }


def run_workflow(base_url, admin_password):
    admin = login(base_url, "admin", admin_password)

    teacher_username = "teacher01"
    teacher_password = "teacher-password"
    user_result, _ = json_request(
        f"{base_url}/api/users",
        method="POST",
        headers=admin["headers"],
        payload={
            "username": teacher_username,
            "displayName": "Teacher One",
            "department": "Online Demo",
            "password": teacher_password,
            "role": "teacher",
            "enabled": True,
        },
    )
    if user_result["user"]["username"] != teacher_username:
        raise RuntimeError(f"teacher create failed: {user_result}")

    project_result, _ = json_request(
        f"{base_url}/api/projects",
        method="POST",
        headers=admin["headers"],
        payload={"name": "Online Workflow Project", "ownerUsername": teacher_username},
    )
    project = project_result["project"]
    project_id = project["id"]
    if project["ownerUsername"] != teacher_username:
        raise RuntimeError(f"project owner mismatch: {project}")

    teacher = login(base_url, teacher_username, teacher_password)
    teacher_projects, _ = json_request(f"{base_url}/api/projects", headers={"Cookie": teacher["cookie"]})
    visible_ids = {item["id"] for item in teacher_projects["projects"]}
    if project_id not in visible_ids:
        raise RuntimeError(f"teacher cannot see assigned project: {teacher_projects}")

    code = "ONLINE-WORKFLOW-001"
    submit_result, _ = json_request(
        f"{base_url}/api/projects/{project_id}/pages/{urllib.parse.quote(code)}",
        method="PUT",
        headers=teacher["headers"],
        payload={
            "category": "Online",
            "source": "Teacher Upload",
            "publishedAt": "2026-07-18",
            "title": "Teacher Submitted Page",
            "subtitle": "Submitted by a teacher account",
            "body": "<p>Teacher content</p>",
            "accent": "#0f766e",
            "enabled": True,
        },
    )
    if submit_result["page"]["reviewStatus"] != "pending":
        raise RuntimeError(f"teacher page was not pending: {submit_result}")

    reviews, _ = json_request(f"{base_url}/api/reviews?status=pending", headers={"Cookie": admin["cookie"]})
    page_reviews = [
        item
        for item in reviews["reviews"]["pages"]
        if item["projectId"] == project_id and item["code"] == code
    ]
    if not page_reviews:
        raise RuntimeError(f"pending review not found: {reviews}")
    review_id = page_reviews[0]["id"]

    approved, _ = json_request(
        f"{base_url}/api/reviews/pages/{review_id}/approve",
        method="POST",
        headers=admin["headers"],
        payload={"note": "approved by workflow test"},
    )
    if approved["item"]["reviewStatus"] != "approved":
        raise RuntimeError(f"review approve failed: {approved}")

    pages, _ = json_request(f"{base_url}/api/projects/{project_id}/pages", headers={"Cookie": admin["cookie"]})
    page = next((item for item in pages["pages"] if item["code"] == code), None)
    if not page or page["reviewStatus"] != "approved":
        raise RuntimeError(f"approved page not visible: {pages}")

    deployed, _ = json_request(
        f"{base_url}/api/deploy/content",
        method="POST",
        headers=admin["headers"],
        payload={"projectId": project_id, "pageIds": [page["id"]]},
    )
    if page["id"] not in deployed["pageIds"]:
        raise RuntimeError(f"deploy did not include page: {deployed}")

    public_page, _ = json_request(f"{base_url}/api/pages/{urllib.parse.quote(code)}")
    if public_page["page"]["title"] != "Teacher Submitted Page":
        raise RuntimeError(f"public page mismatch: {public_page}")

    return project_id, page["id"]


def main():
    with tempfile.TemporaryDirectory() as temp:
        temp_path = Path(temp)
        admin_password = "workflow-admin-password"
        env = os.environ.copy()
        env.update(
            {
                "HOST": "127.0.0.1",
                "PORT": PORT,
                "DB_PATH": str(temp_path / "expo-workflow.db"),
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
            base_url = f"http://127.0.0.1:{PORT}"
            project_id, page_id = run_workflow(base_url, admin_password)
            print("online_workflow_ok=true")
            print(f"project_id={project_id}")
            print(f"page_id={page_id}")
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()


if __name__ == "__main__":
    main()
