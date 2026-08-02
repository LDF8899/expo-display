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
PORT = os.environ.get("REVIEW_DIFF_PORT", "8776")


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


def create_teacher(base_url, admin):
    json_request(
        f"{base_url}/api/users",
        method="POST",
        headers=admin["headers"],
        payload={
            "username": "reviewteacher",
            "displayName": "Review Teacher",
            "department": "Review",
            "password": "Review-Teacher-Password-2026",
            "role": "teacher",
            "enabled": True,
        },
    )


def save_page(base_url, session, project_id, title, body):
    result, _ = json_request(
        f"{base_url}/api/projects/{project_id}/pages/{urllib.parse.quote('REVIEW-DIFF-001')}",
        method="PUT",
        headers=session["headers"],
        payload={
            "category": "Review",
            "source": "Diff Test",
            "publishedAt": "2026-07-18",
            "title": title,
            "subtitle": "Review diff subtitle",
            "body": body,
            "imageUrl": "",
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
                "DB_PATH": str(temp_path / "expo-review-diff.db"),
                "UPLOAD_DIR": str(temp_path / "uploads"),
                "ADMIN_PASSWORD": "Admin-Review-Diff-Password-2026",
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
            admin = login(base_url, "admin", "Admin-Review-Diff-Password-2026")
            create_teacher(base_url, admin)
            project_result, _ = json_request(
                f"{base_url}/api/projects",
                method="POST",
                headers=admin["headers"],
                payload={"name": "Review Diff Project", "ownerUsername": "reviewteacher"},
            )
            project_id = project_result["project"]["id"]
            save_page(base_url, admin, project_id, "Published Title", "<p>published body</p>")
            teacher = login(base_url, "reviewteacher", "Review-Teacher-Password-2026")
            pending = save_page(base_url, teacher, project_id, "Draft Title", "<p>draft body</p>")
            if pending["reviewStatus"] != "pending":
                raise RuntimeError(f"expected pending review: {pending}")

            reviews, _ = json_request(f"{base_url}/api/reviews?status=pending", headers={"Cookie": admin["cookie"]})
            page_reviews = [
                item
                for item in reviews["reviews"]["pages"]
                if item["projectId"] == project_id and item["code"] == "REVIEW-DIFF-001"
            ]
            if not page_reviews:
                raise RuntimeError(f"review not found: {reviews}")
            review = page_reviews[0]
            if review["current"]["title"] != "Published Title" or review["snapshot"]["title"] != "Draft Title":
                raise RuntimeError(f"current/snapshot mismatch: {review}")
            changed = {item["field"] for item in review["diffs"] if item["changed"]}
            if not {"title", "body"}.issubset(changed):
                raise RuntimeError(f"missing changed fields: {review['diffs']}")
            if f"reviewVersion={review['id']}" not in review.get("previewUrl", ""):
                raise RuntimeError(f"preview url missing version: {review.get('previewUrl')}")

            preview, _ = json_request(
                f"{base_url}/api/reviews/pages/{review['id']}/preview",
                headers={"Cookie": admin["cookie"]},
            )
            if preview["page"]["title"] != "Draft Title" or preview["page"]["body"] != "<p>draft body</p>":
                raise RuntimeError(f"preview did not return draft: {preview}")

            print("review_diff_ok=true")
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()


if __name__ == "__main__":
    main()
