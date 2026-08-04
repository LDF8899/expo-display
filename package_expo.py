import shutil
import sqlite3
import sys
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PACKAGE_PATH = ROOT.parent / "expo-display-deploy.zip"

PACKAGE_ITEMS = [
    "启动展会系统.bat",
    "打包展会系统.bat",
    "运行门户质量检查.bat",
    "package_expo.py",
    "start_expo.py",
    "server.py",
    "expo.db",
    "static",
    "uploads",
    "scanner-agent",
    "scripts/portal_quality_gate.py",
    "scripts/portal_logic_smoke_test.py",
    "scripts/frontend_csp_static_test.py",
    "scripts/package_integrity_test.py",
    "sucai/validate_blueprint.py",
    "README.md",
    "docs/portal-quality-gate.md",
    "现场启动说明.md",
    "打包部署说明.md",
    "硬件调用接口说明.md",
    "前端设计说明.md",
    "开发记录.md",
]

PACKAGE_IGNORE_PATTERNS = [
    "__pycache__",
    "*.pyc",
    "*.backup-*",
    "data.backup-*",
    "blueprint.backup-*",
]


def copy_database(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    source = sqlite3.connect(src)
    try:
        target = sqlite3.connect(dst)
        try:
            source.backup(target)
        finally:
            target.close()
    finally:
        source.close()


def copy_item(name, target_root):
    src = ROOT / name
    dst = target_root / name
    if not src.exists():
        return

    if src.name == "expo.db":
        copy_database(src, dst)
        return

    if src.is_dir():
        shutil.copytree(src, dst, ignore=shutil.ignore_patterns(*PACKAGE_IGNORE_PATTERNS))
        return

    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def build_zip(source_root):
    if PACKAGE_PATH.exists():
        PACKAGE_PATH.unlink()
    with zipfile.ZipFile(PACKAGE_PATH, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in source_root.rglob("*"):
            if path.is_file():
                archive.write(path, path.relative_to(source_root))


def main():
    with tempfile.TemporaryDirectory(prefix="expo-display-package-") as tmp:
        package_root = Path(tmp) / "expo-display"
        package_root.mkdir()
        for item in PACKAGE_ITEMS:
            copy_item(item, package_root)
        build_zip(package_root)
    print(f"Package completed: {PACKAGE_PATH}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Package failed: {exc}", file=sys.stderr)
        sys.exit(1)
