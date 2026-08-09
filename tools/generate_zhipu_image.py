#!/usr/bin/env python3
"""智谱 CogView 图片生成脚本（与 ThinkAI 渠道并存）。

用法:
    python tools/generate_zhipu_image.py --prompt "你的提示词" [--size 1920x1088] [--output-dir outputs] [--output-prefix zhipu-image]

密钥从环境变量 ZHIPU_API_KEY 读取（进程级优先，回退到 Windows 用户级环境变量）。
密钥不会写入任何文件或日志。

智谱尺寸限制：边长 512-2880px、宽高均为 16 的倍数、面积不超过 2^21 px。
"""

import argparse
import base64
import json
import os
import subprocess
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

API_URL = "https://open.bigmodel.cn/api/paas/v4/images/generations"
DEFAULT_MODEL = "cogview-4"
MIN_EDGE, MAX_EDGE = 512, 2880
MAX_AREA = 2 ** 21  # 2097152


def get_api_key():
    key = os.environ.get("ZHIPU_API_KEY", "").strip()
    if key:
        return key
    if os.name == "nt":
        try:
            out = subprocess.run(
                ["powershell", "-NoProfile", "-Command",
                 "[Environment]::GetEnvironmentVariable('ZHIPU_API_KEY','User')"],
                capture_output=True, text=True, timeout=10,
            ).stdout.strip()
            if out:
                return out
        except Exception:
            pass
    raise SystemExit("ZHIPU_API_KEY 未配置：请先设置环境变量 ZHIPU_API_KEY")


def validate_size(size):
    """校验并规范化尺寸参数，返回 'WxH' 字符串。"""
    try:
        w, h = (int(x) for x in size.lower().split("x"))
    except ValueError:
        raise SystemExit(f"尺寸格式错误: {size}（应为 WxH，如 1920x1088）")
    if not (MIN_EDGE <= w <= MAX_EDGE and MIN_EDGE <= h <= MAX_EDGE):
        raise SystemExit(f"尺寸超范围: {size}（边长须在 {MIN_EDGE}-{MAX_EDGE}px 之间）")
    if w % 16 != 0 or h % 16 != 0:
        raise SystemExit(f"尺寸不合规: {size}（宽高必须是 16 的倍数）")
    if w * h > MAX_AREA:
        raise SystemExit(f"尺寸过大: {size}（面积须不超过 {MAX_AREA}px）")
    return f"{w}x{h}"


def generate(prompt, model, size, n):
    key = get_api_key()
    payload = {"model": model, "prompt": prompt, "size": size, "n": n}
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=300) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    return body.get("data", [])


def save_items(items, output_dir, prefix, model, size):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    saved = []
    for index, item in enumerate(items, 1):
        base = f"{prefix}-{timestamp}-{index}"
        if item.get("b64_json"):
            out = output_dir / f"{base}.png"
            out.write_bytes(base64.b64decode(item["b64_json"]))
            saved.append(str(out))
        elif item.get("url"):
            out = output_dir / f"{base}.png"
            try:
                urllib.request.urlretrieve(item["url"], out)
            except urllib.error.HTTPError as exc:
                raise SystemExit(f"下载图片失败: HTTP {exc.code}")
            saved.append(str(out))
        else:
            out = output_dir / f"{base}.response.json"
            out.write_text(json.dumps(item, ensure_ascii=False, indent=2), encoding="utf-8")
            saved.append(str(out))

    meta = output_dir / f"{prefix}-{timestamp}.metadata.json"
    metadata = {
        "provider": "zhipu-bigmodel",
        "model": model,
        "size": size,
        "n": len(items),
        "saved": saved,
        "createdAt": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    meta.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    return saved, meta


def main():
    ap = argparse.ArgumentParser(description="智谱 CogView 图片生成")
    ap.add_argument("--prompt", required=True, help="图片提示词")
    ap.add_argument("--size", default="1920x1088",
                    help="图片尺寸 WxH，默认 1920x1088（16 的倍数，面积 ≤ 2^21）")
    ap.add_argument("--model", default=DEFAULT_MODEL, help=f"模型名（默认 {DEFAULT_MODEL}）")
    ap.add_argument("--n", type=int, default=1, help="生成数量（默认 1）")
    ap.add_argument("--output-dir", default="outputs", help="输出目录（默认 outputs）")
    ap.add_argument("--output-prefix", default="zhipu-image", help="输出文件前缀")
    args = ap.parse_args()

    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    size = validate_size(args.size)
    print(f"[生成图片] model={args.model} size={size} n={args.n}")
    items = generate(args.prompt, args.model, size, args.n)
    if not items:
        raise SystemExit("接口未返回图片数据")
    saved, meta = save_items(items, args.output_dir, args.output_prefix, args.model, size)
    for path in saved:
        print(path)
    print(f"[元数据] {meta}")


if __name__ == "__main__":
    main()
