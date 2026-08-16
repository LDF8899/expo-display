from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ADMIN_JS = ROOT / "static" / "admin.js"


def main():
    js = ADMIN_JS.read_text(encoding="utf-8")
    checks = {
        "quality flag uses reviewer permission": "const showTemplateQuality = canReview();" in js,
        "new template admin only": '$("newLowcodeTemplate").hidden = !isAdmin()' in js,
        "import template admin only": '$("importLowcodeTemplate").hidden = !isAdmin()' in js,
        "quality export reviewer only": '$("exportLowcodeTemplateQuality").hidden = !showTemplateQuality' in js,
        "quality line conditional": '${showTemplateQuality ? `<p class="lowcode-form-quality' in js,
        "template edit admin only": '${isAdmin() ? `<button class="button small" type="button" data-lowcode-edit=' in js,
        "teacher fill entry remains": 'data-lowcode-start="${form.id}"' in js,
    }
    missing = [name for name, ok in checks.items() if not ok]
    if missing:
        raise RuntimeError(f"teacher lowcode simplification missing: {', '.join(missing)}")
    print("teacher_lowcode_simplified_static_ok=true")


if __name__ == "__main__":
    main()
