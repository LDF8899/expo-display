#!/usr/bin/env python3
"""图片识别脚本：调用智谱 GLM 视觉模型识别本地图片。

用法:
    python tools/analyze_image.py --image <图片路径> [--prompt "问题"] [--model glm-5.2]

密钥从环境变量 ZHIPU_API_KEY 读取（进程级优先，回退到 Windows 用户级环境变量）。
密钥不会写入任何文件或日志。
"""

import argparse
import base64
import io
import json
import os
import subprocess
import sys
import urllib.request

API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
# 视觉模型：glm-5v-turbo（默认）/ glm-4.5v / glm-4v-plus / glm-4v-flash（省钱）
# 注意：glm-5.2 等纯文本模型不接受图片输入
DEFAULT_MODEL = "glm-5v-turbo"
# 智谱接口限制：图片 base64 后建议不超过 5MB；超出时按比例压缩
MAX_BASE64_BYTES = 5 * 1024 * 1024
MAX_EDGE = 2048


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


def load_image_b64(path):
    try:
        from PIL import Image
    except ImportError:
        raise SystemExit("需要 Pillow：pip install pillow")

    im = Image.open(path)
    im.load()

    # 限制最长边，避免超大图
    if max(im.size) > MAX_EDGE:
        ratio = MAX_EDGE / max(im.size)
        im = im.resize((round(im.width * ratio), round(im.height * ratio)), Image.LANCZOS)

    # 转 RGB 防止 RGBA/P 模式问题
    if im.mode != "RGB":
        im = im.convert("RGB")

    quality = 90
    while True:
        buf = io.BytesIO()
        im.save(buf, format="JPEG", quality=quality)
        data = buf.getvalue()
        if len(data) < MAX_BASE64_BYTES or quality <= 40:
            break
        quality -= 10

    return base64.b64encode(data).decode("ascii")


def chat(image_b64, prompt, model, thinking=True, image_url=None):
    key = get_api_key()
    if image_url:
        img_entry = {"type": "image_url", "image_url": {"url": image_url}}
    else:
        img_entry = {"type": "image_url",
                     "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}}
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    img_entry,
                    {"type": "text", "text": prompt},
                ],
            }
        ],
        "temperature": 0.7,
        "stream": False,
    }
    if thinking:
        payload["thinking"] = {"type": "enabled"}
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    return body["choices"][0]["message"]["content"]


def main():
    ap = argparse.ArgumentParser(description="智谱 GLM 图片识别")
    ap.add_argument("--image", required=True,
                    help="本地图片路径 或 http(s) 图片 URL")
    ap.add_argument("--prompt", default="请详细描述这张图片的内容。",
                    help="识别问题/提示词")
    ap.add_argument("--model", default=DEFAULT_MODEL, help=f"模型名（默认 {DEFAULT_MODEL}）")
    ap.add_argument("--no-thinking", action="store_true",
                    help="关闭思考模式（默认开启，与官方示例一致）")
    args = ap.parse_args()

    # Windows 控制台输出 UTF-8，避免中文乱码
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    if args.image.lower().startswith(("http://", "https://")):
        print(f"[读取图片] {args.image}（URL 直传）")
        image_b64 = None
        image_url = args.image
    else:
        if not os.path.exists(args.image):
            raise SystemExit(f"图片不存在: {args.image}")
        print(f"[读取图片] {args.image}")
        image_b64 = load_image_b64(args.image)
        image_url = None

    print(f"[调用模型] {args.model} (thinking={'off' if args.no_thinking else 'on'}) ...")
    result = chat(image_b64, args.prompt, args.model,
                  thinking=not args.no_thinking, image_url=image_url)
    print("\n===== 识别结果 =====\n")
    print(result)


if __name__ == "__main__":
    main()
