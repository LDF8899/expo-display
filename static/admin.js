const $ = (id) => document.getElementById(id);
const state = { user: null, csrfToken: "", projects: [], users: [], pages: [], contentItems: [], lowcodeForms: [], lowcodeRecords: [], lowcodeVersions: [], lowcodeAssetDrafts: [], activeLowcodeFormId: "", editingLowcodeFormId: "", viewingLowcodeFormId: "", lowcodeFieldDrafts: [], assets: [], contentAssetDrafts: [], activeView: "dashboard", editingProjectId: "", editingCode: "", editingContentItemId: "", assetTargetInput: "", assetReturnView: "", previewImageObjectUrl: "", moduleCoverage: null, generatedCode: "", preferredProjectId: "", preferredModuleKey: "" };
const standardModules = [
  { key: "overview", label: "基本情况", description: "定位、沿革、师资、数据", code: "OVERVIEW" },
  { key: "majors", label: "专业设置", description: "专业群、课程、就业方向", code: "MAJORS" },
  { key: "training", label: "实训基地", description: "实训室、设备、场景", code: "TRAINING" },
  { key: "cooperation", label: "产教融合", description: "校企合作、订单班、共同体", code: "COOP" },
  { key: "achievements", label: "教学成果", description: "课程、竞赛、荣誉、育人成效", code: "RESULTS" },
  { key: "media", label: "视频资源", description: "宣传片、专业介绍、作品", code: "MEDIA" },
  { key: "systems", label: "特色系统入口", description: "业务系统、互动平台", code: "SYSTEMS" },
  { key: "resources", label: "特色数字资源", description: "资源库、专题资料、扫码内容", code: "RESOURCES" },
];
const topicModules = [
  { key: "overview", label: "专题概况", description: "专题背景、建设目标、总体介绍", code: "TOPIC-OVERVIEW", aliases: ["专题概况", "专题简介", "专题介绍", "概况", "简介", "topicOverview"] },
  { key: "majors", label: "专业群布局", description: "专业群、专业方向、课程、就业方向", code: "TOPIC-MAJORS", aliases: ["专业群布局", "专业群", "专业布局", "专业方向", "课程", "就业方向"] },
  { key: "training", label: "实训场景", description: "实训基地、实训室、设备、实践教学", code: "TOPIC-TRAINING", aliases: ["实训场景", "实训基地", "实训", "实践教学", "实训室", "设备"] },
  { key: "cooperation", label: "产教协同", description: "校企合作、订单班、共同体、社会服务", code: "TOPIC-COOP", aliases: ["产教协同", "产教融合", "校企合作", "订单班", "共同体", "社会服务"] },
  { key: "masters", label: "名师名匠", description: "教学名师、技能大师、教师团队", code: "TOPIC-MASTERS", aliases: ["名师名匠", "名师", "名匠", "教师团队", "教学名师", "技能大师"] },
  { key: "alumni", label: "优秀校友", description: "校友人物、成长经历、就业成果", code: "TOPIC-ALUMNI", aliases: ["优秀校友", "校友", "毕业生", "优秀毕业生", "就业典型"] },
  { key: "students", label: "优秀学生", description: "学生人物、竞赛经历、成长故事", code: "TOPIC-STUDENTS", aliases: ["优秀学生", "学生风采", "学生", "成长故事", "技能成才"] },
  { key: "achievements", label: "专题成果", description: "教学成果、项目成果、典型案例", code: "TOPIC-RESULT", aliases: ["专题成果", "教学成果", "项目成果", "成果", "案例", "建设成果", "图文资料", "topicAchievements", "topicGallery"] },
  { key: "competitions", label: "技能大赛", description: "赛事、获奖、承办活动、比赛现场", code: "TOPIC-COMPETE", aliases: ["技能大赛", "大赛", "竞赛", "比赛", "赛项", "获奖"] },
  { key: "honors", label: "荣誉资质", description: "证书、奖项、资质、认定结果", code: "TOPIC-HONOR", aliases: ["荣誉资质", "荣誉", "资质", "证书", "奖项", "认定"] },
  { key: "media", label: "视频资源", description: "视频、宣传片、访谈、纪实片", code: "TOPIC-MEDIA", aliases: ["视频资源", "视频", "宣传片", "访谈", "纪实片", "topicMedia"] },
];
const contentTypes = [
  { key: "article", label: "普通图文", description: "标题、摘要、正文、图片轮播；适合专题概况及兜底资料" },
  { key: "person", label: "人物类", description: "图片与人物介绍并列，适合名师、校友、学生" },
  { key: "activity", label: "活动类", description: "按时间地点、正文段落和图片组织，适合活动与比赛" },
  { key: "honor", label: "荣誉类", description: "证书/奖状优先展示，适合奖项、资质和认定" },
  { key: "achievement", label: "成果类", description: "摘要和关键指标优先，适合成果、案例和项目" },
  { key: "scene", label: "场景类", description: "适合实训室、设备条件、服务课程和开放对象" },
  { key: "video", label: "视频类", description: "播放器或封面为主，适合宣传片、访谈和纪实片" },
];
const contentTypeLabels = Object.fromEntries(contentTypes.map((item) => [item.key, item.label]));
const contentAssetRoles = [
  { key: "cover", label: "封面" },
  { key: "portrait", label: "人物照" },
  { key: "certificate", label: "证书/荣誉" },
  { key: "gallery", label: "图集" },
  { key: "video", label: "视频" },
];
const contentAssetRoleLabels = Object.fromEntries(contentAssetRoles.map((item) => [item.key, item.label]));
const lowcodeFieldTypes = [
  { key: "text", label: "单行文本" },
  { key: "textarea", label: "多行文本" },
  { key: "number", label: "数字" },
  { key: "date", label: "日期" },
  { key: "select", label: "下拉选择" },
  { key: "checkbox", label: "开关" },
  { key: "asset_list", label: "素材组" },
];
const moduleDefaultContentTypes = {
  training: "scene",
  cooperation: "activity",
  masters: "person",
  alumni: "person",
  students: "person",
  achievements: "achievement",
  competitions: "activity",
  honors: "honor",
  media: "video",
};
const portalTypeLabels = { school: "学校门户", department: "系部门户", topic: "专题门户" };
const moduleSets = {
  department: standardModules,
  school: [
    { key: "service", label: "社会服务", description: "技术服务、培训服务、校地合作", code: "SERVICE", aliases: ["社会服务", "技术服务", "培训服务", "校地合作", "服务地方"] },
    { key: "international", label: "国际交流", description: "国际合作、交流项目、开放办学", code: "INTL", aliases: ["国际交流", "国际交流合作", "国际合作", "中外合作", "境外交流"] },
    { key: "education", label: "育人成果", description: "人才培养、优秀毕业生、竞赛成果", code: "EDU", aliases: ["育人成果", "优秀毕业生", "人才培养", "学生成长", "就业创业", "竞赛成果"] },
    { key: "masters", label: "名师名匠", description: "教学名师、技能大师、双师团队", code: "MASTER", aliases: ["名师名匠", "教师团队", "教学名师", "技能大师", "双师"] },
  ],
  topic: topicModules,
};
const richTemplates = {
  overview: {
    category: "基本情况",
    source: "系部门户",
    title: "系部基本情况",
    subtitle: "概括系部定位、发展沿革、师资队伍、办学规模与核心数据。",
    body: "<p>请在这里填写系部简介，建议先说明系部办学定位、发展沿革和服务区域产业的方向。</p><h2>系部概况</h2><ul><li>成立时间、办学基础和发展阶段。</li><li>教师队伍、双师结构、专业负责人和教学团队。</li><li>在校生规模、专业数量、实训条件等核心数据。</li></ul><h2>办学特色</h2><p>用一段话概括本系部最有辨识度的专业特色、育人模式或服务地方成果。</p>",
  },
  majors: {
    category: "专业设置",
    source: "系部门户",
    title: "专业设置与培养方向",
    subtitle: "展示专业群、核心专业、课程模块、培养目标和就业岗位。",
    body: "<p>请按专业群或专业方向组织内容，避免堆长段文字。</p><h2>专业结构</h2><ul><li>专业名称：填写培养方向、核心课程和适配岗位。</li><li>专业名称：填写培养方向、核心课程和适配岗位。</li><li>专业名称：填写培养方向、核心课程和适配岗位。</li></ul><h2>就业面向</h2><p>说明学生毕业后的主要岗位、行业方向和升学发展路径。</p>",
  },
  training: {
    category: "实训基地",
    source: "系部门户",
    title: "实训基地与教学场景",
    subtitle: "集中呈现实训室、校内外基地、设备条件和实践教学能力。",
    body: "<p>请围绕真实场景和设备条件组织内容，建议搭配实训室图片。</p><h2>基地条件</h2><ul><li>实训室名称：填写功能定位、服务课程和主要设备。</li><li>实训室名称：填写功能定位、服务课程和主要设备。</li><li>校外基地：填写合作单位、实践岗位和承载任务。</li></ul><h2>教学应用</h2><p>说明实训基地如何支撑课程教学、技能训练、竞赛备赛和社会培训。</p>",
  },
  cooperation: {
    category: "产教融合",
    source: "系部门户",
    title: "产教融合与校企合作",
    subtitle: "展示合作企业、订单班、共同体建设、项目实践和社会服务。",
    body: "<p>请突出真实合作关系和可展示成果。</p><h2>合作机制</h2><ul><li>合作企业或单位：填写合作内容、合作时间和育人任务。</li><li>订单班/现代学徒制：填写培养模式、学生规模和就业去向。</li><li>产业学院/共同体：填写共建内容和阶段成果。</li></ul><h2>服务成效</h2><p>说明合作项目对专业建设、学生就业、技术服务或地方产业的支撑作用。</p>",
  },
  achievements: {
    category: "教学成果",
    source: "系部门户",
    title: "教学成果与育人成效",
    subtitle: "展示课程建设、技能竞赛、教学成果奖、学生成长和荣誉资质。",
    body: "<p>请优先填写近三年具有代表性的成果，便于大屏快速识别。</p><h2>代表成果</h2><ul><li>成果名称：填写级别、时间、获奖单位或参与师生。</li><li>竞赛名称：填写奖项、赛项和学生团队。</li><li>课程/教材/项目：填写建设级别和应用情况。</li></ul><h2>育人成效</h2><p>说明成果如何体现人才培养质量、学生就业能力或专业影响力。</p>",
  },
  media: {
    category: "视频资源",
    source: "系部门户",
    title: "视频资源",
    subtitle: "用于承载系部宣传片、专业介绍、实训基地介绍或学生作品视频。",
    body: "<p>请填写视频内容说明，并在素材库上传或填写视频地址。</p><h2>视频列表</h2><ul><li>视频名称：填写时长、主题和适用场景。</li><li>视频名称：填写时长、主题和适用场景。</li></ul><h2>展示说明</h2><p>建议视频控制在 1 到 3 分钟，优先使用横屏高清素材。</p>",
  },
  systems: {
    category: "特色系统入口",
    source: "系部门户",
    title: "特色系统入口",
    subtitle: "对接系部业务系统、训练平台、互动系统或外部专题入口。",
    body: "<p>请填写系统名称、用途和访问方式。</p><h2>系统入口</h2><ul><li>系统名称：填写系统功能、适用对象和访问地址。</li><li>系统名称：填写系统功能、适用对象和访问地址。</li></ul><h2>使用场景</h2><p>说明该系统如何支撑教学、实训、管理、展示或互动体验。</p>",
  },
  resources: {
    category: "特色数字资源",
    source: "系部门户",
    title: "特色数字资源",
    subtitle: "聚合资源库、课程资源、专题资料、扫码内容和数字素材。",
    body: "<p>请按资源类型整理，不要把素材说明写成大段连续文字。</p><h2>资源清单</h2><ul><li>资源名称：填写资源类型、用途和访问方式。</li><li>资源名称：填写资源类型、用途和访问方式。</li></ul><h2>资源价值</h2><p>说明资源对课程教学、学生学习、社会服务或展厅互动的支撑作用。</p>",
  },
};
const templateGuides = {
  overview: ["基本情况", "适合系部定位、沿革、师资、规模和办学特色；展示页会把它作为门户开场信息。"],
  majors: ["专业设置", "适合专业群、培养方向、课程模块和就业岗位；建议使用清单化内容。"],
  training: ["实训基地", "适合实训室、设备、基地和实践教学场景；建议搭配多张场景图片。"],
  cooperation: ["产教融合", "适合校企合作、订单班、共同体和社会服务项目；重点写合作机制与成效。"],
  achievements: ["教学成果", "适合教学成果奖、技能竞赛、课程建设和育人成效；优先填写代表性成果。"],
  media: ["视频资源", "适合宣传片、专业介绍、实训基地介绍和学生作品；建议使用横屏高清素材。"],
  systems: ["特色系统入口", "适合业务系统、训练平台、互动系统和外部专题入口；需要填写访问方式。"],
  resources: ["特色数字资源", "适合资源库、课程资源、扫码资料和专题素材；建议按资源类型组织。"],
};
const allowedRichTags = new Set(["A", "B", "BLOCKQUOTE", "BR", "DIV", "EM", "FIGCAPTION", "FIGURE", "H2", "H3", "H4", "HR", "I", "IMG", "LI", "OL", "P", "SPAN", "STRONG", "U", "UL"]);

