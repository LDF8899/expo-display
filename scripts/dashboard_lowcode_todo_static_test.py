from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ADMIN_JS = ROOT / "static" / "admin.js"
ADMIN_CSS = ROOT / "static" / "admin.css"


def main():
    js = ADMIN_JS.read_text(encoding="utf-8")
    css = ADMIN_CSS.read_text(encoding="utf-8")
    checks = {
        "todo renderer": "function renderDashboardLowcodeTodos(rows)" in js,
        "dashboard calls renderer": "const lowcodeTodoHtml = renderDashboardLowcodeTodos(portalRows)" in js,
        "uses lowcode report reminders": "row.lowcodeReport?.groups?.reminders" in js,
        "fetches project lowcode report": "jsonApi(`/api/projects/${project.id}/lowcode/report`)" in js,
        "click target": "data-dashboard-lowcode-records" in js,
        "status filter handoff": "state.lowcodeRecordStatusFilter = lowcodeRecords.dataset.dashboardLowcodeStatus || \"all\"" in js,
        "record filter sync": "$(\"lowcodeRecordStatusFilter\").value = state.lowcodeRecordStatusFilter || \"all\"" in js,
        "panel styles": ".dashboard-lowcode-panel" in css and ".dashboard-lowcode-todo" in css,
        "mobile layout": ".dashboard-lowcode-todo," in css,
    }
    missing = [name for name, ok in checks.items() if not ok]
    if missing:
        raise RuntimeError(f"dashboard lowcode todo missing: {', '.join(missing)}")
    print("dashboard_lowcode_todo_static_ok=true")


if __name__ == "__main__":
    main()
