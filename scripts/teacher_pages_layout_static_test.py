from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ADMIN_HTML = ROOT / "static" / "admin.html"
ADMIN_JS = ROOT / "static" / "admin.js"


def main():
    html = ADMIN_HTML.read_text(encoding="utf-8")
    js = ADMIN_JS.read_text(encoding="utf-8")
    checks = {
        "legacy table id": 'id="legacyPagesTableWrap"' in html,
        "layout function": "function syncTeacherPagesLayout()" in js,
        "teacher role check": "const teacherOnly = isTeacherPortal();" in js,
        "hide content quality": '".content-quality-panel"' in js,
        "hide lowcode reports": '".lowcode-report-panel"' in js,
        "hide structured editor": '".structured-panel"' in js,
        "hide legacy table": '"#legacyPagesTableWrap"' in js,
        "hide manual entry": '"newPage", "newLegacyPage", "pageStatusFilter"' in js,
        "hide exports": '"exportModuleCoverage", "exportModuleGaps"' in js,
        "render hook": "syncTeacherPagesLayout();" in js,
    }
    missing = [name for name, ok in checks.items() if not ok]
    if missing:
        raise RuntimeError(f"teacher pages layout missing: {', '.join(missing)}")
    print("teacher_pages_layout_static_ok=true")


if __name__ == "__main__":
    main()
