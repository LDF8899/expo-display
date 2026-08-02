const $ = (id) => document.getElementById(id);
const state = { user: null, csrfToken: "", projects: [], users: [], pages: [], assets: [], activeView: "dashboard", editingProjectId: "", editingCode: "", assetTargetInput: "", assetReturnView: "", previewImageObjectUrl: "" };
const richTemplates = {
  news: {
    category: "校园新闻",
    source: "党委宣传部",
    title: "学校召开专题会议推进重点工作",
    subtitle: "会议围绕人才培养、专业建设、校园文化和服务地方发展等内容进行部署。",
    body: "<p>近日，学校召开专题会议，围绕近期重点工作进行安排部署。</p><h2>会议重点</h2><ul><li>聚焦专业建设和人才培养质量提升。</li><li>加强校园文化建设，营造积极向上的育人环境。</li><li>完善服务保障机制，提升师生获得感。</li></ul><blockquote>相关部门表示，将进一步细化任务清单，推动各项工作落地见效。</blockquote>",
  },
  activity: {
    category: "活动报道",
    source: "学生工作处",
    title: "学校开展校园文化主题活动",
    subtitle: "活动通过展示、互动和实践环节，集中呈现学生风采与校园文化建设成果。",
    body: "<p>为丰富校园文化生活，展示学生综合素养，学校组织开展校园文化主题活动。</p><h2>活动亮点</h2><p>本次活动突出学生主体地位，鼓励学生在实践中展示技能、交流经验、提升能力。</p><ul><li>社团展示展现青春活力。</li><li>技能实践体现专业特色。</li><li>志愿服务传递校园温度。</li></ul>",
  },
  notice: {
    category: "通知公告",
    source: "学校办公室",
    title: "关于近期校园开放活动安排的通知",
    subtitle: "请相关部门和师生按安排做好接待、讲解、展示和保障工作。",
    body: "<p>根据学校工作安排，近期将组织校园开放活动。现将有关事项通知如下：</p><h2>一、活动安排</h2><ol><li>活动地点：学校主校区及相关实训场所。</li><li>展示内容：校园环境、专业建设、学生作品和特色文化。</li></ol><h2>二、工作要求</h2><p>请各单位提前做好资料准备、现场布置和安全保障。</p>",
  },
  feature: {
    category: "成果展示",
    source: "展示中心",
    title: "特色项目图文展示",
    subtitle: "集中呈现学校办学特色、专业成果和育人成效。",
    body: "<p>本展示项目用于介绍学校特色项目、专业建设成果或校园文化成果。</p><h2>项目概况</h2><p>围绕地方产业需求和学生成长需求，项目持续推进课程建设、实践教学和社会服务。</p><h2>建设成效</h2><ul><li>形成具有辨识度的专业特色。</li><li>提升学生实践能力和综合素养。</li><li>增强学校服务地方发展的能力。</li></ul>",
  },
  profile: {
    category: "人物介绍",
    source: "学校展示",
    title: "优秀师生人物介绍",
    subtitle: "聚焦校园人物故事，展示教师风采、学生成长和榜样力量。",
    body: "<p>本展示项目用于介绍学校教师、学生、校友或团队代表。</p><h2>人物简介</h2><p>请在这里填写人物姓名、所在学院或部门、专业方向、岗位职责及主要经历。</p><h2>主要事迹</h2><ul><li>在教育教学、技能竞赛、科研服务或校园活动中取得突出成绩。</li><li>积极参与专业建设、社会服务、志愿服务或文化传承工作。</li></ul>",
  },
};
const templateGuides = {
  news: ["新闻模板", "适合会议、工作动态、学校新闻；展览页会突出标题、正文要点和引用语。"],
  activity: ["活动模板", "适合校园活动、社团展示、实践过程；展览页以活动概况和亮点列表为主。"],
  notice: ["公告模板", "适合通知、安排、开放日说明；展览页会按事项和要求组织内容。"],
  feature: ["图文模板", "适合成果、项目、专业建设；展览页适合搭配封面图和建设成效列表。"],
  profile: ["人物模板", "适合老师、学生、校友和团队介绍；展览页重点呈现简介和主要事迹。"],
};
const allowedRichTags = new Set(["A", "B", "BLOCKQUOTE", "BR", "DIV", "EM", "FIGCAPTION", "FIGURE", "H2", "H3", "H4", "HR", "I", "IMG", "LI", "OL", "P", "SPAN", "STRONG", "U", "UL"]);

const views = {
  dashboard: ["数据看板", "查看项目、内容、审核和部署概况。"],
  users: ["老师管理", "创建、导入、禁用和维护老师账号。"],
  projects: ["项目管理", "管理员分配项目，老师提交配置审核。"],
  pages: ["内容管理", "编辑展示页，审核通过后生成二维码。"],
  assets: ["资源管理", "上传、复用和删除展示图片资源。"],
  reviews: ["内容审核", "审核页面草稿、删除申请和项目配置草稿。"],
  deploy: ["部署管理", "选择当前展出项目和实际展出页面。"],
  logs: ["操作日志", "查询和导出关键操作日志。"],
  account: ["个人设置", "查看个人资料并修改密码。"],
};
const teacherViews = {
  pages: ["上传展览资料", "上传、编辑并提交展览资料，审核通过后进入展示。"],
  assets: ["图片素材", "上传和复用展览图片素材。"],
  projects: ["展览信息", "查看所属展览项目，提交基础信息修改。"],
  account: ["个人设置", "查看个人资料并修改密码。"],
};
const teacherViewOrder = ["pages", "assets", "projects", "account"];

