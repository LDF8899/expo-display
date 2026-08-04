import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PORT = os.environ.get("PORTAL_LOGIC_SMOKE_PORT", "8788")
BASE_URL = os.environ.get("PORTAL_LOGIC_BASE_URL")
ADMIN_PASSWORD = os.environ.get("PORTAL_LOGIC_ADMIN_PASSWORD", "Admin-Portal-Logic-Smoke-2026")
PLAYWRIGHT_SESSION = os.environ.get("PORTAL_LOGIC_PLAYWRIGHT_SESSION") or f"portal-smoke-{os.getpid()}"


def request(url):
    return urllib.request.urlopen(url, timeout=8)


def json_request(url):
    response = request(url)
    return json.loads(response.read().decode("utf-8"))


def wait_for_health(base_url):
    last_error = None
    for _ in range(30):
        try:
            health = json_request(f"{base_url}/api/health")
            if health.get("ok"):
                return
        except Exception as exc:  # pragma: no cover - diagnostic path
            last_error = exc
        time.sleep(0.25)
    raise RuntimeError(f"server did not become healthy: {last_error}")


def expect_http_error(code, url):
    try:
        request(url)
    except urllib.error.HTTPError as exc:
        if exc.code == code:
            return
        raise RuntimeError(f"expected HTTP {code}, got {exc.code}: {url}") from exc
    raise RuntimeError(f"expected HTTP {code}, request succeeded: {url}")


def assert_no_browser_logic_errors(console_result):
    if "Errors: 0" in console_result:
        return
    meaningful = []
    for line in console_result.splitlines():
        text = line.strip()
        if not text or not text.startswith("[ERROR]"):
            continue
        if "Failed to load resource:" in text:
            continue
        meaningful.append(text)
    if meaningful:
        raise RuntimeError(f"browser console has errors: {console_result}")


def assert_public_portal(base_url, kind, slug):
    data = json_request(f"{base_url}/api/portal/{kind}/{slug}")
    project = data.get("project") or {}
    pages = data.get("pages") or []
    coverage = data.get("coverage") or {}
    modules = coverage.get("modules") or []

    if project.get("pageCount") != len(pages):
        raise RuntimeError(f"{kind}/{slug}: project.pageCount does not match pages length")
    if int(project.get("pendingPageCount") or 0) != 0:
        raise RuntimeError(f"{kind}/{slug}: public portal reports pending pages")
    for page in pages:
        if page.get("reviewStatus") != "approved" or not page.get("enabled", True):
            raise RuntimeError(f"{kind}/{slug}: public API leaked non-public page {page.get('code')}")

    covered = sum(1 for item in modules if item.get("covered"))
    publish_ready = sum(1 for item in modules if item.get("publishReady"))
    missing_labels = [item.get("label") for item in modules if not item.get("covered")]
    if coverage.get("total") != len(modules):
        raise RuntimeError(f"{kind}/{slug}: coverage.total is inconsistent")
    if coverage.get("covered") != covered:
        raise RuntimeError(f"{kind}/{slug}: coverage.covered is inconsistent")
    if coverage.get("publishReady") != publish_ready:
        raise RuntimeError(f"{kind}/{slug}: coverage.publishReady is inconsistent")
    if coverage.get("missingLabels") != missing_labels:
        raise RuntimeError(f"{kind}/{slug}: coverage.missingLabels is inconsistent")

    return {
        "route": f"{kind}/{slug}",
        "pages": len(pages),
        "coverage": f"{covered}/{len(modules)}",
    }


