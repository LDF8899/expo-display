from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ADMIN_JS = ROOT / "static" / "admin.js"
ADMIN_CSS = ROOT / "static" / "admin.css"


def main():
    js = ADMIN_JS.read_text(encoding="utf-8")
    css = ADMIN_CSS.read_text(encoding="utf-8")
    checks = {
        "visual renderer": "function renderDashboardVisualization(dashboard, portalRows)" in js,
        "dashboard calls renderer": "const visualizationHtml = renderDashboardVisualization(data.dashboard || {}, portalRows)" in js,
        "dashboard insertion": "${visualizationHtml}" in js,
        "donut renderer": "function renderDashboardDonut(title, value, total, caption" in js,
        "stacked renderer": "function renderDashboardStackedChart(title, segments, caption)" in js,
        "bar renderer": "function renderDashboardBarChart(title, items, caption)" in js,
        "uses categories": "dashboard.categories || []" in js,
        "uses lowcode stats": "row.lowcodeStats || {}" in js,
        "panel styles": ".dashboard-visual-panel" in css and ".dashboard-chart-grid" in css,
        "chart styles": ".dashboard-donut" in css and ".dashboard-bar-row" in css and ".dashboard-stacked-bar" in css,
        "mobile layout": ".dashboard-chart-grid" in css,
    }
    missing = [name for name, ok in checks.items() if not ok]
    if missing:
        raise RuntimeError(f"dashboard visualization missing: {', '.join(missing)}")
    print("dashboard_visualization_static_ok=true")


if __name__ == "__main__":
    main()