function isAdmin() { return state.user && state.user.role === "admin"; }
function isTeacherPortal() { return !isAdmin(); }
function appBasePath() { return isTeacherPortal() ? "/teacher" : "/admin"; }
function viewMeta(view) { return isTeacherPortal() && teacherViews[view] ? teacherViews[view] : views[view]; }
function escapeHtml(value) {
  return String(value || "").replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;").replaceAll("'", "&#39;");
}
function statusText(status) {
  return { approved: "已通过", pending: "待审核", rejected: "已驳回", pending_delete: "删除待审", deleted: "已删除" }[status] || status || "-";
}
function badge(status) {
  const cls = status === "approved" ? "success" : status === "rejected" || status === "deleted" ? "danger" : "warn";
  return `<span class="badge ${cls}">${escapeHtml(statusText(status))}</span>`;
}
function setStatus(node, text, type = "") {
  node.textContent = text || "";
  node.dataset.state = type;
}
function setText(node, text) {
  if (node) node.textContent = text || "";
}
async function api(url, options) {
  const requestOptions = options ? { ...options } : {};
  const method = String(requestOptions.method || "GET").toUpperCase();
  if (method !== "GET" && state.csrfToken) {
    requestOptions.headers = { ...(requestOptions.headers || {}), "X-CSRF-Token": state.csrfToken };
  }
  const res = await fetch(url, requestOptions);
  if (res.status === 401) location.href = "/login";
  return res;
}
async function jsonApi(url, options) {
  const res = await api(url, options);
  const data = await res.json();
  if (!data.ok) throw new Error(data.error || "请求失败");
  return data;
}
function body(data) {
  return { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data || {}) };
}
function putBody(data) {
  return { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data || {}) };
}
function formatTime(value) {
  if (!value) return "-";
  const d = new Date(value);
  return Number.isNaN(d.getTime()) ? value : d.toLocaleString("zh-CN", { hour12: false });
}
function sanitizeRichHtml(html) {
  const template = document.createElement("template");
  template.innerHTML = String(html || "");
  Array.from(template.content.querySelectorAll("script, style, iframe, object, embed")).forEach((node) => node.remove());
  Array.from(template.content.querySelectorAll("*")).forEach((node) => {
    if (!allowedRichTags.has(node.tagName)) {
      node.replaceWith(document.createTextNode(node.textContent || ""));
      return;
    }
    Array.from(node.attributes).forEach((attribute) => {
      const name = attribute.name.toLowerCase();
      const value = attribute.value || "";
      if (name.startsWith("on") || name === "style") {
        node.removeAttribute(attribute.name);
        return;
      }
      if (node.tagName === "A" && name === "href") {
        if (/^(https?:|mailto:|tel:|\/)/i.test(value)) {
          node.setAttribute("target", "_blank");
          node.setAttribute("rel", "noopener");
          return;
        }
      }
      if (node.tagName === "IMG" && ["src", "alt"].includes(name)) {
        if (name === "src" && !/^(https?:|\/|data:image\/)/i.test(value)) node.removeAttribute(attribute.name);
        return;
      }
      if (name !== "class") node.removeAttribute(attribute.name);
    });
  });
  return template.innerHTML.trim();
}
function textToRichHtml(value) {
  return String(value || "")
    .split(/\n{2,}/)
    .map((item) => item.trim())
    .filter(Boolean)
    .map((item) => `<p>${escapeHtml(item).replaceAll("\n", "<br>")}</p>`)
    .join("");
}
function normalizeRichBody(value) {
  const raw = String(value || "").trim();
  if (!raw) return "";
  return /<[a-z][\s\S]*>/i.test(raw) ? sanitizeRichHtml(raw) : textToRichHtml(raw);
}
function setRichBody(value) {
  $("richBody").innerHTML = normalizeRichBody(value);
  syncRichBody();
}
function syncRichBody() {
  $("pageBody").value = sanitizeRichHtml($("richBody").innerHTML);
  updatePagePreview();
}
function setTemplateGuide(templateKey) {
  const guide = templateGuides[templateKey] || ["自定义内容", "可按展览资料自由编辑字段；右侧预览会同步当前标题、封面和正文结构。"];
  setText($("templateGuideTitle"), guide[0]);
  setText($("templateGuideScene"), guide[1]);
  setText($("templateGuideSummary"), templateKey ? "已套用模板，可继续替换文字和图片" : "选择模板后查看内容结构和展示效果");
}
function updatePagePreview() {
  if (!$("previewTitle")) return;
  setText($("previewCode"), $("pageCode").value.trim() ? `编号 ${$("pageCode").value.trim()}` : "编号");
  setText($("previewCategory"), $("pageCategory").value.trim() || "栏目");
  setText($("previewSource"), $("pageSource").value.trim() || "来源");
  setText($("previewTitle"), $("pageTitle").value.trim() || "标题会显示在这里");
  setText($("previewSubtitle"), $("pageSubtitle").value.trim() || "副标题会显示在这里");
  $("previewBody").innerHTML = $("pageBody").value.trim() || "<p>正文预览会显示在这里。</p>";
  const imageUrl = $("pageImageUrl").value.trim() || state.previewImageObjectUrl;
  if (imageUrl) {
    $("previewImage").src = imageUrl;
    $("previewMedia").hidden = false;
  } else {
    $("previewImage").removeAttribute("src");
    $("previewMedia").hidden = true;
  }
}
function setPreviewFile(file) {
  if (state.previewImageObjectUrl) URL.revokeObjectURL(state.previewImageObjectUrl);
  state.previewImageObjectUrl = file ? URL.createObjectURL(file) : "";
  updatePagePreview();
}
function buildQrUrl(projectId, code) {
  const url = new URL("/display", location.origin);
  url.searchParams.set("project", projectId);
  url.searchParams.set("code", code);
  url.searchParams.set("source", "expo-admin");
  return url.toString();
}

