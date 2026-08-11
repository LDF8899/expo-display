import json
import os
import re
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path


ROOT = Path(__file__).resolve().parent
LOCAL_SCANNER_DIR = ROOT / "scanner-agent"
LOCAL_SCANNER_EXE = LOCAL_SCANNER_DIR / "Txq_csharp_sdk.exe"
WATCH_INTERVAL_SECONDS = int(os.environ.get("SCANNER_WATCH_INTERVAL", "8"))
DEFAULT_PORT = 8000

server = None


def truthy(value):
    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "on"}


def env_int(name, default):
    try:
        return int(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


def configured_host():
    return os.environ.get("HOST", "127.0.0.1")


def scanner_agent_port(default=DEFAULT_PORT):
    exe = scanner_agent_exe()
    if not exe.exists():
        return default
    try:
        text = exe.read_bytes().decode("utf-16le", errors="ignore")
    except Exception:
        return default
    match = re.search(r"http://127\.0\.0\.1:(\d{4,5})/api/scan", text)
    return int(match.group(1)) if match else default


def configured_port():
    if os.environ.get("PORT"):
        return env_int("PORT", DEFAULT_PORT)
    return scanner_agent_port(DEFAULT_PORT)


def app_url(path, port=None):
    host = configured_host()
    port = port or configured_port()
    return f"http://{host}:{port}{path}"


def load_server(port=None):
    global server
    if port is not None:
        os.environ["PORT"] = str(port)
    if server is None:
        import server as server_module
        server = server_module
    return server


def scanner_agent_exe():
    return LOCAL_SCANNER_EXE


def safe_resolved_path(path):
    try:
        return path.resolve()
    except Exception:
        return path


def same_path(left, right):
    return os.path.normcase(str(safe_resolved_path(left))) == os.path.normcase(str(safe_resolved_path(right)))


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


def process_info(pid):
    info = {"pid": pid, "name": "", "commandLine": "", "executablePath": ""}
    if os.name != "nt":
        return info
    try:
        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "[Console]::OutputEncoding = [Text.Encoding]::UTF8; "
                f"Get-CimInstance Win32_Process -Filter \"ProcessId = {int(pid)}\" "
                "| Select-Object -First 1 ProcessId,Name,ExecutablePath,CommandLine "
                "| ConvertTo-Json -Compress",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
        )
        data = json.loads(result.stdout or "{}")
        info.update(
            {
                "name": data.get("Name") or "",
                "commandLine": data.get("CommandLine") or "",
                "executablePath": data.get("ExecutablePath") or "",
            }
        )
    except Exception:
        pass
    return info


def port_processes(port):
    return [process_info(pid) for pid in server_port_pids(port)]


def is_project_server_process(info):
    command = str(info.get("commandLine") or "").lower()
    root = str(ROOT).lower()
    if "start_expo.py" in command:
        return True
    return "server.py" in command and root in command


def describe_process(info):
    command = (info.get("commandLine") or "").strip()
    name = info.get("name") or "process"
    if command:
        return f"PID {info['pid']} · {name} · {command}"
    return f"PID {info['pid']} · {name}"


def stop_existing_server(port=None, force=False):
    port = port or configured_port()
    stopped = []
    skipped = []
    for info in port_processes(port):
        if force or is_project_server_process(info):
            print(f"Stopping existing expo server on port {port}: {describe_process(info)}")
            stop_process(info["pid"])
            stopped.append(info)
        else:
            skipped.append(info)
    if stopped:
        time.sleep(1)
    return stopped, skipped


def tcp_port_available(port, host=None):
    host = host or configured_host()
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((host, int(port)))
        return True
    except OSError:
        return False


def app_health_ok(port=None):
    url = app_url("/api/health", port=port)
    try:
        with urllib.request.urlopen(url, timeout=2) as response:
            if response.status != 200:
                return False
            data = json.loads(response.read().decode("utf-8"))
            return bool(data.get("ok"))
    except Exception:
        return False


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


def find_free_port(start_port, attempts=20):
    for port in range(int(start_port), int(start_port) + attempts):
        if not server_port_pids(port) and tcp_port_available(port):
            return port
    return 0


def print_port_conflict(port, processes):
    scanner_port = scanner_agent_port(DEFAULT_PORT)
    print("")
    print(f"Port {port} is occupied, but it is not this expo display service.")
    print(f"The achievement market hardware agent posts scans to http://127.0.0.1:{scanner_port}/api/scan,")
    print(f"so the official onsite mode must keep port {scanner_port} available.")
    print("")
    print("Processes using this port:")
    for info in processes:
        print(f"  - {describe_process(info)}")
    print("")
    print("Recommended fixes:")
    print(f"  1. Close the program that is binding port {scanner_port}, then run 启动展会系统.bat again.")
    print("  2. For admin-only debugging without scanner hardware:")
    print("     set START_SCANNER_AGENT=0")
    print("     set AUTO_PORT=1")
    print("     python start_expo.py")
    print("  3. To forcibly kill every process on the port, use: python start_expo.py --force-kill-port")
    print("     Use this only when you are sure it will not stop Docker, WSL, or another important service.")
    print("")


