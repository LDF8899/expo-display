from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ADMIN_HTML = ROOT / "static" / "admin.html"
ADMIN_JS = ROOT / "static" / "admin.js"


def main():
    html = ADMIN_HTML.read_text(encoding="utf-8")
    js = ADMIN_JS.read_text(encoding="utf-8")
    checks = {
        "import button": 'id="importLowcodeTemplate"' in html,
        "import file input": 'id="lowcodeTemplateImportFile"' in html,
        "json accept": 'accept="application/json,.json"' in html,
        "import check panel": 'id="lowcodeTemplateImportCheck"' in html,
        "import check summary": 'id="lowcodeTemplateImportCheckSummary"' in html,
        "import check issues": 'id="lowcodeTemplateImportIssues"' in html,
        "export action button": 'data-lowcode-export="${form.id}"' in js,
        "export payload": "function lowcodeTemplateJsonPayload(form)" in js,
        "export function": "function exportLowcodeTemplateJson(form)" in js,
        "export extension": ".lowcode-template.json" in js,
        "import sanitizer": "function safeImportedLowcodeTemplate(" in js,
        "import summary": "function lowcodeTemplateImportSummary(form)" in js,
        "import summary required": "requiredCount" in js,
        "import summary mapping": "mappedCount" in js,
        "import check renderer": "function renderLowcodeTemplateImportCheck(summary)" in js,
        "import function": "function importLowcodeTemplateJson(file)" in js,
        "import fills form": "fillLowcodeTemplateForm(form);" in js,
        "import renders check": "renderLowcodeTemplateImportCheck(summary);" in js,
        "import button listener": '$("importLowcodeTemplate").addEventListener("click", () => $("lowcodeTemplateImportFile").click())' in js,
        "import file listener": '$("lowcodeTemplateImportFile").addEventListener("change", (event) => importLowcodeTemplateJson(event.target.files[0]))' in js,
        "admin only import": '$("importLowcodeTemplate").hidden = !isAdmin()' in js,
        "admin only export": '${isAdmin() ? `<button class="button small" type="button" data-lowcode-edit=' in js and 'data-lowcode-export="${form.id}"' in js,
    }
    missing = [name for name, ok in checks.items() if not ok]
    if missing:
        raise RuntimeError(f"lowcode template import/export missing: {', '.join(missing)}")
    print("lowcode_template_import_export_static_ok=true")


if __name__ == "__main__":
    main()
