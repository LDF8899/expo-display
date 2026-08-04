import os
import subprocess
import sys
import threading
import time
import urllib.request
import webbrowser
from pathlib import Path

import server


ROOT = Path(__file__).resolve().parent
LOCAL_SCANNER_DIR = ROOT / "scanner-agent"
LOCAL_SCANNER_EXE = LOCAL_SCANNER_DIR / "Txq_csharp_sdk.exe"
DEFAULT_DISPLAY_URL = f"http://{server.HOST}:{server.PORT}/display"
DEFAULT_ADMIN_URL = f"http://{server.HOST}:{server.PORT}/admin"
DEFAULT_HEALTH_URL = f"http://{server.HOST}:{server.PORT}/api/health"
WATCH_INTERVAL_SECONDS = int(os.environ.get("SCANNER_WATCH_INTERVAL", "8"))


def truthy(value):
    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "on"}


def scanner_agent_exe():
    return LOCAL_SCANNER_EXE


def scanner_processes():
    if os.name != "nt":
        return []

    try:
        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "[Console]::OutputEncoding = [Text.Encoding]::UTF8; "
                "Get-CimInstance Win32_Process -Filter \"Name = 'Txq_csharp_sdk.exe'\" "
                "| ForEach-Object { \"{0}`t{1}\" -f $_.ProcessId, $_.ExecutablePath }",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
        )
    except Exception:
        return []

    processes = []
    for line in result.stdout.splitlines():
        if not line.strip() or "\t" not in line:
            continue
        pid, path = line.split("\t", 1)
        if pid.strip().isdigit() and path.strip():
            processes.append((int(pid.strip()), Path(path.strip())))
    return processes


def same_path(left, right):
    return os.path.normcase(str(left.resolve())) == os.path.normcase(str(right.resolve()))


def is_scanner_running(exe):
    return any(same_path(path, exe) for _, path in scanner_processes())


def stop_process(pid):
    if pid == os.getpid():
        return
    try:
        subprocess.run(
            ["taskkill", "/PID", str(pid), "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=5,
        )
    except Exception:
        pass


def stop_nonlocal_scanner_agents(exe):
    for pid, path in scanner_processes():
        if same_path(path, exe):
            continue
        print(f"Stopping non-project scanner agent: {path}")
        stop_process(pid)


def stop_local_scanner_agent():
    exe = scanner_agent_exe()
    stopped = False
    for pid, path in scanner_processes():
        if same_path(path, exe):
            print(f"Stopping scanner agent: {path}")
            stop_process(pid)
            stopped = True
    return stopped


def server_port_pids(port):
    if os.name != "nt":
        return []

    try:
        result = subprocess.run(
            ["netstat", "-ano"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
        )
    except Exception:
        return []

    pids = set()
    marker = f":{port}"
    for line in result.stdout.splitlines():
        parts = line.split()
        if len(parts) < 5 or parts[0].upper() != "TCP":
            continue
        local_address = parts[1]
        state = parts[3].upper()
        pid = parts[4]
        if state == "LISTENING" and local_address.endswith(marker) and pid.isdigit():
            process_id = int(pid)
            if process_id != os.getpid():
                pids.add(process_id)
    return sorted(pids)


def stop_existing_server():
    stopped = False
    for pid in server_port_pids(server.PORT):
        print(f"Stopping existing server on port {server.PORT}: PID {pid}")
        stop_process(pid)
        stopped = True
    if stopped:
        time.sleep(1)
    return stopped


def start_scanner_agent():
    if os.environ.get("START_SCANNER_AGENT", "1") == "0":
        print("Scanner agent autostart disabled.")
        return False

    if os.name != "nt":
        print("Scanner agent autostart is only supported on Windows.")
        return False

    exe = scanner_agent_exe()
    if not exe.exists():
        print(f"Scanner agent executable not found: {exe}")
        return False

    dll = exe.parent / "vbar.dll"
    if not dll.exists():
        print(f"Scanner agent dependency missing: {dll}")
        return False

    stop_nonlocal_scanner_agents(exe)

    if is_scanner_running(exe):
        print(f"Scanner agent is already running: {exe}")
        return True

    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    subprocess.Popen(
        [str(exe), "--agent"],
        cwd=str(exe.parent),
        creationflags=creationflags,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print(f"Scanner agent started: {exe}")
    return True


def scanner_watchdog(stop_event):
    if os.environ.get("START_SCANNER_AGENT", "1") == "0":
        return

    last_server_pids = tuple(server_port_pids(server.PORT))
    while not stop_event.wait(WATCH_INTERVAL_SECONDS):
        exe = scanner_agent_exe()
        current_server_pids = tuple(server_port_pids(server.PORT))
        if last_server_pids and current_server_pids and current_server_pids != last_server_pids:
            print("Server process changed; restarting scanner agent.")
            stop_local_scanner_agent()
            start_scanner_agent()
        last_server_pids = current_server_pids
        if not is_scanner_running(exe):
            print("Scanner agent is not running; restarting it.")
            start_scanner_agent()


def wait_for_http(url, timeout_seconds=15):
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if 200 <= response.status < 500:
                    return True
        except Exception:
            time.sleep(0.5)
    return False


def open_start_pages():
    if os.environ.get("OPEN_BROWSER", "1") == "0":
        return

    if not wait_for_http(DEFAULT_HEALTH_URL):
        print("Server health check did not respond; skip opening browser.")
        return

    webbrowser.open(DEFAULT_DISPLAY_URL)
    if os.environ.get("OPEN_ADMIN", "0") == "1":
        webbrowser.open(DEFAULT_ADMIN_URL)


def keep_watchdog_alive(stop_event):
    print("Existing Python server detected.")
    print("This launcher will keep the scanner agent alive.")
    print("Close this window to stop the launcher watchdog.")
    try:
        while True:
            time.sleep(60)
    finally:
        stop_event.set()


def print_usage():
    print("Usage: python start_expo.py [--kill-existing] [--stop]")
    print("")
    print("Options:")
    print("  --kill-existing  Stop any process listening on port 8000 before starting.")
    print("  --stop           Stop the port 8000 server and local scanner agent, then exit.")
    print("")
    print("Environment:")
    print("  KILL_EXISTING_SERVER=1  Same as --kill-existing.")


def main():
    args = set(sys.argv[1:])
    if "--help" in args or "-h" in args:
        print_usage()
        return

    if "--stop" in args:
        stopped_server = stop_existing_server()
        stopped_scanner = stop_local_scanner_agent()
        if not stopped_server and not stopped_scanner:
            print("No expo display server or scanner agent process was found.")
        return

    if "--kill-existing" in args or truthy(os.environ.get("KILL_EXISTING_SERVER")):
        stop_existing_server()

    start_scanner_agent()
    stop_event = threading.Event()
    watchdog = threading.Thread(target=scanner_watchdog, args=(stop_event,), daemon=True)
    browser_opener = threading.Thread(target=open_start_pages, daemon=True)
    watchdog.start()
    browser_opener.start()

    if wait_for_http(DEFAULT_HEALTH_URL, timeout_seconds=1):
        keep_watchdog_alive(stop_event)
        return

    print("Expo launcher is ready.")
    print(f"Display: {DEFAULT_DISPLAY_URL}")
    print(f"Admin:   {DEFAULT_ADMIN_URL}")
    print("Keep this window open during the exhibition.")
    try:
        server.main()
    finally:
        stop_event.set()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