const views = {
  dashboard: ["门户总览", "查看欢迎页、学校门户、系部门户、专题门户和发布状态。"],
  users: ["老师管理", "创建、导入、禁用和维护老师账号。"],
  projects: ["门户管理", "统一维护学校门户、系部门户和专题门户，并分配归属老师。"],
  pages: ["板块资料", "维护门户下的板块资料，审核通过后进入展示。"],
  assets: ["素材库", "上传、复用和删除图片素材。"],
  reviews: ["审核发布", "审核板块资料草稿、删除申请和门户配置草稿。"],
  deploy: ["展厅发布", "选择欢迎页项目和实际展示资料。"],
  logs: ["操作日志", "查询和导出关键操作日志。"],
  account: ["个人设置", "查看个人资料并修改密码。"],
};
const teacherViews = {
  pages: ["板块资料", "上传、编辑并提交板块资料，审核通过后进入展示。"],
  assets: ["素材库", "上传和复用门户展示素材。"],
  projects: ["我的门户", "查看自己负责的门户，提交基础信息修改。"],
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
function normalizePortalType(value) {
  return portalTypeLabels[value] ? value : "department";
}
function portalTypeLabel(value) {
  return portalTypeLabels[normalizePortalType(value)];
}
function normalizePortalSlug(value) {
  return String(value || "")
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9-]+/g, "-")
    .replace(/-{2,}/g, "-")
    .replace(/^-|-$/g, "");
}
function portalPreviewUrl(project) {
  if (!project) return "";
  if (project.previewUrl) return project.previewUrl;
  const type = normalizePortalType(project.portalType);
  const slug = normalizePortalSlug(project.portalSlug);
  if (type === "school") return "/departments";
  if (type === "topic") return slug ? `/topics/${slug}` : "";
  return slug ? `/departments/${slug}` : "";
}
function portalRouteLabel(project) {
  return portalPreviewUrl(project) || "未配置前台路径";
}
function portalOptionLabel(project) {
  return `${portalTypeLabel(project.portalType)} · ${project.name} · ${portalRouteLabel(project)}`;
}
function portalCompletionPreviewUrl(project) {
  if (!project) return "";
  if (normalizePortalType(project.portalType) === "school" && !project.deployed && !project.contentDeployed) return "";
  return portalPreviewUrl(project);
}
function syncProjectPortalSlugField() {
  const input = $("projectPortalSlug");
  if (!input) return;
  const type = normalizePortalType($("projectPortalType").value);
  input.disabled = type === "school";
  if (type === "school") input.value = "";
  input.placeholder = type === "topic" ? "专题路由，如 smart-energy" : type === "department" ? "系部路由，如 finance" : "学校门户无需填写";
}
function currentProject() {
  const selectedId = $("projectSelect") ? $("projectSelect").value : "";
  return state.projects.find((project) => String(project.id) === String(selectedId)) || null;
}
function selectedPortalType() {
  const project = currentProject();
  return normalizePortalType((project && project.portalType) || ($("projectPortalType") && $("projectPortalType").value) || "department");
}
function renderCurrentPortalStrip() {
  const strip = $("currentPortalStrip");
  if (!strip) return;
  const project = currentProject();
  if (!project) {
    strip.innerHTML = `<span>当前未选择门户</span>`;
    return;
  }
  const route = portalPreviewUrl(project);
  const coverage = state.moduleCoverage || buildCoverageFromPages(state.pages, project.portalType);
  const total = Number(coverage.total || 0);
  const ready = Number(coverage.publishReady || 0);
  strip.innerHTML = `
    <div>
      <span>${escapeHtml(portalTypeLabel(project.portalType))}</span>
      <strong>${escapeHtml(project.name)}</strong>
      <code>${escapeHtml(portalRouteLabel(project))}</code>
    </div>
    <div class="current-portal-meta">
      <span>资料 ${state.pages.length}</span>
      <span>可发布 ${ready}/${total || 0}</span>
      ${route ? `<a class="button small" target="_blank" rel="noopener" href="${escapeHtml(route)}">前台预览</a>` : ""}
    </div>
  `;
}
function modulesForPortalType(portalType = selectedPortalType()) {
  return moduleSets[normalizePortalType(portalType)] || standardModules;
}
function moduleMeta(key, portalType = selectedPortalType()) {
  return modulesForPortalType(portalType).find((module) => module.key === key) || null;
}
function normalizeContentType(value, fallback = "article") {
  return contentTypeLabels[value] ? value : fallback;
}
function contentTypeLabel(value) {
  return contentTypeLabels[normalizeContentType(value)] || contentTypeLabels.article;
}
function defaultContentTypeForModule(moduleKey) {
  return moduleDefaultContentTypes[moduleKey] || "article";
}
function contentBodyTemplate(contentType, label) {
  const name = escapeHtml(label || "本资料");
  const templates = {
    person: `<p>请填写人物姓名、身份/职务、专业或班级，以及最能代表人物特色的一句话。</p><h2>人物简介</h2><ul><li>姓名：填写姓名。</li><li>身份：填写教师职务、校友岗位或学生班级。</li><li>标签：填写荣誉、技能特长或成长关键词。</li></ul><h2>主要事迹</h2><p>用短段落描述成长经历、代表成果和可展示亮点，建议配一张清晰人物照。</p>`,
    activity: `<p>请按活动时间、地点、参与单位和活动成效整理资料。</p><h2>活动信息</h2><ul><li>时间：填写活动或比赛时间。</li><li>地点：填写举办地点或实践场景。</li><li>参与单位：填写主办、承办或合作单位。</li></ul><h2>活动亮点</h2><p>用短段落说明活动过程、学生参与、产教协同或比赛成果，并搭配现场图片。</p>`,
    honor: `<p>请优先上传证书、奖状、牌匾等可核验图片。</p><h2>荣誉信息</h2><ul><li>荣誉名称：填写奖项、资质或认定名称。</li><li>级别年份：填写国家级/省级/校级和获评年份。</li><li>获奖单位/个人：填写对应团队或人员。</li></ul><h2>展示说明</h2><p>说明该荣誉对专业建设、人才培养或社会服务的价值。</p>`,
    achievement: `<p>请先写成果摘要，再补充关键指标和佐证材料。</p><h2>成果摘要</h2><ul><li>成果名称：填写项目、课程、案例或建设成果。</li><li>建设周期：填写起止时间或阶段。</li><li>关键指标：填写获奖、立项、服务人数、就业质量等数据。</li></ul><h2>成果价值</h2><p>说明成果如何支撑${name}的人才培养、专业建设或服务地方。</p>`,
    scene: `<p>请围绕真实场景组织资料，优先上传实训室、设备或教学现场图片。</p><h2>场景信息</h2><ul><li>场景名称：填写实训室、基地或设备名称。</li><li>功能定位：填写服务课程、训练项目和开放对象。</li><li>设备条件：填写关键设备、软件平台或工位数量。</li></ul><h2>教学应用</h2><p>说明该场景如何支撑课程教学、技能训练、竞赛备赛或社会培训。</p>`,
    video: `<p>请填写视频标题、时长、主题和适用场景，并在图片地址或正文中放入视频封面/视频链接。</p><h2>视频信息</h2><ul><li>视频标题：填写视频名称。</li><li>时长：填写视频长度。</li><li>适用场景：填写宣传片、访谈、课堂展示或纪实片。</li></ul><h2>内容简介</h2><p>概括视频重点，建议控制在 1 到 3 分钟，优先使用横屏高清素材。</p>`,
    article: `<p>请围绕“${name}”整理资料，优先使用短段落、清单和真实图片。</p><h2>内容要点</h2><ul><li>填写本板块最重要的事实、项目或成果。</li><li>补充关键数据、参与团队、服务对象或建设进度。</li><li>配套上传现场图片、证书图片或代表性资源。</li></ul><h2>展示说明</h2><p>建议控制文字密度，卡片页会显示摘要，抽屉页会展示完整内容。</p>`,
  };
  return templates[normalizeContentType(contentType)] || templates.article;
}
function htmlToPlainText(html) {
  const template = document.createElement("template");
  template.innerHTML = String(html || "");
  return template.content.textContent.replace(/\n{3,}/g, "\n\n").trim();
}
function bodyJsonFromText(value) {
  return String(value || "")
    .split(/\n{2,}|\r?\n/)
    .map((text) => text.trim())
    .filter(Boolean)
    .map((text) => {
      if (text.length <= 28 && !/[。！？；;：:]/.test(text)) return { type: "heading", text };
      return { type: "paragraph", text };
    });
}
function textFromBodyJson(bodyJson) {
  if (!Array.isArray(bodyJson)) return "";
  return bodyJson.map((block) => {
    if (typeof block === "string") return block;
    if (!block || typeof block !== "object") return "";
    if (block.type === "html") return htmlToPlainText(block.html || "");
    return block.text || block.content || block.title || "";
  }).filter(Boolean).join("\n\n");
}
function metaJsonFromText(value) {
  const meta = {};
  String(value || "").split(/\r?\n/).forEach((line) => {
    const text = line.trim();
    if (!text) return;
    const parts = text.split(/[:：]/);
    if (parts.length < 2) return;
    const key = parts.shift().trim();
    const val = parts.join("：").trim();
    if (key) meta[key] = val;
  });
  return meta;
}
function textFromMetaJson(meta) {
  if (!meta || typeof meta !== "object" || Array.isArray(meta)) return "";
  return Object.entries(meta).map(([key, value]) => `${key}：${value}`).join("\n");
}
function parseContentAssets(value) {
  return String(value || "").split(/\r?\n/)
    .map((line, index) => {
      const parts = line.split("|").map((item) => item.trim());
      const url = parts[0] || "";
      if (!url) return null;
      return normalizeContentAsset({
        url,
        caption: parts[1] || "",
        role: parts[2] || (index === 0 ? "cover" : "gallery"),
        sortOrder: index,
      }, index);
    })
    .filter(Boolean);
}
function textFromContentAssets(assets) {
  return (assets || []).map((asset) => [
    asset.url || "",
    asset.caption || asset.title || "",
    asset.role || "gallery",
  ].join(" | ")).join("\n");
}
function normalizeContentAssetRole(role, index = 0) {
  const value = String(role || "").trim();
  if (contentAssetRoleLabels[value]) return value;
  return index === 0 ? "cover" : "gallery";
}
function normalizeContentAsset(asset = {}, index = 0) {
  const url = String(asset.url || asset.src || "").trim();
  if (!url) return null;
  return {
    url,
    caption: String(asset.caption || asset.title || "").trim(),
    role: normalizeContentAssetRole(asset.role, index),
    sortOrder: index,
  };
}
function orderedContentAssets(assets) {
  return (assets || [])
    .map((asset, index) => normalizeContentAsset(asset, index))
    .filter(Boolean)
    .sort((a, b) => Number(a.sortOrder || 0) - Number(b.sortOrder || 0))
    .map((asset, index) => ({ ...asset, sortOrder: index }));
}
function currentContentAssets() {
  return orderedContentAssets(state.contentAssetDrafts.length ? state.contentAssetDrafts : parseContentAssets($("contentAssetsText")?.value || ""));
}
function syncContentAssetsText() {
  const input = $("contentAssetsText");
  if (input) input.value = textFromContentAssets(state.contentAssetDrafts);
}
function setContentAssetDrafts(assets, options = {}) {
  state.contentAssetDrafts = orderedContentAssets(assets);
  syncContentAssetsText();
  renderContentAssetCards();
  if (!options.silent) updateContentPreview();
}
function addContentAsset(asset) {
  const next = normalizeContentAsset(asset, state.contentAssetDrafts.length);
  if (!next) return false;
  setContentAssetDrafts([...state.contentAssetDrafts, next]);
  return true;
}
function updateContentAsset(index, field, value, options = {}) {
  if (!state.contentAssetDrafts[index] || !["url", "caption", "role"].includes(field)) return;
  const next = [...state.contentAssetDrafts];
  next[index] = {
    ...next[index],
    [field]: field === "role" ? normalizeContentAssetRole(value, index) : String(value || "").trim(),
  };
  state.contentAssetDrafts = orderedContentAssets(next);
  syncContentAssetsText();
  if (!options.skipRender) renderContentAssetCards();
  updateContentPreview();
}
function moveContentAsset(index, direction) {
  const target = index + direction;
  if (target < 0 || target >= state.contentAssetDrafts.length) return;
  const next = [...state.contentAssetDrafts];
  [next[index], next[target]] = [next[target], next[index]];
  setContentAssetDrafts(next);
}
function removeContentAsset(index) {
  setContentAssetDrafts(state.contentAssetDrafts.filter((_, itemIndex) => itemIndex !== index));
}
function looksLikeVideoAsset(asset) {
  return asset.role === "video" || /\.(mp4|mov|m4v|webm|ogg)(\?.*)?$/i.test(asset.url);
}
function renderContentAssetCards() {
  const list = $("contentAssetCards");
  if (!list) return;
  const assets = currentContentAssets();
  list.innerHTML = assets.length ? assets.map((asset, index) => `
    <article class="content-asset-card">
      <figure class="content-asset-thumb">
        ${looksLikeVideoAsset(asset) ? `<span>VIDEO</span>` : `<img src="${escapeHtml(asset.url)}" alt="${escapeHtml(asset.caption || "asset")}" loading="lazy" />`}
      </figure>
      <div class="content-asset-fields">
        <input data-content-asset-index="${index}" data-content-asset-field="url" value="${escapeHtml(asset.url)}" placeholder="素材地址" />
        <input data-content-asset-index="${index}" data-content-asset-field="caption" value="${escapeHtml(asset.caption)}" placeholder="图片说明" />
        <select data-content-asset-index="${index}" data-content-asset-field="role">
          ${contentAssetRoles.map((role) => `<option value="${role.key}"${asset.role === role.key ? " selected" : ""}>${escapeHtml(role.label)}</option>`).join("")}
        </select>
      </div>
      <div class="content-asset-actions">
        <button class="button small" type="button" data-content-asset-up="${index}" ${index === 0 ? "disabled" : ""}>上移</button>
        <button class="button small" type="button" data-content-asset-down="${index}" ${index === assets.length - 1 ? "disabled" : ""}>下移</button>
        <button class="button small danger" type="button" data-content-asset-remove="${index}">删除</button>
      </div>
    </article>
  `).join("") : `<div class="content-asset-empty">暂无素材。可上传图片、从素材库选择，或粘贴图片/视频地址。</div>`;
}
function appendContentAssetLine(url, caption = "", role = "gallery") {
  addContentAsset({ url, caption, role });
}
function currentLowcodeForm() {
  return state.lowcodeForms.find((form) => String(form.id) === String(state.activeLowcodeFormId)) || null;
}
function setLowcodeAssetDrafts(assets = []) {
  state.lowcodeAssetDrafts = orderedContentAssets(assets);
  renderLowcodeAssetCards();
}
function addLowcodeAsset(asset) {
  const next = normalizeContentAsset(asset, state.lowcodeAssetDrafts.length);
  if (!next) return false;
  setLowcodeAssetDrafts([...state.lowcodeAssetDrafts, next]);
  return true;
}
function updateLowcodeAsset(index, field, value, options = {}) {
  if (!state.lowcodeAssetDrafts[index] || !["url", "caption", "role"].includes(field)) return;
  const next = [...state.lowcodeAssetDrafts];
  next[index] = {
    ...next[index],
    [field]: field === "role" ? normalizeContentAssetRole(value, index) : String(value || "").trim(),
  };
  state.lowcodeAssetDrafts = orderedContentAssets(next);
  if (!options.skipRender) renderLowcodeAssetCards();
}
function moveLowcodeAsset(index, direction) {
  const target = index + direction;
  if (target < 0 || target >= state.lowcodeAssetDrafts.length) return;
  const next = [...state.lowcodeAssetDrafts];
  [next[index], next[target]] = [next[target], next[index]];
  setLowcodeAssetDrafts(next);
}
function removeLowcodeAsset(index) {
  setLowcodeAssetDrafts(state.lowcodeAssetDrafts.filter((_, itemIndex) => itemIndex !== index));
}
function renderLowcodeAssetCards() {
  const list = $("lowcodeAssetCards");
  if (!list) return;
  const assets = orderedContentAssets(state.lowcodeAssetDrafts);
  list.innerHTML = assets.length ? assets.map((asset, index) => `
    <article class="content-asset-card">
      <figure class="content-asset-thumb">
        ${looksLikeVideoAsset(asset) ? `<span>VIDEO</span>` : `<img src="${escapeHtml(asset.url)}" alt="${escapeHtml(asset.caption || "asset")}" loading="lazy" />`}
      </figure>
      <div class="content-asset-fields">
        <input data-lowcode-asset-index="${index}" data-lowcode-asset-field="url" value="${escapeHtml(asset.url)}" placeholder="素材地址" />
        <input data-lowcode-asset-index="${index}" data-lowcode-asset-field="caption" value="${escapeHtml(asset.caption)}" placeholder="图片说明" />
        <select data-lowcode-asset-index="${index}" data-lowcode-asset-field="role">
          ${contentAssetRoles.map((role) => `<option value="${role.key}"${asset.role === role.key ? " selected" : ""}>${escapeHtml(role.label)}</option>`).join("")}
        </select>
      </div>
      <div class="content-asset-actions">
        <button class="button small" type="button" data-lowcode-asset-up="${index}" ${index === 0 ? "disabled" : ""}>上移</button>
        <button class="button small" type="button" data-lowcode-asset-down="${index}" ${index === assets.length - 1 ? "disabled" : ""}>下移</button>
        <button class="button small danger" type="button" data-lowcode-asset-remove="${index}">删除</button>
      </div>
    </article>
  `).join("") : `<div class="content-asset-empty">暂无素材。可上传图片、从素材库选择，或粘贴图片/视频地址。</div>`;
}
function lowcodeFieldInput(field) {
  const key = escapeHtml(field.key);
  const label = escapeHtml(field.label || field.key);
  const placeholder = escapeHtml(field.placeholder || "");
  const defaultValue = escapeHtml(field.defaultValue || "");
  const required = field.required ? " required" : "";
  if (field.type === "textarea" || field.type === "richtext") {
    return `<label class="lowcode-field wide"><span>${label}${field.required ? " *" : ""}</span><textarea data-lowcode-field="${key}" rows="4" placeholder="${placeholder}"${required}>${defaultValue}</textarea></label>`;
  }
  if (field.type === "checkbox" || field.type === "switch") {
    return `<label class="lowcode-field lowcode-check"><input data-lowcode-field="${key}" type="checkbox" ${field.defaultValue === true || field.defaultValue === "true" || field.defaultValue === "1" ? "checked" : ""} /> <span>${label}</span></label>`;
  }
  if (field.type === "select" && Array.isArray(field.options) && field.options.length) {
    return `<label class="lowcode-field"><span>${label}${field.required ? " *" : ""}</span><select data-lowcode-field="${key}"${required}>${field.options.map((option) => `<option value="${escapeHtml(option.value)}"${String(option.value) === String(field.defaultValue || "") ? " selected" : ""}>${escapeHtml(option.label || option.value)}</option>`).join("")}</select></label>`;
  }
  if (field.type === "asset_list" || field.type === "image_upload" || field.type === "video_upload") {
    return "";
  }
  const type = field.type === "number" ? "number" : field.type === "date" ? "date" : "text";
  return `<label class="lowcode-field"><span>${label}${field.required ? " *" : ""}</span><input data-lowcode-field="${key}" type="${type}" value="${defaultValue}" placeholder="${placeholder}"${required} /></label>`;
}
function renderLowcodeForms() {
  const grid = $("lowcodeFormsGrid");
  if (!grid) return;
  const forms = state.lowcodeForms || [];
  if ($("newLowcodeTemplate")) $("newLowcodeTemplate").hidden = !isAdmin();
  $("lowcodeFormsSummary").textContent = `${forms.length} 个模板`;
  grid.innerHTML = forms.length ? forms.map((form) => {
    const schema = form.schema || {};
    const moduleLabel = schema.moduleLabel || (moduleMeta(form.targetModuleKey, form.targetPortalType) || {}).label || form.targetModuleKey || "-";
    const contentType = form.targetContentType || schema.contentType || "article";
    const fieldCount = (schema.fields || []).filter((field) => field.type !== "asset_list").length;
    const enabled = form.enabled !== false;
    return `<article class="lowcode-form-card">
      <header>
        <div>
          <strong>${escapeHtml(form.name)}</strong>
          <span>${escapeHtml(moduleLabel)} · ${escapeHtml(contentTypeLabel(contentType))}${enabled ? "" : " · 已停用"}</span>
        </div>
        <span class="badge ${enabled ? "" : "warn"}">${fieldCount} 项</span>
      </header>
      <p>${escapeHtml(form.description || "按模板规范填写资料。")}</p>
      <div class="actions">
        <button class="button small primary" type="button" data-lowcode-start="${form.id}" ${enabled ? "" : "disabled"}>按模板填写</button>
        ${isAdmin() ? `<button class="button small" type="button" data-lowcode-edit="${form.id}">编辑模板</button>
        <button class="button small" type="button" data-lowcode-copy="${form.id}">复制</button>
        <button class="button small" type="button" data-lowcode-versions="${form.id}">版本</button>` : ""}
      </div>
    </article>`;
  }).join("") : `<div class="empty">当前门户暂无资料采集模板</div>`;
}
function renderLowcodeVersions(form, versions) {
  const list = $("lowcodeVersionList");
  if (!list) return;
  $("lowcodeVersionTitle").textContent = `模板版本历史：${form ? form.name : "资料采集模板"}`;
  list.innerHTML = versions.length ? versions.map((version) => {
    const schema = version.schema || {};
    const fields = (schema.fields || []).filter((field) => field.type !== "asset_list");
    return `<article class="lowcode-version-card">
      <header>
        <div>
          <strong>版本 v${escapeHtml(version.versionNo)}</strong>
          <span>${escapeHtml(version.createdBy || "-")} · ${formatTime(version.createdAt)}</span>
        </div>
        <span class="badge ${version.status === "active" ? "success" : ""}">${escapeHtml(version.status === "active" ? "当前" : "归档")}</span>
      </header>
      <p>${escapeHtml((schema.moduleLabel || form?.targetModuleKey || "-"))} · ${escapeHtml(contentTypeLabel(schema.contentType || form?.targetContentType))} · ${fields.length} 个字段</p>
      <div class="lowcode-version-fields">
        ${fields.slice(0, 12).map((field) => `<span>${escapeHtml(field.label || field.key)}${field.required ? " *" : ""}</span>`).join("")}
      </div>
    </article>`;
  }).join("") : `<div class="empty">暂无版本记录</div>`;
}
async function showLowcodeVersions(formId) {
  const data = await jsonApi(`/api/lowcode/forms/${formId}/versions`);
  state.viewingLowcodeFormId = formId;
  state.lowcodeVersions = data.versions || [];
  renderLowcodeVersions(data.form, state.lowcodeVersions);
  $("lowcodeVersionPanel").hidden = false;
  $("lowcodeTemplateForm").hidden = true;
  $("lowcodeRecordForm").hidden = true;
  $("contentItemForm").hidden = true;
  $("pageForm").hidden = true;
  $("lowcodeVersionPanel").scrollIntoView({ behavior: "smooth", block: "start" });
}
function renderLowcodeRecords() {
  const listNode = $("lowcodeRecordsList");
  if (!listNode) return;
  const records = state.lowcodeRecords || [];
  const approved = records.filter((record) => (record.effectiveStatus || record.status) === "approved").length;
  $("lowcodeRecordsSummary").textContent = `${approved}/${records.length || 0} 已通过`;
  listNode.innerHTML = records.length ? records.slice(0, 12).map((record) => {
    const status = record.effectiveStatus || record.contentReviewStatus || record.status;
    const data = record.data && record.data.fields ? record.data.fields : {};
    const summary = data.summary || data.subtitle || record.contentTitle || "暂无摘要";
    return `<article class="lowcode-record-card">
      <header>
        <div>
          <strong>${escapeHtml(record.contentTitle || data.title || "未命名资料")}</strong>
          <span>${escapeHtml(record.formName || "资料采集模板")} · v${escapeHtml(record.formVersionNo || "-")} · ${escapeHtml(record.submittedBy || "-")} · ${formatTime(record.submittedAt)}</span>
        </div>
        ${badge(status)}
      </header>
      <p>${escapeHtml(summary)}</p>
      <div class="content-item-meta">
        <span>${escapeHtml(record.contentModuleLabel || "-")}</span>
        <span>${escapeHtml(record.contentTypeLabel || contentTypeLabel(record.contentType))}</span>
        <span>资料 ID ${escapeHtml(record.contentItemId || "-")}</span>
      </div>
      ${record.reviewNote ? `<p class="warn-text">审核意见：${escapeHtml(record.reviewNote)}</p>` : ""}
      <div class="actions">
        ${record.contentItemId ? `<button class="button small primary" type="button" data-lowcode-record-edit="${record.contentItemId}">编辑生成资料</button>` : ""}
        ${record.previewUrl && status === "approved" ? `<a class="button small" target="_blank" rel="noopener" href="${escapeHtml(record.previewUrl)}">预览</a>` : ""}
      </div>
    </article>`;
  }).join("") : `<div class="empty">暂无模板提交记录</div>`;
}
function fillLowcodeRecordForm(form) {
  if (!form) return;
  state.activeLowcodeFormId = form.id;
  setLowcodeAssetDrafts([]);
  const schema = form.schema || {};
  const fields = (schema.fields || []).filter((field) => field.type !== "asset_list" && field.type !== "image_upload" && field.type !== "video_upload");
  $("lowcodeRecordTitle").textContent = form.name || "资料采集模板";
  $("lowcodeRecordHint").textContent = form.description || "按模板填写后自动生成结构化资料。";
  $("lowcodeDynamicFields").innerHTML = fields.map(lowcodeFieldInput).join("");
  $("lowcodeAssetUrl").value = "";
  $("lowcodeAssetCaption").value = "";
  $("lowcodeAssetRole").value = "gallery";
  $("lowcodeAssetFile").value = "";
  $("lowcodeRecordForm").hidden = false;
  $("lowcodeTemplateForm").hidden = true;
  $("lowcodeVersionPanel").hidden = true;
  $("contentItemForm").hidden = true;
  $("pageForm").hidden = true;
  setStatus($("lowcodeRecordStatus"), "", "");
  $("lowcodeRecordForm").scrollIntoView({ behavior: "smooth", block: "start" });
}
function lowcodeRecordPayload() {
  const data = {};
  document.querySelectorAll("[data-lowcode-field]").forEach((field) => {
    const key = field.dataset.lowcodeField;
    data[key] = field.type === "checkbox" ? field.checked : field.value.trim();
  });
  data.assets = orderedContentAssets(state.lowcodeAssetDrafts);
  return { data };
}
function normalizeLowcodeFieldDraft(field = {}, index = 0) {
  const key = String(field.key || `field${index + 1}`).trim();
  const type = lowcodeFieldTypes.some((item) => item.key === field.type) ? field.type : "text";
  return {
    key,
    label: String(field.label || key || "字段").trim(),
    type,
    required: Boolean(field.required),
    mapping: String(field.mapping || "").trim(),
    placeholder: String(field.placeholder || "").trim(),
    defaultValue: field.defaultValue == null ? "" : String(field.defaultValue),
    sortOrder: index,
  };
}
function setLowcodeFieldDrafts(fields = []) {
  state.lowcodeFieldDrafts = fields.map(normalizeLowcodeFieldDraft);
  renderLowcodeFieldEditor();
}
function renderLowcodeTemplatePortalOptions() {
  const select = $("lowcodeTemplatePortalType");
  if (!select) return;
  select.innerHTML = Object.entries(portalTypeLabels)
    .map(([key, label]) => `<option value="${key}">${escapeHtml(label)}</option>`)
    .join("");
}
function renderLowcodeTemplateModuleOptions(portalType = $("lowcodeTemplatePortalType")?.value || selectedPortalType()) {
  const select = $("lowcodeTemplateModule");
  if (!select) return;
  const modules = modulesForPortalType(portalType);
  select.innerHTML = modules.map((module) => `<option value="${module.key}">${escapeHtml(module.label)}</option>`).join("");
}
function renderLowcodeTemplateContentTypeOptions() {
  const select = $("lowcodeTemplateContentType");
  if (!select) return;
  select.innerHTML = contentTypes.map((type) => `<option value="${type.key}">${escapeHtml(type.label)}</option>`).join("");
}
function lowcodeFieldEditorRow(field, index) {
  return `<article class="lowcode-field-editor-row" data-lowcode-field-row="${index}">
    <div class="lowcode-field-editor-main">
      <input data-lowcode-config-field="label" value="${escapeHtml(field.label)}" placeholder="字段名称" />
      <input data-lowcode-config-field="key" value="${escapeHtml(field.key)}" placeholder="字段编码" />
      <select data-lowcode-config-field="type">
        ${lowcodeFieldTypes.map((type) => `<option value="${type.key}"${field.type === type.key ? " selected" : ""}>${escapeHtml(type.label)}</option>`).join("")}
      </select>
      <input data-lowcode-config-field="mapping" list="lowcodeMappingOptions" value="${escapeHtml(field.mapping)}" placeholder="映射目标" />
      <input data-lowcode-config-field="placeholder" value="${escapeHtml(field.placeholder)}" placeholder="提示语" />
      <input data-lowcode-config-field="defaultValue" value="${escapeHtml(field.defaultValue)}" placeholder="默认值" />
    </div>
    <div class="lowcode-field-editor-actions">
      <label class="check-inline"><input data-lowcode-config-field="required" type="checkbox" ${field.required ? "checked" : ""} /> 必填</label>
      <button class="button small" type="button" data-lowcode-field-up="${index}" ${index === 0 ? "disabled" : ""}>上移</button>
      <button class="button small" type="button" data-lowcode-field-down="${index}" ${index === state.lowcodeFieldDrafts.length - 1 ? "disabled" : ""}>下移</button>
      <button class="button small danger" type="button" data-lowcode-field-remove="${index}">删除</button>
    </div>
  </article>`;
}
function renderLowcodeFieldEditor() {
  const list = $("lowcodeFieldEditorList");
  if (!list) return;
  list.innerHTML = state.lowcodeFieldDrafts.length
    ? state.lowcodeFieldDrafts.map(lowcodeFieldEditorRow).join("")
    : `<div class="empty">暂无字段，建议先添加标题、摘要和正文。</div>`;
}
function updateLowcodeFieldDraft(index, field, value) {
  if (!state.lowcodeFieldDrafts[index]) return;
  const next = [...state.lowcodeFieldDrafts];
  next[index] = {
    ...next[index],
    [field]: field === "required" ? Boolean(value) : String(value || "").trim(),
  };
  state.lowcodeFieldDrafts = next.map(normalizeLowcodeFieldDraft);
}
function moveLowcodeFieldDraft(index, direction) {
  const target = index + direction;
  if (target < 0 || target >= state.lowcodeFieldDrafts.length) return;
  const next = [...state.lowcodeFieldDrafts];
  [next[index], next[target]] = [next[target], next[index]];
  setLowcodeFieldDrafts(next);
}
function removeLowcodeFieldDraft(index) {
  setLowcodeFieldDrafts(state.lowcodeFieldDrafts.filter((_, itemIndex) => itemIndex !== index));
}
function addLowcodeFieldDraft() {
  setLowcodeFieldDrafts([...state.lowcodeFieldDrafts, {
    key: `field${state.lowcodeFieldDrafts.length + 1}`,
    label: "新字段",
    type: "text",
    required: false,
    mapping: "content_item.meta_json.新字段",
    placeholder: "",
    defaultValue: "",
  }]);
}
function fillLowcodeTemplateForm(form = {}) {
  if (!isAdmin()) return;
  renderLowcodeTemplatePortalOptions();
  renderLowcodeTemplateContentTypeOptions();
  state.editingLowcodeFormId = form.id || "";
  const portalType = normalizePortalType(form.targetPortalType || selectedPortalType());
  $("lowcodeTemplatePortalType").value = portalType;
  renderLowcodeTemplateModuleOptions(portalType);
  const moduleKey = form.targetModuleKey || (modulesForPortalType(portalType)[0] || {}).key || "";
  const contentType = normalizeContentType(form.targetContentType || defaultContentTypeForModule(moduleKey));
  $("lowcodeTemplateModule").value = moduleKey;
  $("lowcodeTemplateContentType").value = contentType;
  $("lowcodeTemplateName").value = form.name || `${(moduleMeta(moduleKey, portalType) || {}).label || "资料"}采集表`;
  $("lowcodeTemplateCode").value = form.code || `LC-${portalType.toUpperCase()}-${String(moduleKey || "CUSTOM").toUpperCase()}-${Date.now().toString().slice(-4)}`;
  $("lowcodeTemplateDescription").value = form.description || "";
  $("lowcodeTemplateEnabled").checked = form.enabled !== false;
  setLowcodeFieldDrafts(((form.schema || {}).fields || []).filter((field) => field.type !== "asset_list"));
  $("lowcodeTemplateForm").hidden = false;
  $("lowcodeRecordForm").hidden = true;
  $("lowcodeVersionPanel").hidden = true;
  $("contentItemForm").hidden = true;
  $("pageForm").hidden = true;
  setStatus($("lowcodeTemplateStatus"), "", "");
  $("lowcodeTemplateForm").scrollIntoView({ behavior: "smooth", block: "start" });
}
function lowcodeTemplatePayload() {
  const portalType = normalizePortalType($("lowcodeTemplatePortalType").value);
  const moduleKey = $("lowcodeTemplateModule").value;
  const contentType = normalizeContentType($("lowcodeTemplateContentType").value, defaultContentTypeForModule(moduleKey));
  const fields = state.lowcodeFieldDrafts
    .map(normalizeLowcodeFieldDraft)
    .filter((field) => field.key && field.label)
    .map((field, index) => ({ ...field, sortOrder: index }));
  fields.push({
    key: "assets",
    label: "图片/视频素材",
    type: "asset_list",
    required: false,
    mapping: "content_item.assets.gallery",
    placeholder: "可上传、从素材库选择，或一行一个素材地址",
    defaultValue: "",
    sortOrder: fields.length,
  });
  return {
    name: $("lowcodeTemplateName").value.trim(),
    code: $("lowcodeTemplateCode").value.trim(),
    description: $("lowcodeTemplateDescription").value.trim(),
    targetPortalType: portalType,
    targetModuleKey: moduleKey,
    targetContentType: contentType,
    enabled: $("lowcodeTemplateEnabled").checked,
    schema: {
      portalType,
      moduleKey,
      moduleLabel: (moduleMeta(moduleKey, portalType) || {}).label || moduleKey,
      contentType,
      contentTypeLabel: contentTypeLabel(contentType),
      fields,
      mapping: { target: "content_items", moduleKey, contentType },
    },
  };
}
function topicRichTemplate(moduleKey) {
  const meta = moduleMeta(moduleKey, "topic") || topicModules[0];
  const contentType = defaultContentTypeForModule(moduleKey);
  return {
    category: meta.label,
    source: "专题门户",
    title: meta.label,
    subtitle: meta.description,
    contentType,
    body: contentBodyTemplate(contentType, meta.label),
  };
}
function templateForModule(moduleKey) {
  const portalType = selectedPortalType();
  if (portalType === "topic") return richTemplates[`topic:${moduleKey}`] || topicRichTemplate(moduleKey);
  const template = richTemplates[moduleKey] || genericRichTemplate(moduleKey);
  return { ...template, contentType: template.contentType || defaultContentTypeForModule(moduleKey) };
}
function localModuleKeyForCategory(category, portalType = selectedPortalType()) {
  const text = String(category || "").trim();
  if (!text) return "";
  const modules = modulesForPortalType(portalType);
  const lower = text.toLowerCase();
  const exact = modules.find((module) => module.label === text || module.key.toLowerCase() === lower);
  if (exact) return exact.key;
  const aliasMatch = modules.find((module) => (module.aliases || []).some((alias) => text.includes(alias)));
  if (aliasMatch) return aliasMatch.key;
  const aliasMap = {
    overview: ["基本情况", "系部介绍", "系部简介", "概况", "概览", "简介"],
    majors: ["专业设置", "专业", "专业群", "课程", "就业方向"],
    training: ["实训基地", "实训", "实践", "基地", "设备"],
    cooperation: ["产教融合", "校企合作", "订单班", "共同体", "社会服务"],
    achievements: ["教学成果", "成果", "竞赛", "荣誉", "育人成果", "名师名匠", "优秀毕业生", "学生"],
    media: ["视频资源", "视频", "宣传片", "作品"],
    systems: ["特色系统入口", "系统入口", "业务系统", "互动平台", "系统"],
    resources: ["特色数字资源", "数字资源", "资源库", "专题资料", "扫码内容", "专题"],
  };
  return Object.keys(aliasMap).find((key) => aliasMap[key].some((alias) => text.includes(alias))) || "";
}
function buildCoverageFromPages(pages, portalType = selectedPortalType()) {
  const modules = modulesForPortalType(portalType);
  const grouped = Object.fromEntries(modules.map((module) => [module.key, []]));
  const unmatched = [];
  (pages || []).forEach((page) => {
    const key = page.moduleKey || localModuleKeyForCategory(page.category, portalType);
    if (key && grouped[key]) grouped[key].push(page);
    else unmatched.push(page);
  });
  const coverageModules = modules.map((module) => {
    const items = grouped[module.key] || [];
    const approved = items.filter((page) => page.enabled && page.reviewStatus === "approved");
    const pending = items.filter((page) => ["pending", "pending_delete"].includes(page.reviewStatus));
    return {
      ...module,
      count: items.length,
      approvedCount: approved.length,
      pendingCount: pending.length,
      covered: items.length > 0,
      publishReady: approved.length > 0,
      pages: items,
    };
  });
  return {
    portalType: normalizePortalType(portalType),
    portalTypeLabel: portalTypeLabel(portalType),
    total: coverageModules.length,
    covered: coverageModules.filter((module) => module.covered).length,
    publishReady: coverageModules.filter((module) => module.publishReady).length,
    missingLabels: coverageModules.filter((module) => !module.covered).map((module) => module.label),
    modules: coverageModules,
    unmatched,
  };
}
function renderModuleLibrary(coverage = state.moduleCoverage) {
  const portalType = normalizePortalType((coverage && coverage.portalType) || selectedPortalType());
  const modules = modulesForPortalType(portalType);
  const normalized = coverage && coverage.modules ? coverage : buildCoverageFromPages(state.pages, portalType);
  state.moduleCoverage = normalized;
  if (!$("moduleLibrary")) return;
  const total = normalized.total || modules.length;
  const covered = normalized.covered || 0;
  const ready = normalized.publishReady || 0;
  setText($("moduleCoverageSummary"), `已覆盖 ${covered}/${total} 个标准板块，其中 ${ready} 个有已通过资料。`);
  const complete = covered >= total;
  $("moduleCoverageBadge").textContent = complete ? "完整" : `缺 ${total - covered}`;
  $("moduleCoverageBadge").className = `badge ${complete ? "success" : "warn"}`;
  $("moduleCoverageTitle").textContent = `${portalTypeLabel(portalType)}标准板块覆盖`;
  $("moduleLibrary").innerHTML = (normalized.modules || modules).map((module) => {
    const stateClass = module.publishReady ? "is-ready" : module.covered ? "is-covered" : "is-missing";
    const stateText = module.publishReady ? "可发布" : module.covered ? "待审核" : "缺失";
    const pageText = module.count ? `${module.count} 条资料，${module.approvedCount || 0} 条已通过` : "建议补充该板块资料";
    const actionText = module.covered ? "新增资料" : "补齐板块";
    return `<article class="${stateClass}" data-module-key="${module.key}">
      <span class="module-state">${stateText}</span>
      <strong>${escapeHtml(module.label)}</strong>
      <span>${escapeHtml(module.description)}</span>
      <small>${escapeHtml(pageText)}</small>
      <button class="module-create" type="button" data-module-create="${escapeHtml(module.key)}">${actionText}</button>
    </article>`;
  }).join("");
}
function generatedModuleCode(moduleKey) {
  const meta = moduleMeta(moduleKey) || modulesForPortalType()[0];
  const projectId = $("projectSelect") ? $("projectSelect").value || "P" : "P";
  const suffix = Date.now().toString(36).toUpperCase().slice(-5);
  return `${meta.code}-${projectId}-${suffix}`;
}
function applyRichTemplate(moduleKey) {
  const template = templateForModule(moduleKey);
  if (!template) return;
  const currentCode = $("pageCode").value.trim();
  if (!currentCode || currentCode === state.generatedCode) {
    state.generatedCode = generatedModuleCode(moduleKey);
    $("pageCode").value = state.generatedCode;
  }
  $("pageCategory").value = template.category;
  $("pageSource").value = template.source;
  $("pageTitle").value = template.title;
  $("pageSubtitle").value = template.subtitle;
  if ($("pageContentType")) $("pageContentType").value = normalizeContentType(template.contentType || defaultContentTypeForModule(moduleKey));
  setTemplateGuide(moduleKey);
  setRichBody(template.body);
}
function startPageDraft(moduleKey) {
  state.editingCode = "";
  state.generatedCode = "";
  fillPage({ accent: "#f59a13", publishedAt: new Date().toISOString().slice(0, 10), body: "" });
  applyRichTemplate(moduleKey);
  setStatus($("pageStatus"), "已按标准板块生成草稿，请补充文字和图片后保存。", "success");
  $("pageForm").scrollIntoView({ behavior: "smooth", block: "start" });
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
  const meta = moduleMeta(templateKey);
  const portalType = selectedPortalType();
  const selectedType = $("pageContentType") ? normalizeContentType($("pageContentType").value || defaultContentTypeForModule(templateKey)) : defaultContentTypeForModule(templateKey);
  const guide = templateGuides[`${portalType}:${templateKey}`] || (portalType === "topic" ? null : templateGuides[templateKey]) || (meta
    ? [meta.label, `${meta.description}；资料类型：${contentTypeLabel(selectedType)}，前端抽屉会按该类型自动排版。`]
    : ["自定义内容", "可按展览资料自由编辑字段；右侧预览会同步当前标题、封面和正文结构。"]);
  setText($("templateGuideTitle"), guide[0]);
  setText($("templateGuideScene"), guide[1]);
  setText($("templateGuideSummary"), templateKey ? `已套用模板 · ${contentTypeLabel(selectedType)}` : "选择模板后查看内容结构和展示效果");
}
function sourceForPortalType(portalType = selectedPortalType()) {
  return { school: "学校门户", department: "系部门户", topic: "专题门户" }[normalizePortalType(portalType)];
}
function genericRichTemplate(moduleKey) {
  const meta = moduleMeta(moduleKey) || modulesForPortalType()[0];
  const contentType = defaultContentTypeForModule(moduleKey);
  return {
    category: meta.label,
    source: sourceForPortalType(),
    title: meta.label,
    subtitle: meta.description,
    contentType,
    body: contentBodyTemplate(contentType, meta.label),
  };
}
function renderTemplateActions(portalType = selectedPortalType()) {
  if (!$("templateActions")) return;
  const modules = modulesForPortalType(portalType);
  const labelsText = modules.map((module) => module.label).join("、");
  const intro = `按${portalTypeLabel(portalType)}维护${labelsText}等板块资料。`;
  $("templateActions").innerHTML = modules.map((module) => (
    `<button type="button" data-template="${module.key}">${escapeHtml(module.label)}</button>`
  )).join("");
  if ($("moduleCategoryList")) {
    $("moduleCategoryList").innerHTML = modules.map((module) => `<option value="${escapeHtml(module.label)}"></option>`).join("");
  }
  if ($("pageCategory")) {
    $("pageCategory").placeholder = `板块，如 ${modules.slice(0, 3).map((module) => module.label).join(" / ")}`;
  }
  if (state.activeView === "pages") setText($("viewIntro"), intro);
  setText($("pagesPanelIntro"), intro);
}
function renderContentModuleOptions(portalType = selectedPortalType()) {
  if (!$("contentModule")) return;
  $("contentModule").innerHTML = modulesForPortalType(portalType)
    .map((module) => `<option value="${escapeHtml(module.key)}">${escapeHtml(module.label)}</option>`)
    .join("");
}
function renderContentTypeOptions() {
  if (!$("contentType")) return;
  $("contentType").innerHTML = contentTypes
    .map((type) => `<option value="${escapeHtml(type.key)}">${escapeHtml(type.label)}</option>`)
    .join("");
}
function updateContentPreview() {
  if (!$("contentPreview")) return;
  const module = moduleMeta($("contentModule").value) || {};
  const type = normalizeContentType($("contentType").value);
  const assets = currentContentAssets();
  const fields = metaJsonFromText($("contentMetaText").value);
  setText($("contentPreviewMeta"), `${module.label || "板块"} · ${contentTypeLabel(type)} · ${assets.length} 个素材`);
  const fieldHtml = Object.keys(fields).length
    ? `<div class="content-preview-fields">${Object.entries(fields).map(([key, value]) => `<span><b>${escapeHtml(key)}</b>${escapeHtml(value)}</span>`).join("")}</div>`
    : "";
  const firstAsset = assets[0];
  $("contentPreview").innerHTML = `
    ${firstAsset ? `<figure><img src="${escapeHtml(firstAsset.url)}" alt="${escapeHtml(firstAsset.caption || $("contentTitle").value)}" /></figure>` : ""}
    <div>
      <span>${escapeHtml(contentTypeLabel(type))}</span>
      <h3>${escapeHtml($("contentTitle").value.trim() || module.label || "结构化资料")}</h3>
      <p>${escapeHtml($("contentSummary").value.trim() || $("contentSubtitle").value.trim() || module.description || "资料摘要将在这里预览。")}</p>
      ${fieldHtml}
    </div>
  `;
}
function updatePagePreview() {
  if (!$("previewTitle")) return;
  setText($("previewCode"), $("pageCode").value.trim() ? `编号 ${$("pageCode").value.trim()}` : "编号");
  setText($("previewCategory"), $("pageCategory").value.trim() || "栏目");
  const sourceText = $("pageSource").value.trim();
  const typeText = $("pageContentType") ? contentTypeLabel($("pageContentType").value) : "";
  setText($("previewSource"), [sourceText || "来源", typeText].filter(Boolean).join(" · "));
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
  $("brandTitle").textContent = isAdmin() ? "数字门户后台" : "门户资料工作台";
  $("consoleEyebrow").textContent = isAdmin() ? "Portal Exhibition Console" : "Portal Submission";
  document.title = isAdmin() ? "数字门户后台" : "门户资料工作台";
  $("roleBadge").textContent = isAdmin() ? "管理员" : "老师工作台";
  $("projectsHeading").textContent = isAdmin() ? "门户管理" : "我的门户";
  $("projectsIntro").textContent = isAdmin() ? "统一维护学校门户、系部门户和专题门户，并分配归属老师。" : "查看自己负责的门户，必要时提交基础信息修改。";
  $("projectFormTitle").textContent = isAdmin() ? "门户配置" : "门户信息编辑";
  $("projectSubmitButton").textContent = isAdmin() ? "保存/提交审核" : "提交门户信息修改";
  $("pagesHeading").textContent = isAdmin() ? "板块资料" : "上传板块资料";
  setText($("pagesPanelIntro"), isAdmin() ? "按门户维护基本情况、专业设置、实训基地、产教融合、教学成果等板块资料。" : "维护自己门户下的板块资料，提交后由管理员审核发布。");
  $("newPage").textContent = isAdmin() ? "新建板块资料" : "上传板块资料";
  $("pageFormTitle").textContent = isAdmin() ? "板块资料编辑" : "板块资料编辑";
  $("pageSubmitButton").textContent = isAdmin() ? "保存/提交审核" : "提交审核";
  $("assetsHeading").textContent = isAdmin() ? "素材库" : "素材库";
  $("assetsIntro").textContent = isAdmin() ? "上传、复用和删除门户展示素材；老师只能管理自己上传的素材。" : "上传板块资料所需图片，只能查看和管理自己上传的素材。";
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
  return refreshView(view);
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
  $("projectSelect").innerHTML = state.projects.map((p) => `<option value="${p.id}">${escapeHtml(portalOptionLabel(p))}</option>`).join("");
  $("deployProject").innerHTML = state.projects.map((p) => `<option value="${p.id}">${escapeHtml(portalOptionLabel(p))}</option>`).join("");
  if (selected) {
    $("projectSelect").value = selected.id;
    $("deployProject").value = selected.id;
    renderTemplateActions(selected.portalType);
  }
}
async function loadUsers() {
  if (!isAdmin()) return;
  const data = await jsonApi("/api/users");
  state.users = data.users || [];
  $("projectOwner").innerHTML = state.users.map((u) => {
    const role = u.role === "admin" ? "管理员" : "老师";
    const disabled = u.enabled ? "" : " · 已禁用";
    return `<option value="${u.username}">${escapeHtml(u.displayName)} (${escapeHtml(u.username)} · ${role}${disabled})</option>`;
  }).join("");
}

