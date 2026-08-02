import base64
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PORT = os.environ.get("OPERATIONS_DASHBOARD_PORT", "8778")
PNG_1X1 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8"
    "/x8AAwMCAO+/p9sAAAAASUVORK5CYII="
)


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
            "username": "opteacher",
            "displayName": "Ops Teacher",
            "department": "Ops",
            "password": "Ops-Teacher-Password-2026",
            "role": "teacher",
            "enabled": True,
        },
    )


def upload_asset(base_url, session, filename):
    result, _ = json_request(
        f"{base_url}/api/assets",
        method="POST",
        headers=session["headers"],
        payload={"filename": filename, "dataUrl": f"data:image/png;base64,{PNG_1X1}"},
    )
    return result["asset"]


def main():
    with tempfile.TemporaryDirectory() as temp:
        temp_path = Path(temp)
        base_url = f"http://127.0.0.1:{PORT}"
        env = os.environ.copy()
        env.update(
            {
                "HOST": "127.0.0.1",
                "PORT": PORT,
                "DB_PATH": str(temp_path / "expo-ops.db"),
                "UPLOAD_DIR": str(temp_path / "uploads"),
                "ADMIN_PASSWORD": "Admin-Operations-Password-2026",
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
            admin = login(base_url, "admin", "Admin-Operations-Password-2026")
            create_teacher(base_url, admin)
            teacher = login(base_url, "opteacher", "Ops-Teacher-Password-2026")
            project_result, _ = json_request(
                f"{base_url}/api/projects",
                method="POST",
                headers=admin["headers"],
                payload={"name": "Operations Project", "ownerUsername": "opteacher"},
            )
            project_id = project_result["project"]["id"]
            upload_asset(base_url, admin, "admin.png")
            upload_asset(base_url, teacher, "teacher.png")
            json_request(
                f"{base_url}/api/projects/{project_id}",
                method="PUT",
                headers=teacher["headers"],
                payload={"name": "Operations Project Draft"},
            )

            admin_dashboard, _ = json_request(f"{base_url}/api/admin/dashboard", headers={"Cookie": admin["cookie"]})
            ops = admin_dashboard["dashboard"]["operations"]
            if not ops["ready"]["ok"] or not ops["ready"]["checks"]["database"]["ok"]:
                raise RuntimeError(f"ready status missing or unhealthy: {ops}")
            if ops["deployed"]["welcomeProjectId"] <= 0 or ops["deployed"]["contentProjectId"] <= 0:
                raise RuntimeError(f"deployment status missing: {ops['deployed']}")
            if ops["pending"]["projects"] < 1:
                raise RuntimeError(f"pending project count missing: {ops['pending']}")
            if ops["assets"]["count"] < 2:
                raise RuntimeError(f"admin asset count should include all assets: {ops['assets']}")

            teacher_dashboard, _ = json_request(f"{base_url}/api/admin/dashboard", headers={"Cookie": teacher["cookie"]})
            teacher_ops = teacher_dashboard["dashboard"]["operations"]
            if teacher_ops["assets"]["count"] != 1:
                raise RuntimeError(f"teacher asset count leaked global assets: {teacher_ops['assets']}")
            if teacher_ops["pending"]["projects"] != 0:
                raise RuntimeError(f"teacher should not see global pending project count: {teacher_ops['pending']}")

            print("operations_dashboard_ok=true")
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()


if __name__ == "__main__":
    main()