def resolve_start_port(args):
    preferred_port = configured_port()
    force_kill = "--force-kill-port" in args or truthy(os.environ.get("FORCE_KILL_PORT"))
    kill_existing = force_kill or "--kill-existing" in args or truthy(os.environ.get("KILL_EXISTING_SERVER"))

    if kill_existing:
        stopped, skipped = stop_existing_server(preferred_port, force=force_kill)
        if skipped and not force_kill:
            print(f"Skipped non-project process(es) on port {preferred_port}; they were not killed.")

    if app_health_ok(preferred_port):
        return preferred_port, True

    processes = port_processes(preferred_port)
    if not processes and tcp_port_available(preferred_port):
        return preferred_port, False

    if truthy(os.environ.get("AUTO_PORT")) or "--auto-port" in args:
        free_port = find_free_port(preferred_port + 1)
        if free_port:
            if os.environ.get("START_SCANNER_AGENT", "1") != "0":
                print("AUTO_PORT selected a fallback port, so scanner agent autostart is disabled for this run.")
                print(f"Hardware scans require port {scanner_agent_port(DEFAULT_PORT)}. Use fallback ports only for admin/debug work.")
                os.environ["START_SCANNER_AGENT"] = "0"
            os.environ["PORT"] = str(free_port)
            return free_port, False

    print_port_conflict(preferred_port, processes)
    raise SystemExit(2)


def start_scanner_agent():
    if os.environ.get("START_SCANNER_AGENT", "1") == "0":
        print("Scanner agent autostart disabled.")
        return False

    agent_port = scanner_agent_port(DEFAULT_PORT)
    if configured_port() != agent_port:
        print(f"Scanner agent autostart disabled because the server is not on port {agent_port}.")
        print(f"The current scanner agent posts to 127.0.0.1:{agent_port}/api/scan.")
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


def scanner_watchdog(stop_event, port):
    if os.environ.get("START_SCANNER_AGENT", "1") == "0" or port != scanner_agent_port(DEFAULT_PORT):
        return

    last_server_pids = tuple(server_port_pids(port))
    while not stop_event.wait(WATCH_INTERVAL_SECONDS):
        exe = scanner_agent_exe()
        current_server_pids = tuple(server_port_pids(port))
        if last_server_pids and current_server_pids and current_server_pids != last_server_pids:
            print("Server process changed; restarting scanner agent.")
            stop_local_scanner_agent()
            start_scanner_agent()
        last_server_pids = current_server_pids
        if not is_scanner_running(exe):
            print("Scanner agent is not running; restarting it.")
            start_scanner_agent()


def open_start_pages(port):
    if os.environ.get("OPEN_BROWSER", "1") == "0":
        return

    health_url = app_url("/api/health", port=port)
    if not wait_for_http(health_url):
        print("Server health check did not respond; skip opening browser.")
        return

    webbrowser.open(app_url("/display", port=port))
    if os.environ.get("OPEN_ADMIN", "0") == "1":
        webbrowser.open(app_url("/admin", port=port))


def keep_watchdog_alive(stop_event, port):
    print("Existing expo display server detected.")
    print("This launcher will keep the scanner agent alive.")
    print(f"Display: {app_url('/display', port=port)}")
    print(f"Admin:   {app_url('/admin', port=port)}")
    print("Close this window to stop the launcher watchdog.")
    try:
        while True:
            time.sleep(60)
    finally:
        stop_event.set()


def print_usage():
    print("Usage: python start_expo.py [--kill-existing] [--force-kill-port] [--auto-port] [--stop]")
    print("")
    print("Options:")
    print("  --kill-existing   Stop only this project's old Python server on the configured port.")
    print("  --force-kill-port Stop every process listening on the configured port. Use carefully.")
    print("  --auto-port       If the configured port is occupied, use the next free port for admin/debug.")
    print("  --stop            Stop this project's port server and local scanner agent, then exit.")
    print("")
    print("Environment:")
    print("  KILL_EXISTING_SERVER=1  Same as --kill-existing.")
    print("  FORCE_KILL_PORT=1       Same as --force-kill-port.")
    print("  AUTO_PORT=1             Same as --auto-port.")
    print(f"  PORT={scanner_agent_port(DEFAULT_PORT)}               Preferred HTTP port.")
    print("")
    print("Important:")
    print(f"  The scanner agent posts to 127.0.0.1:{scanner_agent_port(DEFAULT_PORT)}/api/scan.")
    print("  Official onsite mode needs the Python server and scanner agent to use the same port.")


def main():
    args = set(sys.argv[1:])
    if "--help" in args or "-h" in args:
        print_usage()
        return

    if "--stop" in args:
        port = configured_port()
        stopped_server, skipped = stop_existing_server(port, force=False)
        stopped_scanner = stop_local_scanner_agent()
        if skipped:
            print(f"Skipped non-project process(es) on port {port}; they were not killed.")
        if not stopped_server and not stopped_scanner:
            print("No expo display server or scanner agent process was found.")
        return

    port, existing_server = resolve_start_port(args)
    load_server(port)

    start_scanner_agent()
    stop_event = threading.Event()
    watchdog = threading.Thread(target=scanner_watchdog, args=(stop_event, port), daemon=True)
    browser_opener = threading.Thread(target=open_start_pages, args=(port,), daemon=True)
    watchdog.start()
    browser_opener.start()

    if existing_server:
        keep_watchdog_alive(stop_event, port)
        return

    print("Expo launcher is ready.")
    print(f"Display: {app_url('/display', port=port)}")
    print(f"Admin:   {app_url('/admin', port=port)}")
    print("Keep this window open during the exhibition.")
    try:
        server.main()
    except OSError as exc:
        print("")
        print(f"Failed to start server on port {port}: {exc}")
        print_port_conflict(port, port_processes(port))
        raise SystemExit(2)
    finally:
        stop_event.set()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