async function loadPortalCompletionRows() {
  if (!state.projects.length) await loadProjects();
  const projects = state.projects.slice().sort((a, b) => {
    const order = { school: 0, department: 1, topic: 2 };
    const typeDelta = (order[normalizePortalType(a.portalType)] ?? 9) - (order[normalizePortalType(b.portalType)] ?? 9);
    return typeDelta || String(a.name || "").localeCompare(String(b.name || ""), "zh-Hans-CN");
  });
  return Promise.all(projects.map(async (project) => {
    try {
      const data = await jsonApi(`/api/projects/${project.id}/pages`);
      const pages = data.pages || [];
      const coverage = data.coverage || buildCoverageFromPages(pages, project.portalType);
      return { project, pages, coverage };
    } catch (err) {
      return {
        project,
        pages: [],
        coverage: buildCoverageFromPages([], project.portalType),
        error: err.message || "读取失败",
      };
    }
  }));
}

function renderPortalCompletionOverview(rows) {
  const readyCount = rows.filter((row) => row.coverage.total && row.coverage.publishReady === row.coverage.total).length;
  const reviewCount = rows.filter((row) => row.coverage.total && row.coverage.covered === row.coverage.total && row.coverage.publishReady < row.coverage.total).length;
  const incompleteCount = Math.max(0, rows.length - readyCount - reviewCount);
  const cards = rows.map(({ project, pages, coverage, error }) => {
    const total = Number(coverage.total || 0);
    const ready = Number(coverage.publishReady || 0);
    const covered = Number(coverage.covered || 0);
    const missingLabels = coverage.missingLabels || [];
    const statusClass = error ? "danger" : total && ready === total ? "ready" : total && covered === total ? "review" : "missing";
    const statusText = error ? "异常" : total && ready === total ? "已就绪" : total && covered === total ? "待审核" : "待补齐";
    const previewUrl = portalCompletionPreviewUrl(project);
    const moduleList = (coverage.modules || []).map((module) => `
      <button class="${module.publishReady ? "ready" : module.covered ? "covered" : "missing"}" type="button" data-dashboard-pages="${project.id}" data-dashboard-module="${escapeHtml(module.key)}">${escapeHtml(module.label)}</button>
    `).join("");
    const missingText = error
      ? escapeHtml(error)
      : missingLabels.length
        ? `缺：${escapeHtml(missingLabels.slice(0, 4).join("、"))}${missingLabels.length > 4 ? " 等" : ""}`
        : "标准板块已覆盖";
    return `
      <article class="portal-completion-card ${statusClass}">
        <header>
          <div>
            <span>${escapeHtml(portalTypeLabel(project.portalType))}</span>
            <strong>${escapeHtml(project.name)}</strong>
          </div>
          <em>${statusText}</em>
        </header>
        <div class="portal-completion-meter" aria-label="完成度">
          <i style="width:${total ? Math.round((ready / total) * 100) : 0}%"></i>
        </div>
        <p>${total ? `已通过 ${ready}/${total}，已维护 ${covered}/${total}` : "暂无标准板块定义"}；资料 ${pages.length} 条</p>
        <small>${missingText}</small>
        ${moduleList ? `<div class="portal-completion-modules">${moduleList}</div>` : ""}
        <div class="actions">
          <button class="button small primary" type="button" data-dashboard-pages="${project.id}">维护资料</button>
          ${previewUrl ? `<a class="button small" target="_blank" rel="noopener" href="${escapeHtml(previewUrl)}">前台预览</a>` : ""}
        </div>
      </article>
    `;
  }).join("");
  return `
    <section class="panel portal-completion-panel">
      <div class="panel-head">
        <div>
          <h2>门户完成度</h2>
          <p>按门户查看标准板块覆盖、审核状态和前台预览入口。</p>
        </div>
        <div class="completion-summary">
          <span>已就绪 ${readyCount}</span>
          <span>待审核 ${reviewCount}</span>
          <span>待补齐 ${incompleteCount}</span>
        </div>
      </div>
      <div class="portal-completion-grid">${cards || `<div class="empty">暂无门户</div>`}</div>
    </section>
  `;
}

