from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ADMIN_HTML = ROOT / "static" / "admin.html"
ADMIN_JS = ROOT / "static" / "admin.js"
ADMIN_CSS = ROOT / "static" / "admin.css"
SERVER = ROOT / "server.py"
DISPLAY_JS = ROOT / "static" / "display.js"
DISPLAY_CSS = ROOT / "static" / "display.css"


def main():
    html = ADMIN_HTML.read_text(encoding="utf-8")
    js = ADMIN_JS.read_text(encoding="utf-8")
    css = ADMIN_CSS.read_text(encoding="utf-8")
    server = SERVER.read_text(encoding="utf-8")
    display_js = DISPLAY_JS.read_text(encoding="utf-8")
    display_css = DISPLAY_CSS.read_text(encoding="utf-8")
    checks = {
        "market overview": 'id="marketOverview"' in html and 'id="marketCategoryGrid"' in html,
        "visual edit entry": 'class="market-entry market-welcome-entry" href="/display?edit=1"' in html and "可视化编辑" in html,
        "welcome workspace": 'id="marketWelcomeWorkspace"' in html and 'id="marketWelcomeImageFile"' in html,
        "category workspace": 'id="marketCategoryWorkspace"' in html and 'id="openMarketCreate"' in html,
        "create modal": 'id="marketCreatePanel"' in html and 'id="createMarketItem"' in html,
        "rich text detail": 'id="marketItemEditorPanel"' in html and 'id="marketRichBody"' in html,
        "detail visual edit entry": "detailEditUrl" in js and "edit=1&marketItem=" in js,
        "five categories": all(label in js for label in ["名师名匠", "优秀校友", "优秀学生", "创新成果", "荣誉资质"]),
        "workspace routing": "function openMarketWorkspace(workspace, categoryKey" in js and "syncMarketAdminUrl" in js,
        "direct image upload": "bindMarketImageUpload" in js and "uploadMarketWelcomeImage" in js,
        "carousel editor": 'id="marketCarouselList"' in html and 'id="marketCarouselImageFiles"' in html,
        "carousel controls": "addMarketCarouselImage" in js and "data-market-carousel-action" in js,
        "carousel persistence": "welcome_carousel_json" in server and '"welcomeCarouselImages"' in server,
        "carousel text persistence": '"welcomeCarouselSlides"' in server and 'config["welcomeCarouselSlides"]' in server,
        "display welcome binding": "function applyMarketWelcomeConfig" in display_js and "welcomeCarouselImages" in display_js,
        "display inline edit auth": 'initialParams.get("edit") === "1"' in display_js and 'displayEditApi("/api/session")' in display_js,
        "display inline image editing": all(name in display_js for name in ["更换左侧大图", "添加轮播图", "carousel-replace", "data-display-slide-action"]),
        "display inline slide text": "dataset.displayEditText" in display_js and "customText" in display_js and "可留空" in display_js,
        "display inline hero text": all(field in display_js for field in ["顶部标识（可留空）", "左侧主标题（可留空）", "左侧文字说明（可留空）"]),
        "detail inline editor": all(name in display_js for name in ["function initDetailEdit", "function saveDetailEdits", "data-detail-upload-body", "detail-edit-cover-tools"]),
        "detail image transform": '"imageTransform"' in server and "image_transform_json" in server and "scale(2.5)" not in display_js,
        "detail category theme payload": '"marketCategoryKey"' in server and "market_category_key" in server,
        "detail category theme binding": "function marketThemeForContent" in display_js and "applyDetailMarketTheme(page)" in display_js,
        "detail category theme styling": "--detail-theme" in display_css and "color-mix(in srgb, var(--detail-theme)" in display_css,
        "management dashboard payload": '"management"' in server and '"achievementMarket"' in server and '"contentItems"' in server,
        "management dashboard layout": "dashboard-command-hero" in js and "dashboard-kpi-grid" in css and "renderDashboardModuleOverview" in js,
        "management dashboard navigation": "data-dashboard-view" in js and "viewButton.dataset.dashboardView" in js,
        "display inline save": 'displayEditApi("/api/achievement-market/config"' in display_js and "X-CSRF-Token" in display_js,
        "display inline styling": ".display-edit-toolbar" in display_css and ".display-edit-slide-controls" in display_css,
        "responsive category grid": ".market-category-grid" in css and "grid-template-columns: 1fr" in css,
    }
    missing = [name for name, ok in checks.items() if not ok]
    if missing:
        raise RuntimeError(f"achievement market admin missing: {', '.join(missing)}")
    print("achievement_market_admin_static_ok=true")


if __name__ == "__main__":
    main()