def run_browser_qr_check(base_url):
    npx = shutil.which("npx")
    if not npx:
        raise RuntimeError("npx is required for the browser QR boundary check")

    cli = [npx, "--yes", "--package", "@playwright/cli", "playwright-cli", f"-s={PLAYWRIGHT_SESSION}"]
    qr_expr = (
        "()=>Array.from(document.querySelectorAll(\".qr-box,#qr,#homeQr,[class*='qr'],[id*='qr']\"))"
        ".filter(el=>{const c=typeof el.className==='string'?el.className:((el.className&&el.className.baseVal)||'');"
        "const h=`${el.id||''} ${c} ${el.getAttribute('aria-label')||''}`.toLowerCase();"
        "if(!h.includes('qr')&&!h.includes('二维码'))return false;"
        "const s=getComputedStyle(el);const r=el.getBoundingClientRect();"
        "return s.display!=='none'&&s.visibility!=='hidden'&&Number(s.opacity||1)!==0&&r.width>8&&r.height>8}).length"
    )
    switch_expr = "()=>document.querySelectorAll('#departmentSwitch option').length"
    routes = [
        ("/display", True, 0),
        ("/departments", True, 0),
        ("/departments/finance?section=overview", False, 5),
        ("/topics/smart-energy?section=majors", False, 8),
    ]

    def run_cli(args, raw=False):
        command = [*cli]
        if raw:
            command.append("--raw")
        command.extend(args)
        return subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=True,
        )

    def raw_json(args):
        output = run_cli(args, raw=True).stdout.strip()
        return json.loads(output)

    try:
        run_cli(["open", base_url + routes[0][0]])
        for path, should_show_qr, min_switch_options in routes:
            run_cli(["goto", base_url + path])
            qr_count = int(raw_json(["eval", qr_expr]))
            if should_show_qr and qr_count < 1:
                raise RuntimeError(f"{path} should show QR")
            if not should_show_qr and qr_count != 0:
                raise RuntimeError(f"{path} should not show QR, got {qr_count}")
            if min_switch_options:
                switch_options = int(raw_json(["eval", switch_expr]))
                if switch_options < min_switch_options:
                    raise RuntimeError(f"{path} switch options too few: {switch_options}")
        console_result = run_cli(["console", "error"]).stdout
        assert_no_browser_logic_errors(console_result)
    finally:
        subprocess.run([*cli, "close"], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def run_browser_department_layout_check(base_url):
    npx = shutil.which("npx")
    if not npx:
        raise RuntimeError("npx is required for the department layout check")

    cli = [npx, "--yes", "--package", "@playwright/cli", "playwright-cli", f"-s={PLAYWRIGHT_SESSION}"]

    def run_cli(args):
        return subprocess.run(
            [*cli, *args],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=True,
        )

    layout_code = f"""
async (page) => {{
  const cases = [
    {{ name: "desktop", width: 1366, height: 768 }},
    {{ name: "compact", width: 820, height: 900 }}
  ];
  for (const item of cases) {{
    await page.setViewportSize({{ width: item.width, height: item.height }});
    await page.goto({json.dumps(base_url + "/departments/finance")});
    await page.waitForSelector(".showcase-board", {{ timeout: 10000 }});
    const result = await page.evaluate(() => {{
      const box = (selector) => {{
        const el = document.querySelector(selector);
        if (!el) return null;
        const r = el.getBoundingClientRect();
        return {{ x: r.x, y: r.y, width: r.width, height: r.height, right: r.right, bottom: r.bottom }};
      }};
      const all = Array.from(document.querySelectorAll("body *"));
      const visible = all.filter((el) => {{
        const r = el.getBoundingClientRect();
        const s = getComputedStyle(el);
        return r.width > 1 && r.height > 1 && s.display !== "none" && s.visibility !== "hidden";
      }});
      const horizontalOverflow = visible
        .filter((el) => {{
          const r = el.getBoundingClientRect();
          return r.left < -2 || r.right > innerWidth + 2;
        }})
        .map((el) => el.className || el.id || el.tagName)
        .slice(0, 5);
      const qrVisible = Array.from(document.querySelectorAll(".qr-box,#qr,#homeQr,[class*=qr],[id*=qr]")).filter((el) => {{
        const r = el.getBoundingClientRect();
        const s = getComputedStyle(el);
        return r.width > 1 && r.height > 1 && s.display !== "none" && s.visibility !== "hidden" && !el.hidden;
      }}).length;
      const chapter = document.querySelector(".chapter-viewport");
      return {{
        topbar: box("#screenDetail .topbar"),
        switchBox: box(".department-switch"),
        board: box(".showcase-board"),
        modules: box(".modules-panel"),
        teaching: box(".teaching-panel"),
        video: box(".video-panel"),
        switchOptions: document.querySelectorAll("#departmentSwitch option").length,
        qrVisible,
        horizontalOverflow,
        chapterScrollable: chapter ? chapter.scrollHeight > chapter.clientHeight : false
      }};
    }});
    if (!result.topbar || result.topbar.height < 44) throw new Error(`${{item.name}} topbar missing or collapsed`);
    if (!result.switchBox || result.switchOptions < 5) throw new Error(`${{item.name}} department switch is not usable`);
    if (!result.board || !result.modules || !result.teaching || !result.video) throw new Error(`${{item.name}} showcase sections missing`);
    if (result.qrVisible !== 0) throw new Error(`${{item.name}} department page should not show QR`);
    if (result.horizontalOverflow.length) throw new Error(`${{item.name}} horizontal overflow: ${{result.horizontalOverflow.join(", ")}}`);
    if (item.width >= 1100 && result.teaching.x <= result.modules.x + result.modules.width - 8) {{
      throw new Error(`${{item.name}} should keep side-by-side showcase layout`);
    }}
    if (item.width < 1100 && result.switchBox.width < 180) throw new Error(`${{item.name}} switch too narrow`);
  }}
}}
"""

    try:
        run_cli(["open", base_url + "/departments/finance"])
        run_cli(["run-code", layout_code])
        console_result = run_cli(["console", "error"]).stdout
        assert_no_browser_logic_errors(console_result)
    finally:
        subprocess.run([*cli, "close"], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def run_browser_portal_navigation_check(base_url):
    npx = shutil.which("npx")
    if not npx:
        raise RuntimeError("npx is required for the portal navigation check")

    cli = [npx, "--yes", "--package", "@playwright/cli", "playwright-cli", f"-s={PLAYWRIGHT_SESSION}"]

    def run_cli(args):
        return subprocess.run(
            [*cli, *args],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=True,
        )

    navigation_code = f"""
async (page) => {{
  await page.goto({json.dumps(base_url + "/departments")});
  await page.waitForSelector(".fusion-card", {{ timeout: 10000 }});
  await page.waitForSelector(".dept-chip[data-go-id='finance']", {{ timeout: 10000 }});
  await page.waitForSelector("#homeDepartmentSwitch", {{ timeout: 10000 }});
  const unityTarget = await page.locator(".unity-test-link").getAttribute("target");
  if (unityTarget === "_blank") throw new Error("Unity test link should stay in the current page");
  const matrix = await page.evaluate(() => {{
    const cards = Array.from(document.querySelectorAll(".fusion-card"));
    const buckets = (values) => Array.from(new Set(values.map((value) => Math.round(value / 8) * 8))).sort((a, b) => a - b);
    return {{
      count: cards.length,
      columns: buckets(cards.map((card) => card.getBoundingClientRect().left)).length,
      rows: buckets(cards.map((card) => card.getBoundingClientRect().top)).length,
    }};
  }});
  if (matrix.count !== 8) throw new Error(`topic matrix should render 8 cards, got ${{matrix.count}}`);
  if (matrix.columns !== 4 || matrix.rows !== 2) throw new Error(`topic matrix should be 4x2, got ${{matrix.columns}}x${{matrix.rows}}`);
  const homeSwitchOptions = await page.locator("#homeDepartmentSwitch option").count();
  if (homeSwitchOptions < 6) throw new Error(`home department switch options too few: ${{homeSwitchOptions}}`);
  const beforePages = page.context().pages().length;
  await page.selectOption("#homeDepartmentSwitch", "finance");
  await page.waitForURL(/\\/departments\\/finance/, {{ timeout: 10000 }});
  await page.click("#backHome");
  await page.waitForURL({json.dumps(base_url + "/departments")}, {{ timeout: 10000 }});
  await page.locator(".dept-chip[data-go-id='finance']").first().click();
  await page.waitForURL(/\\/departments\\/finance/, {{ timeout: 10000 }});
  await page.click("#backHome");
  await page.waitForURL({json.dumps(base_url + "/departments")}, {{ timeout: 10000 }});
  const afterPages = page.context().pages().length;
  if (afterPages !== beforePages) throw new Error(`portal back opened a new page: ${{beforePages}} -> ${{afterPages}}`);
  await page.locator(".dept-chip[data-go-id='finance']").first().click();
  await page.waitForURL(/\\/departments\\/finance/, {{ timeout: 10000 }});
  await page.goBack();
  await page.waitForURL({json.dumps(base_url + "/departments")}, {{ timeout: 10000 }});
  await page.goto({json.dumps(base_url + "/topics/smart-energy")});
  await page.waitForSelector(".chapter-tab", {{ timeout: 10000 }});
  const topicTabs = await page.locator(".chapter-tab").allTextContents();
  const expectedTabs = ["专题概况", "专业群布局", "实训场景", "产教协同", "名师名匠", "优秀校友", "优秀学生", "专题成果", "技能大赛", "荣誉资质", "视频资源"];
  if (JSON.stringify(topicTabs) !== JSON.stringify(expectedTabs)) {{
    throw new Error(`topic tabs should use fixed 11-section template, got ${{JSON.stringify(topicTabs)}}`);
  }}
  await page.goto({json.dumps(base_url + "/topics/digital-tourism?section=competitions")});
  await page.waitForSelector(".topic-loop-card[data-section-id='competitions'][role='button']", {{ timeout: 10000 }});
  await page.locator(".topic-loop-card[data-section-id='competitions'][role='button']").first().click();
  await page.waitForSelector("#drawer:not([hidden]) .topic-display-carousel[data-detail-carousel]", {{ timeout: 10000 }});
  const drawerCarouselBefore = await page.evaluate(() => {{
    const body = document.querySelector("#drawerBody");
    const carousel = document.querySelector("#drawer .topic-display-carousel[data-detail-carousel]");
    const slides = Array.from(carousel.querySelectorAll(".topic-display-carousel-slide"));
    const active = slides.findIndex((slide) => slide.classList.contains("is-active"));
    return {{
      mediaCount: Number(carousel.dataset.mediaCount || 0),
      activeCount: slides.filter((slide) => slide.classList.contains("is-active")).length,
      active,
      overflowY: getComputedStyle(body).overflowY,
      objectFits: Array.from(carousel.querySelectorAll("img")).map((img) => getComputedStyle(img).objectFit),
      loopTrack: !!body.querySelector("[data-drawer-loop-track]"),
    }};
  }});
  if (drawerCarouselBefore.mediaCount < 2) throw new Error(`drawer detail carousel should contain multiple media items, got ${{drawerCarouselBefore.mediaCount}}`);
  if (drawerCarouselBefore.activeCount !== 1) throw new Error(`drawer detail carousel should show one active image, got ${{drawerCarouselBefore.activeCount}}`);
  if (drawerCarouselBefore.overflowY !== "auto" && drawerCarouselBefore.overflowY !== "scroll") throw new Error(`drawer body should be scrollable, got ${{drawerCarouselBefore.overflowY}}`);
  if (!drawerCarouselBefore.loopTrack) throw new Error("drawer should keep auto-loop content track");
  if (!drawerCarouselBefore.objectFits.every((value) => value === "contain")) throw new Error(`drawer images should use contain, got ${{drawerCarouselBefore.objectFits.join(",")}}`);
  await page.waitForTimeout(3800);
  const drawerCarouselAfter = await page.evaluate(() => {{
    const slides = Array.from(document.querySelectorAll("#drawer .topic-display-carousel-slide"));
    return slides.findIndex((slide) => slide.classList.contains("is-active"));
  }});
  if (drawerCarouselAfter === drawerCarouselBefore.active) throw new Error("drawer detail carousel should auto-rotate");
}}
"""

    try:
        run_cli(["open", base_url + "/departments"])
        run_cli(["run-code", navigation_code])
        console_result = run_cli(["console", "error"]).stdout
        assert_no_browser_logic_errors(console_result)
    finally:
        subprocess.run([*cli, "close"], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def run_browser_admin_route_check(base_url):
    npx = shutil.which("npx")
    if not npx:
        raise RuntimeError("npx is required for the admin route check")

    cli = [npx, "--yes", "--package", "@playwright/cli", "playwright-cli", f"-s={PLAYWRIGHT_SESSION}"]

    def run_cli(args):
        return subprocess.run(
            [*cli, *args],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=True,
        )

    route_code = f"""
async (page) => {{
  await page.goto({json.dumps(base_url + "/login")});
  await page.fill("#username", "admin");
  await page.fill("#password", {json.dumps(ADMIN_PASSWORD)});
  await Promise.all([
    page.waitForURL(/\\/admin/, {{ timeout: 10000 }}),
    page.click("button[type=submit]")
  ]);
  await page.goto({json.dumps(base_url + "/admin?view=projects")});
  await page.waitForSelector(".portal-route-line", {{ timeout: 10000 }});
  const routes = await page.locator(".portal-route-line").allTextContents();
  if (!routes.includes("/departments")) throw new Error("project table missing school route");
  if (!routes.includes("/departments/finance")) throw new Error("project table missing department route");
  if (!routes.includes("/topics/modern-agriculture")) throw new Error("project table missing modern agriculture route");
  if (!routes.includes("/topics/smart-energy")) throw new Error("project table missing topic route");
  if (!routes.includes("/topics/campus-culture")) throw new Error("project table missing campus culture route");
  if (routes.includes("/topics/smart-construction")) throw new Error("project table should not seed smart construction as a ninth topic");
  await page.goto({json.dumps(base_url + "/admin?view=pages")});
  await page.waitForSelector("#projectSelect option", {{ timeout: 10000 }});
  await page.waitForSelector("#currentPortalStrip code", {{ timeout: 10000 }});
  const pageOptions = await page.locator("#projectSelect option").allTextContents();
  const currentPortalText = await page.locator("#currentPortalStrip").innerText();
  const currentPortalPreview = await page.locator("#currentPortalStrip a[href]").count();
  if (!pageOptions.some((text) => text.includes("/departments/finance"))) throw new Error("page project select missing department route");
  if (!pageOptions.some((text) => text.includes("/topics/modern-agriculture"))) throw new Error("page project select missing modern agriculture route");
  if (!pageOptions.some((text) => text.includes("/topics/smart-energy"))) throw new Error("page project select missing topic route");
  if (!currentPortalText.includes("/departments")) throw new Error("current portal strip missing route");
  if (currentPortalPreview < 1) throw new Error("current portal strip missing preview link");
  await page.goto({json.dumps(base_url + "/admin?view=deploy")});
  await page.waitForSelector("#deployProject option", {{ timeout: 10000 }});
  const deployOptions = await page.locator("#deployProject option").allTextContents();
  if (!deployOptions.some((text) => text.includes("/departments"))) throw new Error("deploy project select missing portal routes");
}}
"""

    try:
        run_cli(["open", base_url + "/login"])
        run_cli(["run-code", route_code])
        console_result = run_cli(["console", "error"]).stdout
        assert_no_browser_logic_errors(console_result)
    finally:
        subprocess.run([*cli, "close"], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def run_browser_admin_completion_check(base_url):
    npx = shutil.which("npx")
    if not npx:
        raise RuntimeError("npx is required for the admin completion workflow check")

    cli = [npx, "--yes", "--package", "@playwright/cli", "playwright-cli", f"-s={PLAYWRIGHT_SESSION}"]

    def run_cli(args):
        return subprocess.run(
            [*cli, *args],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=True,
        )

    workflow_code = f"""
async (page) => {{
  await page.goto({json.dumps(base_url + "/login")});
  await page.fill("#username", "admin");
  await page.fill("#password", {json.dumps(ADMIN_PASSWORD)});
  await Promise.all([
    page.waitForURL(/\\/admin/, {{ timeout: 10000 }}),
    page.click("button[type=submit]")
  ]);
  await page.goto({json.dumps(base_url + "/admin?view=dashboard")});
  await page.waitForSelector(".portal-completion-card", {{ timeout: 10000 }});
  await page.waitForSelector(".portal-task-card", {{ timeout: 10000 }});
  const taskCount = await page.locator(".portal-task-card").count();
  if (taskCount < 1) throw new Error("expected portal priority task cards");
  const firstTaskAction = await page.locator(".portal-task-card [data-dashboard-pages]").first().count();
  if (firstTaskAction < 1) throw new Error("expected portal task action");
  const financeCard = page.locator(".portal-completion-card").filter({{ hasText: "财政经济系" }}).first();
  await financeCard.getByRole("button", {{ name: "专业设置" }}).click();
  await page.waitForSelector("#pageForm:not([hidden])", {{ timeout: 10000 }});
  const selectedProject = await page.locator("#projectSelect option:checked").textContent();
  const category = await page.locator("#pageCategory").inputValue();
  const title = await page.locator("#pageTitle").inputValue();
  const source = await page.locator("#pageSource").inputValue();
  const bodyText = await page.locator("#richBody").innerText();
  if (!selectedProject.includes("财政经济系")) throw new Error(`expected finance project, got ${{selectedProject}}`);
  if (category !== "专业设置") throw new Error(`expected 专业设置 category, got ${{category}}`);
  if (title !== "专业设置与培养方向") throw new Error(`expected majors template title, got ${{title}}`);
  if (source !== "系部门户") throw new Error(`expected department source, got ${{source}}`);
  if (!bodyText.includes("专业结构") || !bodyText.includes("就业面向")) throw new Error("majors template body missing expected sections");
}}
"""

    try:
        run_cli(["open", base_url + "/login"])
        run_cli(["run-code", workflow_code])
        console_result = run_cli(["console", "error"]).stdout
        assert_no_browser_logic_errors(console_result)
    finally:
        subprocess.run([*cli, "close"], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main():
    process = None
    temp_dir = None
    base_url = BASE_URL

    try:
        if not base_url:
            temp_dir = tempfile.TemporaryDirectory()
            temp_path = Path(temp_dir.name)
            base_url = f"http://127.0.0.1:{PORT}"
            env = os.environ.copy()
            env.update(
                {
                    "HOST": "127.0.0.1",
                    "PORT": PORT,
                    "DB_PATH": str(temp_path / "expo-portal-logic.db"),
                    "UPLOAD_DIR": str(ROOT / "uploads"),
                    "ADMIN_PASSWORD": ADMIN_PASSWORD,
                    "ASSET_STORAGE_BACKEND": "local",
                }
            )
            process = subprocess.Popen(
                [sys.executable, "server.py"],
                cwd=ROOT,
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            wait_for_health(base_url)
        else:
            wait_for_health(base_url)

        department = assert_public_portal(base_url, "departments", "finance")
        topic = assert_public_portal(base_url, "topics", "smart-energy")
        modern_topic = assert_public_portal(base_url, "topics", "modern-agriculture")
        expect_http_error(404, f"{base_url}/api/portal/departments/not-a-portal")
        run_browser_qr_check(base_url)
        run_browser_department_layout_check(base_url)
        run_browser_portal_navigation_check(base_url)
        run_browser_admin_route_check(base_url)
        run_browser_admin_completion_check(base_url)

        print(f"department_portal_ok={department['pages']} pages coverage {department['coverage']}")
        print(f"topic_portal_ok={topic['pages']} pages coverage {topic['coverage']}")
        print(f"modern_agriculture_portal_ok={modern_topic['pages']} pages coverage {modern_topic['coverage']}")
        print("qr_boundary_ok=true")
        print("department_layout_ok=true")
        print("portal_navigation_ok=true")
        print("admin_route_table_ok=true")
        print("admin_completion_workflow_ok=true")
        print("portal_logic_smoke_ok=true")
    finally:
        if process and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        if temp_dir:
            temp_dir.cleanup()


if __name__ == "__main__":
    main()
