import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import server  # noqa: E402


ADMIN_JS = ROOT / "static" / "admin.js"

EXPECTED_REQUIRED = {
    "article": {"bodyText"},
    "person": {"personName", "identity", "story"},
    "activity": {"eventDate", "outcome"},
    "honor": {"honorName", "year", "recipient", "value"},
    "achievement": {"achievementName", "value"},
    "scene": {"sceneName", "positioning", "application"},
    "video": {"videoUrl", "intro"},
    "attachment": {"fileTitle", "fileUrl", "fileIntro"},
}


def server_required_keys(content_type):
    fields = server.LOWCODE_META_FIELDS.get(content_type) or []
    return {field["key"] for field in fields if field.get("required")}


def admin_template_row(text, key):
    match = re.search(rf'\["{re.escape(key)}"\s*,[^\n\]]+\]', text)
    return match.group(0) if match else ""


def main():
    admin_text = ADMIN_JS.read_text(encoding="utf-8", errors="replace")
    failures = []

    for content_type, expected in EXPECTED_REQUIRED.items():
        actual = server_required_keys(content_type)
        missing = sorted(expected - actual)
        if missing:
            failures.append(f"server {content_type} missing required fields: {', '.join(missing)}")

        for key in sorted(expected):
            row = admin_template_row(admin_text, key)
            if not row:
                failures.append(f"admin lowcodeMetaFieldTemplates missing {key}")
            elif not row.rstrip().endswith(", true]"):
                failures.append(f"admin {key} should be required: {row}")

    if "forEach(([key, label, type, mapping, placeholder, maxLength, required])" not in admin_text:
        failures.append("admin lowcodeStandardFields should read the required flag from meta templates")
    if 'maxLength, !!required)' not in admin_text:
        failures.append("admin lowcodeStandardFields should pass required=true into generated fields")

    forms = server.builtin_lowcode_forms()
    for form in forms:
        schema = form.get("schema") or {}
        content_type = form.get("targetContentType")
        expected = EXPECTED_REQUIRED.get(content_type, set())
        if not expected:
            continue
        form_required = {field.get("key") for field in schema.get("fields", []) if field.get("required")}
        missing = sorted(expected - form_required)
        if missing:
            failures.append(f"builtin form {form.get('code')} missing required fields: {', '.join(missing)}")

    if failures:
        print("lowcode_required_fields_static_ok=false")
        for item in failures:
            print(" -", item)
        raise SystemExit(1)

    print("lowcode_required_fields_static_ok=true")


if __name__ == "__main__":
    main()
