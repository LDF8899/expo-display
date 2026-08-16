from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ADMIN_JS = ROOT / "static" / "admin.js"


MANAGEMENT_ENDPOINTS = [
    "/content-items`)",
    "/content-quality`)",
    "/asset-archive`)",
    "/lowcode/report`)",
    "/lowcode/template-quality`)",
]


def main():
    js = ADMIN_JS.read_text(encoding="utf-8")
    checks = {
        "management flag": "const loadManagementReports = canReview();" in js,
        "content items conditional": "loadManagementReports ? jsonApi(`/api/projects/${projectId}/content-items`) : Promise.resolve({ items: [] })" in js,
        "content quality conditional": "loadManagementReports ? jsonApi(`/api/projects/${projectId}/content-quality`) : Promise.resolve({ report: null })" in js,
        "asset archive conditional": "loadManagementReports ? jsonApi(`/api/projects/${projectId}/asset-archive`) : Promise.resolve({ report: null })" in js,
        "lowcode report conditional": "loadManagementReports ? jsonApi(`/api/projects/${projectId}/lowcode/report`) : Promise.resolve({ report: null })" in js,
        "template quality conditional": "loadManagementReports ? jsonApi(`/api/projects/${projectId}/lowcode/template-quality`) : Promise.resolve({ report: null })" in js,
        "teacher still loads forms": "jsonApi(`/api/projects/${projectId}/lowcode/forms`)" in js,
        "teacher still loads records": "jsonApi(`/api/projects/${projectId}/lowcode/records`)" in js,
    }
    missing = [name for name, ok in checks.items() if not ok]
    if missing:
        raise RuntimeError(f"teacher report fetch guard missing: {', '.join(missing)}")
    print("teacher_report_fetch_static_ok=true")


if __name__ == "__main__":
    main()
