from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ADMIN_JS = ROOT / "static" / "admin.js"
ADMIN_CSS = ROOT / "static" / "admin.css"


def main():
    js = ADMIN_JS.read_text(encoding="utf-8")
    css = ADMIN_CSS.read_text(encoding="utf-8")
    checks = {
        "recent renderer": "function renderDashboardRecentUpdates(dashboard)" in js,
        "dashboard calls renderer": "const recentUpdatesHtml = renderDashboardRecentUpdates(data.dashboard || {})" in js,
        "recent projects": "dashboard.recentProjects || []" in js,
        "recent logs": "dashboard.logs || []" in js,
        "recent scans": "dashboard.recentScans || []" in js,
        "dashboard insertion": "${recentUpdatesHtml}" in js,
        "logs shortcut": "data-dashboard-logs" in js and "await showView(\"logs\")" in js,
        "project shortcut": "data-dashboard-pages=\"${project.id}\"" in js,
        "panel styles": ".dashboard-recent-panel" in css and ".dashboard-recent-grid" in css,
        "mobile layout": ".dashboard-recent-grid" in css,
    }
    missing = [name for name, ok in checks.items() if not ok]
    if missing:
        raise RuntimeError(f"dashboard recent updates missing: {', '.join(missing)}")
    print("dashboard_recent_updates_static_ok=true")


if __name__ == "__main__":
    main()