function setupNav() {
  document.body.classList.toggle("teacher-portal", isTeacherPortal());
  const order = isAdmin() ? ["dashboard", "users", "projects", "pages", "assets", "reviews", "deploy", "logs", "account"] : teacherViewOrder;
  $("nav").innerHTML = order.map((view) => `<button type="button" data-view="${view}">${viewMeta(view)[0]}</button>`).join("");
  $("nav").querySelectorAll("button").forEach((button) => button.addEventListener("click", () => showView(button.dataset.view)));
  document.querySelectorAll(".admin-only").forEach((node) => { node.hidden = !isAdmin(); });
  $("brandTitle").textContent = isAdmin() ? "展示后台" : "资料上传";
  $("consoleEyebrow").textContent = isAdmin() ? "Expo Display Console" : "Teacher Submission";
  document.title = isAdmin() ? "展示后台管理" : "展览资料上传";
  $("roleBadge").textContent = isAdmin() ? "管理员" : "老师工作台";
  $("projectsHeading").textContent = isAdmin() ? "项目管理" : "展览信息";
  $("projectsIntro").textContent = isAdmin() ? "管理员创建和分配项目；老师可提交自己项目的配置修改审核。" : "查看自己负责的展览项目，必要时提交基础信息修改。";
  $("projectFormTitle").textContent = isAdmin() ? "项目配置" : "展览信息编辑";
  $("projectSubmitButton").textContent = isAdmin() ? "保存/提交审核" : "提交信息修改";
  $("pagesHeading").textContent = isAdmin() ? "内容管理" : "上传展览资料";
  $("pagesIntro").textContent = isAdmin() ? "老师提交后等待审核；已通过内容可生成二维码。" : "维护自己项目下的展览资料，提交后由管理员审核发布。";
  $("newPage").textContent = isAdmin() ? "新建内容" : "上传资料";
  $("pageFormTitle").textContent = isAdmin() ? "内容编辑" : "资料编辑";
  $("pageSubmitButton").textContent = isAdmin() ? "保存/提交审核" : "提交审核";
  $("assetsHeading").textContent = isAdmin() ? "资源管理" : "图片素材";
  $("assetsIntro").textContent = isAdmin() ? "上传、复用和删除图片资源；老师只能管理自己上传的资源。" : "上传展览资料所需图片，只能查看和管理自己上传的素材。";
}
function showView(view) {
  if (isTeacherPortal() && !teacherViews[view]) view = "pages";
  if (!views[view]) view = isAdmin() ? "dashboard" : "pages";
  state.activeView = view;
  document.querySelectorAll(".view").forEach((node) => node.classList.toggle("active", node.id === `${view}View`));
  $("nav").querySelectorAll("button").forEach((button) => button.classList.toggle("active", button.dataset.view === view));
  $("viewTitle").textContent = viewMeta(view)[0];
  $("viewIntro").textContent = viewMeta(view)[1];
  history.replaceState(null, "", `${appBasePath()}?view=${view}`);
  refreshView(view);
}

async function loadSession() {
  const data = await jsonApi("/api/session");
  state.user = data.user;
  state.csrfToken = data.csrfToken || "";
  if (!state.user) location.href = "/login";
  $("accountName").textContent = `${state.user.displayName} (${state.user.username})`;
  $("roleBadge").textContent = state.user.role === "admin" ? "管理员" : "老师";
  $("profileBox").innerHTML = `
    <strong>${escapeHtml(state.user.displayName)}</strong>
    <p>账号：${escapeHtml(state.user.username)}　角色：${state.user.role === "admin" ? "管理员" : "老师"}　部门：${escapeHtml(state.user.department || "-")}</p>
  `;
}
async function loadProjects(preferredId) {
  const data = await jsonApi("/api/projects");
  state.projects = data.projects || [];
  const selected = state.projects.find((p) => String(p.id) === String(preferredId)) || state.projects[0];
  $("projectSelect").innerHTML = state.projects.map((p) => `<option value="${p.id}">${escapeHtml(p.name)}</option>`).join("");
  $("deployProject").innerHTML = state.projects.map((p) => `<option value="${p.id}">${escapeHtml(p.name)}</option>`).join("");
  if (selected) {
    $("projectSelect").value = selected.id;
    $("deployProject").value = selected.id;
  }
}
async function loadUsers() {
  if (!isAdmin()) return;
  const data = await jsonApi("/api/users");
  state.users = data.users || [];
  $("projectOwner").innerHTML = state.users.filter((u) => u.role === "teacher").map((u) => `<option value="${u.username}">${escapeHtml(u.displayName)} (${escapeHtml(u.username)})</option>`).join("");
}

