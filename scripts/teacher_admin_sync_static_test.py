from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ADMIN_HTML = ROOT / "static" / "admin.html"
ADMIN_JS = ROOT / "static" / "admin.js"
SERVER = ROOT / "server.py"
BLUEPRINT_JS = ROOT / "static" / "blueprint" / "blueprint.js"
BLUEPRINT_HTML = ROOT / "static" / "blueprint" / "index.html"


def main():
    html = ADMIN_HTML.read_text(encoding="utf-8")
    js = ADMIN_JS.read_text(encoding="utf-8")
    server = SERVER.read_text(encoding="utf-8")
    blueprint_js = BLUEPRINT_JS.read_text(encoding="utf-8")
    blueprint_html = BLUEPRINT_HTML.read_text(encoding="utf-8")

    checks = {
        "teacher asset nav copy": 'assets: ["素材中心"' in js and "安装包" in js and "下载" in js,
        "teacher batch file upload": all(token in html for token in [
            'id="lowcodeAssetFile" type="file" multiple',
            'id="contentAssetFile" type="file" multiple',
            'id="assetFile" type="file" multiple',
        ]),
        "asset downloads": "function assetDownloadUrl(asset)" in js and ">下载</a>" in js,
        "digital resource module": '{ key: "media", label: "数字资源"' in js and '"label": "数字资源"' in server,
        "resource module compatibility": "function normalizeModuleKeyForPortal" in js and "def normalize_module_key_for_portal" in server,
        "single digital resource button": 'data-template="media">数字资源</button>' in html and 'data-template="resources"' not in html,
        "topic systems for every page": "function topicUsesSingleSystemsEntry" in blueprint_js and "return true;" in blueprint_js,
        "topic cache bust": "teacher-topic-sync-20260816" in blueprint_html,
        "teacher cache bust": "teacher-admin-sync-20260816" in html,
    }
    missing = [name for name, ok in checks.items() if not ok]
    if missing:
        raise RuntimeError(f"teacher admin sync missing: {', '.join(missing)}")
    print("teacher_admin_sync_static_ok=true")


if __name__ == "__main__":
    main()
