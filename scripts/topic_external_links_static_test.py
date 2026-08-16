from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SERVER = ROOT / "server.py"
ADMIN_JS = ROOT / "static" / "admin.js"
ADMIN_HTML = ROOT / "static" / "admin.html"
BLUEPRINT_JS = ROOT / "static" / "blueprint" / "blueprint.js"
BLUEPRINT_CSS = ROOT / "static" / "blueprint" / "blueprint.css"
BLUEPRINT_HTML = ROOT / "static" / "blueprint" / "index.html"


def main():
    server = SERVER.read_text(encoding="utf-8")
    admin_js = ADMIN_JS.read_text(encoding="utf-8")
    admin_html = ADMIN_HTML.read_text(encoding="utf-8")
    blueprint_js = BLUEPRINT_JS.read_text(encoding="utf-8")
    blueprint_css = BLUEPRINT_CSS.read_text(encoding="utf-8")
    blueprint_html = BLUEPRINT_HTML.read_text(encoding="utf-8")

    checks = {
        "admin role": '{ key: "external_link", label: "跳转按钮" }' in admin_js,
        "admin mapping": 'content_item.assets.external_link' in admin_js,
        "admin hint": "跳转地址" in admin_html,
        "server seed": "SPECIAL_EXPERIENCE_LINKS" in server and "EXT-DIGITAL-INTELLIGENCE-AI" in server,
        "server role": '"role": "external_link"' in server,
        "server no cover": 'asset.get("role") == "external_link"' in server,
        "frontend merge": "mergeExternalLinksFromContentItems" in blueprint_js,
        "frontend extractor": "externalLinksForContentItem" in blueprint_js,
        "frontend render": "renderTopicExperienceActions" in blueprint_js and "renderTopicExperienceMenu" in blueprint_js and "topic-experience-trigger" in blueprint_js,
        "frontend aggregate": "topicExternalLinks(data)" in blueprint_js and "renderTopicExperienceDock(data)" in blueprint_js,
        "frontend label aware dedupe": 'href + "\\n" + label' in blueprint_js,
        "frontend click guard": 'e.target.closest(".experience-link")' in blueprint_js,
        "frontend style": ".topic-showcase-actions" in blueprint_css and ".topic-experience-menu" in blueprint_css,
        "overview placement": "renderTopicExperienceActions(data)" in blueprint_js,
        "topic media title": 'if (section && section.id === "media") return "数字资源";' in blueprint_js,
        "topic single entry": "function topicUsesSingleSystemsEntry" in blueprint_js and "return true;" in blueprint_js and "topicUsesSingleSystemsEntry(data) ? []" in blueprint_js,
        "topic subpage placement": "renderTopicExperienceActions(data)" in blueprint_js and 'isDigitalTourismTopic(data) ? renderTopicExperienceActions(data) : ""' not in blueprint_js,
        "subpage removal": "renderExperienceLinks(model.externalLinks" not in blueprint_js and "renderExperienceLinks(section.externalLinks" not in blueprint_js,
        "cache bust": "teacher-topic-sync-20260816" in blueprint_html,
        "provided urls": all(
            url in server
            for url in [
                "http://sxjsxy.szzfhs.com/#/AigcApply",
                "http://bjsz.szzfhs.com/bjlvh5",
                "http://bjsz.szzfhs.com/bjlvh5/#/pages/spotoverview/spotoverview",
                "http://110.41.133.77:8899/trainai2/#/media-design",
                "https://bjled.szzfhs.com",
                "https://bjled.szzfhs.com/#/LeftScreen",
                "https://bjled.szzfhs.com/#/RightScreen",
            ]
        ),
    }
    missing = [name for name, ok in checks.items() if not ok]
    if missing:
        raise RuntimeError(f"topic external link checks failed: {', '.join(missing)}")
    print("topic_external_links_static_ok=true")


if __name__ == "__main__":
    main()