function portalTaskPriority(row) {
  const coverage = row.coverage || {};
  const modules = coverage.modules || [];
  const missing = modules.filter((module) => !module.covered);
  const coveredNotReady = modules.filter((module) => module.covered && !module.publishReady);
  if (row.error) return 0;
  if (missing.length) return 1;
  if (coveredNotReady.length) return 2;
  return 3;
}

function renderPortalPriorityTasks(rows) {
  const tasks = rows
    .map((row) => {
      const project = row.project;
      const coverage = row.coverage || {};
      const modules = coverage.modules || [];
      const missing = modules.filter((module) => !module.covered);
      const review = modules.filter((module) => module.covered && !module.publishReady);
      const target = missing[0] || review[0] || modules[0] || null;
      const priority = portalTaskPriority(row);
      const actionText = row.error
        ? "检查门户"
        : missing.length
          ? `补齐 ${missing[0].label}`
          : review.length
            ? "处理待审核"
            : "复核前台";
      const detail = row.error
        ? row.error
        : missing.length
          ? `缺 ${missing.map((item) => item.label).slice(0, 3).join("、")}${missing.length > 3 ? " 等" : ""}`
          : review.length
            ? `${review.length} 个板块已维护，等待审核或发布`
            : "标准板块已覆盖，可检查前台呈现";
      return { project, target, priority, actionText, detail, missingCount: missing.length, reviewCount: review.length };
    })
    .sort((a, b) => a.priority - b.priority || b.missingCount - a.missingCount || b.reviewCount - a.reviewCount)
    .slice(0, 5);

  const items = tasks.map((task, index) => {
    const moduleKey = task.target ? ` data-dashboard-module="${escapeHtml(task.target.key)}"` : "";
    const previewUrl = portalCompletionPreviewUrl(task.project);
    const status = task.priority === 1 ? "missing" : task.priority === 2 ? "review" : task.priority === 0 ? "danger" : "ready";
    return `
      <article class="portal-task-card ${status}">
        <span>${index + 1}</span>
        <div>
          <strong>${escapeHtml(task.project.name)}</strong>
          <p>${escapeHtml(portalTypeLabel(task.project.portalType))} · ${escapeHtml(task.detail)}</p>
        </div>
        <div class="actions">
          <button class="button small primary" type="button" data-dashboard-pages="${task.project.id}"${moduleKey}>${escapeHtml(task.actionText)}</button>
          ${previewUrl ? `<a class="button small" target="_blank" rel="noopener" href="${escapeHtml(previewUrl)}">预览</a>` : ""}
        </div>
      </article>
    `;
  }).join("");

  return `
    <section class="panel portal-task-board">
      <div class="panel-head">
        <div>
          <h2>优先处理</h2>
          <p>按缺失板块、待审核资料和发布准备度自动排序，后台进入后先处理这里。</p>
        </div>
      </div>
      <div class="portal-task-list">${items || `<div class="empty">暂无待办</div>`}</div>
    </section>
  `;
}

