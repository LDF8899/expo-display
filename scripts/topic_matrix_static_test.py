import ast
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
BLUEPRINT_JS = ROOT / "static" / "blueprint" / "blueprint.js"
SERVER_PY = ROOT / "server.py"

EXPECTED_TOPICS = [
    "modern-agriculture",
    "digital-tourism",
    "smart-healthcare",
    "finance-commerce",
    "digital-intelligence",
    "smart-energy",
    "smart-manufacturing",
    "campus-culture",
]

EXPECTED_TOPIC_SECTIONS = [
    ("overview", "专题概况"),
    ("majors", "专业群布局"),
    ("training", "实训场景"),
    ("cooperation", "产教协同"),
    ("masters", "名师名匠"),
    ("alumni", "优秀校友"),
    ("students", "优秀学生"),
    ("achievements", "专题成果"),
    ("competitions", "技能大赛"),
    ("honors", "荣誉资质"),
    ("media", "数字资源"),
]

EXPECTED_BACKEND_TOPIC_SECTIONS = EXPECTED_TOPIC_SECTIONS[:-1] + [
    ("systems", "特色系统入口"),
    EXPECTED_TOPIC_SECTIONS[-1],
]

EXPECTED_TOPIC_CONTENT_TYPES = {
    "training": "scene",
    "cooperation": "activity",
    "masters": "person",
    "alumni": "person",
    "students": "person",
    "achievements": "achievement",
    "competitions": "activity",
    "honors": "honor",
    "media": "video",
}


def parse_blueprint_topic_order():
    text = BLUEPRINT_JS.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"topics:\s*\[(?P<body>.*?)\]\s*\}", text, flags=re.S)
    if not match:
        raise RuntimeError("could not find ORDER.topics in blueprint.js")
    return re.findall(r'"([^"]+)"', match.group("body"))


def parse_blueprint_topic_sections():
    text = BLUEPRINT_JS.read_text(encoding="utf-8", errors="replace")
    order_match = re.search(r"var\s+TOPIC_SECTION_ORDER\s*=\s*\[(?P<body>.*?)\];", text, flags=re.S)
    titles_match = re.search(r"var\s+TOPIC_SECTION_TITLES\s*=\s*\{(?P<body>.*?)\};", text, flags=re.S)
    if not order_match:
        raise RuntimeError("could not find TOPIC_SECTION_ORDER in blueprint.js")
    if not titles_match:
        raise RuntimeError("could not find TOPIC_SECTION_TITLES in blueprint.js")
    order = re.findall(r'"([^"]+)"', order_match.group("body"))
    titles = dict(re.findall(r"([a-zA-Z0-9_-]+)\s*:\s*\"([^\"]+)\"", titles_match.group("body")))
    return [(key, titles.get(key, "")) for key in order]


def parse_blueprint_topic_content_types():
    text = BLUEPRINT_JS.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"var\s+TOPIC_DEFAULT_CONTENT_TYPES\s*=\s*\{(?P<body>.*?)\};", text, flags=re.S)
    if not match:
        raise RuntimeError("could not find TOPIC_DEFAULT_CONTENT_TYPES in blueprint.js")
    return dict(re.findall(r"([a-zA-Z0-9_-]+)\s*:\s*\"([^\"]+)\"", match.group("body")))


def assignment_value(tree, name):
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(target, "id", "") == name for target in node.targets):
            return node.value
    raise RuntimeError(f"could not find {name} in server.py")


def parse_server_blueprint_topics():
    tree = ast.parse(SERVER_PY.read_text(encoding="utf-8-sig", errors="replace"))
    topics = []
    for item in getattr(assignment_value(tree, "BLUEPRINT_PORTALS"), "elts", []):
        if not isinstance(item, ast.Dict):
            continue
        values = {}
        for key_node, value_node in zip(item.keys, item.values):
            if isinstance(key_node, ast.Constant) and isinstance(key_node.value, str):
                if isinstance(value_node, ast.Constant) and isinstance(value_node.value, str):
                    values[key_node.value] = value_node.value
        if values.get("portal_type") == "topic":
            topics.append(values.get("portal_slug"))
    return topics


def parse_server_topic_sections():
    tree = ast.parse(SERVER_PY.read_text(encoding="utf-8-sig", errors="replace"))
    modules = ast.literal_eval(assignment_value(tree, "TOPIC_MODULES"))
    return [(item.get("key"), item.get("label")) for item in modules]


def parse_server_topic_content_types():
    tree = ast.parse(SERVER_PY.read_text(encoding="utf-8-sig", errors="replace"))
    defaults = ast.literal_eval(assignment_value(tree, "MODULE_DEFAULT_CONTENT_TYPES"))
    return {key: defaults.get(key) for key in EXPECTED_TOPIC_CONTENT_TYPES}


def main():
    checks = {
        "frontend ORDER.topics": parse_blueprint_topic_order(),
        "backend BLUEPRINT_PORTALS topics": parse_server_blueprint_topics(),
    }
    failures = []
    for label, actual in checks.items():
        if actual != EXPECTED_TOPICS:
            failures.append(f"{label} should be {EXPECTED_TOPICS}, got {actual}")
        if len(actual) != len(set(actual)):
            failures.append(f"{label} contains duplicate topic slugs: {actual}")

    frontend_sections = parse_blueprint_topic_sections()
    backend_sections = parse_server_topic_sections()
    if frontend_sections != EXPECTED_TOPIC_SECTIONS:
        failures.append(f"frontend TOPIC_SECTION_ORDER/TITLES should be {EXPECTED_TOPIC_SECTIONS}, got {frontend_sections}")
    if backend_sections != EXPECTED_BACKEND_TOPIC_SECTIONS:
        failures.append(f"backend TOPIC_MODULES should be {EXPECTED_BACKEND_TOPIC_SECTIONS}, got {backend_sections}")
    for label, actual in {
        "frontend TOPIC_SECTION_ORDER/TITLES": frontend_sections,
        "backend TOPIC_MODULES": backend_sections,
    }.items():
        keys = [key for key, _ in actual]
        if len(keys) != len(set(keys)):
            failures.append(f"{label} contains duplicate section keys: {actual}")

    content_type_checks = {
        "frontend TOPIC_DEFAULT_CONTENT_TYPES": parse_blueprint_topic_content_types(),
        "backend MODULE_DEFAULT_CONTENT_TYPES": parse_server_topic_content_types(),
    }
    for label, actual in content_type_checks.items():
        if actual != EXPECTED_TOPIC_CONTENT_TYPES:
            failures.append(f"{label} should be {EXPECTED_TOPIC_CONTENT_TYPES}, got {actual}")

    if failures:
        print("topic_matrix_static_ok=false")
        for item in failures:
            print(" -", item)
        raise SystemExit(1)

    print("topic_matrix_static_ok=true")


if __name__ == "__main__":
    main()
