import os
import shutil
import subprocess


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_URL = os.environ.get("EXPO_BASE_URL", "http://127.0.0.1:8000")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "123456")
PLAYWRIGHT_SESSION = os.environ.get("ADMIN_IA_PLAYWRIGHT_SESSION") or f"admin-ia-{os.getpid()}"


def run_cli(args, check=True):
    npx = shutil.which("npx")
    if not npx:
        raise RuntimeError("npx is required for the admin IA browser check")
    cli = [npx, "--yes", "--package", "@playwright/cli", "playwright-cli", f"-s={PLAYWRIGHT_SESSION}"]
    result = subprocess.run(
        [*cli, *args],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=check,
    )
    return result


def main():
    code = f"""
async (page) => {{
  await page.goto({BASE_URL + "/login"!r});
  await page.fill("#username", "admin");
  await page.fill("#password", {ADMIN_PASSWORD!r});
  await page.click("button[type=submit]");
  await page.waitForSelector("#nav button", {{ timeout: 10000 }});

  const navLabels = await page.locator("#nav button").evaluateAll((nodes) => nodes.map((node) => node.textContent.trim()));
  const expectedNav = ["工作台", "门户管理", "内容工作台", "素材中心", "审核发布", "数据与报表", "系统设置"];
  if (JSON.stringify(navLabels) !== JSON.stringify(expectedNav)) throw new Error(`nav mismatch: ${{JSON.stringify(navLabels)}}`);

  const visibleBySelector = async (selector) => await page.locator(selector).evaluate((el) => !el.hidden && getComputedStyle(el).display !== "none");

  await page.click("#nav button[data-view='pages']");
  await page.waitForSelector("#contentWorkspaceNav:not([hidden])");
  await page.waitForSelector("#contentPortalTree button");
  const contentTitle = (await page.textContent("#viewTitle")).trim();
  if (contentTitle !== "内容工作台") throw new Error(`content title mismatch: ${{contentTitle}}`);
  if (!(await visibleBySelector(".portal-tree-panel"))) throw new Error("portal tree should be visible in content mode");
  if (!(await visibleBySelector(".workspace-status-panel"))) throw new Error("workspace status should be visible in content mode");
  if ((await page.locator("#workspaceActionList button").count()) < 1) throw new Error("workspace actions should be visible");
  if (!(await visibleBySelector(".structured-panel"))) throw new Error("structured panel should be visible in content mode");
  if (await visibleBySelector(".lowcode-template-panel")) throw new Error("template panel should be hidden in content mode");
  const workflowLayout = await page.evaluate(() => {{
    const shell = document.querySelector(".content-workflow-shell");
    const tree = document.querySelector(".portal-tree-panel");
    const board = document.querySelector(".module-coverage-panel");
    const status = document.querySelector(".workspace-status-panel");
    const rect = (node) => {{
      const box = node.getBoundingClientRect();
      return {{ x: box.x, y: box.y, width: box.width, height: box.height }};
    }};
    return {{ shell: rect(shell), tree: rect(tree), board: rect(board), status: rect(status), overflow: document.documentElement.scrollWidth > window.innerWidth + 1 }};
  }});
  if (workflowLayout.overflow) throw new Error("content workflow creates horizontal overflow");
  if (workflowLayout.tree.width < 160 || workflowLayout.board.width < 360 || workflowLayout.status.width < 170) throw new Error(`workflow columns too narrow: ${{JSON.stringify(workflowLayout)}}`);
  if (!(workflowLayout.tree.x < workflowLayout.board.x && workflowLayout.board.x < workflowLayout.status.x)) throw new Error(`workflow columns are not ordered: ${{JSON.stringify(workflowLayout)}}`);

  await page.click("#moduleLibrary [data-module-filter]");
  if ((await page.locator(".module-library article.is-active").count()) !== 1) throw new Error("module board should mark selected module");

  await page.click("[data-content-mode='templates']");
  if (!(await visibleBySelector(".lowcode-template-panel"))) throw new Error("template panel should be visible in templates mode");
  if (await visibleBySelector(".structured-panel")) throw new Error("structured panel should be hidden in templates mode");

  await page.click("#nav button[data-view='reports']");
  const reportTitle = (await page.textContent("#viewTitle")).trim();
  if (reportTitle !== "数据与报表") throw new Error(`report title mismatch: ${{reportTitle}}`);
  if (!(await visibleBySelector(".lowcode-report-panel"))) throw new Error("lowcode report panel should be visible in reports mode");
  if (await visibleBySelector(".lowcode-template-panel")) throw new Error("template panel should be hidden in reports mode");

  await page.click("#nav button[data-view='settings']");
  await page.waitForSelector("#settingsView.active");
  const settingsTitle = (await page.textContent("#viewTitle")).trim();
  if (settingsTitle !== "系统设置") throw new Error(`settings title mismatch: ${{settingsTitle}}`);
  await page.click("[data-settings-view='deploy']");
  await page.waitForSelector("#deployView.active");
  const deployTitle = (await page.textContent("#viewTitle")).trim();
  if (deployTitle !== "展厅发布") throw new Error(`deploy title mismatch: ${{deployTitle}}`);

  await page.screenshot({{ path: "output/playwright/admin-ia-phase1.png", fullPage: true }});
}}
"""
    try:
        run_cli(["open", f"{BASE_URL}/login"])
        run_cli(["run-code", code])
        screenshot = run_cli(["screenshot"], check=False)
        if screenshot.returncode == 0:
            print(screenshot.stdout)
        console = run_cli(["console", "error"], check=False)
        if "Errors: 0" not in console.stdout:
            raise RuntimeError(console.stdout)
    finally:
        run_cli(["close"], check=False)
    print("admin_ia_phase1_browser_ok=true")


if __name__ == "__main__":
    main()
