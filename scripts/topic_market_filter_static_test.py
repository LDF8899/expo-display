from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SERVER = ROOT / "server.py"
BLUEPRINT_JS = ROOT / "static" / "blueprint" / "blueprint.js"
DISPLAY_JS = ROOT / "static" / "display.js"
BLUEPRINT_HTML = ROOT / "static" / "blueprint" / "index.html"
DISPLAY_HTML = ROOT / "static" / "display.html"


def main():
    server = SERVER.read_text(encoding="utf-8")
    blueprint_js = BLUEPRINT_JS.read_text(encoding="utf-8")
    display_js = DISPLAY_JS.read_text(encoding="utf-8")
    blueprint_html = BLUEPRINT_HTML.read_text(encoding="utf-8")
    display_html = DISPLAY_HTML.read_text(encoding="utf-8")
    checks = {
        "server topic marker": "def achievement_market_topic_marker" in server and "marker in str(item.get(\"code\")" in server,
        "campus culture excluded": 'ACHIEVEMENT_MARKET_TOPIC_EXCLUDED = {"campus-culture"}' in server,
        "public topic query": 'topic_slug = (query.get("topic") or [""])[0]' in server and "public_achievement_market_payload(category_key, topic_slug)" in server,
        "portal payload includes market": '"achievementMarket": public_achievement_market_payload("", portal_slug) if portal_type == "topic" else None' in server,
        "topic carousel categories": "ACHIEVEMENT_MARKET_CATEGORIES" in blueprint_js and "renderTopicAchievementMarketCarousel" in blueprint_js,
        "carousel market jump": "data-market-url" in blueprint_js and "location.href = slide.dataset.marketUrl" in blueprint_js,
        "cover upload hook": "editSectionId: category.sectionId" in blueprint_js and "data-coverflow-edit" in blueprint_js,
        "display topic filter": 'initialParams.get("topic")' in display_js and "&topic=${encodeURIComponent(topicSlug)}" in display_js,
        "cache bust": "topic-market-entry-20260815" in blueprint_html and "topic-market-filter-20260815" in display_html,
    }
    missing = [name for name, ok in checks.items() if not ok]
    if missing:
        raise RuntimeError(f"topic market filter missing: {', '.join(missing)}")
    print("topic_market_filter_static_ok=true")


if __name__ == "__main__":
    main()
