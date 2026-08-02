# -*- coding: utf-8 -*-
"""处理数字文旅视频: 拷贝 mp4, ffmpeg 提取封面帧与时长, 写入 JSON media 章节。"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VIDEO_SRC = [
    (r"D:\杂\修改资料7.27\修改资料7.27\创新育人区\创新育人-数字文旅\2d4fbf012e1d466d56cfbc45a0980f5e.mp4", "黔菜师傅培养纪实（一）"),
    (r"D:\杂\修改资料7.27\修改资料7.27\创新育人区\创新育人-数字文旅\3d14324e38cec6f57fbfd29439540d38.mp4", "黔菜师傅培养纪实（二）"),
]
VIDEO_DIR = ROOT / "uploads" / "blueprint" / "topics" / "digital-tourism" / "videos"
JSON_PATH = ROOT / "static" / "blueprint" / "data" / "topics" / "digital-tourism.json"


def probe_duration(path: Path) -> str:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True, timeout=60,
    )
    try:
        secs = float(r.stdout.strip())
        m, s = int(secs // 60), int(secs % 60)
        return f"{m}:{s:02d}"
    except ValueError:
        return ""


def make_cover(src: Path, dst: Path):
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(src), "-frames:v", "1", "-q:v", "3",
         "-vf", "scale=1280:-2", str(dst)],
        capture_output=True, timeout=120,
    )


def main():
    VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    videos = []
    for src_str, title in VIDEO_SRC:
        src = Path(src_str)
        if not src.exists():
            print(f"missing: {src}")
            continue
        target = VIDEO_DIR / src.name
        if not target.exists():
            target.write_bytes(src.read_bytes())
        poster = VIDEO_DIR / (src.stem + ".jpg")
        make_cover(src, poster)
        videos.append({
            "type": "video",
            "src": f"/uploads/blueprint/topics/digital-tourism/videos/{src.name}",
            "poster": f"/uploads/blueprint/topics/digital-tourism/videos/{poster.name}",
            "title": title,
            "duration": probe_duration(src),
        })
        print(f"video ready: {title} {probe_duration(src)}")

    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    # 查找或创建 media 章节
    media_sec = next((s for s in data["sections"] if s["id"] == "media"), None)
    if media_sec is None:
        media_sec = {"id": "media", "title": "视频资源", "blocks": []}
        data["sections"].append(media_sec)
    else:
        media_sec["blocks"] = [b for b in media_sec["blocks"] if b["type"] != "video"]
    media_sec["blocks"].extend(videos)
    # 去掉空文本块
    media_sec["blocks"] = [b for b in media_sec["blocks"] if b["type"] != "text" or b["content"].strip()]
    JSON_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"updated {JSON_PATH}")


if __name__ == "__main__":
    main()
