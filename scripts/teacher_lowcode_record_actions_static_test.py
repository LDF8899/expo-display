from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ADMIN_JS = ROOT / "static" / "admin.js"


def main():
    js = ADMIN_JS.read_text(encoding="utf-8")
    checks = {
        "record renderer teacher flag": "const teacherOnly = isTeacherPortal();" in js,
        "hide record exports": '["exportLowcodeRecords", "exportLowcodeRecordDetails"]' in js,
        "generated edit hidden": "record.contentItemId && !teacherOnly" in js,
        "teacher click guard": "if (edit && isTeacherPortal()) return;" in js,
        "draft resume remains": 'status === "draft" ? `<button class="button small primary" type="button" data-lowcode-record-resume=' in js,
        "rejected resume remains": 'status === "rejected" ? `<button class="button small primary" type="button" data-lowcode-record-resume=' in js,
        "approved preview remains": 'record.previewUrl && status === "approved"' in js,
    }
    missing = [name for name, ok in checks.items() if not ok]
    if missing:
        raise RuntimeError(f"teacher lowcode record actions missing: {', '.join(missing)}")
    print("teacher_lowcode_record_actions_static_ok=true")


if __name__ == "__main__":
    main()
