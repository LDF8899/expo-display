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
PORT = os.environ.get("CONTENT_QUALITY_REPORT_PORT", "8782")


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


def create_content_item(base_url, admin, project_id):
    result, _ = json_request(
        f"{base_url}/api/projects/{project_id}/content-items",
        method="POST",
        headers=admin["headers"],
        payload={
            "moduleKey": "media",
            "contentType": "video",
            "title": "质量检查视频资料",
            "summary": "",
            "body": "内容较短",
            "enabled": True,
            "assets": [],
        },
    )
    return result["item"]


def main():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp:
        temp_path = Path(temp)
        db_path = temp_path / "expo-content-quality-report.db"
        base_url = f"http://127.0.0.1:{PORT}"
        env = os.environ.copy()
        env.update(
            {
                "HOST": "127.0.0.1",
                "PORT": PORT,
                "DB_PATH": str(db_path),
                "UPLOAD_DIR": str(temp_path / "uploads"),
                "ADMIN_PASSWORD": "Admin-Content-Quality-2026",
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
            admin = login(base_url, "admin", "Admin-Content-Quality-2026")
            create_user(base_url, admin, "qualityteacher", "Quality-Teacher-2026", "财经商贸", "teacher")
            create_user(base_url, admin, "otherteacher", "Other-Teacher-2026", "现代农业", "teacher")
            create_user(base_url, admin, "qualitydept", "Quality-Dept-2026", "财经商贸", "department_admin")
            project = create_project(base_url, admin, "qualityteacher", "财经商贸质量报告门户")
            other_project = create_project(base_url, admin, "otherteacher", "现代农业质量报告门户")
            item = create_content_item(base_url, admin, project["id"])

            report_data, _ = json_request(
                f"{base_url}/api/projects/{project['id']}/content-quality",
                headers={"Cookie": admin["cookie"]},
            )
            report = report_data["report"]
            if report["checked"] != 1 or report["issueItemCount"] != 1:
                raise RuntimeError(f"unexpected report totals: {report}")
            entry = report["entries"][0]
            issue_labels = {issue["label"] for issue in entry["issues"]}
            expected = {"缺少卡片摘要", "正文少于 80 字", "缺少图片/视频素材", "视频类资料缺少视频素材"}
            if item["id"] != entry["itemId"] or not expected.issubset(issue_labels):
                raise RuntimeError(f"quality issues missing: {entry}")
            if report["highCount"] < 1 or report["mediumCount"] < 3:
                raise RuntimeError(f"quality severity counts wrong: {report}")

            dept_admin = login(base_url, "qualitydept", "Quality-Dept-2026")
            scoped_data, _ = json_request(
                f"{base_url}/api/projects/{project['id']}/content-quality",
                headers={"Cookie": dept_admin["cookie"]},
            )
            if scoped_data["report"]["entries"][0]["itemId"] != item["id"]:
                raise RuntimeError(f"department admin report mismatch: {scoped_data}")
            expect_status(
                404,
                f"{base_url}/api/projects/{other_project['id']}/content-quality",
                headers={"Cookie": dept_admin["cookie"]},
            )
            print("content_quality_report_ok=true")
        finally:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()


if __name__ == "__main__":
    main()
