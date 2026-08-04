// 用 CDP 验证展厅页面渲染：等待数据加载后检查 DOM 并截图
// 用法: node sucai/verify_blueprint.js <url> <outdir> [checks...]
const fs = require("fs");
const path = require("path");

const url = process.argv[2];
const outDir = process.argv[3] || "/tmp/bp_shots";
const checks = process.argv.slice(4);

const PORT = 9333;
const CDP = "http://127.0.0.1:" + PORT;

async function main() {
  const targets = await (await fetch(CDP + "/json")).json();
  const page = targets.find((t) => t.type === "page");
  if (!page) throw new Error("no page target");
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  let msgId = 0;
  const pending = new Map();
  const send = (method, params = {}) =>
    new Promise((resolve, reject) => {
      const id = ++msgId;
      pending.set(id, { resolve, reject });
      ws.send(JSON.stringify({ id, method, params }));
    });
  ws.onmessage = (ev) => {
    const msg = JSON.parse(ev.data);
    if (msg.id && pending.has(msg.id)) {
      const p = pending.get(msg.id);
      pending.delete(msg.id);
      msg.error ? p.reject(new Error(msg.error.message)) : p.resolve(msg.result);
    }
  };
  await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
  await send("Page.enable");
  await send("Runtime.enable");
  // 等待渲染完成
  for (let i = 0; i < 40; i++) {
    const r = await send("Runtime.evaluate", {
      expression:
        "({cards: document.querySelectorAll('.dept-card').length, topics: document.querySelectorAll('.topic-card').length, ready: !!document.getElementById('deptGrid').children.length})",
      returnByValue: true,
    });
    const v = r.result.value;
    if (v.ready) {
      console.log("RENDER_READY cards=" + v.cards + " topics=" + v.topics);
      break;
    }
    await new Promise((r) => setTimeout(r, 500));
  }
  // 执行检查
  for (const expr of checks) {
    const r = await send("Runtime.evaluate", { expression: expr, returnByValue: true });
    console.log("CHECK " + expr + " => " + JSON.stringify(r.result.value));
  }
  // 截图
  const shot = await send("Page.captureScreenshot", { format: "png" });
  fs.mkdirSync(outDir, { recursive: true });
  const name = url.replace(/[^a-z0-9]+/gi, "_").slice(0, 60) + ".png";
  fs.writeFileSync(path.join(outDir, name), Buffer.from(shot.data, "base64"));
  console.log("SHOT " + path.join(outDir, name));
  ws.close();
}

main().catch((e) => { console.error("FAIL", e.message); process.exit(1); });