async function renderDashboard() {
  const data = await jsonApi("/api/admin/dashboard");
  const s = data.dashboard.summary || {};
  const ops = data.dashboard.operations || {};
  const ready = ops.ready || {};
  const checks = ready.checks || {};
  const deployed = ops.deployed || {};
  const pending = ops.pending || {};
  const config = ops.config || {};
  const configIssues = [...(config.errors || []), ...(config.warnings || [])];
  const readyOk = Boolean(ready.ok);
  $("dashboardView").innerHTML = `
    <div class="metric-grid">
      <article class="metric"><span>项目</span><strong>${s.projects || 0}</strong></article>
      <article class="metric"><span>展示页</span><strong>${s.pages || 0}</strong></article>
      <article class="metric"><span>待审核</span><strong>${s.pendingPages || 0}</strong></article>
      <article class="metric"><span>已驳回</span><strong>${s.rejectedPages || 0}</strong></article>
    </div>
    <section class="panel ops-panel">
      <div class="panel-head"><div><h2>运行状态</h2><p>${formatTime(ready.time)}</p></div><span class="badge ${readyOk ? "success" : "danger"}">${readyOk ? "Ready" : "异常"}</span></div>
      <div class="ops-grid">
        <article><span>数据库</span><strong>${checks.database && checks.database.ok ? "正常" : "异常"}</strong><small>${escapeHtml((checks.database && checks.database.backend) || "-")}</small></article>
        <article><span>资源存储</span><strong>${checks.storage && checks.storage.ok ? "正常" : "异常"}</strong><small>${escapeHtml((checks.storage && checks.storage.backend) || "-")}</small></article>
        <article><span>运行模式</span><strong>${checks.runtime && checks.runtime.onlineMode ? "线上" : "本地"}</strong><small>${escapeHtml((checks.runtime && checks.runtime.publicBaseUrl) || checks.runtime && checks.runtime.host || "-")}</small></article>
        <article><span>资源数</span><strong>${ops.assets ? ops.assets.count : 0}</strong><small>${isAdmin() ? "全部资源" : "我的资源"}</small></article>
      </div>
    </section>
    <section class="panel ops-panel">
      <div class="panel-head">
        <div><h2>上线配置</h2><p>公网部署前需要处理的配置项</p></div>
        <div class="toolbar"><a class="button ghost" href="/api/admin/acceptance-report.json">导出验收报告</a><span class="badge ${config.ok ? "success" : "danger"}">${config.ok ? "可用" : "需处理"}</span></div>
      </div>
      ${configIssues.length ? `<div class="config-issue-list">${configIssues.map((item) => `
        <article class="config-issue ${item.level === "error" ? "danger" : "warn"}">
          <strong>${escapeHtml(item.code)}</strong>
          <span>${escapeHtml(item.message)}</span>
        </article>
      `).join("")}</div>` : `<div class="empty">暂无上线配置风险</div>`}
    </section>
    <section class="panel ops-panel">
      <div class="panel-head"><div><h2>部署状态</h2><p>当前大屏发布目标</p></div></div>
      <div class="ops-grid">
        <article><span>欢迎页</span><strong>${escapeHtml(deployed.welcomeProjectName || s.welcomeDeployed || "未部署")}</strong><small>ID ${deployed.welcomeProjectId || "-"}</small></article>
        <article><span>内容项目</span><strong>${escapeHtml(deployed.contentProjectName || s.contentDeployed || "未部署")}</strong><small>ID ${deployed.contentProjectId || "-"}</small></article>
        <article><span>页面待审</span><strong>${pending.pages || 0}</strong><small>提交后需审核</small></article>
        <article><span>项目待审</span><strong>${pending.projects || 0}</strong><small>配置变更</small></article>
      </div>
    </section>
  `;
}
function renderUsers() {
  $("usersTable").innerHTML = state.users.length ? state.users.map((u) => `
    <tr>
      <td>${escapeHtml(u.username)}</td><td>${escapeHtml(u.displayName)}</td><td>${escapeHtml(u.department || "-")}</td>
      <td>${u.projectCount || 0}</td><td>${u.enabled ? badge("approved") : badge("deleted")}</td>
      <td><div class="actions">
        <button class="button small" data-user-edit="${u.username}">编辑</button>
        <button class="button small" data-user-reset="${u.username}">重置密码</button>
        <button class="button small ${u.enabled ? "danger" : ""}" data-user-toggle="${u.username}" data-enabled="${u.enabled ? "0" : "1"}">${u.enabled ? "禁用" : "启用"}</button>
      </div></td>
    </tr>`).join("") : `<tr><td colspan="6" class="empty">暂无老师</td></tr>`;
}
function renderProjects() {
  const pagesLabel = isAdmin() ? "内容" : "资料";
  const configLabel = isAdmin() ? "配置" : "信息";
  const emptyText = isAdmin() ? "暂无项目" : "暂无分配的展览项目";
  $("projectsTable").innerHTML = state.projects.length ? state.projects.map((p) => `
    <tr>
      <td><strong>${escapeHtml(p.name)}</strong><div class="muted">ID ${p.id}</div></td>
      <td>${escapeHtml(p.ownerDisplayName || p.ownerUsername || "-")}</td>
      <td>${badge(p.configStatus || "approved")} ${p.deployed ? '<span class="badge success">欢迎页</span>' : ""} ${p.contentDeployed ? '<span class="badge success">内容部署</span>' : ""}</td>
      <td>${p.pageCount || 0} / 待审 ${p.pendingPageCount || 0}</td>
      <td><div class="actions">
        <button class="button small primary" data-project-pages="${p.id}">${pagesLabel}</button>
        <button class="button small" data-project-edit="${p.id}">${configLabel}</button>
        <button class="button small" data-project-history="${p.id}">历史</button>
        ${isAdmin() ? `<button class="button small danger" data-project-delete="${p.id}">删除</button>` : ""}
      </div></td>
    </tr>`).join("") : `<tr><td colspan="5" class="empty">${emptyText}</td></tr>`;
}
async function loadPages(projectId = $("projectSelect").value) {
  if (!projectId) { state.pages = []; renderPages(); return; }
  const data = await jsonApi(`/api/projects/${projectId}/pages`);
  state.pages = data.pages || [];
  renderPages();
}
function renderPages() {
  const filter = $("pageStatusFilter").value;
  const list = filter ? state.pages.filter((p) => p.reviewStatus === filter) : state.pages;
  const editLabel = isAdmin() ? "编辑" : "编辑资料";
  const deleteLabel = isAdmin() ? "删除" : "申请删除";
  const emptyText = isAdmin() ? "暂无内容" : "暂无展览资料";
  $("pagesTable").innerHTML = list.length ? list.map((p) => {
    const qr = p.qrAvailable ? `<a class="button small" target="_blank" href="/api/qr?data=${encodeURIComponent(buildQrUrl(p.projectId, p.code))}">二维码</a>` : `<span class="muted">审核后可用</span>`;
    return `<tr>
      <td>${escapeHtml(p.code)}</td><td>${escapeHtml(p.title)}${p.reviewNote ? `<div class="muted">驳回：${escapeHtml(p.reviewNote)}</div>` : ""}</td>
      <td>${escapeHtml(p.category || "-")}</td><td>${badge(p.reviewStatus)}</td><td>${qr}</td>
      <td><div class="actions">
        <button class="button small primary" data-page-edit="${escapeHtml(p.code)}">${editLabel}</button>
        <button class="button small" data-page-history="${escapeHtml(p.code)}">历史</button>
        ${p.qrAvailable ? `<a class="button small" target="_blank" href="${buildQrUrl(p.projectId, p.code)}">预览</a>` : ""}
        <button class="button small danger" data-page-delete="${escapeHtml(p.code)}">${deleteLabel}</button>
      </div></td>
    </tr>`;
  }).join("") : `<tr><td colspan="6" class="empty">${emptyText}</td></tr>`;
}
function shortReviewValue(value) {
  const text = String(value || "");
  if (!text) return "-";
  return text.length > 160 ? `${text.slice(0, 160)}...` : text;
}
function renderReviewDiffs(item) {
  const changed = (item.diffs || []).filter((diff) => diff.changed);
  if (!changed.length) return `<div class="muted">暂无字段变化</div>`;
  return `
    <div class="review-diff-grid">
      ${changed.slice(0, 8).map((diff) => `
        <div class="review-diff-row">
          <strong>${escapeHtml(diff.label || diff.field)}</strong>
          <span>${escapeHtml(shortReviewValue(diff.before))}</span>
          <span>${escapeHtml(shortReviewValue(diff.after))}</span>
        </div>
      `).join("")}
    </div>
  `;
}
function reviewOperationText(item, type) {
  if (type === "project") return "项目配置";
  if (item.operation === "delete") return "删除申请";
  return "内容变更";
}
function historyTitle(item, type) {
  if (type === "project") return (item.snapshot && item.snapshot.name) || item.projectName || "项目配置";
  return (item.snapshot && item.snapshot.title) || item.code || "内容";
}
function renderVersionHistory(containerId, versions, type) {
  $(containerId).innerHTML = versions.length ? versions.map((item) => `
    <article class="history-item">
      <header>
        <strong>${escapeHtml(historyTitle(item, type))}</strong>
        ${badge(item.status)}
      </header>
      <div class="history-meta">
        <span>${escapeHtml(reviewOperationText(item, type))}</span>
        <span>提交：${escapeHtml(item.submittedBy || "-")} / ${formatTime(item.submittedAt)}</span>
        <span>审核：${escapeHtml(item.reviewedBy || "-")} / ${formatTime(item.reviewedAt)}</span>
      </div>
      ${item.reviewNote ? `<p class="muted">审核意见：${escapeHtml(item.reviewNote)}</p>` : ""}
      ${item.changes ? `<p>${escapeHtml(item.changes)}</p>` : ""}
      ${renderReviewDiffs(item)}
      ${type === "page" && item.previewUrl ? `<div class="actions"><a class="button small" target="_blank" href="${escapeHtml(item.previewUrl)}">版本预览</a></div>` : ""}
    </article>
  `).join("") : `<div class="empty">暂无版本历史</div>`;
}
async function showProjectHistory(projectId) {
  const data = await jsonApi(`/api/projects/${projectId}/versions`);
  $("projectHistoryTitle").textContent = `项目历史：${data.project ? data.project.name : projectId}`;
  renderVersionHistory("projectHistory", data.versions || [], "project");
  $("projectHistoryPanel").hidden = false;
  $("projectHistoryPanel").scrollIntoView({ behavior: "smooth", block: "nearest" });
}
async function showPageHistory(code) {
  const projectId = $("projectSelect").value;
  const data = await jsonApi(`/api/projects/${projectId}/pages/${encodeURIComponent(code)}/versions`);
  $("pageHistoryTitle").textContent = `内容历史：${code}`;
  renderVersionHistory("pageHistory", data.versions || [], "page");
  $("pageHistoryPanel").hidden = false;
  $("pageHistoryPanel").scrollIntoView({ behavior: "smooth", block: "nearest" });
}
async function renderReviews() {
  const data = await jsonApi("/api/reviews?status=pending");
  const pages = data.reviews.pages || [];
  const projects = data.reviews.projects || [];
  const items = [
    ...projects.map((r) => ({ ...r, type: "projects", label: "项目配置" })),
    ...pages.map((r) => ({ ...r, type: "pages", label: r.operation === "delete" ? "删除申请" : "页面内容" })),
  ];
  $("reviewsList").innerHTML = items.length ? items.map((r) => `
    <article class="review-item">
      <header>
        <label><input type="checkbox" data-review-check="${r.type}:${r.id}" /> <strong>${r.label}</strong> ${escapeHtml(r.projectName || "")}</label>
        <span>${formatTime(r.submittedAt)} / ${escapeHtml(r.submittedBy)}</span>
      </header>
      <div class="review-preview">
        <strong>${escapeHtml((r.snapshot && (r.snapshot.title || r.snapshot.name)) || r.code || "")}</strong>
        <p>${escapeHtml(r.changes || "无变更摘要")}</p>
        ${r.snapshot && r.snapshot.subtitle ? `<p>${escapeHtml(r.snapshot.subtitle)}</p>` : ""}
        ${renderReviewDiffs(r)}
      </div>
      <div class="actions">
        ${r.type === "pages" ? `<a class="button small" target="_blank" href="/display?project=${r.projectId}&code=${encodeURIComponent(r.code)}">当前发布版</a>` : ""}
        ${r.type === "pages" && r.previewUrl ? `<a class="button small" target="_blank" href="${escapeHtml(r.previewUrl)}">草稿预览</a>` : ""}
        <button class="button small primary" data-review-approve="${r.type}:${r.id}">通过</button>
        <button class="button small danger" data-review-reject="${r.type}:${r.id}">驳回</button>
      </div>
    </article>`).join("") : `<div class="empty">暂无待审核内容</div>`;
}
async function renderDeploy() {
  const projectId = $("deployProject").value || (state.projects[0] && state.projects[0].id);
  if (!projectId) { $("deployPages").innerHTML = `<div class="empty">暂无项目</div>`; return; }
  const pagesData = await jsonApi(`/api/projects/${projectId}/pages`);
  const deployed = await jsonApi(`/api/deploy/content/${projectId}`);
  const checkData = await jsonApi(`/api/deploy/check/${projectId}`);
  const selected = new Set((deployed.pageIds || []).map(String));
  const approved = (pagesData.pages || []).filter((p) => p.reviewStatus === "approved" && p.enabled);
  renderDeployCheck(checkData.check || {});
  $("deployPages").innerHTML = approved.length ? approved.map((p) => `
    <label class="check-item"><input type="checkbox" value="${p.id}" ${selected.size ? (selected.has(String(p.id)) ? "checked" : "") : "checked"} /> ${escapeHtml(p.code)} - ${escapeHtml(p.title)}</label>
  `).join("") : `<div class="empty">该项目暂无已通过页面</div>`;
}
function renderDeployCheck(check) {
  const errors = check.errors || [];
  const warnings = check.warnings || [];
  const stateLabel = errors.length ? "发布前必须处理" : warnings.length ? "可以发布，但建议先处理" : "检查通过";
  $("deployCheck").innerHTML = `
    <div class="deploy-check-box ${errors.length ? "danger" : warnings.length ? "warn" : "success"}">
      <strong>${stateLabel}</strong>
      <span>可发布页面 ${check.eligiblePageIds ? check.eligiblePageIds.length : 0}，已选 ${check.pageIds ? check.pageIds.length : 0}</span>
      ${errors.length ? `<ul>${errors.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>` : ""}
      ${warnings.length ? `<ul>${warnings.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>` : ""}
    </div>
  `;
}
async function loadAssets() {
  const data = await jsonApi("/api/assets");
  state.assets = data.assets || [];
}
function formatBytes(value) {
  const size = Number(value || 0);
  if (size >= 1024 * 1024) return `${(size / 1024 / 1024).toFixed(1)} MB`;
  if (size >= 1024) return `${(size / 1024).toFixed(1)} KB`;
  return `${size} B`;
}
function renderAssets() {
  $("cancelAssetPick").hidden = !state.assetTargetInput;
  $("assetsGrid").innerHTML = state.assets.length ? state.assets.map((asset) => `
    <article class="asset-card">
      <div class="asset-thumb"><img src="${escapeHtml(asset.url)}" alt="${escapeHtml(asset.originalFilename)}" loading="lazy" /></div>
      <div class="asset-meta">
        <strong title="${escapeHtml(asset.originalFilename)}">${escapeHtml(asset.originalFilename || asset.storageKey)}</strong>
        <span>${escapeHtml(asset.ownerUsername)} · ${formatBytes(asset.sizeBytes)} · ${formatTime(asset.createdAt)}</span>
      </div>
      <div class="actions">
        ${state.assetTargetInput ? `<button class="button small primary" data-asset-use="${asset.id}">使用</button>` : ""}
        <button class="button small" data-asset-copy="${asset.id}">复制地址</button>
        <button class="button small danger" data-asset-delete="${asset.id}">删除</button>
      </div>
    </article>
  `).join("") : `<div class="empty">暂无资源</div>`;
}
async function openAssetPicker(inputId) {
  state.assetTargetInput = inputId;
  state.assetReturnView = state.activeView;
  await showView("assets");
}
function useAsset(asset) {
  if (!asset || !state.assetTargetInput) return;
  const target = $(state.assetTargetInput);
  if (target) target.value = asset.url;
  const returnView = state.assetReturnView || "assets";
  state.assetTargetInput = "";
  state.assetReturnView = "";
  showView(returnView);
}
async function renderLogs() {
  const params = new URLSearchParams();
  if ($("logUser").value) params.set("username", $("logUser").value);
  if ($("logAction").value) params.set("action", $("logAction").value);
  if ($("logFrom").value) params.set("from", $("logFrom").value);
  if ($("logTo").value) params.set("to", $("logTo").value);
  const data = await jsonApi(`/api/admin/logs?${params}`);
  $("logsTable").innerHTML = (data.logs || []).length ? data.logs.map((l) => `
    <tr><td>${formatTime(l.createdAt)}</td><td>${escapeHtml(l.username)}</td><td>${escapeHtml(l.action)}</td><td>${escapeHtml(l.targetLabel || l.targetId)}</td><td>${escapeHtml(l.changes || l.detail)}</td><td>${escapeHtml(l.ip)}</td></tr>
  `).join("") : `<tr><td colspan="6" class="empty">暂无日志</td></tr>`;
}
async function refreshView(view = state.activeView) {
  if (view === "dashboard") await renderDashboard();
  if (view === "users") { await loadUsers(); renderUsers(); }
  if (view === "projects") { await loadUsers(); await loadProjects(); renderProjects(); }
  if (view === "pages") { await loadProjects(); await loadPages(); }
  if (view === "assets") { await loadAssets(); renderAssets(); }
  if (view === "reviews") await renderReviews();
  if (view === "deploy") { await loadProjects(); await renderDeploy(); }
  if (view === "logs") await renderLogs();
}

async function uploadImage(file, statusNode) {
  if (!file) return "";
  const reader = new FileReader();
  const dataUrl = await new Promise((resolve, reject) => {
    reader.onload = () => resolve(reader.result);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
  const data = await jsonApi("/api/assets", body({ filename: file.name, dataUrl }));
  setStatus(statusNode, "图片已上传", "success");
  return data.url;
}
function fillProject(project) {
  state.editingProjectId = project.id;
  $("projectName").value = project.name || "";
  $("projectOwner").value = project.ownerUsername || "";
  $("projectAccent").value = project.accent || "#f59a13";
  $("idleTitle").value = project.idleTitle || "";
  $("idleKicker").value = project.idleKicker || "";
  $("idleCopy").value = project.idleCopy || "";
  $("defaultImageUrl").value = project.defaultImageUrl || "";
  $("projectFormHint").textContent = isAdmin() ? "管理员保存后立即生效。" : "修改展览基础信息后提交管理员审核。";
  $("projectForm").hidden = false;
}
function projectPayload() {
  return {
    name: $("projectName").value.trim(),
    ownerUsername: $("projectOwner").value || state.user.username,
    accent: $("projectAccent").value,
    idleTitle: $("idleTitle").value.trim(),
    idleKicker: $("idleKicker").value.trim(),
    idleCopy: $("idleCopy").value.trim(),
    defaultImageUrl: $("defaultImageUrl").value.trim(),
  };
}
function fillPage(page) {
  state.editingCode = page.code || "";
  setPreviewFile(null);
  setTemplateGuide("");
  $("pageCode").value = page.code || "";
  $("pageCategory").value = page.category || "";
  $("pagePublishedAt").value = page.publishedAt || "";
  $("pageSource").value = page.source || "";
  $("pageTitle").value = page.title || "";
  $("pageSubtitle").value = page.subtitle || "";
  setRichBody(page.body || "");
  $("pageAccent").value = page.accent || "#f59a13";
  $("pageImageUrl").value = page.imageUrl || "";
  $("pageImageFile").value = "";
  $("pageFormHint").textContent = isAdmin() ? "管理员保存后立即通过。" : "资料保存后会提交管理员审核，通过后进入展示。";
  $("pageForm").hidden = false;
  updatePagePreview();
}
function pagePayload() {
  syncRichBody();
  return {
    previousCode: state.editingCode,
    category: $("pageCategory").value.trim(),
    publishedAt: $("pagePublishedAt").value,
    source: $("pageSource").value.trim(),
    title: $("pageTitle").value.trim(),
    subtitle: $("pageSubtitle").value.trim(),
    body: $("pageBody").value.trim(),
    accent: $("pageAccent").value,
    imageUrl: $("pageImageUrl").value.trim(),
    enabled: true,
  };
}

$("logout").addEventListener("click", async () => { await api("/api/logout", { method: "POST" }); location.href = "/login"; });
$("refreshData").addEventListener("click", () => refreshView());
$("projectSelect").addEventListener("change", () => loadPages());
$("pageStatusFilter").addEventListener("change", renderPages);
$("deployProject").addEventListener("change", renderDeploy);
$("filterLogs").addEventListener("click", renderLogs);
$("exportLogs").addEventListener("click", () => {
  const params = new URLSearchParams();
  if ($("logUser").value) params.set("username", $("logUser").value);
  if ($("logAction").value) params.set("action", $("logAction").value);
  if ($("logFrom").value) params.set("from", $("logFrom").value);
  if ($("logTo").value) params.set("to", $("logTo").value);
  location.href = `/api/admin/logs.csv?${params}`;
});
$("richBody").addEventListener("input", syncRichBody);
$("richBody").addEventListener("paste", () => setTimeout(() => setRichBody($("richBody").innerHTML), 0));
["pageCode", "pageCategory", "pageSource", "pageTitle", "pageSubtitle", "pageImageUrl"].forEach((id) => {
  $(id).addEventListener("input", updatePagePreview);
});
$("pageImageFile").addEventListener("change", () => setPreviewFile($("pageImageFile").files[0] || null));
document.querySelectorAll("[data-template]").forEach((button) => {
  button.addEventListener("click", () => {
    const template = richTemplates[button.dataset.template];
    if (!template) return;
    setTemplateGuide(button.dataset.template);
    $("pageCategory").value = template.category;
    $("pageSource").value = template.source;
    $("pageTitle").value = template.title;
    $("pageSubtitle").value = template.subtitle;
    setRichBody(template.body);
  });
});
document.querySelectorAll("[data-command]").forEach((button) => {
  button.addEventListener("click", () => {
    $("richBody").focus();
    document.execCommand(button.dataset.command, false, null);
    syncRichBody();
  });
});
document.querySelectorAll("[data-block]").forEach((button) => {
  button.addEventListener("click", () => {
    $("richBody").focus();
    document.execCommand("formatBlock", false, button.dataset.block);
    syncRichBody();
  });
});
document.querySelectorAll("[data-insert]").forEach((button) => {
  button.addEventListener("click", () => {
    $("richBody").focus();
    const type = button.dataset.insert;
    if (type === "quote") document.execCommand("insertHTML", false, "<blockquote>请输入引用内容</blockquote>");
    if (type === "divider") document.execCommand("insertHTML", false, "<hr>");
    if (type === "image") {
      const url = prompt("请输入图片地址，例如 /uploads/example.jpg");
      if (url) document.execCommand("insertHTML", false, `<figure><img src="${escapeHtml(url)}" alt=""><figcaption>图片说明</figcaption></figure>`);
    }
    setRichBody($("richBody").innerHTML);
  });
});

$("userForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    await jsonApi("/api/users", body({ username: $("userUsername").value, displayName: $("userDisplayName").value, department: $("userDepartment").value, password: $("userPassword").value, role: "teacher", enabled: true }));
    setStatus($("userStatus"), "老师已保存", "success");
    event.target.reset();
    await refreshView("users");
  } catch (err) { setStatus($("userStatus"), err.message, "error"); }
});
$("importUsers").addEventListener("click", async () => {
  try {
    const data = await jsonApi("/api/users/import-csv", body({ csv: $("csvImport").value }));
    setStatus($("userStatus"), `导入完成：新增 ${data.result.created}，更新 ${data.result.updated}，项目 ${data.result.projects}`, "success");
    await refreshView("users");
  } catch (err) { setStatus($("userStatus"), err.message, "error"); }
});
$("usersTable").addEventListener("click", async (event) => {
  const edit = event.target.closest("[data-user-edit]");
  const reset = event.target.closest("[data-user-reset]");
  const toggle = event.target.closest("[data-user-toggle]");
  try {
    if (edit) {
      const u = state.users.find((item) => item.username === edit.dataset.userEdit);
      $("userUsername").value = u.username; $("userDisplayName").value = u.displayName; $("userDepartment").value = u.department || ""; $("userPassword").value = "";
    }
    if (reset) {
      const password = prompt("输入新密码", "");
      if (password) await jsonApi(`/api/users/${reset.dataset.userReset}/reset-password`, body({ password }));
      await refreshView("users");
    }
    if (toggle) {
      const action = toggle.dataset.enabled === "1" ? "enable" : "disable";
      await jsonApi(`/api/users/${toggle.dataset.userToggle}/${action}`, body({}));
      await refreshView("users");
    }
  } catch (err) { setStatus($("userStatus"), err.message, "error"); }
});

$("newProject").addEventListener("click", () => fillProject({ id: "", ownerUsername: state.users.find((u) => u.role === "teacher")?.username || "", accent: "#f59a13" }));
$("closeProjectForm").addEventListener("click", () => { $("projectForm").hidden = true; });
$("projectForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    const fileUrl = await uploadImage($("projectImageFile").files[0], $("projectStatus"));
    if (fileUrl) $("defaultImageUrl").value = fileUrl;
    const id = state.editingProjectId;
    const url = id ? `/api/projects/${id}` : "/api/projects";
    const method = id ? putBody(projectPayload()) : body(projectPayload());
    await jsonApi(url, method);
    setStatus($("projectStatus"), isAdmin() ? "项目已保存" : "展览信息已提交审核", "success");
    await loadProjects(id);
    renderProjects();
  } catch (err) { setStatus($("projectStatus"), err.message, "error"); }
});
$("selectProjectAsset").addEventListener("click", () => openAssetPicker("defaultImageUrl"));
$("projectsTable").addEventListener("click", async (event) => {
  const edit = event.target.closest("[data-project-edit]");
  const pages = event.target.closest("[data-project-pages]");
  const historyButton = event.target.closest("[data-project-history]");
  const del = event.target.closest("[data-project-delete]");
  if (edit) fillProject(state.projects.find((p) => String(p.id) === edit.dataset.projectEdit));
  if (pages) { $("projectSelect").value = pages.dataset.projectPages; showView("pages"); await loadPages(pages.dataset.projectPages); }
  if (historyButton) await showProjectHistory(historyButton.dataset.projectHistory);
  if (del && confirm("确定删除项目及其内容？")) { await api(`/api/projects/${del.dataset.projectDelete}`, { method: "DELETE" }); await refreshView("projects"); }
});
$("closeProjectHistory").addEventListener("click", () => { $("projectHistoryPanel").hidden = true; });

