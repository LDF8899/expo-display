# -*- coding: utf-8 -*-
"""把截图转成低分辨率亮度字符画，快速目视定位渲染问题。"""
import sys
from pathlib import Path
from PIL import Image

CHARS = " .:-=+*#%@"


def ascii_art(path: Path, cols=96, rows=40):
    img = Image.open(str(path)).convert("L")
    w, h = img.size
    thumb = img.resize((cols, rows))
    lines = []
    for y in range(rows):
        row = ""
        for x in range(cols):
            v = thumb.getpixel((x, y))
            row += CHARS[min(9, v * 10 // 256)]
        lines.append(row)
    print("\n".join(lines))


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        p = Path(arg)
        print(f"===== {p.name} =====")
        ascii_art(p)
