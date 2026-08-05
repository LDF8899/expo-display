from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DISPLAY_CSS = ROOT / "static" / "display.css"


def main():
    css = DISPLAY_CSS.read_text(encoding="utf-8")
    checks = {
        "detail media uses grid": ".detail-media {\n  position: relative;\n  min-height: 0;\n  display: grid;" in css,
        "detail media reserves caption row": "grid-template-rows: minmax(0, 1fr) auto;" in css,
        "detail media has stable gap": "gap: clamp(18px, 2.2vh, 30px);" in css,
        "detail image constrained to media row": ".detail-media img {\n  position: relative;" in css and "max-height: 100%;" in css,
        "detail caption not absolute": ".detail-caption {\n  position: relative;" in css,
        "detail caption uses full width": "justify-self: stretch;" in css,
        "detail caption title bounded": ".detail-caption h2 {\n  max-width: 100%;" in css,
        "detail caption title responsive": "font-size: clamp(34px, 3.4vw, 58px);" in css,
        "detail caption title can wrap": "overflow-wrap: anywhere;" in css and "text-wrap: balance;" in css,
    }
    missing = [name for name, ok in checks.items() if not ok]
    if missing:
        raise RuntimeError(f"display detail layout guard missing: {', '.join(missing)}")
    print("display_detail_layout_static_ok=true")


if __name__ == "__main__":
    main()
