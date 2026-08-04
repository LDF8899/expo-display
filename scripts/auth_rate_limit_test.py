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
PORT = os.environ.get("AUTH_RATE_LIMIT_PORT", "8768")


def post_json(url, payload):
    req = urllib.request.Request(
        url,
        method="POST",
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload).encode("utf-8"),
    )
    return urllib.request.urlopen(req, timeout=5)


def main():
    with tempfile.TemporaryDirectory() as temp:
        env = os.environ.copy()
        env.update(
            {
                "HOST": "127.0.0.1",
                "PORT": PORT,
                "DB_PATH": str(Path(temp) / "expo-auth-rate.db"),
                "UPLOAD_DIR": str(Path(temp) / "uploads"),
                "ADMIN_PASSWORD": "auth-rate-password",
                "LOGIN_RATE_LIMIT": "2",
                "LOGIN_RATE_WINDOW_SECONDS": "60",
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
            statuses = []
            for _ in range(3):
                try:
                    post_json(
                        f"http://127.0.0.1:{PORT}/api/login",
                        {"username": "admin", "password": "wrong-password"},
                    )
                    statuses.append(200)
                except urllib.error.HTTPError as exc:
                    statuses.append(exc.code)
            if statuses != [401, 401, 429]:
                raise RuntimeError(f"unexpected login statuses: {statuses}")
            print("login_rate_limit_ok=true")
            print(f"statuses={statuses}")
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()


if __name__ == "__main__":
    main()
