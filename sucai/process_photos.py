# -*- coding: utf-8 -*-
"""处理系部外部照片目录: 三档 WebP + 拷贝到 uploads/blueprint/<kind>/<id>/images/。"""
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
MEDIA_ROOT = ROOT / "uploads" / "blueprint"


def process_photos(kind, pid, photos):
    """photos: [(源路径, 目标序号)]"""
    out_dir = MEDIA_ROOT / kind / pid / "images"
    out_dir.mkdir(parents=True, exist_ok=True)
    urls = []
    for src, idx in photos:
        p = Path(src)
        if not p.exists():
            print(f"missing: {p}")
            continue
        img = Image.open(str(p))
        img = img.convert("RGB")
        w, h = img.size
        stem = f"img{idx:02d}"
        for label, max_w in (("", 1920), ("_1280", 1280), ("_640", 640)):
            if w <= max_w and label:
                continue
            tw = min(w, max_w)
            th = max(1, round(h * tw / w))
            thumb = img if tw == w else img.resize((tw, th), Image.LANCZOS)
            thumb.save(out_dir / f"{stem}{label}.webp", "WEBP", quality=82, method=4)
        url = f"/uploads/blueprint/{kind}/{pid}/images/{stem}.webp"
        urls.append(url)
        print(url)
    return urls


if __name__ == "__main__":
    kind = sys.argv[1]
    pid = sys.argv[2]
    photos = []
    for arg in sys.argv[3:]:
        idx_str, src = arg.split("=", 1)
        photos.append((src, int(idx_str)))
    process_photos(kind, pid, photos)