async function renderDashboard() {
  if (!state.projects.length) await loadProjects();
  const [data, portalRows] = await Promise.all([
    jsonApi("/api/admin/dashboard"),
    loadPortalCompletionRows(),
  ]);
  const portalCompletionHtml = renderPortalCompletionOverview(portalRows);
  const portalPriorityHtml = renderPortalPriorityTasks(portalRows);
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
    <section class="panel portal-map">
      <div class="panel-head">
        <div>
          <h2>展厅页面逻辑</h2>
          <p>先维护学校门户，再维护各系部门户，最后补充每个板块的资料和特色入口。</p>
        </div>
        <a class="button ghost" href="/departments" target="_blank" rel="noopener">预览学校门户</a>
      </div>
      <div class="portal-flow">
        <article><span>1</span><strong>学校门户</strong><p>/departments：学校总入口，负责进入各系部和创新育人专题。</p></article>
        <article><span>2</span><strong>系部门户</strong><p>/departments/系部：展示系部概览、核心数据和板块入口。</p></article>
        <article><span>3</span><strong>板块资料</strong><p>基本情况、专业设置、实训基地、产教融合、教学成果、视频资源。</p></article>
        <article><span>4</span><strong>特色功能</strong><p>特色系统入口、特色数字资源、专题内容和扫码联动。</p></article>
      </div>
      <div class="portal-rules">
        <article><strong>二维码边界</strong><p>只有 /display 欢迎页和 /departments 学校门户展示学校官网二维码；系部、专题和扫码详情页保持内容沉浸。</p></article>
        <article><strong>顶部栏统一</strong><p>学校标识、四个学校级栏目和二级页切换入口保持一致，减少观众在不同页面间的认知跳转。</p></article>
      </div>
    </section>
    <div class="metric-grid">
      <article class="metric"><span>门户</span><strong>${s.projects || 0}</strong></article>
      <article class="metric"><span>板块资料</span><strong>${s.pages || 0}</strong></article>
      <article class="metric"><span>待审核</span><strong>${s.pendingPages || 0}</strong></article>
      <article class="metric"><span>已驳回</span><strong>${s.rejectedPages || 0}</strong></article>
    </div>
    ${portalPriorityHtml}
    ${portalCompletionHtml}
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
        <article><span>欢迎页项目</span><strong>${escapeHtml(deployed.welcomeProjectName || s.welcomeDeployed || "未部署")}</strong><small>ID ${deployed.welcomeProjectId || "-"}</small></article>
        <article><span>当前门户</span><strong>${escapeHtml(deployed.contentProjectName || s.contentDeployed || "未部署")}</strong><small>ID ${deployed.contentProjectId || "-"}</small></article>
        <article><span>资料待审</span><strong>${pending.pages || 0}</strong><small>提交后需审核</small></article>
        <article><span>门户待审</span><strong>${pending.projects || 0}</strong><small>配置变更</small></article>
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
  const pagesLabel = isAdmin() ? "板块资料" : "资料";
  const configLabel = isAdmin() ? "门户配置" : "门户信息";
  const typeFilter = $("projectTypeFilter") ? $("projectTypeFilter").value : "";
  const visibleProjects = typeFilter ? state.projects.filter((project) => normalizePortalType(project.portalType) === typeFilter) : state.projects;
  const emptyText = typeFilter
    ? `暂无${portalTypeLabel(typeFilter)}`
    : isAdmin() ? "暂无门户" : "暂无分配的门户";
  $("projectsTable").innerHTML = visibleProjects.length ? visibleProjects.map((p) => `
    <tr>
      <td><strong>${escapeHtml(p.name)}</strong><div class="portal-route-line">${escapeHtml(portalRouteLabel(p))}</div><div class="muted">ID ${p.id}</div></td>
      <td>${escapeHtml(p.ownerDisplayName || p.ownerUsername || "-")}</td>
      <td><span class="badge">${escapeHtml(portalTypeLabel(p.portalType))}</span> ${badge(p.configStatus || "approved")} ${p.deployed ? '<span class="badge success">欢迎页已发布</span>' : ""} ${p.contentDeployed ? '<span class="badge success">资料已发布</span>' : ""}</td>
      <td>${p.pageCount || 0} / 待审 ${p.pendingPageCount || 0}</td>
      <td><div class="actions">
        ${portalPreviewUrl(p) ? `<a class="button small" target="_blank" rel="noopener" href="${escapeHtml(portalPreviewUrl(p))}">预览</a>` : ""}
        <button class="button small primary" data-project-pages="${p.id}">${pagesLabel}</button>
        <button class="button small" data-project-edit="${p.id}">${configLabel}</button>
        <button class="button small" data-project-history="${p.id}">历史</button>
        ${isAdmin() ? `<button class="button small danger" data-project-delete="${p.id}">删除</button>` : ""}
      </div></td>
    </tr>`).join("") : `<tr><td colspan="5" class="empty">${escapeHtml(emptyText)}</td></tr>`;
}
function selectedDeployProject() {
  const projectId = String($("deployProject").value || "");
  return state.projects.find((project) => String(project.id) === projectId) || null;
}
function syncDeployWelcomeAction(project) {
  const button = $("deployWelcome");
  if (!button) return;
  const isSchoolPortal = normalizePortalType(project && project.portalType) === "school";
  button.disabled = !isSchoolPortal;
  button.title = isSchoolPortal ? "将该学校门户发布为 /display 欢迎页" : "只有学校门户可发布为欢迎页";
}
async function loadPages(projectId = $("projectSelect").value) {
  if (!projectId) {
    state.pages = [];
    state.contentItems = [];
    state.lowcodeForms = [];
    state.lowcodeRecords = [];
    state.moduleCoverage = buildCoverageFromPages([]);
    renderCurrentPortalStrip();
    renderTemplateActions();
    renderContentModuleOptions();
    renderPages();
    return;
  }
  const [data, contentData, lowcodeData, lowcodeRecordsData] = await Promise.all([
    jsonApi(`/api/projects/${projectId}/pages`),
    jsonApi(`/api/projects/${projectId}/content-items`),
    jsonApi(`/api/projects/${projectId}/lowcode/forms`),
    jsonApi(`/api/projects/${projectId}/lowcode/records`),
  ]);
  state.pages = data.pages || [];
  state.contentItems = contentData.items || [];
  state.lowcodeForms = lowcodeData.forms || [];
  state.lowcodeRecords = lowcodeRecordsData.records || [];
  state.moduleCoverage = data.coverage || buildCoverageFromPages(state.pages);
  renderTemplateActions((state.moduleCoverage && state.moduleCoverage.portalType) || selectedPortalType());
  renderContentModuleOptions((state.moduleCoverage && state.moduleCoverage.portalType) || selectedPortalType());
  renderContentTypeOptions();
  renderCurrentPortalStrip();
  renderPages();
}
function renderPages() {
  const filter = $("pageStatusFilter").value;
  const list = filter ? state.pages.filter((p) => p.reviewStatus === filter) : state.pages;
  const editLabel = isAdmin() ? "编辑" : "编辑资料";
  const deleteLabel = isAdmin() ? "删除" : "申请删除";
  const emptyText = isAdmin() ? "暂无板块资料" : "暂无板块资料";
  renderModuleLibrary();
  renderLowcodeForms();
  renderLowcodeRecords();
  renderContentItems(filter);
  $("pagesTable").innerHTML = list.length ? list.map((p) => {
    const qr = p.qrAvailable ? `<a class="button small" target="_blank" href="/api/qr?data=${encodeURIComponent(buildQrUrl(p.projectId, p.code))}">二维码</a>` : `<span class="muted">审核后可用</span>`;
    const moduleLabel = p.moduleLabel || (moduleMeta(p.moduleKey) || {}).label || "";
    const typeLine = `<div class="muted">资料类型：${escapeHtml(p.contentTypeLabel || contentTypeLabel(p.contentType))}</div>`;
    const category = moduleLabel
      ? `${escapeHtml(p.category || "-")}<div class="muted">标准板块：${escapeHtml(moduleLabel)}</div>${typeLine}`
      : `${escapeHtml(p.category || "-")}<div class="muted warn-text">未匹配标准板块</div>${typeLine}`;
    return `<tr>
      <td>${escapeHtml(p.code)}</td><td>${escapeHtml(p.title)}${p.reviewNote ? `<div class="muted">驳回：${escapeHtml(p.reviewNote)}</div>` : ""}</td>
      <td>${category}</td><td>${badge(p.reviewStatus)}</td><td>${qr}</td>
      <td><div class="actions">
        <button class="button small primary" data-page-edit="${escapeHtml(p.code)}">${editLabel}</button>
        <button class="button small" data-page-history="${escapeHtml(p.code)}">历史</button>
        ${p.qrAvailable ? `<a class="button small" target="_blank" href="${buildQrUrl(p.projectId, p.code)}">预览</a>` : ""}
        <button class="button small danger" data-page-delete="${escapeHtml(p.code)}">${deleteLabel}</button>
      </div></td>
    </tr>`;
  }).join("") : `<tr><td colspan="6" class="empty">${emptyText}</td></tr>`;
}
function renderContentItems(filter = $("pageStatusFilter").value) {
  if (!$("contentItemsGrid")) return;
  const list = filter ? state.contentItems.filter((item) => item.reviewStatus === filter) : state.contentItems;
  const ready = state.contentItems.filter((item) => item.reviewStatus === "approved" && item.enabled).length;
  $("contentItemsSummary").textContent = `${ready}/${state.contentItems.length || 0} 可展示`;
  $("contentItemsGrid").innerHTML = list.length ? list.map((item) => {
    const moduleLabel = item.moduleLabel || (moduleMeta(item.moduleKey) || {}).label || item.moduleKey || "-";
    const assetCount = (item.assets || []).length;
    const qr = item.reviewStatus === "approved" && item.enabled
      ? `<a class="button small" target="_blank" href="${buildQrUrl(item.projectId, item.code)}">预览</a>`
      : `<span class="muted">审核后可预览</span>`;
    return `<article class="content-item-card">
      <header>
        <div>
          <strong>${escapeHtml(item.title || "未命名资料")}</strong>
          ${item.reviewNote ? `<span class="warn-text">驳回：${escapeHtml(item.reviewNote)}</span>` : ""}
        </div>
        ${badge(item.reviewStatus)}
      </header>
      <p>${escapeHtml(item.summary || item.subtitle || "暂无摘要")}</p>
      <div class="content-item-meta">
        <span>${escapeHtml(moduleLabel)}</span>
        <span>${escapeHtml(item.contentTypeLabel || contentTypeLabel(item.contentType))}</span>
        <span>素材 ${assetCount}</span>
        ${item.featured ? "<span>重点</span>" : ""}
      </div>
      <div class="actions">
        <button class="button small primary" data-content-edit="${item.id}">编辑</button>
        ${qr}
        <button class="button small danger" data-content-delete="${item.id}">${isAdmin() ? "删除" : "申请删除"}</button>
      </div>
    </article>`;
  }).join("") : `<div class="empty">暂无结构化资料</div>`;
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
  if (type === "project") return "门户配置";
  if (type === "contentItem") return item.operation === "delete" ? "结构化资料删除" : "结构化资料";
  if (item.operation === "delete") return "删除申请";
  return "资料变更";
}
function historyTitle(item, type) {
  if (type === "project") return (item.snapshot && item.snapshot.name) || item.projectName || "门户配置";
  if (type === "contentItem") return (item.snapshot && item.snapshot.title) || item.contentItemId || "结构化资料";
  return (item.snapshot && item.snapshot.title) || item.code || "板块资料";
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
  $("projectHistoryTitle").textContent = `门户历史：${data.project ? data.project.name : projectId}`;
  renderVersionHistory("projectHistory", data.versions || [], "project");
  $("projectHistoryPanel").hidden = false;
  $("projectHistoryPanel").scrollIntoView({ behavior: "smooth", block: "nearest" });
}
async function showPageHistory(code) {
  const projectId = $("projectSelect").value;
  const data = await jsonApi(`/api/projects/${projectId}/pages/${encodeURIComponent(code)}/versions`);
  $("pageHistoryTitle").textContent = `板块资料历史：${code}`;
  renderVersionHistory("pageHistory", data.versions || [], "page");
  $("pageHistoryPanel").hidden = false;
  $("pageHistoryPanel").scrollIntoView({ behavior: "smooth", block: "nearest" });
}
async function renderReviews() {
  const data = await jsonApi("/api/reviews?status=pending");
  const pages = data.reviews.pages || [];
  const projects = data.reviews.projects || [];
  const contentItems = data.reviews.contentItems || [];
  const items = [
    ...projects.map((r) => ({ ...r, type: "projects", label: "门户配置" })),
    ...contentItems.map((r) => ({ ...r, type: "content-items", label: r.operation === "delete" ? "结构化资料删除" : "结构化资料" })),
    ...pages.map((r) => ({ ...r, type: "pages", label: r.operation === "delete" ? "删除申请" : "板块资料" })),
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
        ${r.type === "content-items" && r.snapshot && r.snapshot.code ? `<a class="button small" target="_blank" href="/display?project=${r.projectId}&code=${encodeURIComponent(r.snapshot.code)}">同步页预览</a>` : ""}
        <button class="button small primary" data-review-approve="${r.type}:${r.id}">通过</button>
        <button class="button small danger" data-review-reject="${r.type}:${r.id}">驳回</button>
      </div>
    </article>`).join("") : `<div class="empty">暂无待审核资料</div>`;
}
async function renderDeploy() {
  const projectId = $("deployProject").value || (state.projects[0] && state.projects[0].id);
  const project = selectedDeployProject() || state.projects.find((item) => String(item.id) === String(projectId)) || null;
  syncDeployWelcomeAction(project);
  if (!projectId) { $("deployPages").innerHTML = `<div class="empty">暂无门户</div>`; syncDeployWelcomeAction(null); return; }
  const pagesData = await jsonApi(`/api/projects/${projectId}/pages`);
  const deployed = await jsonApi(`/api/deploy/content/${projectId}`);
  const checkData = await jsonApi(`/api/deploy/check/${projectId}`);
  const selected = new Set((deployed.pageIds || []).map(String));
  const approved = (pagesData.pages || []).filter((p) => p.reviewStatus === "approved" && p.enabled);
  renderDeployCheck(checkData.check || {}, project);
  $("deployPages").innerHTML = approved.length ? approved.map((p) => `
    <label class="check-item"><input type="checkbox" value="${p.id}" ${selected.size ? (selected.has(String(p.id)) ? "checked" : "") : "checked"} /> ${escapeHtml(p.code)} - ${escapeHtml(p.title)}</label>
  `).join("") : `<div class="empty">该门户暂无已通过板块资料</div>`;
}
function renderDeployCheck(check, project = null) {
  const errors = check.errors || [];
  const warnings = check.warnings || [];
  const coverage = check.moduleCoverage || check.eligibleModuleCoverage || buildCoverageFromPages([]);
  const portalType = normalizePortalType((project && project.portalType) || coverage.portalType);
  const isSchoolPortal = portalType === "school";
  const previewUrl = portalPreviewUrl(project || {});
  const policyCards = [
    {
      className: isSchoolPortal ? "success" : "warn",
      title: "欢迎页发布",
      badge: isSchoolPortal ? "可发布" : "仅学校门户",
      body: isSchoolPortal
        ? "发布后影响 /display 欢迎页，适合放学校统一入口和官网二维码。"
        : "当前门户不能发布为 /display 欢迎页；欢迎页只允许选择学校门户。"
    },
    {
      className: "info",
      title: "门户实时资料",
      badge: previewUrl || "门户预览",
      body: "已通过且启用的资料会进入对应门户页；草稿、待审核、禁用资料不会出现在前台。"
    },
    {
      className: "info",
      title: "扫码大屏资料",
      badge: "按勾选发布",
      body: "下方勾选只控制扫码大屏可打开的资料范围，不改变门户页的实时资料。"
    },
    {
      className: "info",
      title: "二维码边界",
      badge: "/display /departments",
      body: "学校官网二维码只在欢迎页和学校门户显示；系部、专题、资料详情页保持沉浸展示。"
    }
  ];
  const coverageText = coverage.total ? `${escapeHtml(coverage.portalTypeLabel || portalTypeLabel(coverage.portalType))}标准板块 ${coverage.covered}/${coverage.total}，可发布 ${coverage.publishReady}/${coverage.total}` : "标准板块待统计";
  const moduleList = (coverage.modules || []).map((module) => `
    <span class="${module.publishReady ? "ready" : module.covered ? "covered" : "missing"}">${escapeHtml(module.label)}</span>
  `).join("");
  const stateLabel = errors.length ? "发布前必须处理" : warnings.length ? "可以发布，但建议先处理" : "检查通过";
  $("deployCheck").innerHTML = `
    <div class="deploy-policy-grid">
      ${policyCards.map((item) => `
        <article class="deploy-policy-card ${item.className}">
          <div><strong>${escapeHtml(item.title)}</strong><span>${escapeHtml(item.badge)}</span></div>
          <p>${escapeHtml(item.body)}</p>
        </article>
      `).join("")}
    </div>
    <div class="deploy-check-box ${errors.length ? "danger" : warnings.length ? "warn" : "success"}">
      <strong>${stateLabel}</strong>
      <span>可发布资料 ${check.eligiblePageIds ? check.eligiblePageIds.length : 0}，已选 ${check.pageIds ? check.pageIds.length : 0}；${coverageText}</span>
      ${moduleList ? `<div class="deploy-module-strip">${moduleList}</div>` : ""}
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
  if (state.assetTargetInput === "__contentAssetManager") {
    const role = state.contentAssetDrafts.length ? "gallery" : "cover";
    addContentAsset({ url: asset.url, caption: $("contentTitle")?.value.trim() || asset.originalFilename || "", role });
    const returnView = state.assetReturnView || "pages";
    state.assetTargetInput = "";
    state.assetReturnView = "";
    showView(returnView);
    return;
  }
  if (state.assetTargetInput === "__lowcodeAssetManager") {
    const role = state.lowcodeAssetDrafts.length ? "gallery" : "cover";
    addLowcodeAsset({ url: asset.url, caption: asset.originalFilename || "", role });
    const returnView = state.assetReturnView || "pages";
    state.assetTargetInput = "";
    state.assetReturnView = "";
    showView(returnView);
    return;
  }
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
  if (view === "pages") {
    const preferredProjectId = state.preferredProjectId || $("projectSelect").value;
    state.preferredProjectId = "";
    await loadProjects(preferredProjectId);
    const projectId = state.projects.some((project) => String(project.id) === String(preferredProjectId))
      ? preferredProjectId
      : $("projectSelect").value;
    await loadPages(projectId);
    if (state.preferredModuleKey) {
      const moduleKey = state.preferredModuleKey;
      state.preferredModuleKey = "";
      startContentItemDraft(moduleKey);
    }
  }
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
  $("projectPortalType").value = normalizePortalType(project.portalType || "department");
  $("projectPortalSlug").value = project.portalSlug || "";
  syncProjectPortalSlugField();
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
    portalType: normalizePortalType($("projectPortalType").value),
    portalSlug: normalizePortalSlug($("projectPortalSlug").value),
    ownerUsername: $("projectOwner").value || state.user.username,
    accent: $("projectAccent").value,
    idleTitle: $("idleTitle").value.trim(),
    idleKicker: $("idleKicker").value.trim(),
    idleCopy: $("idleCopy").value.trim(),
    defaultImageUrl: $("defaultImageUrl").value.trim(),
  };
}
function fillContentItem(item = {}) {
  state.editingContentItemId = item.id || "";
  renderContentModuleOptions();
  renderContentTypeOptions();
  const moduleKey = item.moduleKey || (modulesForPortalType()[0] || {}).key || "";
  const contentType = normalizeContentType(item.contentType || defaultContentTypeForModule(moduleKey));
  $("contentCode").value = item.code || "";
  $("contentModule").value = moduleKey;
  $("contentType").value = contentType;
  $("contentSortOrder").value = item.sortOrder || 0;
  $("contentTitle").value = item.title || "";
  $("contentSubtitle").value = item.subtitle || "";
  $("contentSummary").value = item.summary || "";
  $("contentBodyText").value = textFromBodyJson(item.bodyJson || []);
  $("contentMetaText").value = textFromMetaJson(item.metaJson || {});
  setContentAssetDrafts(item.assets || [], { silent: true });
  $("contentFeatured").checked = Boolean(item.featured);
  $("contentEnabled").checked = item.enabled !== false;
  $("contentAssetFile").value = "";
  $("contentAssetUrl").value = "";
  $("contentAssetCaption").value = "";
  $("contentAssetRole").value = state.contentAssetDrafts.length ? "gallery" : "cover";
  $("contentItemFormHint").textContent = isAdmin()
    ? "管理员保存后立即通过，并同步生成扫码详情页。"
    : "保存后提交管理员审核，通过后同步进入展示。";
  $("contentItemForm").hidden = false;
  $("lowcodeRecordForm").hidden = true;
  $("lowcodeTemplateForm").hidden = true;
  $("lowcodeVersionPanel").hidden = true;
  $("pageForm").hidden = true;
  updateContentPreview();
  $("contentItemForm").scrollIntoView({ behavior: "smooth", block: "start" });
}
function startContentItemDraft(moduleKey) {
  const meta = moduleMeta(moduleKey) || modulesForPortalType()[0] || {};
  const type = defaultContentTypeForModule(moduleKey);
  fillContentItem({
    moduleKey: moduleKey || meta.key || "",
    contentType: type,
    title: meta.label || "",
    subtitle: meta.description || "",
    summary: meta.description || "",
    bodyJson: bodyJsonFromText(htmlToPlainText(contentBodyTemplate(type, meta.label || ""))),
    metaJson: {},
    assets: [],
    enabled: true,
  });
  setStatus($("contentItemStatus"), "已按标准板块生成结构化草稿。", "success");
}
function contentItemPayload() {
  return {
    code: $("contentCode").value.trim(),
    moduleKey: $("contentModule").value,
    contentType: normalizeContentType($("contentType").value),
    title: $("contentTitle").value.trim(),
    subtitle: $("contentSubtitle").value.trim(),
    summary: $("contentSummary").value.trim(),
    bodyJson: bodyJsonFromText($("contentBodyText").value),
    metaJson: metaJsonFromText($("contentMetaText").value),
    assets: currentContentAssets(),
    sortOrder: Number($("contentSortOrder").value || 0),
    featured: $("contentFeatured").checked,
    enabled: $("contentEnabled").checked,
  };
}
function fillPage(page) {
  state.editingCode = page.code || "";
  state.generatedCode = "";
  setPreviewFile(null);
  setTemplateGuide("");
  $("pageCode").value = page.code || "";
  $("pageCategory").value = page.category || "";
  $("pagePublishedAt").value = page.publishedAt || "";
  $("pageSource").value = page.source || "";
  $("pageTitle").value = page.title || "";
  $("pageSubtitle").value = page.subtitle || "";
  if ($("pageContentType")) $("pageContentType").value = normalizeContentType(page.contentType || defaultContentTypeForModule(page.moduleKey || localModuleKeyForCategory(page.category)));
  setRichBody(page.body || "");
  $("pageAccent").value = page.accent || "#f59a13";
  $("pageImageUrl").value = page.imageUrl || "";
  $("pageImageFile").value = "";
  $("pageFormHint").textContent = isAdmin() ? "管理员保存后立即通过。" : "资料保存后会提交管理员审核，通过后进入展示。";
  $("pageForm").hidden = false;
  $("lowcodeRecordForm").hidden = true;
  $("lowcodeTemplateForm").hidden = true;
  $("lowcodeVersionPanel").hidden = true;
  $("contentItemForm").hidden = true;
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
    contentType: normalizeContentType($("pageContentType").value),
    accent: $("pageAccent").value,
    imageUrl: $("pageImageUrl").value.trim(),
    enabled: true,
  };
}

