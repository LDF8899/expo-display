import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def free_port(excluded=None):
    excluded = set(excluded or [])
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        if port not in excluded:
            return port


def json_request(url):
    try:
        with urllib.request.urlopen(url, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"request failed {exc.code}: {body}") from exc


def cleanup_port(port):
    if os.name != "nt":
        return
    subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            (
                f"Get-NetTCPConnection -LocalPort {int(port)} -State Listen -ErrorAction SilentlyContinue | "
                "Select-Object -ExpandProperty OwningProcess -Unique | "
                "ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }"
            ),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )


def main():
    app_port = int(os.environ.get("UNITY_MODEL_FALLBACK_APP_PORT") or free_port())
    preferred_port = free_port({app_port})
    fallback_port = free_port({app_port, preferred_port})
    blocker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    blocker.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    blocker.bind(("127.0.0.1", preferred_port))
    blocker.listen(1)

    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp:
        temp_path = Path(temp)
        model_dir = temp_path / "uploads" / "unityceshi111"
        model_dir.mkdir(parents=True)
        (model_dir / "index.html").write_text(
            "<!doctype html><title>Unity WebGL</title><canvas id='unity-canvas'></canvas><script src='Build/app.js'></script>",
            encoding="utf-8",
        )
        env = os.environ.copy()
        env.update(
            {
                "HOST": "127.0.0.1",
                "PORT": str(app_port),
                "DB_PATH": str(temp_path / "expo-unity-fallback.db"),
                "UPLOAD_DIR": str(temp_path / "uploads"),
                "ADMIN_PASSWORD": "Admin-Unity-Fallback-2026",
                "UNITY_MODEL_PORT": str(preferred_port),
                "UNITY_MODEL_FALLBACK_PORTS": str(fallback_port),
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
            result = json_request(f"http://127.0.0.1:{app_port}/api/unityceshi111/start")
            if not result.get("ok") or result.get("port") != fallback_port or result.get("fallbackFrom") != preferred_port:
                raise RuntimeError(f"unity fallback did not select fallback port: {result}")
            if not str(result.get("url", "")).startswith("http://127.0.0.1:"):
                raise RuntimeError(f"unity fallback should return 127.0.0.1 url: {result}")
            html = urllib.request.urlopen(result["url"], timeout=5).read().decode("utf-8", errors="replace")
            if "unity-canvas" not in html:
                raise RuntimeError(f"fallback url did not serve unity index: {result}")
            print("unity_model_fallback_ok=true")
        finally:
            blocker.close()
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
            cleanup_port(fallback_port)


if __name__ == "__main__":
    main()
