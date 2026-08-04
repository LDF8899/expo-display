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
PORT = os.environ.get("UPLOAD_SMOKE_PORT", "8766")
PNG_1X1 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8"
    "/x8AAwMCAO+/p9sAAAAASUVORK5CYII="
)


def request(url, method="GET", headers=None, body=None):
    req = urllib.request.Request(url, method=method, headers=headers or {}, data=body)
    return urllib.request.urlopen(req, timeout=5)


def json_body(payload):
    return json.dumps(payload, ensure_ascii=False).encode("utf-8")


def main():
    with tempfile.TemporaryDirectory() as temp:
        temp_path = Path(temp)
        db_path = temp_path / "expo-smoke.db"
        upload_dir = temp_path / "uploads"
        env = os.environ.copy()
        env.update(
            {
                "HOST": "127.0.0.1",
                "PORT": PORT,
                "DB_PATH": str(db_path),
                "UPLOAD_DIR": str(upload_dir),
                "ADMIN_PASSWORD": "smoke-password",
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
            login = request(
                f"http://127.0.0.1:{PORT}/api/login",
                method="POST",
                headers={"Content-Type": "application/json"},
                body=json_body({"username": "admin", "password": "smoke-password"}),
            )
            cookie = login.headers.get("Set-Cookie", "").split(";", 1)[0]
            session = request(f"http://127.0.0.1:{PORT}/api/session", headers={"Cookie": cookie})
            csrf_token = json.loads(session.read().decode("utf-8"))["csrfToken"]
            upload = request(
                f"http://127.0.0.1:{PORT}/api/assets",
                method="POST",
                headers={"Content-Type": "application/json", "Cookie": cookie, "X-CSRF-Token": csrf_token},
                body=json_body(
                    {
                        "filename": "pixel.png",
                        "dataUrl": f"data:image/png;base64,{PNG_1X1}",
                    }
                ),
            )
            result = json.loads(upload.read().decode("utf-8"))
            if not result.get("ok") or not str(result.get("url", "")).startswith("/uploads/"):
                raise RuntimeError(f"upload failed: {result}")
            saved_name = str(result["url"]).removeprefix("/uploads/")
            saved_path = upload_dir / saved_name
            if not saved_path.exists() or not saved_path.read_bytes():
                raise RuntimeError(f"uploaded file missing: {saved_path}")
            print("upload_ok=true")
            print(f"url={result['url']}")
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()


if __name__ == "__main__":
    main()
