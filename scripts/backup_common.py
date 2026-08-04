import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def timestamp():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def load_env_file(path):
    if not path:
        return
    env_path = Path(path)
    if not env_path.exists():
        raise FileNotFoundError(f"env file not found: {env_path}")
    for line in env_path.read_text(encoding="utf-8").splitlines():
        text = line.strip()
        if not text or text.startswith("#") or "=" not in text:
            continue
        name, value = text.split("=", 1)
        os.environ.setdefault(name.strip(), value.strip().strip('"').strip("'"))


def mysql_env():
    return {
        "host": os.environ.get("MYSQL_HOST", "127.0.0.1"),
        "port": os.environ.get("MYSQL_PORT", "3306"),
        "user": os.environ.get("MYSQL_USER", "root"),
        "password": os.environ.get("MYSQL_PASSWORD", ""),
        "database": os.environ.get("MYSQL_DATABASE", "expo_display"),
    }


def compose_command(compose_file, env_file, service, command):
    cmd = ["docker", "compose", "-f", str(compose_file)]
    if env_file:
        cmd.extend(["--env-file", str(env_file)])
    cmd.extend(["exec", "-T", service])
    cmd.extend(command)
    return cmd


def run_streaming(cmd, stdin=None, stdout=None):
    result = subprocess.run(cmd, stdin=stdin, stdout=stdout)
    if result.returncode != 0:
        raise SystemExit(result.returncode)