$("newPage").addEventListener("click", () => { state.editingCode = ""; fillPage({ accent: "#f59a13", category: "校园新闻", source: "学校展示", publishedAt: new Date().toISOString().slice(0, 10), body: "" }); });
$("closePageForm").addEventListener("click", () => { $("pageForm").hidden = true; });
$("pageForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    const fileUrl = await uploadImage($("pageImageFile").files[0], $("pageStatus"));
    if (fileUrl) $("pageImageUrl").value = fileUrl;
    await jsonApi(`/api/projects/${$("projectSelect").value}/pages/${encodeURIComponent($("pageCode").value.trim())}`, putBody(pagePayload()));
    setStatus($("pageStatus"), isAdmin() ? "内容已保存并通过" : "展览资料已提交审核", "success");
    await loadPages();
  } catch (err) { setStatus($("pageStatus"), err.message, "error"); }
});
$("selectPageAsset").addEventListener("click", () => openAssetPicker("pageImageUrl"));
$("pagesTable").addEventListener("click", async (event) => {
  const edit = event.target.closest("[data-page-edit]");
  const historyButton = event.target.closest("[data-page-history]");
  const del = event.target.closest("[data-page-delete]");
  if (edit) fillPage(state.pages.find((p) => p.code === edit.dataset.pageEdit));
  if (historyButton) await showPageHistory(historyButton.dataset.pageHistory);
  if (del && confirm(isAdmin() ? "确定删除该内容？" : "确定提交删除该资料的审核申请？")) { await api(`/api/projects/${$("projectSelect").value}/pages/${encodeURIComponent(del.dataset.pageDelete)}`, { method: "DELETE" }); await loadPages(); }
});
$("closePageHistory").addEventListener("click", () => { $("pageHistoryPanel").hidden = true; });

