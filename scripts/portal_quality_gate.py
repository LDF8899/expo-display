import subprocess
import shutil
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def tooling_check():
    missing = []
    details = [f"python={sys.executable}"]
    for name in ("node", "npx"):
        path = shutil.which(name)
        if path:
            details.append(f"{name}={path}")
        else:
            missing.append(name)
    if missing:
        safe_print("Missing required command(s): " + ", ".join(missing), stream=sys.stderr)
        safe_print("Install Node.js/npm, then rerun this gate.", stream=sys.stderr)
        return 1, "\n".join(details)
    return 0, "\n".join(details)


CHECKS = [
    ("tooling", tooling_check),
    (
        "python_compile",
        [
            sys.executable,
            "-m",
            "py_compile",
            "package_expo.py",
            "server.py",
            "scripts/portal_logic_smoke_test.py",
            "scripts/frontend_csp_static_test.py",
            "scripts/blueprint_navigation_static_test.py",
            "scripts/topic_matrix_static_test.py",
            "scripts/lowcode_choice_render_static_test.py",
            "scripts/lowcode_required_fields_static_test.py",
            "scripts/dashboard_lowcode_todo_static_test.py",
            "scripts/dashboard_recent_updates_static_test.py",
            "scripts/review_status_filter_static_test.py",
            "scripts/lowcode_template_quality_export_static_test.py",
            "scripts/content_quality_report_test.py",
            "scripts/asset_archive_report_test.py",
            "scripts/lowcode_progress_report_test.py",
            "scripts/acceptance_report_test.py",
            "scripts/package_integrity_test.py",
        ],
    ),
    ("admin_js_syntax", ["node", "--check", "static/admin.js"]),
    ("blueprint_js_syntax", ["node", "--check", "static/blueprint/blueprint.js"]),
    ("blueprint_data", [sys.executable, "sucai/validate_blueprint.py"]),
    ("frontend_csp_static", [sys.executable, "scripts/frontend_csp_static_test.py"]),
    ("blueprint_navigation_static", [sys.executable, "scripts/blueprint_navigation_static_test.py"]),
    ("topic_matrix_static", [sys.executable, "scripts/topic_matrix_static_test.py"]),
    ("lowcode_choice_render_static", [sys.executable, "scripts/lowcode_choice_render_static_test.py"]),
    ("lowcode_required_fields_static", [sys.executable, "scripts/lowcode_required_fields_static_test.py"]),
    ("dashboard_lowcode_todo_static", [sys.executable, "scripts/dashboard_lowcode_todo_static_test.py"]),
    ("dashboard_recent_updates_static", [sys.executable, "scripts/dashboard_recent_updates_static_test.py"]),
    ("review_status_filter_static", [sys.executable, "scripts/review_status_filter_static_test.py"]),
    ("lowcode_template_quality_export_static", [sys.executable, "scripts/lowcode_template_quality_export_static_test.py"]),
    ("content_quality_report", [sys.executable, "scripts/content_quality_report_test.py"]),
    ("asset_archive_report", [sys.executable, "scripts/asset_archive_report_test.py"]),
    ("lowcode_progress_report", [sys.executable, "scripts/lowcode_progress_report_test.py"]),
    ("acceptance_report", [sys.executable, "scripts/acceptance_report_test.py"]),
    ("portal_logic_smoke", [sys.executable, "scripts/portal_logic_smoke_test.py"]),
    ("package_integrity", [sys.executable, "scripts/package_integrity_test.py"]),
]


def safe_print(text, *, stream=None):
    stream = stream or sys.stdout
    try:
        print(text, file=stream)
    except UnicodeEncodeError:
        encoding = getattr(stream, "encoding", None) or "utf-8"
        safe_text = text.encode(encoding, errors="replace").decode(encoding, errors="replace")
        print(safe_text, file=stream)


def run_check(name, command):
    started = time.perf_counter()
    safe_print(f"== {name} ==")
    if callable(command):
        returncode, output = command()
        stdout = output or ""
        stderr = ""
    else:
        result = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
        )
        returncode = result.returncode
        stdout = result.stdout
        stderr = result.stderr
    elapsed = time.perf_counter() - started
    if stdout.strip():
        safe_print(stdout.strip())
    if stderr.strip():
        safe_print(stderr.strip(), stream=sys.stderr)
    safe_print(f"{name}_ok={returncode == 0} elapsed={elapsed:.1f}s")
    if returncode != 0:
        raise SystemExit(returncode)


def main():
    total_started = time.perf_counter()
    for name, command in CHECKS:
        run_check(name, command)
    safe_print(f"portal_quality_gate_ok=true elapsed={time.perf_counter() - total_started:.1f}s")


if __name__ == "__main__":
    main()
