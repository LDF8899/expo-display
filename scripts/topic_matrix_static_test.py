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


def parse_blueprint_topic_order():
    text = BLUEPRINT_JS.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"topics:\s*\[(?P<body>.*?)\]\s*\}", text, flags=re.S)
    if not match:
        raise RuntimeError("could not find ORDER.topics in blueprint.js")
    return re.findall(r'"([^"]+)"', match.group("body"))


def parse_server_blueprint_topics():
    tree = ast.parse(SERVER_PY.read_text(encoding="utf-8-sig", errors="replace"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(target, "id", "") == "BLUEPRINT_PORTALS" for target in node.targets):
            topics = []
            for item in getattr(node.value, "elts", []):
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
    raise RuntimeError("could not find BLUEPRINT_PORTALS in server.py")


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

    if failures:
        print("topic_matrix_static_ok=false")
        for item in failures:
            print(" -", item)
        raise SystemExit(1)

    print("topic_matrix_static_ok=true")


if __name__ == "__main__":
    main()
