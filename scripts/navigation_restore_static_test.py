from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
BLUEPRINT_JS = ROOT / "static" / "blueprint" / "blueprint.js"
BLUEPRINT_HTML = ROOT / "static" / "blueprint" / "index.html"
ADMIN_HTML = ROOT / "static" / "admin.html"
ADMIN_JS = ROOT / "static" / "admin.js"


def main():
    blueprint_js = BLUEPRINT_JS.read_text(encoding="utf-8")
    blueprint_html = BLUEPRINT_HTML.read_text(encoding="utf-8")
    admin_html = ADMIN_HTML.read_text(encoding="utf-8")
    admin_js = ADMIN_JS.read_text(encoding="utf-8")

    internal_blank_patterns = [
        'href="/departments" target="_blank"',
        'href="/display" target="_blank"',
        'target="_blank" href="/display',
        'target="_blank" href="${buildQrUrl',
        'target="_blank" rel="noopener" href="${escapeHtml(portalPreviewUrl',
    ]
    checks = {
        "unity same tab": "window.location.assign(url)" in blueprint_js,
        "pagehide cleanup": 'window.addEventListener("pagehide"' in blueprint_js
        and "stopTopicMediaCarousels()" in blueprint_js
        and "stopDrawerAutoLoop()" in blueprint_js,
        "pageshow restore": 'window.addEventListener("pageshow"' in blueprint_js
        and "restoreRouteFromCache" in blueprint_js
        and "event.persisted" in blueprint_js,
        "blueprint cache bust": "design-20260805e" in blueprint_html,
        "admin cache bust": "nav-restore-20260805a" in admin_html,
        "no internal blank": not any(pattern in admin_html or pattern in admin_js for pattern in internal_blank_patterns),
    }
    missing = [name for name, ok in checks.items() if not ok]
    if missing:
        raise RuntimeError(f"navigation restore checks failed: {', '.join(missing)}")
    print("navigation_restore_static_ok=true")


if __name__ == "__main__":
    main()