$("refreshAssets").addEventListener("click", async () => {
  await loadAssets();
  renderAssets();
});
$("uploadAsset").addEventListener("click", async () => {
  try {
    const url = await uploadImage($("assetFile").files[0], $("assetStatus"));
    if (!url) {
      setStatus($("assetStatus"), "请选择图片", "error");
      return;
    }
    $("assetFile").value = "";
    await loadAssets();
    renderAssets();
  } catch (err) { setStatus($("assetStatus"), err.message, "error"); }
});
$("cancelAssetPick").addEventListener("click", () => {
  const returnView = state.assetReturnView || (isAdmin() ? "projects" : "pages");
  state.assetTargetInput = "";
  state.assetReturnView = "";
  showView(returnView);
});
$("assetsGrid").addEventListener("click", async (event) => {
  const use = event.target.closest("[data-asset-use]");
  const copy = event.target.closest("[data-asset-copy]");
  const del = event.target.closest("[data-asset-delete]");
  const id = (use && use.dataset.assetUse) || (copy && copy.dataset.assetCopy) || (del && del.dataset.assetDelete);
  const asset = state.assets.find((item) => String(item.id) === String(id));
  if (!asset) return;
  try {
    if (use) {
      useAsset(asset);
      return;
    }
    if (copy) {
      if (navigator.clipboard) await navigator.clipboard.writeText(asset.url);
      setStatus($("assetStatus"), `图片地址：${asset.url}`, "success");
      return;
    }
    if (del && confirm("确定删除该资源？")) {
      await jsonApi(`/api/assets/${asset.id}`, { method: "DELETE" });
      await loadAssets();
      renderAssets();
      setStatus($("assetStatus"), "资源已删除", "success");
    }
  } catch (err) { setStatus($("assetStatus"), err.message, "error"); }
});

