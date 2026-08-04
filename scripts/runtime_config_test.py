import os
import subprocess
import sys


def run_case(env_overrides):
    env = os.environ.copy()
    env.update(env_overrides)
    return subprocess.run(
        [sys.executable, "server.py"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=5,
    )


def main():
    process = run_case(
        {
            "HOST": "0.0.0.0",
            "PORT": "8769",
            "ADMIN_PASSWORD": "123456",
            "CSRF_SECRET": "runtime-config-test-secret",
        }
    )
    output = process.stdout + process.stderr
    if process.returncode == 0 or "ADMIN_PASSWORD 必须是强随机值" not in output:
        raise RuntimeError(f"runtime validation did not fail as expected: {process.returncode}\n{output}")
    print("default_admin_password_blocked=true")

    process = run_case(
        {
            "HOST": "0.0.0.0",
            "PORT": "8771",
            "ADMIN_PASSWORD": "runtime-config-strong-password",
            "CSRF_SECRET": "REPLACE_WITH_RANDOM_CSRF_SECRET",
        }
    )
    output = process.stdout + process.stderr
    if process.returncode == 0 or "CSRF_SECRET 必须是强随机值" not in output:
        raise RuntimeError(f"CSRF validation did not fail as expected: {process.returncode}\n{output}")
    print("weak_csrf_secret_blocked=true")


if __name__ == "__main__":
    main()
