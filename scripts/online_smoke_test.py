import json
import os
import subprocess
import sys
import time
import urllib.request


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = os.environ.get("SMOKE_PORT", "8765")


def request(url, method="GET", headers=None):
    req = urllib.request.Request(url, method=method, headers=headers or {})
    return urllib.request.urlopen(req, timeout=5)


def main():
    env = os.environ.copy()
    env["HOST"] = "127.0.0.1"
    env["PORT"] = PORT
    process = subprocess.Popen(
        [sys.executable, "server.py"],
        cwd=ROOT,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        time.sleep(2)
        health_response = request(f"http://127.0.0.1:{PORT}/api/health")
        health = json.loads(health_response.read().decode("utf-8"))
        if not health.get("ok"):
            raise RuntimeError(f"health check failed: {health}")
        csp = health_response.headers.get("Content-Security-Policy", "")
        if "object-src 'none'" not in csp:
            raise RuntimeError("Content-Security-Policy header is missing or incomplete")
        ready = json.loads(request(f"http://127.0.0.1:{PORT}/api/ready").read().decode("utf-8"))
        if not ready.get("ok"):
            raise RuntimeError(f"ready check failed: {ready}")
        if not ready.get("checks", {}).get("database", {}).get("ok"):
            raise RuntimeError(f"database readiness failed: {ready}")
        if not ready.get("checks", {}).get("storage", {}).get("ok"):
            raise RuntimeError(f"storage readiness failed: {ready}")

        preflight = request(
            f"http://127.0.0.1:{PORT}/api/session",
            method="OPTIONS",
            headers={"Origin": "https://example.invalid"},
        )
        cors_header = preflight.headers.get("Access-Control-Allow-Origin", "")
        if cors_header:
            raise RuntimeError(f"CORS should be closed by default, got {cors_header!r}")

        print("health_ok=true")
        print("ready_ok=true")
        print("csp_header=present")
        print(f"preflight_status={preflight.status}")
        print("cors_default=closed")
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()


if __name__ == "__main__":
    main()
