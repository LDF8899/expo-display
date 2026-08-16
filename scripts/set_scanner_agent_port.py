import argparse
import datetime as dt
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
AGENT_EXE = ROOT / "scanner-agent" / "Txq_csharp_sdk.exe"


def utf16(text):
    return text.encode("utf-16le")


def current_ports(data):
    text = data.decode("utf-16le", errors="ignore")
    ports = sorted(set(int(item) for item in re.findall(r"http://127\.0\.0\.1:(\d{4})/(?:api/scan|display)", text)))
    return ports


def patch_port(data, old_port, new_port):
    old = str(old_port)
    new = str(new_port)
    if len(old) != len(new):
        raise ValueError("当前 Agent 只能安全替换相同长度的端口号；请使用 1000-9999 的四位端口。")
    replacements = 0
    for prefix in ("http://127.0.0.1:",):
        target = utf16(prefix + old)
        replacement = utf16(prefix + new)
        count = data.count(target)
        if count:
            data = data.replace(target, replacement)
            replacements += count
    if not replacements:
        raise ValueError(f"没有在 Agent 中找到端口 {old_port}，未做修改。")
    return data, replacements


def main():
    parser = argparse.ArgumentParser(description="Patch scanner Agent localhost port safely.")
    parser.add_argument("--port", type=int, required=True, help="新的四位端口，例如 8010")
    parser.add_argument("--agent", default=str(AGENT_EXE), help="Agent exe 路径")
    parser.add_argument("--yes", action="store_true", help="确认写入修改")
    args = parser.parse_args()

    if args.port < 1000 or args.port > 9999:
        raise SystemExit("端口必须是 1000-9999 的四位端口。")

    agent = Path(args.agent)
    if not agent.exists():
        raise SystemExit(f"Agent 不存在：{agent}")

    data = agent.read_bytes()
    ports = current_ports(data)
    if not ports:
        raise SystemExit("未识别到 Agent 内置端口，不能安全修改。")
    if len(ports) > 1:
        raise SystemExit(f"Agent 内识别到多个端口 {ports}，请先人工确认后再改。")

    old_port = ports[0]
    if old_port == args.port:
        print(f"scanner_agent_port={old_port}")
        print("already_current=true")
        return

    patched, replacements = patch_port(data, old_port, args.port)
    backup = agent.with_name(f"{agent.name}.backup-{dt.datetime.now().strftime('%Y%m%d-%H%M%S')}")

    print(f"agent={agent}")
    print(f"old_port={old_port}")
    print(f"new_port={args.port}")
    print(f"replacements={replacements}")
    print(f"backup={backup}")

    if not args.yes:
        print("dry_run=true")
        print("加 --yes 才会写入修改。")
        return

    shutil.copy2(agent, backup)
    agent.write_bytes(patched)
    print("updated=true")


if __name__ == "__main__":
    main()