$("logout").addEventListener("click", async () => { await api("/api/logout", { method: "POST" }); location.href = "/login"; });
$("refreshData").addEventListener("click", () => refreshView());
$("projectTypeFilter").addEventListener("change", renderProjects);
$("projectSelect").addEventListener("change", () => loadPages());
$("projectPortalType").addEventListener("change", () => {
  syncProjectPortalSlugField();
  renderTemplateActions($("projectPortalType").value);
});
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
["pageCode", "pageCategory", "pageSource", "pageTitle", "pageSubtitle", "pageContentType", "pageImageUrl"].forEach((id) => {
  $(id).addEventListener("input", updatePagePreview);
});
$("pageContentType").addEventListener("change", () => {
  const moduleKey = localModuleKeyForCategory($("pageCategory").value) || (modulesForPortalType()[0] || {}).key || "";
  setTemplateGuide(moduleKey);
});
$("pageImageFile").addEventListener("change", () => setPreviewFile($("pageImageFile").files[0] || null));
$("templateActions").addEventListener("click", (event) => {
  const button = event.target.closest("[data-template]");
  if (button) applyRichTemplate(button.dataset.template);
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

$("dashboardView").addEventListener("click", async (event) => {
  const pages = event.target.closest("[data-dashboard-pages]");
  if (!pages) return;
  state.preferredProjectId = pages.dataset.dashboardPages;
  state.preferredModuleKey = pages.dataset.dashboardModule || "";
  await showView("pages");
});

$("newProject").addEventListener("click", () => fillProject({
  id: "",
  portalType: "department",
  ownerUsername: state.users.find((u) => u.role === "teacher" && u.enabled)?.username || state.user.username,
  accent: "#f59a13",
}));
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
    setStatus($("projectStatus"), isAdmin() ? "门户已保存" : "门户信息已提交审核", "success");
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
  if (pages) { state.preferredProjectId = pages.dataset.projectPages; await showView("pages"); }
  if (historyButton) await showProjectHistory(historyButton.dataset.projectHistory);
  if (del && confirm("确定删除该门户及其板块资料？")) { await api(`/api/projects/${del.dataset.projectDelete}`, { method: "DELETE" }); await refreshView("projects"); }
});
$("closeProjectHistory").addEventListener("click", () => { $("projectHistoryPanel").hidden = true; });

