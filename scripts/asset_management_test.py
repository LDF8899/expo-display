import base64
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
PORT = os.environ.get("ASSET_MANAGEMENT_PORT", "8775")
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
    json_request(
        f"{base_url}/api/users",
        method="POST",
        headers=admin["headers"],
        payload={
            "username": username,
            "displayName": username.title(),
            "department": "Assets",
            "password": password,
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
    if not result.get("ok") or not result.get("asset"):
        raise RuntimeError(f"upload did not return asset metadata: {result}")
    return result["asset"]


def create_project_with_asset(base_url, admin, owner, asset_url):
    result, _ = json_request(
        f"{base_url}/api/projects",
        method="POST",
        headers=admin["headers"],
        payload={"name": f"{owner} asset project", "ownerUsername": owner, "defaultImageUrl": asset_url},
    )
    return result["project"]


def create_project(base_url, admin, owner):
    result, _ = json_request(
        f"{base_url}/api/projects",
        method="POST",
        headers=admin["headers"],
        payload={"name": f"{owner} review project", "ownerUsername": owner},
    )
    return result["project"]


def save_page(base_url, session, project_id, code, title, image_url=""):
    result, _ = json_request(
        f"{base_url}/api/projects/{project_id}/pages/{code}",
        method="PUT",
        headers=session["headers"],
        payload={
            "category": "Assets",
            "source": "Asset Test",
            "publishedAt": "2026-07-18",
            "title": title,
            "body": "<p>asset usage</p>",
            "imageUrl": image_url,
            "enabled": True,
        },
    )
    return result["page"]


def asset_ids(base_url, session):
    result, _ = json_request(f"{base_url}/api/assets", headers={"Cookie": session["cookie"]})
    return {item["id"] for item in result["assets"]}, result["assets"]


def main():
    with tempfile.TemporaryDirectory() as temp:
        temp_path = Path(temp)
        upload_dir = temp_path / "uploads"
        base_url = f"http://127.0.0.1:{PORT}"
        env = os.environ.copy()
        env.update(
            {
                "HOST": "127.0.0.1",
                "PORT": PORT,
                "DB_PATH": str(temp_path / "expo-assets.db"),
                "UPLOAD_DIR": str(upload_dir),
                "ADMIN_PASSWORD": "Admin-Asset-Password-2026",
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
            admin = login(base_url, "admin", "Admin-Asset-Password-2026")
            create_teacher(base_url, admin, "assetone", "Asset-One-Password-2026")
            create_teacher(base_url, admin, "assettwo", "Asset-Two-Password-2026")
            one = login(base_url, "assetone", "Asset-One-Password-2026")
            two = login(base_url, "assettwo", "Asset-Two-Password-2026")

            asset_one = upload_asset(base_url, one, "one.png")
            asset_two = upload_asset(base_url, two, "two.png")
            if asset_one["ownerUsername"] != "assetone" or asset_two["ownerUsername"] != "assettwo":
                raise RuntimeError(f"asset owners mismatch: {asset_one}, {asset_two}")

            path_one = upload_dir / asset_one["storageKey"]
            path_two = upload_dir / asset_two["storageKey"]
            if not path_one.exists() or not path_two.exists():
                raise RuntimeError("uploaded files missing")

            one_ids, one_assets = asset_ids(base_url, one)
            two_ids, two_assets = asset_ids(base_url, two)
            if one_ids != {asset_one["id"]}:
                raise RuntimeError(f"teacher one asset list leaked: {one_assets}")
            if two_ids != {asset_two["id"]}:
                raise RuntimeError(f"teacher two asset list leaked: {two_assets}")

            admin_ids, _ = asset_ids(base_url, admin)
            if not {asset_one["id"], asset_two["id"]}.issubset(admin_ids):
                raise RuntimeError(f"admin cannot see all assets: {admin_ids}")

            expect_status(404, f"{base_url}/api/assets/{asset_two['id']}", method="DELETE", headers=one["headers"], payload={})
            if not path_two.exists():
                raise RuntimeError("forbidden delete removed another user's file")

            create_project_with_asset(base_url, admin, "assettwo", asset_two["url"])
            expect_status(400, f"{base_url}/api/assets/{asset_two['id']}", method="DELETE", headers=two["headers"], payload={})
            if not path_two.exists():
                raise RuntimeError("in-use delete removed referenced file")

            asset_three = upload_asset(base_url, one, "pending.png")
            path_three = upload_dir / asset_three["storageKey"]
            project = create_project(base_url, admin, "assetone")
            save_page(base_url, admin, project["id"], "ASSET-PENDING", "Approved Page")
            pending_page = save_page(base_url, one, project["id"], "ASSET-PENDING", "Pending Page", asset_three["url"])
            if pending_page["reviewStatus"] != "pending":
                raise RuntimeError(f"expected pending page update: {pending_page}")
            expect_status(400, f"{base_url}/api/assets/{asset_three['id']}", method="DELETE", headers=one["headers"], payload={})
            if not path_three.exists():
                raise RuntimeError("pending-version delete removed referenced file")

            deleted, _ = json_request(
                f"{base_url}/api/assets/{asset_one['id']}",
                method="DELETE",
                headers=one["headers"],
                payload={},
            )
            if deleted["asset"]["id"] != asset_one["id"]:
                raise RuntimeError(f"delete returned wrong asset: {deleted}")
            if path_one.exists():
                raise RuntimeError("deleted asset file still exists")
            one_ids_after, _ = asset_ids(base_url, one)
            if asset_one["id"] in one_ids_after:
                raise RuntimeError(f"deleted asset still listed: {one_ids_after}")

            print("asset_management_ok=true")
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()


if __name__ == "__main__":
    main()
