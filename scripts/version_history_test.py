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
PORT = os.environ.get("VERSION_HISTORY_PORT", "8791")


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
        "headers": {
            "Content-Type": "application/json",
            "Cookie": cookie,
            "X-CSRF-Token": session["csrfToken"],
        },
    }


def create_teacher(base_url, admin, username):
    json_request(
        f"{base_url}/api/users",
        method="POST",
        headers=admin["headers"],
        payload={
            "username": username,
            "displayName": username,
            "department": "History",
            "password": f"{username}-Password-2026",
            "role": "teacher",
            "enabled": True,
        },
    )


def save_page(base_url, session, project_id, code, title):
    result, _ = json_request(
        f"{base_url}/api/projects/{project_id}/pages/{urllib.parse.quote(code)}",
        method="PUT",
        headers=session["headers"],
        payload={
            "category": "History",
            "source": "Version Test",
            "publishedAt": "2026-07-18",
            "title": title,
            "subtitle": "Version history subtitle",
            "body": f"<p>{title}</p>",
            "imageUrl": "",
            "enabled": True,
        },
    )
    return result["page"]


def pending_review(base_url, admin, review_type, project_id, code=None):
    reviews, _ = json_request(f"{base_url}/api/reviews?status=pending", headers={"Cookie": admin["cookie"]})
    items = reviews["reviews"][review_type]
    for item in items:
        if item["projectId"] == project_id and (code is None or item.get("code") == code):
            return item
    raise RuntimeError(f"pending {review_type} review not found: {reviews}")


def expect_404(url, headers):
    try:
        json_request(url, headers=headers)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return
        raise
    raise RuntimeError(f"expected 404 for {url}")


def main():
    with tempfile.TemporaryDirectory() as temp:
        temp_path = Path(temp)
        base_url = f"http://127.0.0.1:{PORT}"
        admin_password = "Admin-Version-History-Password-2026"
        env = os.environ.copy()
        env.update(
            {
                "HOST": "127.0.0.1",
                "PORT": PORT,
                "DB_PATH": str(temp_path / "expo-version-history.db"),
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
            admin = login(base_url, "admin", admin_password)
            create_teacher(base_url, admin, "historyteacher")
            create_teacher(base_url, admin, "otherhistoryteacher")

            project_result, _ = json_request(
                f"{base_url}/api/projects",
                method="POST",
                headers=admin["headers"],
                payload={"name": "Version History Project", "ownerUsername": "historyteacher"},
            )
            project_id = project_result["project"]["id"]
            teacher = login(base_url, "historyteacher", "historyteacher-Password-2026")
            other_teacher = login(base_url, "otherhistoryteacher", "otherhistoryteacher-Password-2026")

            code = "VERSION-HISTORY-001"
            save_page(base_url, admin, project_id, code, "Published Title")
            save_page(base_url, teacher, project_id, code, "Rejected Draft Title")
            rejected_review = pending_review(base_url, admin, "pages", project_id, code)
            json_request(
                f"{base_url}/api/reviews/pages/{rejected_review['id']}/reject",
                method="POST",
                headers=admin["headers"],
                payload={"note": "history rejection"},
            )

            save_page(base_url, teacher, project_id, code, "Approved Draft Title")
            approved_review = pending_review(base_url, admin, "pages", project_id, code)
            json_request(
                f"{base_url}/api/reviews/pages/{approved_review['id']}/approve",
                method="POST",
                headers=admin["headers"],
                payload={"note": "history approval"},
            )

            json_request(
                f"{base_url}/api/projects/{project_id}",
                method="PUT",
                headers=teacher["headers"],
                payload={"name": "Rejected Project Config", "idleTitle": "Draft welcome title"},
            )
            project_review = pending_review(base_url, admin, "projects", project_id)
            json_request(
                f"{base_url}/api/reviews/projects/{project_review['id']}/reject",
                method="POST",
                headers=admin["headers"],
                payload={"note": "project history rejection"},
            )

            project_history, _ = json_request(
                f"{base_url}/api/projects/{project_id}/versions",
                headers={"Cookie": teacher["cookie"]},
            )
            project_statuses = {item["status"] for item in project_history["versions"]}
            if not {"approved", "rejected"}.issubset(project_statuses):
                raise RuntimeError(f"project history missing statuses: {project_history}")
            if not any(item["reviewNote"] == "project history rejection" for item in project_history["versions"]):
                raise RuntimeError(f"project review note missing: {project_history}")

            page_history, _ = json_request(
                f"{base_url}/api/projects/{project_id}/pages/{urllib.parse.quote(code)}/versions",
                headers={"Cookie": admin["cookie"]},
            )
            page_statuses = [item["status"] for item in page_history["versions"]]
            if page_statuses.count("approved") < 2 or "rejected" not in page_statuses:
                raise RuntimeError(f"page history missing statuses: {page_history}")
            if not any(item["reviewNote"] == "history rejection" for item in page_history["versions"]):
                raise RuntimeError(f"page rejection note missing: {page_history}")
            if not any("reviewVersion=" in item.get("previewUrl", "") for item in page_history["versions"]):
                raise RuntimeError(f"page preview url missing: {page_history}")
            if not any(any(diff["changed"] and diff["field"] == "title" for diff in item["diffs"]) for item in page_history["versions"]):
                raise RuntimeError(f"page history diffs missing title changes: {page_history}")

            expect_404(
                f"{base_url}/api/projects/{project_id}/versions",
                headers={"Cookie": other_teacher["cookie"]},
            )
            expect_404(
                f"{base_url}/api/projects/{project_id}/pages/{urllib.parse.quote(code)}/versions",
                headers={"Cookie": other_teacher["cookie"]},
            )

            print("version_history_ok=true")
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()


if __name__ == "__main__":
    main()
