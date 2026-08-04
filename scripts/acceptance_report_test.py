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
PORT = os.environ.get("ACCEPTANCE_REPORT_PORT", "8780")


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


def expect_status(code, url, headers=None):
    try:
        request(url, headers=headers)
    except urllib.error.HTTPError as exc:
        if exc.code == code:
            return
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"expected {code}, got {exc.code}: {body}") from exc
    raise RuntimeError(f"expected {code}, request succeeded")


def main():
    with tempfile.TemporaryDirectory() as temp:
        temp_path = Path(temp)
        base_url = f"http://127.0.0.1:{PORT}"
        admin_password = "Admin-Acceptance-Report-Password-2026"
        env = os.environ.copy()
        env.update(
            {
                "HOST": "127.0.0.1",
                "PORT": PORT,
                "DB_PATH": str(temp_path / "expo-acceptance.db"),
                "UPLOAD_DIR": str(temp_path / "uploads"),
                "ADMIN_PASSWORD": admin_password,
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
            admin = login(base_url, "admin", admin_password)
            json_request(
                f"{base_url}/api/users",
                method="POST",
                headers=admin["headers"],
                payload={
                    "username": "reportteacher",
                    "displayName": "Report Teacher",
                    "department": "Report",
                    "password": "Report-Teacher-Password-2026",
                    "role": "teacher",
                    "enabled": True,
                },
            )
            teacher = login(base_url, "reportteacher", "Report-Teacher-Password-2026")
            expect_status(401, f"{base_url}/api/admin/acceptance-report.json", headers={"Cookie": teacher["cookie"]})

            report_data, response = json_request(
                f"{base_url}/api/admin/acceptance-report.json",
                headers={"Cookie": admin["cookie"]},
            )
            disposition = response.headers.get("Content-Disposition", "")
            if "expo-acceptance-report.json" not in disposition:
                raise RuntimeError(f"missing attachment filename: {disposition}")
            report = report_data["report"]
            for key in ("generatedAt", "generatedBy", "summary", "ready", "config", "deployed", "deployCheck", "pending", "assets", "portalReports"):
                if key not in report:
                    raise RuntimeError(f"report missing {key}: {report}")
            if not report["ready"]["ok"] or not report["deployCheck"]["ok"]:
                raise RuntimeError(f"report health should be ok in temp app: {report}")
            portal_reports = report["portalReports"]
            for key in ("contentQuality", "assetArchive", "lowcode", "reminders"):
                if key not in portal_reports:
                    raise RuntimeError(f"portal report missing {key}: {portal_reports}")
            if "stats" not in portal_reports["lowcode"] or "byKind" not in portal_reports["assetArchive"]:
                raise RuntimeError(f"portal report summary malformed: {portal_reports}")
            raw = json.dumps(report_data, ensure_ascii=False)
            if admin_password in raw or "CSRF_SECRET" in raw:
                raise RuntimeError("acceptance report leaked a secret")
            print("acceptance_report_ok=true")
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()


if __name__ == "__main__":
    main()
