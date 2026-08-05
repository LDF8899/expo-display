from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ADMIN_HTML = ROOT / "static" / "admin.html"
ADMIN_JS = ROOT / "static" / "admin.js"
ADMIN_CSS = ROOT / "static" / "admin.css"
SERVER = ROOT / "server.py"
MYSQL_SCHEMA = ROOT / "database" / "mysql_schema.sql"


def main():
    html = ADMIN_HTML.read_text(encoding="utf-8")
    js = ADMIN_JS.read_text(encoding="utf-8")
    css = ADMIN_CSS.read_text(encoding="utf-8")
    server = SERVER.read_text(encoding="utf-8")
    mysql_schema = MYSQL_SCHEMA.read_text(encoding="utf-8")
    checks = {
        "list state": "const listState = {" in js,
        "pager helper": "function renderPager(containerId, key, total" in js,
        "filter helper": "function bindListFilters(ids, key, render)" in js,
        "pager click handler": "data-list-page" in js and "const renderers = {" in js,
        "user controls": 'id="userSearch"' in html and 'id="userRoleFilter"' in html,
        "project controls": 'id="projectSearch"' in html and 'id="projectPublishFilter"' in html,
        "page controls": 'id="pageSearch"' in html and 'id="pageModuleFilter"' in html,
        "asset controls": 'id="assetSearch"' in html and 'id="assetTypeFilter"' in html,
        "review controls": 'id="reviewSearch"' in html and 'id="reviewsPager"' in html,
        "deploy controls": 'id="deployPageSearch"' in html and "deploySelectedPageIds" in js,
        "log pager": 'id="logsPager"' in html,
        "pager styles": ".list-pager" in css and ".list-controls" in css,
        "publish fields sqlite": "deployed_at TEXT NOT NULL DEFAULT ''" in server and "content_deployed_at TEXT NOT NULL DEFAULT ''" in server,
        "publish fields mysql": "deployed_at VARCHAR(40) NOT NULL DEFAULT ''" in mysql_schema and "content_deployed_at VARCHAR(40) NOT NULL DEFAULT ''" in mysql_schema,
        "deploy writes time": "deployed_at = CASE WHEN id = ? THEN ?" in server and "content_deployed_at = CASE WHEN id = ? THEN ?" in server,
        "deploy page records": "def deployed_page_records(project_id):" in server and '"records": deployed_page_records(project_id)' in server,
        "project payload times": '"deployedAt": deployed_at or ""' in server and '"contentDeployedAt": content_deployed_at or ""' in server,
        "frontend time display": "欢迎页发布时间" in js and "资料发布时间" in js and "已发布于" in js,
    }
    missing = [name for name, ok in checks.items() if not ok]
    if missing:
        raise RuntimeError(f"admin list management missing: {', '.join(missing)}")
    print("admin_list_management_static_ok=true")


if __name__ == "__main__":
    main()
