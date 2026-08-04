import argparse
import os
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from online_workflow_test import run_workflow


ROOT = Path(__file__).resolve().parent.parent


def run(cmd, env=None, check=True):
    print("+ " + " ".join(str(item) for item in cmd), flush=True)
    result = subprocess.run(cmd, cwd=ROOT, env=env)
    if check and result.returncode != 0:
        raise SystemExit(result.returncode)
    return result


def wait_ready(base_url, timeout_seconds):
    deadline = time.time() + timeout_seconds
    last_error = None
    while time.time() < deadline:
        try:
            urllib.request.urlopen(f"{base_url}/api/ready", timeout=5).read()
            return
        except Exception as exc:
            last_error = exc
            time.sleep(3)
    raise RuntimeError(f"compose app did not become ready: {last_error}")


def write_env(path, port, admin_password):
    path.write_text(
        "\n".join(
            [
                f"HTTP_PORT={port}",
                f"PUBLIC_BASE_URL=http://localhost:{port}",
                "SESSION_COOKIE_SECURE=0",
                "DATABASE_BACKEND=mysql",
                "MYSQL_HOST=db",
                "MYSQL_PORT=3306",
                "MYSQL_ROOT_PASSWORD=Root-Strong-Password-2026",
                "MYSQL_DATABASE=expo_display",
                "MYSQL_USER=expo_user",
                "MYSQL_PASSWORD=Db-Strong-Password-2026",
                "ADMIN_USERNAME=admin",
                f"ADMIN_PASSWORD={admin_password}",
                "CSRF_SECRET=csrf-secret-0123456789abcdef0123456789abcdef",
                "ASSET_STORAGE_BACKEND=local",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main():
    parser = argparse.ArgumentParser(description="Run Docker Compose online stack and execute the online workflow test.")
    parser.add_argument("--port", default="18080", help="host HTTP port for nginx")
    parser.add_argument("--project-name", default="expo-display-e2e", help="compose project name")
    parser.add_argument("--timeout", type=int, default=180, help="seconds to wait for /api/ready")
    parser.add_argument("--keep", action="store_true", help="keep containers and volumes after the test")
    args = parser.parse_args()

    admin_password = "Admin-Strong-Password-2026"
    with tempfile.TemporaryDirectory() as temp:
        env_file = Path(temp) / "compose.env"
        write_env(env_file, args.port, admin_password)
        compose = [
            "docker",
            "compose",
            "-p",
            args.project_name,
            "-f",
            "docker-compose.online.yml",
            "--env-file",
            str(env_file),
        ]
        started = False
        try:
            run(["docker", "info"])
            run(compose + ["up", "-d", "--build"])
            started = True
            base_url = f"http://127.0.0.1:{args.port}"
            wait_ready(base_url, args.timeout)
            project_id, page_id = run_workflow(base_url, admin_password)
            print("compose_online_workflow_ok=true")
            print(f"project_id={project_id}")
            print(f"page_id={page_id}")
        finally:
            if started and not args.keep:
                run(compose + ["down", "-v"], check=False)


if __name__ == "__main__":
    main()
