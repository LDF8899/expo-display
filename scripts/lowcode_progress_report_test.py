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
PORT = os.environ.get("LOWCODE_PROGRESS_REPORT_PORT", "8784")


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


def expect_json_status(code, url, method="GET", headers=None, payload=None):
    try:
        request(url, method=method, headers=headers, payload=payload)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        if exc.code != code:
            raise RuntimeError(f"expected {code}, got {exc.code}: {body}") from exc
        try:
            return json.loads(body)
        except json.JSONDecodeError as decode_error:
            raise RuntimeError(f"expected json error body, got: {body}") from decode_error
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


def create_user(base_url, admin, username, password, department, role):
    result, _ = json_request(
        f"{base_url}/api/users",
        method="POST",
        headers=admin["headers"],
        payload={
            "username": username,
            "displayName": username.title(),
            "department": department,
            "password": password,
            "role": role,
            "enabled": True,
        },
    )
    return result["user"]


def create_project(base_url, admin, owner, name):
    result, _ = json_request(
        f"{base_url}/api/projects",
        method="POST",
        headers=admin["headers"],
        payload={"name": name, "ownerUsername": owner},
    )
    return result["project"]


def submit_lowcode_record(base_url, teacher, project_id):
    forms, _ = json_request(f"{base_url}/api/projects/{project_id}/lowcode/forms", headers={"Cookie": teacher["cookie"]})
    form = forms["forms"][0]
    if not form.get("quality") or "checks" not in form["quality"]:
        raise RuntimeError(f"lowcode form quality missing: {form}")
    result, _ = json_request(
        f"{base_url}/api/projects/{project_id}/lowcode/forms/{form['id']}/records",
        method="POST",
        headers=teacher["headers"],
        payload={
            "data": {
                "title": "进度报告模板填报",
                "summary": "用于验证低代码进度报告。",
                "bodyText": "这是一条用于验证模板、部门、填报人和提醒统计的资料。",
            }
        },
    )
    return form, result["record"]


def assert_required_field_submit_rules(base_url, teacher, project_id):
    forms, _ = json_request(f"{base_url}/api/projects/{project_id}/lowcode/forms", headers={"Cookie": teacher["cookie"]})
    form = None
    missing_required_keys = []
    for candidate in forms["forms"]:
        fields = (candidate.get("schema") or {}).get("fields") or []
        required_keys = [
            field.get("key")
            for field in fields
            if field.get("required") and field.get("key") not in {"title", "summary"}
        ]
        if required_keys:
            form = candidate
            missing_required_keys = required_keys
            break
    if not form:
        raise RuntimeError(f"no lowcode form with content required fields: {forms}")

    incomplete_payload = {
        "data": {
            "title": "缺字段验证",
            "summary": "用于验证正式提交会拦截模板必填字段。",
        }
    }
    error = expect_json_status(
        400,
        f"{base_url}/api/projects/{project_id}/lowcode/forms/{form['id']}/records",
        method="POST",
        headers=teacher["headers"],
        payload=incomplete_payload,
    )
    if "不能为空" not in str(error.get("error", "")):
        raise RuntimeError(f"required field error missing: {error}; keys={missing_required_keys}")

    draft_result, _ = json_request(
        f"{base_url}/api/projects/{project_id}/lowcode/forms/{form['id']}/records",
        method="POST",
        headers=teacher["headers"],
        payload={"draft": True, **incomplete_payload},
    )
    draft = draft_result["record"]
    if draft["status"] != "draft" or draft.get("contentItemId"):
        raise RuntimeError(f"incomplete draft should be saved without publishing content: {draft}")