$("newPage").addEventListener("click", () => {
  startContentItemDraft((modulesForPortalType()[0] || standardModules[0]).key);
});
$("newLegacyPage").addEventListener("click", () => {
  state.editingCode = "";
  fillPage({ accent: "#f59a13", publishedAt: new Date().toISOString().slice(0, 10), body: "" });
  applyRichTemplate((modulesForPortalType()[0] || standardModules[0]).key);
});
$("moduleLibrary").addEventListener("click", (event) => {
  const button = event.target.closest("[data-module-create]");
  if (!button) return;
  startContentItemDraft(button.dataset.moduleCreate);
});
$("lowcodeFormsGrid").addEventListener("click", (event) => {
  const start = event.target.closest("[data-lowcode-start]");
  const edit = event.target.closest("[data-lowcode-edit]");
  const copy = event.target.closest("[data-lowcode-copy]");
  const versions = event.target.closest("[data-lowcode-versions]");
  if (start) {
    fillLowcodeRecordForm(state.lowcodeForms.find((form) => String(form.id) === String(start.dataset.lowcodeStart)));
    return;
  }
  if (edit) {
    fillLowcodeTemplateForm(state.lowcodeForms.find((form) => String(form.id) === String(edit.dataset.lowcodeEdit)));
    return;
  }
  if (copy) {
    const form = state.lowcodeForms.find((item) => String(item.id) === String(copy.dataset.lowcodeCopy));
    if (!form) return;
    const name = prompt("复制后的模板名称", `${form.name} 副本`);
    if (!name) return;
    jsonApi(`/api/lowcode/forms/${form.id}/copy`, body({ name, enabled: false }))
      .then(async (data) => {
        await loadPages();
        fillLowcodeTemplateForm(data.form);
        setStatus($("lowcodeTemplateStatus"), "模板副本已创建，检查字段后可启用。", "success");
      })
      .catch((err) => alert(err.message));
    return;
  }
  if (versions) {
    showLowcodeVersions(versions.dataset.lowcodeVersions).catch((err) => alert(err.message));
  }
});
$("lowcodeRecordsList").addEventListener("click", (event) => {
  const edit = event.target.closest("[data-lowcode-record-edit]");
  if (!edit) return;
  const item = state.contentItems.find((entry) => String(entry.id) === String(edit.dataset.lowcodeRecordEdit));
  if (item) fillContentItem(item);
});
$("newLowcodeTemplate").addEventListener("click", () => fillLowcodeTemplateForm({}));
$("closeLowcodeRecordForm").addEventListener("click", () => { $("lowcodeRecordForm").hidden = true; });
$("closeLowcodeTemplateForm").addEventListener("click", () => { $("lowcodeTemplateForm").hidden = true; });
$("closeLowcodeVersionPanel").addEventListener("click", () => { $("lowcodeVersionPanel").hidden = true; });
$("lowcodeTemplatePortalType").addEventListener("change", () => {
  const portalType = normalizePortalType($("lowcodeTemplatePortalType").value);
  renderLowcodeTemplateModuleOptions(portalType);
  const moduleKey = $("lowcodeTemplateModule").value;
  $("lowcodeTemplateContentType").value = defaultContentTypeForModule(moduleKey);
});
$("lowcodeTemplateModule").addEventListener("change", () => {
  const moduleKey = $("lowcodeTemplateModule").value;
  $("lowcodeTemplateContentType").value = defaultContentTypeForModule(moduleKey);
});
$("addLowcodeField").addEventListener("click", addLowcodeFieldDraft);
$("lowcodeFieldEditorList").addEventListener("input", (event) => {
  const input = event.target.closest("[data-lowcode-config-field]");
  const row = event.target.closest("[data-lowcode-field-row]");
  if (!input || !row || input.type === "checkbox") return;
  updateLowcodeFieldDraft(Number(row.dataset.lowcodeFieldRow), input.dataset.lowcodeConfigField, input.value);
});
$("lowcodeFieldEditorList").addEventListener("change", (event) => {
  const input = event.target.closest("[data-lowcode-config-field]");
  const row = event.target.closest("[data-lowcode-field-row]");
  if (!input || !row) return;
  updateLowcodeFieldDraft(Number(row.dataset.lowcodeFieldRow), input.dataset.lowcodeConfigField, input.type === "checkbox" ? input.checked : input.value);
});
$("lowcodeFieldEditorList").addEventListener("click", (event) => {
  const up = event.target.closest("[data-lowcode-field-up]");
  const down = event.target.closest("[data-lowcode-field-down]");
  const remove = event.target.closest("[data-lowcode-field-remove]");
  if (up) moveLowcodeFieldDraft(Number(up.dataset.lowcodeFieldUp), -1);
  if (down) moveLowcodeFieldDraft(Number(down.dataset.lowcodeFieldDown), 1);
  if (remove) removeLowcodeFieldDraft(Number(remove.dataset.lowcodeFieldRemove));
});
$("lowcodeTemplateForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    const id = state.editingLowcodeFormId;
    const url = id ? `/api/lowcode/forms/${id}` : "/api/lowcode/forms";
    const method = id ? putBody(lowcodeTemplatePayload()) : body(lowcodeTemplatePayload());
    await jsonApi(url, method);
    setStatus($("lowcodeTemplateStatus"), "资料采集模板已保存", "success");
    await loadPages();
  } catch (err) { setStatus($("lowcodeTemplateStatus"), err.message, "error"); }
});
$("lowcodeRecordForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const projectId = $("projectSelect").value;
  const form = currentLowcodeForm();
  if (!projectId || !form) {
    setStatus($("lowcodeRecordStatus"), "请先选择门户和资料采集模板", "error");
    return;
  }
  try {
    const result = await jsonApi(`/api/projects/${projectId}/lowcode/forms/${form.id}/records`, body(lowcodeRecordPayload()));
    setStatus($("lowcodeRecordStatus"), isAdmin() ? "资料已按模板生成并同步展示页" : "资料已按模板提交审核", "success");
    state.editingContentItemId = result.item && result.item.id ? result.item.id : "";
    await loadPages();
  } catch (err) { setStatus($("lowcodeRecordStatus"), err.message, "error"); }
});
$("uploadLowcodeAsset").addEventListener("click", async () => {
  try {
    const url = await uploadImage($("lowcodeAssetFile").files[0], $("lowcodeRecordStatus"));
    if (!url) {
      setStatus($("lowcodeRecordStatus"), "请选择图片", "error");
      return;
    }
    addLowcodeAsset({
      url,
      caption: $("lowcodeAssetCaption").value.trim(),
      role: $("lowcodeAssetRole").value,
    });
    $("lowcodeAssetFile").value = "";
    setStatus($("lowcodeRecordStatus"), "素材已加入模板资料", "success");
  } catch (err) { setStatus($("lowcodeRecordStatus"), err.message, "error"); }
});
$("addLowcodeAssetUrl").addEventListener("click", () => {
  const url = $("lowcodeAssetUrl").value.trim();
  if (!url) {
    setStatus($("lowcodeRecordStatus"), "请先填写素材地址", "error");
    return;
  }
  addLowcodeAsset({
    url,
    caption: $("lowcodeAssetCaption").value.trim(),
    role: $("lowcodeAssetRole").value,
  });
  $("lowcodeAssetUrl").value = "";
  $("lowcodeAssetCaption").value = "";
  $("lowcodeAssetRole").value = state.lowcodeAssetDrafts.length ? "gallery" : "cover";
  setStatus($("lowcodeRecordStatus"), "素材已加入模板资料", "success");
});
$("selectLowcodeAsset").addEventListener("click", () => openAssetPicker("__lowcodeAssetManager"));
$("lowcodeAssetCards").addEventListener("input", (event) => {
  const field = event.target.closest("[data-lowcode-asset-field]");
  if (!field || field.tagName === "SELECT") return;
  updateLowcodeAsset(Number(field.dataset.lowcodeAssetIndex), field.dataset.lowcodeAssetField, field.value, { skipRender: true });
});
$("lowcodeAssetCards").addEventListener("change", (event) => {
  const field = event.target.closest("[data-lowcode-asset-field]");
  if (!field) return;
  updateLowcodeAsset(Number(field.dataset.lowcodeAssetIndex), field.dataset.lowcodeAssetField, field.value, { skipRender: field.tagName !== "SELECT" });
});
$("lowcodeAssetCards").addEventListener("click", (event) => {
  const up = event.target.closest("[data-lowcode-asset-up]");
  const down = event.target.closest("[data-lowcode-asset-down]");
  const remove = event.target.closest("[data-lowcode-asset-remove]");
  if (up) moveLowcodeAsset(Number(up.dataset.lowcodeAssetUp), -1);
  if (down) moveLowcodeAsset(Number(down.dataset.lowcodeAssetDown), 1);
  if (remove) removeLowcodeAsset(Number(remove.dataset.lowcodeAssetRemove));
});
$("closeContentItemForm").addEventListener("click", () => { $("contentItemForm").hidden = true; });
$("contentItemForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    const projectId = $("projectSelect").value;
    const id = state.editingContentItemId;
    const url = id ? `/api/projects/${projectId}/content-items/${id}` : `/api/projects/${projectId}/content-items`;
    const method = id ? putBody(contentItemPayload()) : body(contentItemPayload());
    const data = await jsonApi(url, method);
    state.editingContentItemId = data.item.id;
    setStatus($("contentItemStatus"), isAdmin() ? "结构化资料已保存并同步展示页" : "结构化资料已提交审核", "success");
    await loadPages();
  } catch (err) { setStatus($("contentItemStatus"), err.message, "error"); }
});
$("uploadContentAsset").addEventListener("click", async () => {
  try {
    const url = await uploadImage($("contentAssetFile").files[0], $("contentItemStatus"));
    if (!url) {
      setStatus($("contentItemStatus"), "请选择图片", "error");
      return;
    }
    appendContentAssetLine(url, $("contentTitle").value.trim(), state.contentAssetDrafts.length ? "gallery" : "cover");
    $("contentAssetFile").value = "";
  } catch (err) { setStatus($("contentItemStatus"), err.message, "error"); }
});
$("addContentAssetUrl").addEventListener("click", () => {
  const url = $("contentAssetUrl").value.trim();
  if (!url) {
    setStatus($("contentItemStatus"), "请先填写素材地址", "error");
    return;
  }
  addContentAsset({
    url,
    caption: $("contentAssetCaption").value.trim(),
    role: $("contentAssetRole").value,
  });
  $("contentAssetUrl").value = "";
  $("contentAssetCaption").value = "";
  $("contentAssetRole").value = state.contentAssetDrafts.length ? "gallery" : "cover";
  setStatus($("contentItemStatus"), "素材已加入图片/视频组", "success");
});
$("selectContentAsset").addEventListener("click", () => openAssetPicker("__contentAssetManager"));
$("contentAssetCards").addEventListener("input", (event) => {
  const field = event.target.closest("[data-content-asset-field]");
  if (!field || field.tagName === "SELECT") return;
  updateContentAsset(Number(field.dataset.contentAssetIndex), field.dataset.contentAssetField, field.value, { skipRender: true });
});
$("contentAssetCards").addEventListener("change", (event) => {
  const field = event.target.closest("[data-content-asset-field]");
  if (!field) return;
  updateContentAsset(Number(field.dataset.contentAssetIndex), field.dataset.contentAssetField, field.value, { skipRender: field.tagName !== "SELECT" });
});
$("contentAssetCards").addEventListener("click", (event) => {
  const up = event.target.closest("[data-content-asset-up]");
  const down = event.target.closest("[data-content-asset-down]");
  const remove = event.target.closest("[data-content-asset-remove]");
  if (up) moveContentAsset(Number(up.dataset.contentAssetUp), -1);
  if (down) moveContentAsset(Number(down.dataset.contentAssetDown), 1);
  if (remove) removeContentAsset(Number(remove.dataset.contentAssetRemove));
});
["contentCode", "contentModule", "contentType", "contentSortOrder", "contentTitle", "contentSubtitle", "contentSummary", "contentBodyText", "contentMetaText", "contentAssetsText"].forEach((id) => {
  $(id).addEventListener("input", updateContentPreview);
  $(id).addEventListener("change", updateContentPreview);
});
$("contentModule").addEventListener("change", () => {
  const type = defaultContentTypeForModule($("contentModule").value);
  if (!$("contentType").value || $("contentType").value === "article") $("contentType").value = type;
  updateContentPreview();
});
$("closePageForm").addEventListener("click", () => { $("pageForm").hidden = true; });
$("pageForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    const fileUrl = await uploadImage($("pageImageFile").files[0], $("pageStatus"));
    if (fileUrl) $("pageImageUrl").value = fileUrl;
    await jsonApi(`/api/projects/${$("projectSelect").value}/pages/${encodeURIComponent($("pageCode").value.trim())}`, putBody(pagePayload()));
    setStatus($("pageStatus"), isAdmin() ? "板块资料已保存并通过" : "板块资料已提交审核", "success");
    await loadPages();
  } catch (err) { setStatus($("pageStatus"), err.message, "error"); }
});
$("selectPageAsset").addEventListener("click", () => openAssetPicker("pageImageUrl"));
$("contentItemsGrid").addEventListener("click", async (event) => {
  const edit = event.target.closest("[data-content-edit]");
  const del = event.target.closest("[data-content-delete]");
  if (edit) {
    const item = state.contentItems.find((entry) => String(entry.id) === String(edit.dataset.contentEdit));
    if (item) fillContentItem(item);
  }
  if (del && confirm(isAdmin() ? "确定删除该结构化资料？" : "确定提交删除该结构化资料的审核申请？")) {
    await api(`/api/projects/${$("projectSelect").value}/content-items/${del.dataset.contentDelete}`, { method: "DELETE" });
    await loadPages();
  }
});
$("pagesTable").addEventListener("click", async (event) => {
  const edit = event.target.closest("[data-page-edit]");
  const historyButton = event.target.closest("[data-page-history]");
  const del = event.target.closest("[data-page-delete]");
  if (edit) fillPage(state.pages.find((p) => p.code === edit.dataset.pageEdit));
  if (historyButton) await showPageHistory(historyButton.dataset.pageHistory);
  if (del && confirm(isAdmin() ? "确定删除该板块资料？" : "确定提交删除该板块资料的审核申请？")) { await api(`/api/projects/${$("projectSelect").value}/pages/${encodeURIComponent(del.dataset.pageDelete)}`, { method: "DELETE" }); await loadPages(); }
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
      setStatus($("assetStatus"), "素材已删除", "success");
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
  const project = selectedDeployProject();
  if (normalizePortalType(project && project.portalType) !== "school") {
    setStatus($("deployStatus"), "只有学校门户可发布为欢迎页", "error");
    return;
  }
  try {
    await jsonApi(`/api/projects/${projectId}/deploy`, body({}));
    setStatus($("deployStatus"), "欢迎页已发布", "success");
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
    setStatus($("deployStatus"), "板块资料已发布", "success");
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
