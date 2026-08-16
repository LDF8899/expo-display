from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ADMIN_HTML = ROOT / "static" / "admin.html"
ADMIN_JS = ROOT / "static" / "admin.js"


def main():
    html = ADMIN_HTML.read_text(encoding="utf-8")
    js = ADMIN_JS.read_text(encoding="utf-8")
    checks = {
        "export button": 'id="exportLowcodeTemplateQuality"' in html,
        "export function": "function exportLowcodeTemplateQualityCsv()" in js,
        "button listener": '$("exportLowcodeTemplateQuality").addEventListener("click", exportLowcodeTemplateQualityCsv)' in js,
        "report source": "state.lowcodeTemplateQualityReport?.entries" in js,
        "csv filename": "资料采集模板质量" in js,
        "issue columns": '"问题级别", "问题标题", "问题说明", "整改建议"' in js,
    }
    missing = [name for name, ok in checks.items() if not ok]
    if missing:
        raise RuntimeError(f"lowcode template quality export missing: {', '.join(missing)}")
    print("lowcode_template_quality_export_static_ok=true")


if __name__ == "__main__":
    main()
