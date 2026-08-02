# -*- coding: utf-8 -*-
"""分析展厅截图关键区域像素，验证元素是否真实渲染（文字/QR 白色 vs 背景深蓝）。"""
import sys
from pathlib import Path
from PIL import Image

# 区域: (名称, x, y, w, h) 按 1920×1080 基准坐标（截图已按窗口尺寸生成，按比例换算）
REGIONS = {
    "brand_area": (120, 40, 500, 80),   # 校名+英文区
    "qr_area": (1750, 40, 120, 120),     # 二维码区
    "nav_area": (100, 180, 600, 60),     # 章节导航文字区
    "content_area": (200, 400, 400, 80), # 正文区
}


def analyze(path: Path, scale: float):
    img = Image.open(str(path)).convert("RGB")
    w, h = img.size
    print(f"== {path.name} ({w}x{h}) ==")
    for name, (x, y, rw, rh) in REGIONS.items():
        bx, by, bw, bh = int(x * scale), int(y * scale), max(1, int(rw * scale)), max(1, int(rh * scale))
        region = img.crop((bx, by, min(w, bx + bw), min(h, by + bh)))
        pixels = list(region.getdata())
        # 统计亮色像素（文字白 #F7FBFF 与 QR 白底）
        bright = sum(1 for p in pixels if p[0] > 200 and p[1] > 200 and p[2] > 200)
        light_blue = sum(1 for p in pixels if p[2] > p[0] + 40)  # 冰蓝系
        total = len(pixels)
        print(f"  {name}: bright={bright/total:.1%} lightblue={light_blue/total:.1%}")


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        p = Path(arg)
        # 截图尺寸换算: 假设窗口 1920x1080 时 scale=1, 其他按宽高比
        img = Image.open(str(p))
        scale = img.size[0] / 1920.0
        analyze(p, scale)
