from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
BLUEPRINT_FILES = [
    ROOT / "static" / "blueprint" / "index.html",
    ROOT / "static" / "blueprint" / "blueprint.js",
]


def main():
    failures = []
    forbidden = [
        ('target="_blank"', "blueprint portal links should stay in the current page"),
        ("target='_blank'", "blueprint portal links should stay in the current page"),
        ("window.open", "blueprint portal navigation should not open new browser tabs"),
    ]
    for path in BLUEPRINT_FILES:
        text = path.read_text(encoding="utf-8", errors="replace")
        for needle, message in forbidden:
            if needle in text:
                failures.append(f"{path.relative_to(ROOT)}: {message}: {needle}")

    if failures:
        print("blueprint_navigation_static_ok=false")
        for item in failures:
            print(" -", item)
        raise SystemExit(1)

    print("blueprint_navigation_static_ok=true")


if __name__ == "__main__":
    main()