def main():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp:
        temp_path = Path(temp)
        db_path = temp_path / "expo-lowcode-progress-report.db"
        base_url = f"http://127.0.0.1:{PORT}"
        env = os.environ.copy()
        env.update(
            {
                "HOST": "127.0.0.1",
                "PORT": PORT,
                "DB_PATH": str(db_path),
                "UPLOAD_DIR": str(temp_path / "uploads"),
                "ADMIN_PASSWORD": "Admin-Lowcode-Report-2026",
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
            admin = login(base_url, "admin", "Admin-Lowcode-Report-2026")
            create_user(base_url, admin, "reportteacher", "Report-Teacher-2026", "财经商贸", "teacher")
            create_user(base_url, admin, "otherteacher", "Other-Report-2026", "现代农业", "teacher")
            create_user(base_url, admin, "reportdept", "Report-Dept-2026", "财经商贸", "department_admin")
            project = create_project(base_url, admin, "reportteacher", "财经商贸低代码报告门户")
            other_project = create_project(base_url, admin, "otherteacher", "现代农业低代码报告门户")
            validation_project = create_project(base_url, admin, "reportteacher", "低代码必填校验门户")
            teacher = login(base_url, "reportteacher", "Report-Teacher-2026")
            assert_required_field_submit_rules(base_url, teacher, validation_project["id"])
            form, record = submit_lowcode_record(base_url, teacher, project["id"])
            expect_status(
                401,
                f"{base_url}/api/projects/{project['id']}/lowcode/report",
                headers={"Cookie": teacher["cookie"]},
            )
            expect_status(
                401,
                f"{base_url}/api/projects/{project['id']}/lowcode/template-quality",
                headers={"Cookie": teacher["cookie"]},
            )

            report_data, _ = json_request(
                f"{base_url}/api/projects/{project['id']}/lowcode/report",
                headers={"Cookie": admin["cookie"]},
            )
            report = report_data["report"]
            if report["stats"]["total"] != 1 or report["stats"]["pending"] != 1:
                raise RuntimeError(f"unexpected lowcode totals: {report}")
            if report.get("templateQuality", {}).get("total", 0) < 1:
                raise RuntimeError(f"template quality summary missing: {report}")
            template_rows = report["groups"]["templates"]
            template_row = next((row for row in template_rows if str(row["key"]) == str(form["id"])), None)
            if not template_row or template_row["stats"]["pending"] != 1:
                raise RuntimeError(f"template stats missing: {template_rows}")
            department_rows = report["groups"]["departments"]
            if not any(row["label"] == "财经商贸" and row["stats"]["total"] == 1 for row in department_rows):
                raise RuntimeError(f"department stats missing: {department_rows}")
            submitter_rows = report["groups"]["submitters"]
            if not any(row["key"] == "reportteacher" and row["stats"]["total"] == 1 for row in submitter_rows):
                raise RuntimeError(f"submitter stats missing: {submitter_rows}")
            reminders = report["groups"]["reminders"]
            reminder = next((row for row in reminders if row["key"] == record["contentModuleKey"]), None)
            if not reminder or reminder["stats"]["pending"] != 1:
                raise RuntimeError(f"reminder stats missing: {reminders}")
            template_quality_data, _ = json_request(
                f"{base_url}/api/projects/{project['id']}/lowcode/template-quality",
                headers={"Cookie": admin["cookie"]},
            )
            template_quality = template_quality_data["report"]
            if template_quality["summary"]["total"] < 1:
                raise RuntimeError(f"template quality report empty: {template_quality}")
            quality_entry = next((entry for entry in template_quality["entries"] if str(entry["formId"]) == str(form["id"])), None)
            if not quality_entry or not quality_entry.get("quality", {}).get("checks"):
                raise RuntimeError(f"template quality entry missing: {template_quality}")

            dept_admin = login(base_url, "reportdept", "Report-Dept-2026")
            scoped_data, _ = json_request(
                f"{base_url}/api/projects/{project['id']}/lowcode/report",
                headers={"Cookie": dept_admin["cookie"]},
            )
            if scoped_data["report"]["stats"]["total"] != 1:
                raise RuntimeError(f"department admin lowcode report mismatch: {scoped_data}")
            expect_status(
                404,
                f"{base_url}/api/projects/{other_project['id']}/lowcode/report",
                headers={"Cookie": dept_admin["cookie"]},
            )
            scoped_quality, _ = json_request(
                f"{base_url}/api/projects/{project['id']}/lowcode/template-quality",
                headers={"Cookie": dept_admin["cookie"]},
            )
            if scoped_quality["report"]["summary"]["total"] < 1:
                raise RuntimeError(f"department admin template quality empty: {scoped_quality}")
            expect_status(
                404,
                f"{base_url}/api/projects/{other_project['id']}/lowcode/template-quality",
                headers={"Cookie": dept_admin["cookie"]},
            )
            print("lowcode_progress_report_ok=true")
        finally:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()


if __name__ == "__main__":
    main()
