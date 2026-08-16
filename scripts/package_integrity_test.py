import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PACKAGE_PATH = ROOT.parent / "expo-display-deploy.zip"

REQUIRED_FILES = [
    "启动展会系统.bat",
    "打包展会系统.bat",
    "运行门户质量检查.bat",
    "package_expo.py",
    "start_expo.py",
    "server.py",
    "expo.db",
    "README.md",
    "docs/portal-quality-gate.md",
    "scanner-agent/Txq_csharp_sdk.exe",
    "scanner-agent/Txq_csharp_sdk.exe.config",
    "scanner-agent/vbar.dll",
    "scripts/portal_quality_gate.py",
    "scripts/portal_logic_smoke_test.py",
    "scripts/frontend_csp_static_test.py",
    "scripts/package_integrity_test.py",
    "sucai/validate_blueprint.py",
    "static/admin.html",
    "static/admin.js",
    "static/admin.css",
    "static/blueprint/index.html",
    "static/blueprint/blueprint.js",
    "static/blueprint/blueprint.css",
    "static/display.html",
    "static/display.js",
    "static/login.html",
    "static/login.js",
]

REQUIRED_PREFIXES = [
    "uploads/",
    "static/blueprint/data/departments/",
    "static/blueprint/data/topics/",
]

FORBIDDEN_PARTS = [
    "__pycache__",
    ".playwright-cli/",
    "output/playwright/",
    ".backup-",
    "data.backup-",
    "blueprint.backup-",
]


def main():
    if not PACKAGE_PATH.exists():
        print(f"package_integrity_ok=false missing package {PACKAGE_PATH}")
        raise SystemExit(1)

    with zipfile.ZipFile(PACKAGE_PATH) as archive:
        entries = {item.filename for item in archive.infolist() if not item.is_dir()}

    missing = [item for item in REQUIRED_FILES if item not in entries]
    missing_prefixes = [prefix for prefix in REQUIRED_PREFIXES if not any(item.startswith(prefix) for item in entries)]
    forbidden = sorted(item for item in entries if any(part in item for part in FORBIDDEN_PARTS))

    if missing or missing_prefixes or forbidden:
        print("package_integrity_ok=false")
        for item in missing:
            print(f" - missing file: {item}")
        for prefix in missing_prefixes:
            print(f" - missing content under: {prefix}")
        for item in forbidden[:20]:
            print(f" - forbidden artifact: {item}")
        raise SystemExit(1)

    print(f"package_entries={len(entries)}")
    print("package_integrity_ok=true")


if __name__ == "__main__":
    main()