async function reviewAction(type, id, action) {
  const note = action === "reject" ? prompt("驳回原因（可选）", "") || "" : "";
  await jsonApi(`/api/reviews/${type}/${id}/${action}`, body({ note }));
}
$("reviewsList").addEventListener("click", async (event) => {
  const approve = event.target.closest("[data-review-approve]");
  const reject = event.target.closest("[data-review-reject]");
  if (!approve && !reject) return;
  const [type, id] = (approve ? approve.dataset.reviewApprove : reject.dataset.reviewReject).split(":");
  try { await reviewAction(type, id, approve ? "approve" : "reject"); await renderReviews(); } catch (err) { alert(err.message); }
});
$("batchApprove").addEventListener("click", async () => {
  const checks = Array.from(document.querySelectorAll("[data-review-check]:checked"));
  if (!checks.length || !confirm(`确定通过 ${checks.length} 项审核？`)) return;
  for (const check of checks) {
    const [type, id] = check.dataset.reviewCheck.split(":");
    await reviewAction(type, id, "approve");
  }
  await renderReviews();
});
$("deployWelcome").addEventListener("click", async () => {
  const projectId = $("deployProject").value;
  try {
    await jsonApi(`/api/projects/${projectId}/deploy`, body({}));
    setStatus($("deployStatus"), "欢迎页已部署", "success");
    await renderDeploy();
  } catch (err) {
    setStatus($("deployStatus"), err.message, "error");
    await renderDeploy();
  }
});
$("deployContent").addEventListener("click", async () => {
  const projectId = $("deployProject").value;
  const pageIds = Array.from($("deployPages").querySelectorAll("input:checked")).map((input) => Number(input.value));
  try {
    await jsonApi("/api/deploy/content", body({ projectId, pageIds }));
    setStatus($("deployStatus"), "内容项目已部署", "success");
    await renderDeploy();
  } catch (err) {
    setStatus($("deployStatus"), err.message, "error");
    await renderDeploy();
  }
});
$("passwordForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    await jsonApi("/api/account/password", body({ oldPassword: $("oldPassword").value, newPassword: $("newPassword").value }));
    setStatus($("accountStatus"), "密码已修改", "success");
    event.target.reset();
  } catch (err) { setStatus($("accountStatus"), err.message, "error"); }
});

(async function init() {
  try {
    await loadSession();
    setupNav();
    await loadUsers();
    await loadProjects();
    const preferred = new URLSearchParams(location.search).get("view") || (isAdmin() ? "dashboard" : "pages");
    showView(preferred);
  } catch (err) {
    console.error(err);
    location.href = "/login";
  }
})();
