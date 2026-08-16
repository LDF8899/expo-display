from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
BLUEPRINT_HTML = ROOT / "static" / "blueprint" / "index.html"
BLUEPRINT_CSS = ROOT / "static" / "blueprint" / "blueprint.css"


def main():
    html = BLUEPRINT_HTML.read_text(encoding="utf-8")
    css = BLUEPRINT_CSS.read_text(encoding="utf-8")
    logo_block = css.split(".brand-logo {", 1)[1].split("}", 1)[0]
    checks = {
        "cache bust": "blueprint.css?v=design-20260811f" in html and "blueprint.js?v=design-20260811f" in html,
        "logo scales to display visual size": "max-height: 90px;" in logo_block and "flex: 0 0 540px;" in logo_block,
        "logo contains full width": "width: min(540px, 100%);" in logo_block,
        "logo no circle crop": "border-radius" not in logo_block and "width: 82px;" not in logo_block and "height: 82px;" not in logo_block,
        "home brand column reserved": "grid-template-columns: minmax(540px, 0.92fr)" in css,
        "detail brand column reserved": ".detail-bar {\n  grid-template-columns: auto minmax(540px, 0.92fr)" in css,
        "compact logo still horizontal": ".brand-lockup.compact .brand-logo" in css and "flex-basis: 540px;" in css,
        "department mode logo still horizontal": ".department-showcase-mode > .topbar .brand-logo" in css and "flex-basis: 540px;" in css and "max-height: 90px;" in css,
    }
    missing = [name for name, ok in checks.items() if not ok]
    if missing:
        raise RuntimeError(f"blueprint logo layout missing: {', '.join(missing)}")
    print("blueprint_logo_layout_static_ok=true")


if __name__ == "__main__":
    main()
