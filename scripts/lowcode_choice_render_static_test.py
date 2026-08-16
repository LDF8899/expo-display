from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ADMIN_JS = ROOT / "static" / "admin.js"


def main():
    text = ADMIN_JS.read_text(encoding="utf-8")
    if '(!rawValue && index === 0)' in text:
        raise RuntimeError("optional radio fields still auto-select the first option")
    if 'field.required ? "请选择" : "不选择"' not in text:
        raise RuntimeError("select fields should render an explicit empty option")
    if 'field.required ? "required" : ""' not in text:
        raise RuntimeError("required radio groups should use browser required validation")
    print("lowcode_choice_render_static_ok=true")


if __name__ == "__main__":
    main()
