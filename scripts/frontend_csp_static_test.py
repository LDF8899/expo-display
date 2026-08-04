import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
STATIC_DIR = ROOT / "static"

HTML_INLINE_SCRIPT = re.compile(r"<script(?![^>]*\bsrc=)[^>]*>", re.IGNORECASE)
INLINE_EVENT = re.compile(r"\s(on[a-z]+)\s*=", re.IGNORECASE)
JAVASCRIPT_URL = re.compile(r"\b(?:href|src)\s*=\s*(['\"])\s*javascript:", re.IGNORECASE)
UNSAFE_INLINE = re.compile(r"unsafe-inline", re.IGNORECASE)
STATIC_ASSET_VERSION = re.compile(r"""<(?:link|script)\b[^>]*(?:href|src)=["'](?P<url>/static/[^"']+\.(?:css|js))\?v=(?P<version>[^"']+)["']""", re.IGNORECASE)
STATIC_ASSET_REF = re.compile(r"""<(?:link|script)\b[^>]*(?:href|src)=["'](?P<url>/static/[^"']+\.(?:css|js)(?:\?[^"']*)?)["']""", re.IGNORECASE)

CHECKED_EXTENSIONS = {".html", ".js", ".css"}
SKIP_FILES = {
    STATIC_DIR / "sample.svg",
}


def line_for(text, index):
    return text.count("\n", 0, index) + 1


def check_file(path):
    text = path.read_text(encoding="utf-8", errors="replace")
    errors = []

    if path.suffix.lower() == ".html":
        for match in HTML_INLINE_SCRIPT.finditer(text):
            errors.append((line_for(text, match.start()), "inline <script> is blocked by script-src 'self'"))
        for match in INLINE_EVENT.finditer(text):
            errors.append((line_for(text, match.start()), f"inline event handler {match.group(1)} is blocked by script-src 'self'"))
        for match in JAVASCRIPT_URL.finditer(text):
            errors.append((line_for(text, match.start()), "javascript: URL is not allowed"))
        for match in STATIC_ASSET_REF.finditer(text):
            if "?v=" not in match.group("url"):
                errors.append((line_for(text, match.start()), "static CSS/JS asset should include a cache version (?v=...)"))
        versions_by_group = {}
        for match in STATIC_ASSET_VERSION.finditer(text):
            url = match.group("url")
            version = match.group("version")
            if url.startswith("/static/blueprint/"):
                group = "blueprint"
            else:
                group = url.rsplit("/", 1)[-1].split(".", 1)[0]
            versions_by_group.setdefault(group, set()).add(version)
        for group, versions in versions_by_group.items():
            if len(versions) > 1:
                errors.append((1, f"{group} static assets should share one cache version"))

    if path.suffix.lower() == ".css":
        for match in UNSAFE_INLINE.finditer(text):
            errors.append((line_for(text, match.start()), "CSS should not relax CSP with unsafe-inline"))

    return errors


def main():
    failures = []
    checked = 0
    for path in sorted(STATIC_DIR.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in CHECKED_EXTENSIONS:
            continue
        if path in SKIP_FILES:
            continue
        checked += 1
        for line, message in check_file(path):
            failures.append(f"{path.relative_to(ROOT)}:{line}: {message}")

    if failures:
        print("frontend_csp_static_ok=false")
        for item in failures:
            print(" -", item)
        sys.exit(1)

    print(f"frontend_csp_static_checked={checked}")
    print("frontend_csp_static_ok=true")


if __name__ == "__main__":
    main()
