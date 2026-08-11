/* ============================================================
   毕节职业技术学院数字门户展厅 · 蓝图展陈
   数据驱动 SPA: /departments 学校门户, /departments/<id> 与 /topics/<id> 二级门户
   ============================================================ */
(function () {
  "use strict";

  var DATA = { departments: {}, topics: {} };
  var FIXED_SCHOOL_LOGO_URL = "/static/blueprint/school-logo.png";
  var FIXED_SCHOOL_QR_URL = "/static/blueprint/school-qr.jpg";
  var PORTAL_CHROME = {
    logoImageUrl: FIXED_SCHOOL_LOGO_URL,
    navText: "社会服务 · 国际交流 · 育人成果 · 名师名匠",
    schoolQrImageUrl: FIXED_SCHOOL_QR_URL
  };
  var PORTAL_HOME = {
    schoolName: "",
    schoolMeta: "",
    summaryKicker: "School Portal",
    summaryTitle: "学校门户",
    summaryCopy: "",
    routeLabels: [],
    sectionKicker: "Integrated Showcase",
    sectionTitle: "创新育人矩阵",
    sectionCopy: "",
    footer: ""
  };
  var HOME_CARDS = [];
  var INLINE_EDIT = {
    enabled: new URLSearchParams(location.search).get("edit") === "1",
    focus: new URLSearchParams(location.search).get("focus") || "",
    ready: false,
    initPromise: null,
    csrfToken: "",
    projects: [],
    projectMap: {},
    dirty: {},
    dirtyPages: {},
    undoStack: [],
    maxUndo: 40,
    statusNode: null,
    uploadTargetProjectId: ""
  };
  var ORDER = {
    departments: [],
    topics: [
      "modern-agriculture",
      "digital-tourism",
      "smart-healthcare",
      "finance-commerce",
      "digital-intelligence",
      "smart-energy",
      "smart-manufacturing",
      "campus-culture"
    ]
  };
  var DEPT_SUMMARY = {};
  var TOPIC_SUMMARY = {
    "modern-agriculture": "山地特色农业、乡村振兴与数字化生产服务",
    "digital-tourism": "数字文旅、酒店运营、烹饪技艺与服务场景",
    "smart-healthcare": "护理康养、急救教育、健康管理与服务运营",
    "smart-energy": "绿色能源、智能开采与化工安全",
    "smart-manufacturing": "智能装备、新能源汽车与无人机应用",
    "finance-commerce": "数字商贸、电商物流与产教融合",
    "digital-intelligence": "人工智能、网络安全、数据应用与跨专业赋能",
    "campus-culture": "同心育人、校园文化、学生成长与服务地方"
  };
  var TOPIC_DEPARTMENTS = {
    "modern-agriculture": ["电子信息工程系", "旅游管理系", "工矿建筑系"],
    "digital-tourism": ["旅游管理系", "电子信息工程系", "财政经济系"],
    "smart-healthcare": ["医学护理系", "旅游管理系", "电子信息工程系"],
    "finance-commerce": ["财政经济系", "电子信息工程系", "旅游管理系"],
    "digital-intelligence": ["电子信息工程系", "财政经济系", "工矿建筑系", "医学护理系", "旅游管理系"],
    "smart-energy": ["工矿建筑系", "电子信息工程系"],
    "smart-manufacturing": ["工矿建筑系", "电子信息工程系", "财政经济系"],
    "campus-culture": ["工矿建筑系", "财政经济系", "电子信息工程系", "医学护理系", "旅游管理系"]
  };
  var MODULE_META = {
    overview: ["基本情况", "系部定位、发展沿革、师资队伍与核心数据。"],
    majors: ["专业设置", "专业列表、培养方向、课程模块和就业岗位。"],
    training: ["实训基地", "实训室、校内基地、实践教学场景和设备条件。"],
    cooperation: ["产教融合", "校企合作、订单班、共同体建设和社会服务。"],
    achievements: ["教学成果", "课程建设、技能竞赛、荣誉成果和育人成效。"],
    media: ["视频资源", "宣传片、专业介绍视频、实训基地视频和学生作品。"],
    systems: ["特色系统入口", "对接系部特色系统、业务平台或互动入口。"],
    resources: ["特色数字资源", "集中呈现数字资源、专题内容和可扫码访问资料。"]
  };
  var MODULE_SEQUENCE = [
    ["overview", "概览", "基本情况"],
    ["majors", "专业", "专业设置"],
    ["training", "实训", "实训基地"],
    ["cooperation", "合作", "产教融合"],
    ["achievements", "成果", "教学成果"],
    ["media", "视频", "视频资源"],
    ["systems", "系统", "特色系统入口"],
    ["resources", "资源", "特色数字资源"]
  ];
  var SECTION_EN = {
    "overview": "OVERVIEW", "majors": "MAJORS", "training": "TRAINING",
    "cooperation": "COOPERATION", "achievements": "ACHIEVEMENTS",
    "competitions": "COMPETITIONS", "honors": "HONORS", "masters": "MASTERS",
    "alumni": "ALUMNI", "students": "STUDENTS", "media": "MEDIA",
    "faculty": "FACULTY", "orders": "ORDERS", "industry-school": "INDUSTRY"
  };
  var TOPIC_SECTION_ORDER = [
    "overview", "majors", "training", "cooperation", "masters", "alumni",
    "students", "achievements", "competitions", "honors", "media"
  ];
  var TOPIC_SECTION_TITLES = {
    overview: "专题概况",
    majors: "专业群布局",
    training: "实训场景",
    cooperation: "产教协同",
    masters: "名师名匠",
    alumni: "优秀校友",
    students: "优秀学生",
    achievements: "专题成果",
    competitions: "技能大赛",
    honors: "荣誉资质",
    media: "视频资源"
  };
  var CONTENT_TYPE_LABELS = {
    article: "普通图文",
    person: "人物类",
    activity: "活动类",
    honor: "荣誉类",
    achievement: "成果类",
    scene: "场景类",
    video: "视频类",
    attachment: "附件资料"
  };
  var TOPIC_DEFAULT_CONTENT_TYPES = {
    training: "scene",
    cooperation: "activity",
    masters: "person",
    alumni: "person",
    students: "person",
    achievements: "achievement",
    competitions: "activity",
    honors: "honor",
    media: "video"
  };
  var LONG_TEXT_LIMIT = 260;
  var IDLE_MS = 120000;

  var $ = function (id) { return document.getElementById(id); };
  var stage = $("bpStage"), screenHome = $("screenHome"), screenDetail = $("screenDetail");

  var state = { kind: null, id: null, section: 0, sections: [], lastScanAt: 0, playingVideo: false };
  var idleTimer = null, lbImages = [], lbIndex = 0, topicMediaCarouselTimers = [], drawerMediaCarouselTimers = [], topicCoverflowTimers = [];
  var drawerLoopTimer = null, drawerLoopLastAt = 0, drawerLoopCycle = 0, drawerLoopPauseUntil = 0;
  var personDrawerContext = null, entryDrawerContext = null;
  var DRAWER_LOOP_SPEED = 24;
  var DRAWER_LOOP_RESUME_MS = 2600;

  /* ---------- 工具 ---------- */
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  var MEDIA_RATIO_CLASSES = ["media-tall", "media-portrait", "media-square", "media-landscape", "media-wide"];
  function adaptiveMediaTarget(img) {
    return img.closest(".photo-frame, .fusion-card, .topic-loop-slide, .topic-loop-video, .video-player, .person-card") || img;
  }
  function classifyMediaRatio(ratio) {
    if (ratio < 0.62) return "media-tall";
    if (ratio < 0.86) return "media-portrait";
    if (ratio > 1.9) return "media-wide";
    if (ratio > 1.18) return "media-landscape";
    return "media-square";
  }
  function applyAdaptiveMediaClass(img, onReady) {
    var target = adaptiveMediaTarget(img);
    var apply = function () {
      var w = img.naturalWidth || 0;
      var h = img.naturalHeight || 0;
      if (!w || !h) return;
      var ratio = w / h;
      var cls = classifyMediaRatio(ratio);
      [img, target].forEach(function (node) {
        if (!node) return;
        MEDIA_RATIO_CLASSES.forEach(function (name) { node.classList.remove(name); });
        node.classList.add("media-ready", cls);
        node.style.setProperty("--media-ratio", ratio.toFixed(4));
      });
      if (onReady) onReady();
    };
    if (img.complete && img.naturalWidth) apply();
    else {
      img.addEventListener("load", apply, { once: true });
      img.addEventListener("error", function () {
        if (target) target.classList.add("media-error");
        if (onReady) onReady();
      }, { once: true });
    }
  }
  function prepareAdaptiveMedia(root, onReady) {
    if (!root) return;
    root.querySelectorAll(".photo-frame img, .fusion-photo, .topic-loop-slide img, .topic-loop-video img, .video-player img, .person-card img").forEach(function (img) {
      applyAdaptiveMediaClass(img, onReady);
    });
  }
  function parsePath() {
    var path = location.pathname.replace(/\/+$/, "") || "/";
    var q = new URLSearchParams(location.search);
    var m = path.match(/^\/(departments|topics)(?:\/([a-z0-9-]+))?$/);
    if (!m) return { kind: "home" };
    var kind = m[1], id = m[2] || null;
    if (!id) return { kind: "home" };
    var list = kind === "departments" ? DATA.departments : DATA.topics;
    if (!list[id]) return { kind: "home" };
    var section = q.get("section");
    var sections = sectionsForPortal(kind, list[id]);
    var idx = section ? sections.findIndex(function (s) { return s.id === section; }) : 0;
    return { kind: kind, id: id, section: idx >= 0 ? idx : 0 };
  }
  function urlFor(kind, id, section) {
    var params = [];
    if (INLINE_EDIT.enabled) params.push("edit=1");
    if (section != null) {
      var data = (kind === "departments" ? DATA.departments : DATA.topics)[id];
      var sec = sectionsForPortal(kind, data)[section];
      if (sec) params.push("section=" + encodeURIComponent(sec.id));
    }
    return "/" + kind + "/" + id + (params.length ? "?" + params.join("&") : "");
  }

  /* ---------- 数据加载 ---------- */
  function fetchJsonWithRetry(url, attempts) {
    return fetch(url).then(function (r) {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.json();
    }).catch(function (err) {
      if (attempts <= 1) throw err;
      return new Promise(function (resolve) {
        window.setTimeout(resolve, 140);
      }).then(function () {
        return fetchJsonWithRetry(url, attempts - 1);
      });
    });
  }

  function loadData() {
    var jobs = [];
    ["departments", "topics"].forEach(function (kind) {
      ORDER[kind].forEach(function (id) {
        jobs.push(fetchJsonWithRetry("/static/blueprint/data/" + kind + "/" + id + ".json", 3)
          .then(function (d) { DATA[kind][id] = d; })
          .catch(function () { console.warn("load failed:", id); }));
      });
    });
    return Promise.all(jobs);
  }

  function mergePortalHomePayload(payload) {
    if (!payload || !payload.ok) return;
    var school = payload.school || {};
    var schoolConfig = school.displayConfig || {};
    PORTAL_CHROME.navText = String(schoolConfig.schoolMeta || PORTAL_CHROME.navText).trim();
    PORTAL_CHROME.logoImageUrl = FIXED_SCHOOL_LOGO_URL;
    PORTAL_CHROME.schoolQrImageUrl = FIXED_SCHOOL_QR_URL;
    PORTAL_HOME.schoolName = String(schoolConfig.schoolName || school.name || PORTAL_HOME.schoolName || "").trim();
    PORTAL_HOME.schoolMeta = String(schoolConfig.schoolMeta || PORTAL_HOME.schoolMeta || "").trim();
    PORTAL_HOME.summaryKicker = String(schoolConfig.portalHomeKicker || PORTAL_HOME.summaryKicker).trim();
    PORTAL_HOME.summaryTitle = String(schoolConfig.portalHomeTitle || PORTAL_HOME.summaryTitle).trim();
    PORTAL_HOME.summaryCopy = String(schoolConfig.portalHomeCopy || PORTAL_HOME.summaryCopy).trim();
    PORTAL_HOME.routeLabels = Array.isArray(schoolConfig.portalHomeRouteLabels) ? schoolConfig.portalHomeRouteLabels : PORTAL_HOME.routeLabels;
    PORTAL_HOME.sectionKicker = String(schoolConfig.portalHomeSectionKicker || PORTAL_HOME.sectionKicker).trim();
    PORTAL_HOME.sectionTitle = String(schoolConfig.portalHomeSectionTitle || PORTAL_HOME.sectionTitle).trim();
    PORTAL_HOME.sectionCopy = String(schoolConfig.portalHomeSectionCopy || PORTAL_HOME.sectionCopy).trim();
    PORTAL_HOME.footer = String(schoolConfig.portalHomeFooter || PORTAL_HOME.footer).trim();

    HOME_CARDS = [];
    (payload.cards || []).forEach(function (card) {
      // 系部已由专题页面取代，仅保留专题卡片
      if (card.kind === "departments") return;
      var kind = card.kind === "departments" ? "departments" : "topics";
      var id = String(card.id || "").trim();
      if (!id) return;
      if (ORDER[kind].indexOf(id) < 0) ORDER[kind].push(id);
      var list = kind === "departments" ? DATA.departments : DATA.topics;
      var data = list[id] || {
        id: id,
        type: kind === "departments" ? "department" : "topic",
        name: card.name || id,
        summary: card.summary || "",
        cover: card.cover || "",
        stats: [],
        sections: []
      };
      data.name = card.name || data.name;
      data.summary = card.summary || data.summary;
      data.cover = card.cover || data.cover;
      data.homeCard = card;
      data.backendProjectId = card.projectId || data.backendProjectId;
      list[id] = data;
      HOME_CARDS.push(Object.assign({}, card, { kind: kind, id: id }));
    });
  }

  function loadPortalHome() {
    return fetch("/api/portal/home", { cache: "no-store" })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(mergePortalHomePayload)
      .catch(function () { /* static home remains the fallback */ });
  }

  function inlineEditStatus(message, kind) {
    if (!INLINE_EDIT.statusNode) return;
    INLINE_EDIT.statusNode.textContent = message || "";
    INLINE_EDIT.statusNode.dataset.kind = kind || "";
  }

  function inlineEditApi(url, options) {
    options = options || {};
    var headers = Object.assign({}, options.headers || {});
    if (options.method && options.method !== "GET" && INLINE_EDIT.csrfToken) {
      headers["X-CSRF-Token"] = INLINE_EDIT.csrfToken;
    }
    return fetch(url, Object.assign({}, options, { headers: headers }))
      .then(function (response) {
        return response.json().catch(function () { return {}; }).then(function (payload) {
          if (!response.ok || payload.ok === false) throw new Error(payload.error || "操作失败");
          return payload;
        });
      });
  }

  function inlineEditBody(data) {
    return {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data || {})
    };
  }

  function inlineProjectPayload(project) {
    return {
      name: project.name || "",
      portalType: project.portalType || "topic",
      portalSlug: project.portalSlug || "",
      ownerUsername: project.ownerUsername || "",
      accent: project.accent || "#f59a13",
      idleTitle: project.idleTitle || project.name || "",
      idleKicker: project.idleKicker || "",
      idleCopy: project.idleCopy || "",
      defaultImageUrl: project.defaultImageUrl || "",
      displayConfig: project.displayConfig || {}
    };
  }

  function inlineClone(value) {
    return JSON.parse(JSON.stringify(value || null));
  }

  function inlineSnapshot() {
    return inlineClone(INLINE_EDIT.projects);
  }

  function pushInlineUndo(label) {
    if (!INLINE_EDIT.ready) return;
    INLINE_EDIT.undoStack.push({ label: label || "edit", projects: inlineSnapshot() });
    if (INLINE_EDIT.undoStack.length > INLINE_EDIT.maxUndo) INLINE_EDIT.undoStack.shift();
  }

  function inlineConfig(project) {
    project.displayConfig = project.displayConfig || {};
    return project.displayConfig;
  }

  function rebuildInlineHomeModel() {
    if (!INLINE_EDIT.ready) return;
    var school = INLINE_EDIT.projects.find(function (project) {
      return project.portalType === "school";
    });
    if (school) {
      var schoolConfig = inlineConfig(school);
      PORTAL_HOME.schoolName = String(schoolConfig.schoolName || school.name || "").trim();
      PORTAL_HOME.schoolMeta = String(schoolConfig.schoolMeta || PORTAL_HOME.schoolMeta || "").trim();
      PORTAL_HOME.summaryKicker = String(schoolConfig.portalHomeKicker || "School Portal").trim();
      PORTAL_HOME.summaryTitle = String(schoolConfig.portalHomeTitle || "学校门户").trim();
      PORTAL_HOME.summaryCopy = String(schoolConfig.portalHomeCopy || "").trim();
      PORTAL_HOME.routeLabels = Array.isArray(schoolConfig.portalHomeRouteLabels) ? schoolConfig.portalHomeRouteLabels : [];
      PORTAL_HOME.sectionKicker = String(schoolConfig.portalHomeSectionKicker || "Integrated Showcase").trim();
      PORTAL_HOME.sectionTitle = String(schoolConfig.portalHomeSectionTitle || "创新育人矩阵").trim();
      PORTAL_HOME.sectionCopy = String(schoolConfig.portalHomeSectionCopy || "").trim();
      PORTAL_HOME.footer = String(schoolConfig.portalHomeFooter || "").trim();
    }
    HOME_CARDS = INLINE_EDIT.projects
      .filter(function (project) {
        var type = project.portalType === "department" ? "departments" : "topics";
        return project.portalType !== "school" && project.portalSlug && !inlineConfig(project).portalHomeCardHidden && (type === "topics" || type === "departments");
      })
      .map(function (project) {
        var cfg = inlineConfig(project);
        return {
          id: project.portalSlug,
          kind: project.portalType === "department" ? "departments" : "topics",
          projectId: project.id,
          name: project.name || "",
          cover: project.defaultImageUrl || "",
          label: cfg.portalHomeCardLabel || "创新育人专题",
          summary: cfg.portalHomeCardSummary || project.idleCopy || "",
          chips: [],
          sortOrder: Number(cfg.portalHomeCardSortOrder || 0),
          hidden: Boolean(cfg.portalHomeCardHidden),
          accent: project.accent || "#f59a13",
          previewUrl: project.previewUrl || ""
        };
      })
      .sort(function (a, b) {
        return Number(a.sortOrder || 0) - Number(b.sortOrder || 0) || String(a.name).localeCompare(String(b.name), "zh-CN");
      });
  }

  function restoreInlineSnapshot(snapshot, message) {
    if (!snapshot) return;
    INLINE_EDIT.projects = inlineClone(snapshot) || [];
    INLINE_EDIT.projectMap = {};
    INLINE_EDIT.projects.forEach(function (project) {
      project.displayConfig = project.displayConfig || {};
      INLINE_EDIT.projectMap[String(project.id)] = project;
      INLINE_EDIT.dirty[String(project.id)] = true;
    });
    rebuildInlineHomeModel();
    renderHome();
    inlineEditStatus(message || "已回退，记得保存", "warn");
  }

  function undoInlineEdit() {
    var last = INLINE_EDIT.undoStack.pop();
    if (!last) {
      inlineEditStatus("无可撤销", "ok");
      return;
    }
    restoreInlineSnapshot(last.projects, "已撤销上一步，记得保存");
  }

  function resetInlineDefaults() {
    if (!INLINE_EDIT.ready) return;
    if (screenHome.hidden) {
      inlineEditStatus("恢复默认仅限首页", "error");
      return;
    }
    pushInlineUndo("reset");
    INLINE_EDIT.projects.forEach(function (project) {
      var cfg = inlineConfig(project);
      if (project.portalType === "school") {
        cfg.portalHomeKicker = "School Portal";
        cfg.portalHomeTitle = "学校门户";
        cfg.portalHomeCopy = "以专题门户为主线，串联专业建设、实训基地、产教融合、教学成果与专题资源。";
        cfg.portalHomeRouteLabels = ["学校门户", "专题门户", "板块资料", "专题展区"];
        cfg.portalHomeSectionKicker = "Integrated Showcase";
        cfg.portalHomeSectionTitle = "创新育人矩阵";
        cfg.portalHomeSectionCopy = "以专题牵引院系共建，集中呈现跨系专业群、实训资源、产教融合与文化成果。";
        cfg.portalHomeFooter = "触摸卡片进入二级页面 · 长按返回首页";
      } else if (project.portalSlug) {
        cfg.portalHomeCardHidden = false;
        cfg.portalHomeCardLabel = "创新育人专题";
        cfg.portalHomeCardSummary = project.idleCopy || "";
        cfg.portalHomeCardChips = [];
      }
      INLINE_EDIT.dirty[String(project.id)] = true;
    });
    rebuildInlineHomeModel();
    renderHome();
    inlineEditStatus("已恢复默认，待保存", "warn");
  }

  function markInlineDirty(projectId) {
    if (!projectId) return;
    INLINE_EDIT.dirty[String(projectId)] = true;
    inlineEditStatus("有未保存修改", "warn");
  }

  function setInlinePath(project, path, value) {
    if (!project) return;
    var parts = path.split(".");
    var target = project;
    while (parts.length > 1) {
      var key = parts.shift();
      if (!target[key] || typeof target[key] !== "object") target[key] = {};
      target = target[key];
    }
    target[parts[0]] = value;
    markInlineDirty(project.id);
  }

  function bindInlineText(node, projectId, path, options) {
    if (!node || node.dataset.inlineBound === "1") return;
    var project = INLINE_EDIT.projectMap[String(projectId)];
    if (!project) return;
    node.dataset.inlineBound = "1";
    node.dataset.inlineEditField = path;
    node.contentEditable = "true";
    node.spellcheck = false;
    node.addEventListener("focus", function () { pushInlineUndo("text"); });
    node.addEventListener("click", function (event) { event.stopPropagation(); });
    node.addEventListener("keydown", function (event) {
      event.stopPropagation();
      if (!options || !options.multiline) {
        if (event.key === "Enter") {
          event.preventDefault();
          node.blur();
        }
      }
    });
    node.addEventListener("input", function () {
      setInlinePath(project, path, node.textContent.trim());
    });
    node.addEventListener("blur", function () {
      setInlinePath(project, path, node.textContent.trim());
    });
  }

  function fileToDataUrl(file) {
    return new Promise(function (resolve, reject) {
      var reader = new FileReader();
      reader.onload = function () { resolve(reader.result); };
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  }

  function createInlineToolbar() {
    var existing = document.querySelector(".inline-edit-toolbar");
    if (existing) existing.remove();
    var toolbar = document.createElement("div");
    toolbar.className = "inline-edit-toolbar";
    toolbar.innerHTML = '<strong>预览编辑</strong><span data-inline-edit-status>点文字改、点图换</span>' +
      '<button type="button" data-inline-undo>上一步</button>' +
      '<button type="button" data-inline-reset>恢复默认</button>' +
      '<button type="button" data-inline-save>保存</button>' +
      '<a class="inline-edit-admin-link" href="/admin">后台管理</a>' +
      '<a href="' + exitEditUrl() + '">退出编辑</a>' +
      '<input data-inline-file type="file" accept="image/*" hidden>';
    document.body.appendChild(toolbar);
    INLINE_EDIT.statusNode = toolbar.querySelector("[data-inline-edit-status]");
    toolbar.querySelector("[data-inline-undo]").addEventListener("click", undoInlineEdit);
    toolbar.querySelector("[data-inline-reset]").addEventListener("click", resetInlineDefaults);
    toolbar.querySelector("[data-inline-save]").addEventListener("click", saveInlineEdits);
    toolbar.querySelector("[data-inline-file]").addEventListener("change", uploadInlineImage);
  }

  function exitEditUrl() {
    var url = new URL(location.href);
    url.searchParams.delete("edit");
    url.searchParams.delete("focus");
    return url.pathname + url.search;
  }

  function addInlineImageButton(card, projectId) {
    if (!card || card.querySelector(".inline-edit-image-button")) return;
    var button = document.createElement("button");
    button.className = "inline-edit-image-button inline-edit-control";
    button.type = "button";
    button.textContent = "换图";
    button.addEventListener("click", function (event) {
      event.preventDefault();
      event.stopPropagation();
      INLINE_EDIT.uploadTargetProjectId = String(projectId || "");
      var input = document.querySelector("[data-inline-file]");
      if (input) {
        input.value = "";
        input.click();
      }
    });
    card.appendChild(button);
  }

  function addInlineDeleteButton(card, projectId) {
    if (!card || card.querySelector(".inline-edit-delete-button")) return;
    var button = document.createElement("button");
    button.className = "inline-edit-delete-button inline-edit-control";
    button.type = "button";
    button.textContent = "删除";
    button.addEventListener("click", function (event) {
      event.preventDefault();
      event.stopPropagation();
      var project = INLINE_EDIT.projectMap[String(projectId || "")];
      if (!project) return;
      pushInlineUndo("delete-card");
      inlineConfig(project).portalHomeCardHidden = true;
      markInlineDirty(project.id);
      rebuildInlineHomeModel();
      renderHome();
      inlineEditStatus("已删除卡片，待保存", "warn");
    });
    card.appendChild(button);
  }

  function bindInlineCardChips(card, projectId) {
    var project = INLINE_EDIT.projectMap[String(projectId)];
    if (!card || !project) return;
    var chips = Array.prototype.slice.call(card.querySelectorAll(".dept-chip"));
    chips.forEach(function (chip) {
      if (chip.dataset.inlineBound === "1") return;
      chip.dataset.inlineBound = "1";
      chip.dataset.inlineEditField = "displayConfig.portalHomeCardChips";
      chip.contentEditable = "true";
      chip.spellcheck = false;
      chip.addEventListener("focus", function () { pushInlineUndo("chips"); });
      chip.addEventListener("click", function (event) { event.preventDefault(); event.stopPropagation(); });
      chip.addEventListener("keydown", function (event) {
        event.stopPropagation();
        if (event.key === "Enter") {
          event.preventDefault();
          chip.blur();
        }
      });
      chip.addEventListener("input", function () {
        project.displayConfig = project.displayConfig || {};
        project.displayConfig.portalHomeCardChips = chips.map(function (item) {
          return {
            label: item.textContent.trim(),
            targetId: item.dataset.goId || "",
            targetKind: item.dataset.goKind || "departments"
          };
        }).filter(function (item) { return item.label; });
        markInlineDirty(project.id);
      });
    });
  }

  function bindInlineRouteLabels(project) {
    if (!project) return;
    var labels = Array.prototype.slice.call(document.querySelectorAll(".portal-route span"));
    labels.forEach(function (label) {
      if (label.dataset.inlineBound === "1") return;
      label.dataset.inlineBound = "1";
      label.dataset.inlineEditField = "displayConfig.portalHomeRouteLabels";
      label.contentEditable = "true";
      label.spellcheck = false;
      label.addEventListener("focus", function () { pushInlineUndo("route"); });
      label.addEventListener("click", function (event) { event.stopPropagation(); });
      label.addEventListener("keydown", function (event) {
        event.stopPropagation();
        if (event.key === "Enter") {
          event.preventDefault();
          label.blur();
        }
      });
      label.addEventListener("input", function () {
        project.displayConfig = project.displayConfig || {};
        project.displayConfig.portalHomeRouteLabels = labels.map(function (item) {
          return item.textContent.trim();
        }).filter(Boolean);
        markInlineDirty(project.id);
      });
    });
  }

  function uploadInlineImage(event) {
    var file = event.target.files && event.target.files[0];
    var project = INLINE_EDIT.projectMap[INLINE_EDIT.uploadTargetProjectId];
    if (!file || !project) return;
    pushInlineUndo("image");
    inlineEditStatus("图片上传中…", "warn");
    fileToDataUrl(file)
      .then(function (dataUrl) {
        return inlineEditApi("/api/assets", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ filename: file.name, dataUrl: dataUrl })
        });
      })
      .then(function (payload) {
        var url = payload.url || (payload.asset && payload.asset.url) || "";
        if (!url) throw new Error("上传成功但未返回图片地址");
        project.defaultImageUrl = url;
        markInlineDirty(project.id);
        document.querySelectorAll('.fusion-card[data-edit-project-id="' + String(project.id) + '"] .fusion-photo')
          .forEach(function (img) {
            img.style.display = "";
            img.src = url;
          });
        document.querySelectorAll('[data-inline-cover-project="' + String(project.id) + '"] img, [data-inline-cover-project="' + String(project.id) + '"] .inline-edit-cover-fallback')
          .forEach(function (node) {
            if (node.tagName === "IMG") {
              node.style.display = "";
              node.src = url;
            } else {
              node.style.display = "none";
            }
          });
        if (!screenHome.hidden) updateDetailCover(project, url, currentDetailData());
        inlineEditStatus("图片已上传，待保存", "warn");
      })
      .catch(function (error) {
        inlineEditStatus(error.message || "上传失败", "error");
      });
  }

  function saveInlineEdits() {
    var ids = Object.keys(INLINE_EDIT.dirty);
    var pageKeys = Object.keys(INLINE_EDIT.dirtyPages);
    if (!ids.length && !pageKeys.length) {
      inlineEditStatus("无修改可保存", "ok");
      return;
    }
    inlineEditStatus("保存中…", "warn");
    var chain = ids.reduce(function (promise, id) {
      return promise.then(function () {
        var project = INLINE_EDIT.projectMap[id];
        if (!project) return null;
        return inlineEditApi("/api/projects/" + encodeURIComponent(id), inlineEditBody(inlineProjectPayload(project)));
      });
    }, Promise.resolve());
    chain = chain.then(function () {
      return pageKeys.reduce(function (promise, key) {
        return promise.then(function () {
          var entry = INLINE_EDIT.dirtyPages[key];
          if (!entry) return null;
          return inlineEditApi(
            "/api/projects/" + encodeURIComponent(entry.projectId) + "/pages/" + encodeURIComponent(entry.code),
            inlineEditBody(entry.payload)
          );
        });
      }, Promise.resolve());
    });
    chain.then(function () {
      INLINE_EDIT.dirty = {};
      INLINE_EDIT.dirtyPages = {};
      inlineEditStatus("已保存", "ok");
      reloadPortalDetail();
    }).catch(function (error) {
      inlineEditStatus(error.message || "保存失败", "error");
    });
  }

  function applyInlineHomeControls() {
    if (!INLINE_EDIT.ready || screenHome.hidden) return;
    document.body.classList.add("inline-edit-mode");
    createInlineToolbar();
    var school = INLINE_EDIT.projects.find(function (project) {
      return project.portalType === "school";
    });
    if (school) {
      bindInlineText(document.querySelector(".portal-summary .portal-kicker"), school.id, "displayConfig.portalHomeKicker");
      bindInlineText(document.querySelector(".portal-summary h2"), school.id, "displayConfig.portalHomeTitle");
      bindInlineText(document.querySelector(".portal-summary p"), school.id, "displayConfig.portalHomeCopy", { multiline: true });
      bindInlineText(document.querySelector(".fusion-head .portal-kicker"), school.id, "displayConfig.portalHomeSectionKicker");
      bindInlineText(document.querySelector(".fusion-head .section-title"), school.id, "displayConfig.portalHomeSectionTitle");
      bindInlineText(document.querySelector(".fusion-head p"), school.id, "displayConfig.portalHomeSectionCopy", { multiline: true });
      bindInlineText(document.querySelector(".statusline"), school.id, "displayConfig.portalHomeFooter");
      document.querySelectorAll(".school-name").forEach(function (node) {
        bindInlineText(node, school.id, "displayConfig.schoolName");
      });
      document.querySelectorAll(".school-meta").forEach(function (node) {
        bindInlineText(node, school.id, "displayConfig.schoolMeta");
      });
      bindInlineRouteLabels(school);
    }
    document.querySelectorAll(".fusion-card[data-edit-project-id]").forEach(function (card) {
      var projectId = card.dataset.editProjectId;
      bindInlineText(card.querySelector(".fusion-label"), projectId, "displayConfig.portalHomeCardLabel");
      bindInlineText(card.querySelector("h3"), projectId, "name");
      bindInlineText(card.querySelector(".fusion-copy p"), projectId, "displayConfig.portalHomeCardSummary", { multiline: true });
      bindInlineCardChips(card, projectId);
      addInlineImageButton(card, projectId);
      addInlineDeleteButton(card, projectId);
      if (INLINE_EDIT.focus && card.dataset.editSlug === INLINE_EDIT.focus) {
        card.classList.add("inline-edit-focused");
        window.setTimeout(function () { card.scrollIntoView({ block: "center", inline: "center" }); }, 120);
      }
    });
  }

  /* ---------- 二级页可视化编辑 ---------- */
  function currentDetailData() {
    return getData();
  }

  function detailProjectFor(data) {
    return INLINE_EDIT.projectMap[String(data.backendProjectId || "")];
  }

  function pagePayloadForSection(section) {
    return {
      code: section.backendPageCode || section.id || "",
      title: section.title || "",
      body: blocksToHtml(section.blocks || []),
      contentType: section.contentType || "article",
      enabled: true
    };
  }

  function markPageDirty(projectId, code, payload) {
    var resolvedCode = (payload && payload.code) || code || "";
    if (!projectId || !resolvedCode) return;
    INLINE_EDIT.dirtyPages[String(projectId) + ":" + String(resolvedCode)] = {
      projectId: String(projectId),
      code: String(resolvedCode),
      payload: payload
    };
    inlineEditStatus("有未保存修改", "warn");
  }

  function blocksToHtml(blocks) {
    return (blocks || []).map(function (b) {
      if (b.type === "text") return "<p>" + esc(b.content) + "</p>";
      if (b.type === "image") {
        var cap = b.caption ? "<figcaption>" + esc(b.caption) + "</figcaption>" : "";
        return '<figure class="image">' + (b.src ? '<img src="' + esc(b.src) + '" alt="">' : "") + cap + "</figure>";
      }
      if (b.type === "video") {
        var poster = b.poster ? ' poster="' + esc(b.poster) + '"' : "";
        var cap = b.title ? "<figcaption><strong>" + esc(b.title) + "</strong></figcaption>" : "";
        return '<figure class="video">' + (b.src ? '<video src="' + esc(b.src) + '" controls' + poster + "></video>" : "") + cap + "</figure>";
      }
      if (b.type === "attachment") {
        return '<p><a href="' + esc(b.href) + '" target="_blank" rel="noopener">' + esc(b.title || b.href) + "</a></p>";
      }
      return "";
    }).join("");
  }

  function renderCurrentDetail() {
    if (screenDetail.hidden) return;
    if (state.kind === "departments") renderDepartmentDetail();
    else renderChapter(false);
    resetIdle();
  }

  function reloadPortalDetail() {
    return loadPortalContent().then(function () {
      if (screenDetail.hidden) return;
      renderCurrentDetail();
    }).catch(function () { renderCurrentDetail(); });
  }

  function firstImageBlockOwner(data) {
    var sections = (data && data.sections) || [];
    for (var i = 0; i < sections.length; i++) {
      var blocks = sections[i].blocks || [];
      for (var j = 0; j < blocks.length; j++) {
        if (blocks[j].type === "image" && blocks[j].src) return { section: sections[i], block: blocks[j] };
      }
    }
    return null;
  }

  function updateDetailCover(project, url, data) {
    var owner = firstImageBlockOwner(data);
    if (owner && owner.section) {
      owner.block.src = url;
      markPageDirty(project.id, owner.section.id, pagePayloadForSection(owner.section));
    }
    document.querySelectorAll('[data-inline-cover-project="' + String(project.id) + '"] img')
      .forEach(function (img) {
        img.style.display = "";
        img.src = url;
      });
  }

  function addInlineDetailCoverButton(project, container) {
    if (!container || container.querySelector(".inline-edit-cover-button")) return;
    container.dataset.inlineCoverProject = String(project.id);
    var button = document.createElement("button");
    button.className = "inline-edit-cover-button inline-edit-control";
    button.type = "button";
    button.textContent = "换图";
    button.addEventListener("click", function (event) {
      event.preventDefault();
      event.stopPropagation();
      INLINE_EDIT.uploadTargetProjectId = String(project.id);
      var input = document.querySelector("[data-inline-file]");
      if (input) {
        input.value = "";
        input.click();
      }
    });
    container.appendChild(button);
  }

  function bindInlineSectionTitle(node, section, project) {
    if (!node || node.dataset.inlineBound === "1") return;
    node.querySelectorAll(".topic-showcase-coop-empty").forEach(function (s) { s.remove(); });
    node.dataset.inlineBound = "1";
    node.dataset.inlineEditField = "section:" + (section.id || "");
    node.contentEditable = "true";
    node.spellcheck = false;
    node.addEventListener("focus", function () { pushInlineUndo("section-title"); });
    node.addEventListener("click", function (event) { event.stopPropagation(); });
    node.addEventListener("keydown", function (event) {
      event.stopPropagation();
      if (event.key === "Enter") {
        event.preventDefault();
        node.blur();
      }
    });
    node.addEventListener("input", function () {
      section.title = node.textContent.trim();
      markPageDirty(project.id, section.id, pagePayloadForSection(section));
    });
  }

  function bindInlineCoopBody(node, project, section) {
    if (!node || node.dataset.inlineBound === "1") return;
    node.querySelectorAll(".topic-showcase-coop-empty").forEach(function (s) { s.remove(); });
    node.dataset.inlineBound = "1";
    node.contentEditable = "true";
    node.spellcheck = false;
    node.addEventListener("focus", function () { pushInlineUndo("coop-body"); });
    node.addEventListener("click", function (event) { event.stopPropagation(); });
    var apply = function () {
      var newText = String(node.innerText || "").replace(/\u00a0/g, " ").trim();
      var oldText = (section.blocks || []).filter(function (b) { return b.type === "text"; })
        .map(function (b) { return String(b.content || "").trim(); }).join("\n\n");
      if (newText === oldText) return;
      var kept = (section.blocks || []).filter(function (b) { return b.type !== "text"; });
      var texts = String(newText).split(/\n{2,}/).map(function (t) { return t.trim(); }).filter(Boolean)
        .map(function (t) { return { type: "text", content: t }; });
      section.blocks = texts.concat(kept);
      markPageDirty(project.id, section.id, pagePayloadForSection(section));
    };
    node.addEventListener("input", apply);
    node.addEventListener("blur", apply);
  }

  function sectionEditorOverlay(section, project) {
    var existing = document.querySelector(".section-editor-overlay");
    if (existing) existing.remove();
    var overlay = document.createElement("div");
    overlay.className = "section-editor-overlay";
    var texts = (section.blocks || []).filter(function (b) { return b.type === "text" && b.content; })
      .map(function (b) { return b.content; });
    var images = (section.blocks || []).filter(function (b) { return b.type === "image"; });
    var keptKinds = (section.blocks || []).filter(function (b) { return b.type === "video" || b.type === "attachment"; });
    var hasKept = keptKinds.length > 0;
    overlay.innerHTML =
      '<div class="section-editor-panel" role="dialog" aria-label="编辑板块">' +
      '<header><strong>编辑板块：' + esc(section.title || section.id || "") + '</strong>' +
      '<button type="button" class="section-editor-close" aria-label="关闭">×</button></header>' +
      '<label class="section-editor-field"><span>板块标题</span><input class="section-editor-title" value="' + esc(section.title || "") + '"></label>' +
      '<label class="section-editor-field"><span>正文（空行分段）</span><textarea class="section-editor-body" rows="8">' + esc(texts.join("\n\n")) + '</textarea></label>' +
      '<div class="section-editor-field"><span>图片地址（每行一张）</span><div class="section-editor-images">' +
      (images.length ? images.map(function (img) {
        return '<div class="section-editor-image-row"><input value="' + esc(img.src || "") + '" placeholder="/uploads/... 或 http(s)://"><button type="button" class="section-editor-image-remove">删除</button></div>';
      }).join("") : '<div class="section-editor-image-row"><input value="" placeholder="/uploads/... 或 http(s)://"><button type="button" class="section-editor-image-remove">删除</button></div>') +
      '</div><button type="button" class="section-editor-image-add">＋ 添加图片</button></div>' +
      (hasKept ? '<p class="section-editor-note">板块中的视频和附件保持不变。</p>' : "") +
      '<div class="section-editor-actions">' +
      '<button type="button" class="section-editor-delete">删除板块</button>' +
      '<span class="section-editor-status"></span>' +
      '<button type="button" class="section-editor-save primary">保存修改</button></div>' +
      '</div>';
    document.body.appendChild(overlay);
    var statusNode = overlay.querySelector(".section-editor-status");
    var setStatus = function (message, kind) {
      statusNode.textContent = message || "";
      statusNode.dataset.kind = kind || "";
    };
    overlay.querySelector(".section-editor-close").addEventListener("click", function () { overlay.remove(); });
    overlay.addEventListener("click", function (event) { if (event.target === overlay) overlay.remove(); });
    overlay.querySelector(".section-editor-image-add").addEventListener("click", function () {
      var row = document.createElement("div");
      row.className = "section-editor-image-row";
      row.innerHTML = '<input value="" placeholder="/uploads/... 或 http(s)://"><button type="button" class="section-editor-image-remove">删除</button>';
      overlay.querySelector(".section-editor-images").appendChild(row);
    });
    overlay.querySelectorAll(".section-editor-image-remove").forEach(function (button) {
      button.addEventListener("click", function () { button.closest(".section-editor-image-row").remove(); });
    });
    overlay.querySelector(".section-editor-delete").addEventListener("click", function () {
      var code = section.backendPageCode;
      if (!code) {
        setStatus("该板块还没有后端页面，无需删除", "error");
        return;
      }
      if (!confirm("确定删除板块“" + (section.title || code) + "”的后端页面？")) return;
      inlineEditApi("/api/projects/" + encodeURIComponent(project.id) + "/pages/" + encodeURIComponent(code), { method: "DELETE" })
        .then(function () {
          overlay.remove();
          delete INLINE_EDIT.dirtyPages[String(project.id) + ":" + String(code)];
          inlineEditStatus("板块已删除", "ok");
          reloadPortalDetail();
        })
        .catch(function (error) { setStatus(error.message || "删除失败", "error"); });
    });
    overlay.querySelector(".section-editor-save").addEventListener("click", function () {
      var title = overlay.querySelector(".section-editor-title").value.trim();
      var text = overlay.querySelector(".section-editor-body").value;
      var urls = Array.prototype.map.call(overlay.querySelectorAll(".section-editor-images input"), function (input) {
        return input.value.trim();
      }).filter(Boolean);
      var blocks = [];
      String(text).split(/\n{2,}/).map(function (t) { return t.trim(); }).filter(Boolean)
        .forEach(function (t) { blocks.push({ type: "text", content: t }); });
      urls.forEach(function (src) { blocks.push({ type: "image", src: src, caption: "" }); });
      blocks = blocks.concat(keptKinds);
      var code = section.backendPageCode || section.id || "";
      section.title = title;
      section.blocks = blocks;
      if (code) {
        markPageDirty(project.id, code, pagePayloadForSection(section));
      }
      overlay.remove();
      inlineEditStatus("板块已修改，待保存", "warn");
      renderCurrentDetail();
    });
    var titleInput = overlay.querySelector(".section-editor-title");
    if (titleInput) titleInput.focus();
  }

  function addInlineSectionEditButton(container, section, project) {
    if (!container || container.querySelector(".inline-edit-section-button")) return;
    var button = document.createElement("button");
    button.className = "inline-edit-section-button inline-edit-control";
    button.type = "button";
    button.textContent = "编辑板块";
    button.addEventListener("click", function (event) {
      event.preventDefault();
      event.stopPropagation();
      sectionEditorOverlay(section, project);
    });
    container.appendChild(button);
  }

  function availableSectionOptions(data) {
    var used = {};
    ((data && data.sections) || []).forEach(function (s) {
      if (s && s.id) used[s.id] = true;
    });
    var candidates = state.kind === "departments"
      ? MODULE_SEQUENCE.map(function (item) { return { id: item[0], label: item[2] || item[1] }; })
      : TOPIC_SECTION_ORDER.map(function (id) { return { id: id, label: TOPIC_SECTION_TITLES[id] || id }; });
    return candidates.filter(function (item) { return !used[item.id]; });
  }

  function closeSectionAddMenu() {
    var menu = document.querySelector(".section-add-menu");
    if (menu) menu.remove();
  }

  function attachDetailAddSection(data, project) {
    var target = document.querySelector(".showcase-board") || document.querySelector(".topic-showcase-page") ||
      document.querySelector(".topic-section-page");
    if (!target || target.querySelector(".inline-edit-add-section")) return;
    var button = document.createElement("button");
    button.className = "inline-edit-add-section inline-edit-control";
    button.type = "button";
    button.textContent = "＋ 添加板块";
    button.addEventListener("click", function (event) {
      event.preventDefault();
      event.stopPropagation();
      var options = availableSectionOptions(data);
      if (!options.length) {
        inlineEditStatus("板块已齐全", "error");
        return;
      }
      closeSectionAddMenu();
      var menu = document.createElement("div");
      menu.className = "section-add-menu";
      menu.innerHTML = '<strong>选择要添加的板块</strong>' + options.map(function (o) {
        return '<button type="button" data-add-section-id="' + esc(o.id) + '">' + esc(o.label) + '</button>';
      }).join("");
      document.body.appendChild(menu);
      var rect = button.getBoundingClientRect();
      menu.style.top = Math.min(rect.bottom + 6, window.innerHeight - menu.offsetHeight - 12) + "px";
      menu.style.left = Math.max(12, Math.min(rect.left, window.innerWidth - menu.offsetWidth - 12)) + "px";
      var pick = function (option) {
        closeSectionAddMenu();
        inlineEditApi(
          "/api/projects/" + encodeURIComponent(project.id) + "/pages/" + encodeURIComponent(option.id),
          inlineEditBody({ code: option.id, title: option.label, body: "", contentType: "article" })
        ).then(function () {
          inlineEditStatus("板块已创建", "ok");
          reloadPortalDetail();
        }).catch(function (error) {
          inlineEditStatus(error.message || "创建板块失败", "error");
        });
      };
      menu.querySelectorAll("[data-add-section-id]").forEach(function (item) {
        item.addEventListener("click", function () {
          var option = options.find(function (o) { return String(o.id) === String(item.dataset.addSectionId); });
          if (option) pick(option);
        });
      });
      window.setTimeout(function () {
        document.addEventListener("click", function onDocClick(e) {
          if (!e.target.closest(".section-add-menu") && !e.target.closest(".inline-edit-add-section")) {
            closeSectionAddMenu();
            document.removeEventListener("click", onDocClick);
          }
        });
      }, 0);
    });
    target.appendChild(button);
  }

  function applyInlineDetailControls() {
    if (!INLINE_EDIT.enabled || screenDetail.hidden) return;
    if (!INLINE_EDIT.ready) {
      initInlineEdit().then(applyInlineDetailControls);
      return;
    }
    var data = currentDetailData();
    var project = detailProjectFor(data);
    if (!project) {
      inlineEditStatus("未关联后台项目，仅可预览", "error");
      return;
    }
    document.body.classList.add("inline-edit-mode");
    createInlineToolbar();
    bindInlineText(document.querySelector(".showcase-identity h2"), project.id, "name");
    bindInlineText(document.querySelector(".showcase-identity p"), project.id, "idleCopy", { multiline: true });
    bindInlineText(document.querySelector(".topic-showcase-title-row strong"), project.id, "name");
    bindInlineText(document.querySelector(".topic-section-heading p"), project.id, "idleCopy", { multiline: true });
    bindInlineText(document.querySelector(".topic-showcase-brand p"), project.id, "idleCopy", { multiline: true });

    if (state.kind === "departments") {
      var coverContainer = document.querySelector(".showcase-media");
      addInlineDetailCoverButton(project, coverContainer);
    }

    if (state.kind === "departments") {
      document.querySelectorAll(".showcase-card[data-module]").forEach(function (card) {
        var moduleId = card.dataset.module;
        var section = firstSectionById(data, moduleId);
        if (!section) {
          section = { id: moduleId, title: "", blocks: [], contentType: "article" };
          data.sections = data.sections || [];
          data.sections.push(section);
        }
        var wrap = card.closest(".showcase-card-wrap");
        var editButton = wrap ? wrap.querySelector("[data-section-edit]") : null;
        if (editButton && !editButton.dataset.inlineBound) {
          editButton.dataset.inlineBound = "1";
          editButton.addEventListener("click", function (event) {
            event.preventDefault();
            event.stopPropagation();
            sectionEditorOverlay(section, project);
          });
        }
      });
    } else if (state.sections && state.sections[state.section]) {
      var section = state.sections[state.section];
      var heading = document.querySelector(".topic-section-heading");
      if (heading) {
        bindInlineSectionTitle(heading.querySelector("h2"), section, project);
        addInlineDeleteSectionButton(heading, project, section);
      }
      var model = topicSectionModel(section);
      if (!model.leadTextBlock && !model.pointTextBlocks.length) {
        var seedBlock = { type: "text", content: "" };
        section.blocks = section.blocks || [];
        section.blocks.push(seedBlock);
        model = topicSectionModel(section);
      }
      var leadNode = document.querySelector(".topic-section-lead");
      if (leadNode && model.leadTextBlock) bindInlineBlockText(leadNode, project, section, [model.leadTextBlock], 0);
      var storyTitle = document.querySelector(".topic-section-story h3");
      if (storyTitle && model.titleTextBlock) bindInlineBlockText(storyTitle, project, section, [model.titleTextBlock], 0);
      document.querySelectorAll(".topic-section-points li span[data-block-text-idx]").forEach(function (span) {
        var idx = parseInt(span.dataset.blockTextIdx, 10);
        if (isFinite(idx) && model.pointTextBlocks[idx]) bindInlineBlockText(span, project, section, model.pointTextBlocks, idx);
      });
      document.querySelectorAll(".inline-edit-point-remove").forEach(function (btn) {
        if (btn.dataset.inlineBound) return;
        btn.dataset.inlineBound = "1";
        btn.addEventListener("click", function (event) {
          event.preventDefault();
          event.stopPropagation();
          var block = model.pointTextBlocks[parseInt(btn.dataset.pointIdx, 10)];
          if (!block) return;
          pushInlineUndo("point-remove");
          section.blocks = (section.blocks || []).filter(function (b) { return b !== block; });
          markPageDirty(project.id, section.id, pagePayloadForSection(section));
          renderCurrentDetail();
        });
      });
      var addPoint = document.querySelector(".inline-edit-add-point");
      if (addPoint && !addPoint.dataset.inlineBound) {
        addPoint.dataset.inlineBound = "1";
        addPoint.addEventListener("click", function (event) {
          event.preventDefault();
          event.stopPropagation();
          pushInlineUndo("point-add");
          var blocks = section.blocks || [];
          var lastTextIdx = -1;
          blocks.forEach(function (b, i) { if (b.type === "text") lastTextIdx = i; });
          blocks.splice(lastTextIdx + 1, 0, { type: "text", content: "" });
          section.blocks = blocks;
          markPageDirty(project.id, section.id, pagePayloadForSection(section));
          renderCurrentDetail();
          var newSpan = document.querySelector('.topic-section-points li span[data-block-text-idx="' + (lastTextIdx + 1) + '"]');
          if (newSpan) newSpan.focus();
        });
      }
      var mediaBox = document.querySelector("[data-section-media]");
      if (mediaBox) addInlineMediaImageButton(mediaBox, project, section);
      document.querySelectorAll("[data-upload-video]").forEach(function (btn) {
        if (btn.dataset.inlineBound) return;
        btn.dataset.inlineBound = "1";
        btn.addEventListener("click", function (event) {
          event.preventDefault();
          event.stopPropagation();
          var mediaSec = firstSectionById(data, "media");
          if (!mediaSec) {
            mediaSec = { id: "media", title: "", blocks: [], contentType: "article" };
            data.sections = data.sections || [];
            data.sections.push(mediaSec);
          }
          uploadSectionVideo(project, mediaSec);
        });
      });
      var coopPhoto = document.querySelector(".topic-showcase-coop-photo");
      var coopTitle = document.querySelector(".topic-showcase-coop-title");
      var coopBody = document.querySelector(".topic-showcase-coop-body");
      if (coopPhoto || coopTitle || coopBody) {
        var coopSection = firstSectionById(data, "cooperation");
        if (!coopSection) {
          coopSection = { id: "cooperation", title: "", blocks: [], contentType: "article" };
          data.sections = data.sections || [];
          data.sections.push(coopSection);
        }
        if (coopPhoto) addInlineMediaImageButton(coopPhoto, project, coopSection);
        if (coopTitle) bindInlineSectionTitle(coopTitle, coopSection, project);
        if (coopBody) bindInlineCoopBody(coopBody, project, coopSection);
      }
      document.querySelectorAll("[data-coverflow-edit]").forEach(function (btn) {
        if (btn.dataset.inlineBound) return;
        btn.dataset.inlineBound = "1";
        var sec = firstSectionById(data, btn.dataset.coverflowEdit);
        if (!sec) {
          sec = { id: btn.dataset.coverflowEdit, title: "", blocks: [], contentType: "article" };
          data.sections = data.sections || [];
          data.sections.push(sec);
        }
        btn.addEventListener("click", function (event) {
          event.preventDefault();
          event.stopPropagation();
          uploadSectionImage(project, sec);
        });
      });
      document.querySelectorAll(".topic-showcase-mini[data-section-id], .topic-showcase-partner[data-section-id]").forEach(function (card) {
        var sec = firstSectionById(data, card.dataset.sectionId);
        if (!sec) {
          sec = { id: card.dataset.sectionId, title: "", blocks: [], contentType: "article" };
          data.sections = data.sections || [];
          data.sections.push(sec);
        }
        var secBlocks = sectionTextBlocks(data, sec.id);
        if (!secBlocks.length) {
          var emptyTextBlock = { type: "text", content: "" };
          sec.blocks = sec.blocks || [];
          sec.blocks.push(emptyTextBlock);
          secBlocks = [emptyTextBlock];
        }
        var cardText = card.querySelector("p[data-block-text-idx]");
        if (cardText && secBlocks[0]) bindInlineBlockText(cardText, project, sec, secBlocks, 0);
        addInlineMediaImageButton(card, project, sec);
        addInlineDeleteSectionButton(card, project, sec);
      });
    }
    attachDetailAddSection(data, project);
    inlineEditStatus("点击修改，点“保存”生效", "warn");
  }

  function sectionTextBlocks(data, secId) {
    var section = firstSectionById(data, secId);
    return (section && section.blocks || []).filter(function (b) {
      return b.type === "text" && String(b.content || "").trim();
    });
  }

  function bindInlineBlockText(node, project, section, blocks, idx) {
    if (!node || node.dataset.inlineBound === "1") return;
    var block = blocks && blocks[idx];
    if (!block) return;
    node.dataset.inlineBound = "1";
    node.dataset.inlineBlockText = String(idx);
    node.contentEditable = "true";
    node.spellcheck = false;
    node.addEventListener("focus", function () { pushInlineUndo("block-text"); });
    node.addEventListener("click", function (event) { event.stopPropagation(); });
    node.addEventListener("keydown", function (event) {
      event.stopPropagation();
      if (event.key === "Enter") {
        event.preventDefault();
        node.blur();
      }
    });
    var apply = function () {
      var newText = node.textContent.trim();
      if (newText === String(block.content || "").trim()) return;
      block.content = newText;
      if (section) {
        markPageDirty(project.id, section.id, pagePayloadForSection(section));
      }
    };
    node.addEventListener("input", apply);
    node.addEventListener("blur", apply);
  }

  function addInlineDeleteSectionButton(container, project, section) {
    if (!container || container.querySelector(".inline-edit-delete-section")) return;
    var button = document.createElement("button");
    button.className = "inline-edit-delete-section inline-edit-control";
    button.type = "button";
    button.textContent = "删除板块";
    button.title = "删除该板块的后端页面";
    button.addEventListener("click", function (event) {
      event.preventDefault();
      event.stopPropagation();
      var code = section.backendPageCode;
      if (!code) {
        inlineEditStatus("无页面可删除", "error");
        return;
      }
      if (!confirm("确定删除板块“" + (section.title || code) + "”的后端页面？")) return;
      inlineEditApi("/api/projects/" + encodeURIComponent(project.id) + "/pages/" + encodeURIComponent(code), { method: "DELETE" })
        .then(function () {
          delete INLINE_EDIT.dirtyPages[String(project.id) + ":" + String(code)];
          inlineEditStatus("板块已删除", "ok");
          reloadPortalDetail();
        })
        .catch(function (error) { inlineEditStatus(error.message || "删除失败", "error"); });
    });
    container.appendChild(button);
  }

  function uploadSectionImage(project, section) {
    var input = document.createElement("input");
    input.type = "file";
    input.accept = "image/*";
    input.style.cssText = "position:fixed;left:-9999px;top:0;width:1px;height:1px;opacity:0;pointer-events:none;";
    document.body.appendChild(input);
    input.addEventListener("change", function () {
      var file = input.files && input.files[0];
      if (!file) return;
      pushInlineUndo("image");
      inlineEditStatus("图片上传中…", "warn");
      fileToDataUrl(file)
        .then(function (dataUrl) {
          return inlineEditApi("/api/assets", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ filename: file.name, dataUrl: dataUrl })
          });
        })
        .then(function (payload) {
          var url = payload.url || (payload.asset && payload.asset.url) || "";
          if (!url) throw new Error("上传成功但未返回图片地址");
          var blocks = section.blocks || [];
          var imgBlock = null;
          for (var i = 0; i < blocks.length; i++) {
            if (blocks[i].type === "image") { imgBlock = blocks[i]; break; }
          }
          if (imgBlock) imgBlock.src = url;
          else blocks.push({ type: "image", src: url, caption: "" });
          section.blocks = blocks;
          markPageDirty(project.id, section.id, pagePayloadForSection(section));
          renderCurrentDetail();
          inlineEditStatus("图片已更换，待保存", "warn");
        })
        .catch(function (error) { inlineEditStatus(error.message || "上传失败", "error"); });
    });
    input.click();
  }

  function addInlineMediaImageButton(container, project, section) {
    if (!container || container.querySelector(".inline-edit-media-button")) return;
    var button = document.createElement("button");
    button.className = "inline-edit-media-button inline-edit-control";
    button.type = "button";
    button.textContent = "换图";
    button.addEventListener("click", function (event) {
      event.preventDefault();
      event.stopPropagation();
      uploadSectionImage(project, section);
    });
    container.appendChild(button);
  }

  function uploadSectionVideo(project, section) {
    var input = document.createElement("input");
    input.type = "file";
    input.accept = "video/mp4,video/webm";
    input.style.cssText = "position:fixed;left:-9999px;top:0;width:1px;height:1px;opacity:0;pointer-events:none;";
    document.body.appendChild(input);
    input.addEventListener("change", function () {
      var file = input.files && input.files[0];
      if (!file) return;
      pushInlineUndo("video");
      inlineEditStatus("视频上传中…", "warn");
      fileToDataUrl(file)
        .then(function (dataUrl) {
          return inlineEditApi("/api/assets", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ filename: file.name, dataUrl: dataUrl })
          });
        })
        .then(function (payload) {
          var url = payload.url || (payload.asset && payload.asset.url) || "";
          if (!url) throw new Error("上传成功但未返回视频地址");
          var blocks = section.blocks || [];
          var vb = null;
          for (var i = 0; i < blocks.length; i++) {
            if (blocks[i].type === "video") { vb = blocks[i]; break; }
          }
          var poster = "";
          for (var j = 0; j < blocks.length; j++) {
            if (blocks[j].type === "image" && blocks[j].src) { poster = blocks[j].src; break; }
          }
          if (vb) {
            vb.src = url;
            if (!vb.poster) vb.poster = poster;
          } else {
            blocks.push({ type: "video", src: url, poster: poster, title: "视频资源" });
          }
          section.blocks = blocks;
          markPageDirty(project.id, section.id, pagePayloadForSection(section));
          renderCurrentDetail();
          inlineEditStatus("视频已上传，待保存", "warn");
        })
        .catch(function (error) { inlineEditStatus(error.message || "上传失败", "error"); });
    });
    input.click();
  }

  function initInlineEdit() {
    if (!INLINE_EDIT.enabled) return Promise.resolve();
    if (INLINE_EDIT.initPromise) return INLINE_EDIT.initPromise;
    INLINE_EDIT.initPromise = inlineEditApi("/api/session")
      .then(function (session) {
        if (!session.authenticated || !(session.permissions || []).some(function (item) { return item === "admin" || item === "review" || item === "department_admin"; })) {
          throw new Error("请先登录后台管理员账号，再进入预览编辑。");
        }
        INLINE_EDIT.csrfToken = session.csrfToken || "";
        return inlineEditApi("/api/projects");
      })
      .then(function (payload) {
        INLINE_EDIT.projects = payload.projects || [];
        INLINE_EDIT.projectMap = {};
        INLINE_EDIT.projects.forEach(function (project) {
          project.displayConfig = project.displayConfig || {};
          INLINE_EDIT.projectMap[String(project.id)] = project;
        });
        INLINE_EDIT.ready = true;
        applyInlineHomeControls();
      })
      .catch(function (error) {
        createInlineToolbar();
        inlineEditStatus(error.message || "编辑模式不可用", "error");
      });
    return INLINE_EDIT.initPromise;
  }

  function activateInlineEditIfNeeded() {
    if (!INLINE_EDIT.enabled) return;
    initInlineEdit().then(applyInlineHomeControls);
  }

  /* ---------- 二维码 ---------- */
  function loadPortalContent() {
    var jobs = [];
    ["departments", "topics"].forEach(function (kind) {
      ORDER[kind].forEach(function (id) {
        jobs.push(fetch("/api/portal/" + kind + "/" + encodeURIComponent(id), { cache: "no-store" })
          .then(function (r) { return r.ok ? r.json() : null; })
          .then(function (payload) { mergePortalPayload(kind, id, payload); })
          .catch(function () { /* static blueprint data remains the fallback */ }));
      });
    });
    return Promise.all(jobs);
  }

  function mergePortalPayload(kind, id, payload) {
    if (!payload || !payload.ok || !payload.project) return;
    var data = (kind === "departments" ? DATA.departments : DATA.topics)[id];
    if (!data) {
      data = {
        id: id,
        type: kind === "departments" ? "department" : "topic",
        name: payload.project.name || id,
        summary: payload.project.idleCopy || "",
        cover: payload.project.defaultImageUrl || "",
        stats: [],
        sections: []
      };
      (kind === "departments" ? DATA.departments : DATA.topics)[id] = data;
    }
    data.name = payload.project.name || data.name;
    data.summary = payload.project.idleCopy || data.summary;
    data.cover = payload.project.defaultImageUrl || data.cover;
    data.backendProjectId = payload.project.id;
    data.backendCoverage = payload.coverage || null;
    data.backendModuleMap = {};
    ((payload.coverage && payload.coverage.modules) || []).forEach(function (module) {
      data.backendModuleMap[module.key] = module;
    });

    var sectionById = {};
    (data.sections || []).forEach(function (section) {
      if (section && section.id) sectionById[section.id] = section;
    });

    payload.pages.forEach(function (page, index) {
      var sectionId = sectionIdForPage(kind, page, index);
      var blocks = pageToBlocks(page);
      if (!blocks.length) return;
      var title = page.title || page.moduleLabel || page.category || "Content";
      var section = sectionById[sectionId];
      if (!section) {
        section = { id: sectionId, title: title, blocks: [] };
        data.sections.push(section);
        sectionById[sectionId] = section;
      }
      section.title = title || section.title;
      section.blocks = blocks;
      section.contentType = normalizeContentType(page.contentType || section.contentType || defaultContentTypeForSection(sectionId));
      section.backendPageTitle = page.title || "";
      section.backendPageCode = page.code || "";
      section.backendUpdatedAt = page.updatedAt || "";
    });
    mergeExternalLinksFromContentItems(kind, data, sectionById, payload.contentItems || []);
    if (kind === "topics") {
      data.cooperationItems = (payload.contentItems || []).filter(function (item) {
        return String(item.moduleKey || "").toLowerCase() === "cooperation";
      }).map(function (item) {
        return {
          title: String(item.title || "").trim(),
          summary: String(item.summary || "").trim()
        };
      }).filter(function (item) { return item.title; });
      data.sectionItems = {};
      (payload.contentItems || []).forEach(function (item, index) {
        var secId = sectionIdForPage(kind, {
          id: item.id || index + 1,
          code: item.code || "",
          moduleKey: item.moduleKey || "",
          category: item.moduleLabel || "",
          title: item.title || ""
        }, index);
        if (!secId) return;
        var assets = Array.isArray(item.assets) ? item.assets : [];
        var firstAsset = assets.find(function (a) { return a && a.url && (a.role === "cover" || a.role === "image" || a.role === "gallery"); }) || assets[0] || null;
        (data.sectionItems[secId] = data.sectionItems[secId] || []).push({
          id: item.id,
          code: item.code || "",
          title: String(item.title || "").trim(),
          summary: String(item.summary || "").trim(),
          imageUrl: (firstAsset && firstAsset.url) || "",
          bodyHtml: bodyHtmlFromContentItem(item),
          updatedAt: item.updatedAt || ""
        });
      });
    }
  }

  function mergeExternalLinksFromContentItems(kind, data, sectionById, items) {
    if (kind !== "topics") return;
    (items || []).forEach(function (item, index) {
      var links = externalLinksForContentItem(item);
      if (!links.length) return;
      var sectionId = sectionIdForPage(kind, {
        id: item.id || index + 1,
        code: item.code || "",
        moduleKey: item.moduleKey || "",
        category: item.moduleLabel || "",
        title: item.title || ""
      }, index);
      var section = sectionById[sectionId];
      if (!section) {
        section = {
          id: sectionId,
          title: item.moduleLabel || item.title || sectionId,
          blocks: itemToBlocks(item),
          contentType: item.contentType || defaultContentTypeForSection(sectionId)
        };
        data.sections.push(section);
        sectionById[sectionId] = section;
      }
      section.externalLinks = uniqueExternalLinks((section.externalLinks || []).concat(links));
      if (item.updatedAt && (!section.backendUpdatedAt || item.updatedAt > section.backendUpdatedAt)) {
        section.backendUpdatedAt = item.updatedAt;
      }
    });
  }

  function externalLinksForContentItem(item) {
    var assets = Array.isArray(item && item.assets) ? item.assets : [];
    return assets.filter(function (asset) {
      return asset && String(asset.role || "").toLowerCase() === "external_link" && String(asset.url || "").trim();
    }).map(function (asset) {
      return {
        label: asset.caption || asset.title || item.title || "打开体验系统",
        href: String(asset.url || "").trim(),
        description: item.summary || asset.title || "",
        sourceTitle: item.title || ""
      };
    });
  }

  function uniqueExternalLinks(links) {
    var seen = {};
    return (links || []).filter(function (link) {
      var href = String(link && link.href || "").trim();
      var label = String(link && link.label || "").trim();
      var key = href + "\n" + label;
      if (!href || seen[key]) return false;
      seen[key] = true;
      return true;
    });
  }

  function itemToBlocks(item) {
    var blocks = [];
    if (item && item.summary) blocks.push({ type: "text", content: item.summary });
    var body = Array.isArray(item && item.bodyJson) ? item.bodyJson : [];
    body.forEach(function (block) {
      if (!block) return;
      if (typeof block === "string") blocks.push({ type: "text", content: block });
      else if (block.type === "paragraph" && block.text) blocks.push({ type: "text", content: block.text });
      else if (block.type === "html" && block.html) blocks = blocks.concat(htmlToBlocks(block.html));
      else if ((block.type === "text" || block.type === "heading") && (block.content || block.text)) {
        blocks.push({ type: "text", content: block.content || block.text });
      }
    });
    return uniqueMediaBlocks(blocks);
  }

  function sectionIdForPage(kind, page, index) {
    var code = String(page && page.code || "").toLowerCase().replace(/_/g, "-");
    var known = [
      "overview", "majors", "training", "cooperation", "achievements",
      "competitions", "honors", "masters", "alumni", "students", "media",
      "faculty", "orders", "industry-school", "systems", "resources", "gallery"
    ];
    for (var i = 0; i < known.length; i += 1) {
      if (code.indexOf("-" + known[i]) >= 0 || code === known[i]) {
        return kind === "topics" && known[i] === "gallery" ? "achievements" : known[i];
      }
    }
    var moduleKey = String(page && page.moduleKey || "");
    if (kind === "departments") {
      if (moduleKey) return moduleKey;
    } else {
      if (TOPIC_SECTION_ORDER.indexOf(moduleKey) >= 0) return moduleKey;
      if (moduleKey === "topicOverview") return "overview";
      if (moduleKey === "topicAchievements") return "achievements";
      if (moduleKey === "topicGallery") return "achievements";
      if (moduleKey === "topicMedia") return "media";
    }
    return "backend-" + (page.id || index + 1);
  }

  function pageToBlocks(page) {
    var blocks = htmlToBlocks(page && page.body);
    var imageUrl = String(page && page.imageUrl || "").trim();
    var hasMedia = blocks.some(function (block) {
      return block && (block.type === "image" || block.type === "video") && block.src;
    });
    if (imageUrl && !hasMedia) {
      blocks.unshift({ type: "image", src: imageUrl, caption: page.title || page.category || "" });
    }
    if (!blocks.length && page && page.subtitle) {
      blocks.push({ type: "text", content: page.subtitle });
    }
    return uniqueMediaBlocks(blocks);
  }

  function htmlToBlocks(html) {
    var box = document.createElement("div");
    box.innerHTML = String(html || "");
    var blocks = [];
    var pushText = function (text) {
      text = String(text || "").replace(/\s+/g, " ").trim();
      if (text) blocks.push({ type: "text", content: text });
    };
    var isAttachmentHref = function (href) {
      return /\.(pdf|doc|docx|xls|xlsx|ppt|pptx|txt|csv|zip)(\?|#|$)/i.test(String(href || ""));
    };
    var pushAttachmentLinks = function (node) {
      var links = Array.prototype.slice.call(node.querySelectorAll ? node.querySelectorAll("a[href]") : []);
      links.forEach(function (link) {
        var href = link.getAttribute("href") || "";
        if (isAttachmentHref(href)) {
          blocks.push({
            type: "attachment",
            href: href,
            title: link.textContent.trim() || href
          });
        }
      });
      return links.some(function (link) { return isAttachmentHref(link.getAttribute("href") || ""); });
    };
    var walk = function (node) {
      if (!node) return;
      if (node.nodeType === 3) {
        pushText(node.nodeValue);
        return;
      }
      if (node.nodeType !== 1) return;
      var tag = node.tagName.toLowerCase();
      if (tag === "figure") {
        var img = node.querySelector("img");
        var videoEl = node.querySelector("video");
        var link = node.querySelector("figcaption a[href]");
        var caption = node.querySelector("figcaption");
        var title = node.querySelector("strong, h2, h3");
        var href = link ? link.getAttribute("href") : "";
        if (videoEl && videoEl.getAttribute("src")) {
          blocks.push({
            type: "video",
            src: videoEl.getAttribute("src"),
            poster: videoEl.getAttribute("poster") || (img ? img.getAttribute("src") : ""),
            title: title ? title.textContent.trim() : ""
          });
          return;
        }
        if (href && /\.(mp4|webm|ogg)(\?|#|$)/i.test(href)) {
          blocks.push({
            type: "video",
            src: href,
            poster: img ? img.getAttribute("src") : "",
            title: title ? title.textContent.trim() : ""
          });
          return;
        }
        if (img && img.getAttribute("src")) {
          blocks.push({
            type: "image",
            src: img.getAttribute("src"),
            caption: caption ? caption.textContent.trim() : (img.getAttribute("alt") || "")
          });
          return;
        }
      }
      if (tag === "img" && node.getAttribute("src")) {
        blocks.push({ type: "image", src: node.getAttribute("src"), caption: node.getAttribute("alt") || "" });
        return;
      }
      if (tag === "a" && node.getAttribute("href") && isAttachmentHref(node.getAttribute("href"))) {
        blocks.push({ type: "attachment", href: node.getAttribute("href"), title: node.textContent.trim() || node.getAttribute("href") });
        return;
      }
      if (/^(p|li|blockquote|h2|h3|h4)$/.test(tag)) {
        if (pushAttachmentLinks(node)) return;
        pushText(node.textContent);
        return;
      }
      Array.prototype.forEach.call(node.childNodes, walk);
    };
    Array.prototype.forEach.call(box.childNodes, walk);
    return blocks;
  }

  function uniqueMediaBlocks(blocks) {
    var seen = {};
    return blocks.filter(function (block) {
      if (!block || (block.type !== "image" && block.type !== "video" && block.type !== "attachment")) return true;
      var key = block.type + ":" + (block.src || block.href || "");
      if ((!block.src && !block.href) || seen[key]) return false;
      seen[key] = true;
      return true;
    });
  }

  function loadPortalChrome() {
    if (PORTAL_HOME.schoolName) return Promise.resolve();
    return fetch("/api/display/project")
      .then(function (r) { return r.json(); })
      .then(function (payload) {
        var config = payload && payload.project && payload.project.displayConfig;
        if (!config) return;
        PORTAL_CHROME.navText = String(config.schoolMeta || PORTAL_CHROME.navText).trim();
        PORTAL_CHROME.logoImageUrl = FIXED_SCHOOL_LOGO_URL;
        PORTAL_CHROME.schoolQrImageUrl = FIXED_SCHOOL_QR_URL;
      })
      .catch(function () { /* 使用本地默认配置 */ });
  }

  function setText(selector, value) {
    var node = document.querySelector(selector);
    if (node && value) node.textContent = value;
  }

  function applyPortalHomeText() {
    setText(".portal-summary .portal-kicker", PORTAL_HOME.summaryKicker);
    setText(".portal-summary h2", PORTAL_HOME.summaryTitle);
    setText(".portal-summary p", PORTAL_HOME.summaryCopy);
    setText(".fusion-head .portal-kicker", PORTAL_HOME.sectionKicker);
    setText(".fusion-head .section-title", PORTAL_HOME.sectionTitle);
    setText(".fusion-head p", PORTAL_HOME.sectionCopy);
    setText(".statusline", PORTAL_HOME.footer);
    if (PORTAL_HOME.schoolName) {
      document.querySelectorAll(".school-name").forEach(function (node) { node.textContent = PORTAL_HOME.schoolName; });
    }
    if (PORTAL_HOME.schoolMeta) {
      document.querySelectorAll(".school-meta").forEach(function (node) { node.textContent = PORTAL_HOME.schoolMeta; });
    }
    var route = document.querySelector(".portal-route");
    if (route && PORTAL_HOME.routeLabels && PORTAL_HOME.routeLabels.length) {
      route.innerHTML = PORTAL_HOME.routeLabels.map(function (label) {
        return "<span>" + esc(label) + "</span>";
      }).join("");
    }
  }

  function applyPortalChrome() {
    document.querySelectorAll(".brand-logo").forEach(function (img) {
      img.addEventListener("error", function () {
        img.style.display = "none";
        if (img.nextElementSibling) img.nextElementSibling.removeAttribute("hidden");
      }, { once: true });
      if (!PORTAL_CHROME.logoImageUrl) return;
      img.src = PORTAL_CHROME.logoImageUrl;
    });
    document.querySelectorAll(".page-label").forEach(function (label) {
      label.textContent = PORTAL_CHROME.navText;
    });
    applyPortalHomeText();
  }

  function bindUnityStartLink() {
    document.addEventListener("click", function (event) {
      var link = event.target.closest(".unity-test-link[data-unity-start]");
      if (!link) return;
      event.preventDefault();
      var go = function (url) {
        window.location.assign(url);
      };
      fetch(link.dataset.unityStart, { cache: "no-store" })
        .then(function (response) { return response.ok ? response.json() : null; })
        .then(function (payload) { go((payload && payload.url) || link.href); })
        .catch(function () { go(link.href); });
    });
  }

  function renderSchoolQr(box) {
    if (!box) return;
    box.innerHTML = "";
    var img = document.createElement("img");
    img.alt = "学校官网二维码";
    img.onerror = function () {
      box.innerHTML = '<div class="qr-placeholder">学校官网<br>二维码</div>';
    };
    img.src = PORTAL_CHROME.schoolQrImageUrl;
    box.appendChild(img);
  }

  function initDepartmentSwitch() {
    var select = $("departmentSwitch");
    if (select) select.innerHTML = "";
    var homeSelect = $("homeDepartmentSwitch");
    if (!homeSelect) return;
    homeSelect.innerHTML = '<option value="">选择系部</option>';
    ORDER.departments.forEach(function (itemId) {
      var item = DATA.departments[itemId];
      if (!item) return;
      var opt = document.createElement("option");
      opt.value = itemId;
      opt.textContent = item.name;
      homeSelect.appendChild(opt);
    });
  }

  function syncDepartmentSwitch(kind, id) {
    var wrap = $("departmentSwitchWrap");
    var select = $("departmentSwitch");
    var label = $("departmentSwitchLabel");
    var homeSelect = $("homeDepartmentSwitch");
    if (homeSelect) homeSelect.value = kind === "departments" ? id : "";
    if (!wrap || !select) return;
    var isKnownPortal = kind === "departments" || kind === "topics";
    wrap.hidden = !isKnownPortal;
    if (!isKnownPortal) return;
    var list = kind === "departments" ? DATA.departments : DATA.topics;
    select.dataset.kind = kind;
    select.setAttribute("aria-label", kind === "departments" ? "切换系部" : "切换专题");
    if (label) label.textContent = kind === "departments" ? "切换系部" : "切换专题";
    select.innerHTML = "";
    ORDER[kind].forEach(function (itemId) {
      var item = list[itemId];
      if (!item) return;
      var opt = document.createElement("option");
      opt.value = itemId;
      opt.textContent = item.name;
      select.appendChild(opt);
    });
    select.value = id;
  }

  function allBlocks(data) {
    var out = [];
    (data.sections || []).forEach(function (sec) {
      (sec.blocks || []).forEach(function (b) {
        out.push(Object.assign({ sectionTitle: sec.title, sectionId: sec.id }, b));
      });
    });
    return out;
  }

  function cleanLeadText(text) {
    return String(text || "")
      .replace(/^系部简介[:：]\s*/g, "")
      .replace(/^旅游管理系简介[:：]\s*/g, "")
      .trim();
  }

  function isTitleOnlyText(text, data) {
    var t = cleanLeadText(text);
    if (!t) return true;
    if (t === data.name || t === data.name + "简介") return true;
    if (t.length <= 12 && /系$|系部$|简介$/.test(t)) return true;
    return false;
  }

  function getTextByKeyword(texts, keywords, fallbackIndex) {
    var found = texts.find(function (t) {
      return keywords.some(function (kw) { return t.indexOf(kw) >= 0; });
    });
    return found || texts[fallbackIndex] || texts[0] || "";
  }

  function clipText(text, limit) {
    text = cleanLeadText(text);
    if (text.length <= limit) return text;
    return text.slice(0, limit) + "…";
  }

  function displaySectionTitle(section) {
    if (state.kind === "topics") return TOPIC_SECTION_TITLES[section.id] || section.title;
    return section.title;
  }

  function normalizeContentType(value) {
    return CONTENT_TYPE_LABELS[value] ? value : "article";
  }

  function defaultContentTypeForSection(sectionId) {
    return TOPIC_DEFAULT_CONTENT_TYPES[sectionId] || "article";
  }

  function sectionsForPortal(kind, data) {
    var source = (data && data.sections) || [];
    if (kind !== "topics") return source;
    var byId = {};
    source.forEach(function (section) {
      if (section && section.id) byId[section.id] = section;
    });
    return TOPIC_SECTION_ORDER.map(function (id) {
      var existing = byId[id] || {};
      return Object.assign({
        id: id,
        title: TOPIC_SECTION_TITLES[id] || id,
        blocks: [],
        contentType: defaultContentTypeForSection(id),
        isTemplateSlot: true
      }, existing, {
        id: id,
        title: TOPIC_SECTION_TITLES[id] || existing.title || id,
        contentType: normalizeContentType(existing.contentType || defaultContentTypeForSection(id))
      });
    });
  }

  function setPortalDocumentTitle(label) {
    document.title = "毕节职业技术学院 · " + (label || "数字门户展厅");
  }

  function renderTopicIntro(section) {
    var data = getData();
    if (state.kind !== "topics" || !section || section.id !== "overview") return "";
    return '<section class="topic-intro-panel">' +
      '<span>专题导览</span>' +
      '<strong>' + esc(data.name || "专题展区") + '</strong>' +
      '<p>' + esc(data.summary || "围绕重点专业群、成果资源和展示素材组织专题内容。") + '</p>' +
      '</section>';
  }

  function isTopicNarrativeSection(section) {
    var id = section && section.id;
    return id === "overview" || id === "cooperation" || id === "achievements";
  }

  function normalizeTopicText(text, section) {
    var t = String(text || "").trim();
    if (state.kind !== "topics" || !isTopicNarrativeSection(section)) return t;

    var data = getData();
    var id = section && section.id;
    var topicName = data.name || "";
    var topicLabel = topicName ? topicName + "专题" : "本专题";

    if (id === "overview" && /^系部简介[:：]/.test(t)) {
      return "专题概况：" + (topicName || t.replace(/^系部简介[:：]\s*/, ""));
    }

    if (id === "overview") {
      t = t.replace(/^(工矿建筑系|财政经济系|旅游管理系)(?=于|从|2008|2010)/, "本专题依托$1建设，");
      t = t.replace(/^未来，旅游管理系将/, "未来，" + topicLabel + "将依托旅游管理系，");
    } else {
      t = t.replace(/^(工矿建筑系|财政经济系|旅游管理系)(?=立足|教学改革)/, topicLabel + "依托$1，");
    }

    return t
      .replace(/系部现有/g, "专题依托相关系部现有")
      .replace(/系部获/g, "专题相关成果获")
      .replace(/我系/g, "相关系部");
  }

  function normalizeTopicBlock(block, section) {
    if (state.kind !== "topics" || !block || block.type !== "text") return block;
    return Object.assign({}, block, { content: normalizeTopicText(block.content, section) });
  }

  function hasBackendCoverage(data) {
    return !!(data && data.backendModuleMap);
  }

  function moduleCoverageFor(data, moduleId) {
    return data && data.backendModuleMap ? data.backendModuleMap[moduleId] : null;
  }

  function moduleIsMissing(data, moduleId) {
    var coverage = moduleCoverageFor(data, moduleId);
    return hasBackendCoverage(data) && (!coverage || !coverage.covered);
  }

  function showcaseCard(moduleId, kicker, title, text, missing) {
    var full = esc(cleanLeadText(text));
    var status = missing ? "待补充" : "已维护";
    var body = missing ? "后台暂未维护该标准板块资料，补齐后将在此处展示。" : clipText(text, 58);
    var card = '<button class="showcase-card' + (missing ? " is-missing" : "") + '" type="button" data-module="' + esc(moduleId) + '" data-full="' + full + '">' +
      '<span class="showcase-kicker">' + esc(kicker) + '<em>' + esc(status) + '</em></span>' +
      '<strong>' + esc(title) + '</strong>' +
      '<p>' + esc(body) + '</p></button>';
    if (INLINE_EDIT.enabled) {
      return '<div class="showcase-card-wrap">' + card +
        '<button class="inline-edit-section-button inline-edit-control" type="button" data-section-edit="' + esc(moduleId) + '">编辑板块</button></div>';
    }
    return card;
  }

  function moduleTextFor(data, moduleId) {
    if (moduleIsMissing(data, moduleId)) return "";
    var blocks = allBlocks(data);
    var texts = blocks.filter(function (b) { return b.type === "text"; })
      .map(function (b) { return cleanLeadText(b.content); })
      .filter(function (t) { return !isTitleOnlyText(t, data); });
    if (moduleId === "overview") return texts[0] || data.summary || "";
    if (moduleId === "majors") return getTextByKeyword(texts, ["专业", "专业群", "课程"], 1);
    if (moduleId === "training") return getTextByKeyword(texts, ["实训", "基地", "实践"], 2);
    if (moduleId === "cooperation") return getTextByKeyword(texts, ["校企", "产教", "合作", "订单"], 3);
    if (moduleId === "achievements") return getTextByKeyword(texts, ["成果", "竞赛", "获奖", "荣誉", "就业", "升本"], 4);
    if (moduleId === "media") return "可接入宣传片、专业介绍视频、实训基地视频或学生作品视频。";
    if (moduleId === "systems") return "特色系统入口用于承接系部业务平台、训练系统、互动系统或外部专题入口。";
    if (moduleId === "resources") return "特色数字资源用于聚合专题内容、数字素材、课程资源和扫码访问资料。";
    return "";
  }

  function renderTopicActionButtons() {
    return '<div class="module-actions">' + ORDER.topics.map(function (topicId) {
      var topic = DATA.topics[topicId];
      if (!topic) return "";
      return '<button type="button" data-go-kind="topics" data-go-id="' + esc(topicId) + '">' +
        esc(topic.name) + '专题</button>';
    }).join("") + '</div>';
  }

  function departmentIdForName(name) {
    for (var i = 0; i < ORDER.departments.length; i += 1) {
      var id = ORDER.departments[i];
      var department = DATA.departments[id];
      if (department && department.name === name) return id;
    }
    return "";
  }

  function openDepartmentModule(moduleId) {
    var data = getData();
    var meta = MODULE_META[moduleId] || ["板块详情", ""];
    var images = allBlocks(data).filter(function (b) { return b.type === "image" && b.src; }).slice(0, 8);
    var videos = allBlocks(data).filter(function (b) { return b.type === "video" && b.src; }).slice(0, 3);
    var missing = moduleIsMissing(data, moduleId);
    var text = moduleTextFor(data, moduleId);
    var topicLinks = moduleId === "systems" || moduleId === "resources"
      ? renderTopicActionButtons() : "";
    var videoDetailHtml = moduleId === "media" && videos.length ? '<div class="module-video-list">' + videos.map(function (video) {
      return renderVideo(video);
    }).join("") + '</div>' : "";
    var photoHtml = images.length ? '<div class="module-photo-grid">' + images.map(function (img) {
      return '<figure class="photo-frame" tabindex="0" data-lightbox="' + esc(img.src) + '" data-caption="' + esc(img.caption || data.name) + '">' +
        '<img src="' + esc(img.src) + '" alt="' + esc(img.caption || data.name) + '" loading="lazy"></figure>';
    }).join("") + '</div>' : "";
    openDrawer('<article class="module-detail">' +
      '<p class="module-eyebrow">' + esc(data.name) + '</p>' +
      '<h2>' + esc(meta[0]) + '</h2>' +
      '<p class="module-intro">' + esc(meta[1]) + '</p>' +
      '<div class="module-copy">' + esc(text || "该板块资料待补充。") + '</div>' +
      topicLinks +
      (missing ? "" : videoDetailHtml + photoHtml) +
      '</article>');
  }

  function renderDepartmentShowcase(data) {
    var blocks = allBlocks(data);
    var texts = blocks.filter(function (b) { return b.type === "text"; })
      .map(function (b) { return cleanLeadText(b.content); })
      .filter(function (t) { return !isTitleOnlyText(t, data); });
    var images = blocks.filter(function (b) { return b.type === "image" && b.src; });
    var videos = blocks.filter(function (b) { return b.type === "video" && b.src; });
    var stats = data.stats || [];
    var overview = texts[0] || data.summary || DEPT_SUMMARY[data.id] || "";
    var majors = getTextByKeyword(texts, ["专业", "专业群", "课程"], 1);
    var training = getTextByKeyword(texts, ["实训", "基地", "实践"], 2);
    var cooperation = getTextByKeyword(texts, ["校企", "产教", "合作", "订单"], 3);
    var achievements = getTextByKeyword(texts, ["成果", "竞赛", "获奖", "荣誉", "就业", "升本"], 4);
    var hero = images[0] || { src: data.cover || "", caption: data.name };
    var gallery = images.slice(1, 9);

    var statHtml = stats.length ? '<div class="showcase-stat-row">' + stats.slice(0, 5).map(function (s) {
      return '<div class="showcase-stat"><b>' + esc(s.value) + '</b><span>' + esc(s.label) + '</span></div>';
    }).join("") + '</div>' : "";

    var galleryHtml = gallery.length ? '<div class="showcase-thumbs" style="--thumb-count:' + gallery.length + '">' + gallery.map(function (img) {
      return '<figure class="showcase-thumb photo-frame" tabindex="0" data-lightbox="' + esc(img.src) + '" data-caption="' + esc(img.caption || data.name) + '">' +
        '<img src="' + esc(img.src) + '" alt="' + esc(img.caption || data.name) + '" loading="lazy"></figure>';
    }).join("") + '</div>' : "";

    var videoHtml;
    if (videos.length) {
      videoHtml = '<div class="showcase-video-wrap">' + renderVideo(videos[0]) + '</div>';
    } else {
      videoHtml = '<div class="showcase-video-empty">' +
        '<span class="showcase-play" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M8 5.5v13l10-6.5-10-6.5z" fill="currentColor"/></svg></span>' +
        '<div><h3>系部宣传片待接入</h3><p>可接入宣传片、专业介绍视频、实训基地视频或学生作品视频。</p></div></div>';
    }

    var moduleHtml = MODULE_SEQUENCE.map(function (item) {
      return showcaseCard(item[0], item[1], item[2], moduleTextFor(data, item[0]), moduleIsMissing(data, item[0]));
    }).join("");
    var homestayModelHtml = data.id === "tourism"
      ? '<a class="homestay-model-card" href="/model/homestay">' +
        '<span>3D Model</span><strong>民宿三维模型</strong><p>启动民宿场景建模窗口</p></a>'
      : "";

    return '<section class="showcase-board" aria-label="' + esc(data.name) + '展示页面">' +
      '<header class="showcase-hero">' +
      '<div class="showcase-identity"><div><span class="showcase-label">Department Showcase</span>' +
      '<h2>' + esc(data.name) + '</h2><p>' + esc(data.summary || DEPT_SUMMARY[data.id] || "系部门户") + '</p></div>' +
      '<div class="showcase-dept-name">' + esc(data.name) + '</div></div>' +
      statHtml +
      '</header>' +
      '<div class="showcase-grid">' +
      '<article class="showcase-panel modules-panel"><div class="showcase-panel-head"><h3>系部板块导航</h3><span>8 个标准板块</span></div>' +
      '<p class="module-map-intro">' + esc(clipText(overview || data.summary, 78)) + '</p>' +
      homestayModelHtml + '<div class="showcase-module-grid">' + moduleHtml + '</div></article>' +
      '<article class="showcase-panel teaching-panel"><div class="showcase-panel-head"><h3>图像资料</h3><span>代表场景</span></div>' +
      '<figure class="showcase-media photo-frame" tabindex="0" data-lightbox="' + esc(hero.src) + '" data-caption="' + esc(hero.caption || data.name) + '">' +
      (hero.src ? '<img src="' + esc(hero.src) + '" alt="' + esc(hero.caption || data.name) + '" loading="lazy">' : '<div class="showcase-slot">图片待放置</div>') +
      '<figcaption><h4>' + esc(hero.caption || "教学成果展示区") + '</h4><p>' + esc(clipText(achievements || overview, 68)) + '</p></figcaption></figure>' +
      galleryHtml + '</article>' +
      '<article class="showcase-panel video-panel"><div class="showcase-panel-head"><h3>视频资源</h3><span>播放区</span></div>' +
      videoHtml + '</article>' +
      '</div></section>';
  }

  function firstSectionById(data, id) {
    return ((data && data.sections) || []).find(function (section) {
      return section && section.id === id;
    }) || null;
  }

  function sectionBlocks(data, id) {
    var section = firstSectionById(data, id);
    return section ? (section.blocks || []) : [];
  }

  function sectionTexts(data, id) {
    return sectionBlocks(data, id).filter(function (b) {
      return b.type === "text" && String(b.content || "").trim();
    }).map(function (b) {
      return cleanLeadText(b.content);
    }).filter(function (text) {
      return !isTitleOnlyText(text, data);
    });
  }

  function sectionImages(data, id) {
    return sectionBlocks(data, id).filter(function (b) {
      return b.type === "image" && b.src;
    });
  }

  function compactParagraph(text, limit) {
    return esc(clipText(text || "", limit || 86));
  }

  function topicPhotoFigure(image, fallback, className) {
    var src = (image && image.src) || fallback || "";
    var caption = (image && image.caption) || "";
    return '<figure class="topic-showcase-photo photo-frame ' + esc(className || "") + '" tabindex="0" data-lightbox="' + esc(src) + '" data-caption="' + esc(caption) + '">' +
      (src ? '<img src="' + esc(src) + '" alt="' + esc(caption || "专题图片") + '" loading="lazy">' : '<div class="showcase-slot">图片待放置</div>') +
      '</figure>';
  }

  function topicPanelTitle(title, note) {
    return '<div class="topic-showcase-panel-head">' +
      '<h3><span aria-hidden="true"></span>' + esc(title) + '</h3>' +
      '<em>' + esc(note || "") + '</em>' +
      '</div>';
  }

  /* ---------- coverflow 轮播(与 /display 页面一致) ---------- */
  function coverflowImageUrl(src) {
    return "url('" + String(src || "").replace(/\\/g, "%5C").replace(/'/g, "%27") + "')";
  }

  function renderTopicCoverflowCarousel(items, options) {
    options = options || {};
    var fallbackImage = options.fallbackImage || "";
    var list = items && items.length ? items : [{ title: options.title || "", body: "", imageUrl: fallbackImage }];
    var slides = list.map(function (item, index) {
      var src = item.imageUrl || fallbackImage;
      var editBtn = INLINE_EDIT.enabled && item.sectionId
        ? '<button type="button" class="inline-edit-media-button inline-edit-control" data-coverflow-edit="' + esc(item.sectionId) + '" aria-label="更换图片">换图</button>'
        : "";
      return '<article class="topic-coverflow-slide' + (index === 0 ? " is-active" : "") + (item.video ? " is-video" : "") + '"' +
        ' style="--slide-image: ' + coverflowImageUrl(src) + '"' +
        (item.sectionId ? ' data-section-id="' + esc(item.sectionId) + '"' : "") +
        (item.lightbox ? ' data-lightbox="' + esc(item.lightbox) + '" data-caption="' + esc(item.caption || "") + '"' : "") +
        '>' +
        (item.video ? '<span class="topic-coverflow-play" aria-hidden="true"></span>' : "") +
        '<p class="topic-coverflow-caption">' + esc(item.caption || "SHOWCASE " + String(index + 1).padStart(2, "0")) + '</p>' +
        '<h3>' + esc(item.title || "") + '</h3>' +
        '<p class="topic-coverflow-copy">' + esc(item.body || "") + '</p>' +
        editBtn +
        '</article>';
    }).join("");
    var dots = list.map(function (item, index) {
      return '<button type="button" class="topic-coverflow-dot' + (index === 0 ? " is-active" : "") + '" aria-label="切换到第 ' + (index + 1) + ' 张"></button>';
    }).join("");
    return '<div class="topic-coverflow" data-topic-coverflow data-count="' + list.length + '">' +
      '<div class="topic-coverflow-stage">' + slides + '</div>' +
      (list.length > 1 ? '<div class="topic-coverflow-dots">' + dots + '</div>' : "") +
      (list.length > 1 ? '<div class="topic-coverflow-controls"><button type="button" class="topic-coverflow-prev" aria-label="上一张">‹</button><button type="button" class="topic-coverflow-next" aria-label="下一张">›</button></div>' : "") +
      '</div>';
  }

  function startTopicCoverflowCarousels(root) {
    stopTopicCoverflowCarousels();
    if (!root) return;
    root.querySelectorAll("[data-topic-coverflow]").forEach(function (carousel) {
      var slides = Array.prototype.slice.call(carousel.querySelectorAll(".topic-coverflow-slide"));
      var dots = Array.prototype.slice.call(carousel.querySelectorAll(".topic-coverflow-dot"));
      if (slides.length <= 1) return;
      var active = 0;
      var wrapIndex = function (index) {
        return (index + slides.length) % slides.length;
      };
      var shortestOffset = function (index, current) {
        var offset = index - current;
        var half = slides.length / 2;
        if (offset > half) offset -= slides.length;
        if (offset < -half) offset += slides.length;
        return offset;
      };
      var showSlide = function (index) {
        active = wrapIndex(index);
        slides.forEach(function (slide, idx) {
          var offset = shortestOffset(idx, active);
          var abs = Math.abs(offset);
          var x = offset * 210;
          var rotateY = offset * -46;
          var depth = abs * -116;
          var scale = idx === active ? 1.04 : Math.max(0.76, 1 - abs * 0.16);
          slide.classList.toggle("is-active", idx === active);
          slide.style.zIndex = String(10 - abs);
          slide.style.opacity = abs > 1.5 ? "0" : "1";
          slide.style.pointerEvents = abs > 1.5 ? "none" : "auto";
          slide.style.transform = "translate3d(calc(-50% + " + x + "px), 0, " + depth + "px) rotateY(" + rotateY + "deg) scale(" + scale + ")";
        });
        dots.forEach(function (dot, idx) {
          dot.classList.toggle("is-active", idx === active);
        });
      };
      var timer = 0;
      var restart = function () {
        window.clearTimeout(timer);
        if (slides.length > 1) {
          timer = window.setTimeout(function () {
            showSlide(active + 1);
            restart();
          }, 4200);
        }
        topicCoverflowTimers.push(timer);
      };
      slides.forEach(function (slide, idx) {
        slide.addEventListener("click", function (e) {
          e.stopPropagation();
          if (slide.dataset.sectionId) {
            openTopicLoopSection(slide.dataset.sectionId);
            return;
          }
          if (idx !== active) {
            showSlide(idx);
            restart();
            return;
          }
          if (slide.dataset.lightbox) openLightbox(slide.dataset.lightbox, slide.dataset.caption || "");
        });
      });
      dots.forEach(function (dot, idx) {
        dot.addEventListener("click", function (e) {
          e.stopPropagation();
          showSlide(idx);
          restart();
        });
      });
      var prev = carousel.querySelector(".topic-coverflow-prev");
      var next = carousel.querySelector(".topic-coverflow-next");
      if (prev) prev.addEventListener("click", function (e) { e.stopPropagation(); showSlide(active - 1); restart(); });
      if (next) next.addEventListener("click", function (e) { e.stopPropagation(); showSlide(active + 1); restart(); });
      showSlide(0);
      restart();
    });
  }

  function stopTopicCoverflowCarousels() {
    topicCoverflowTimers.forEach(function (timer) { window.clearTimeout(timer); });
    topicCoverflowTimers.length = 0;
  }

  var TOPIC_SHOWCASE = {
    "modern-agriculture": {
      slogan: "现代山地特色高效农业 · 产教融合 · 数字赋能 · 乡村振兴",
      basic: [["山地农业概况", "overview"], ["专业群建设", "majors"], ["实训基地", "training"]],
      coop: [["校企合作项目", "cooperation"], ["产教融合成果", "achievements"]],
      story: [["课程成果", "masters"], ["学生项目", "students"], ["技能竞赛", "competitions"], ["乡村服务", "honors"]],
      video: "现代山地特色高效农业宣传片"
    },
    "digital-tourism": {
      slogan: "数字文旅 · 智慧酒店 · 烹饪技艺 · 服务地方",
      basic: [["数字文旅概况", "overview"], ["专业群建设", "majors"], ["实训基地", "training"]],
      coop: [["校企合作项目", "cooperation"], ["产教融合成果", "achievements"]],
      story: [["课程成果", "masters"], ["学生项目", "students"], ["技能竞赛", "competitions"], ["荣誉资质", "honors"]],
      video: "数字文旅专题宣传片"
    },
    "smart-healthcare": {
      slogan: "智慧康养 · 护理急救 · 健康管理 · 产教融合",
      basic: [["智慧康养概况", "overview"], ["专业群建设", "majors"], ["实训基地", "training"]],
      coop: [["校企合作项目", "cooperation"], ["产教融合成果", "achievements"]],
      story: [["课程成果", "masters"], ["学生项目", "students"], ["技能竞赛", "competitions"], ["荣誉资质", "honors"]],
      video: "智慧康养专题宣传片"
    },
    "smart-energy": {
      slogan: "绿色能源 · 智能开采 · 化工安全 · 数字赋能",
      basic: [["智慧能源概况", "overview"], ["专业群建设", "majors"], ["实训基地", "training"]],
      coop: [["校企合作项目", "cooperation"], ["产教融合成果", "achievements"]],
      story: [["课程成果", "masters"], ["学生项目", "students"], ["技能竞赛", "competitions"], ["荣誉资质", "honors"]],
      video: "智慧能源专题宣传片"
    },
    "smart-manufacturing": {
      slogan: "智能装备 · 新能源汽车 · 无人机应用 · 产教融合",
      basic: [["智能制造概况", "overview"], ["专业群建设", "majors"], ["实训基地", "training"]],
      coop: [["校企合作项目", "cooperation"], ["产教融合成果", "achievements"]],
      story: [["课程成果", "masters"], ["学生项目", "students"], ["技能竞赛", "competitions"], ["荣誉资质", "honors"]],
      video: "智能制造专题宣传片"
    },
    "finance-commerce": {
      slogan: "数字商贸 · 智慧物流 · 财务实践 · 产教融合",
      basic: [["财经商贸概况", "overview"], ["专业群建设", "majors"], ["实训基地", "training"]],
      coop: [["校企合作项目", "cooperation"], ["产教融合成果", "achievements"]],
      story: [["课程成果", "masters"], ["学生项目", "students"], ["技能竞赛", "competitions"], ["荣誉资质", "honors"]],
      video: "财经商贸专题宣传片"
    },
    "digital-intelligence": {
      slogan: "人工智能 · 网络安全 · 数据应用 · 跨专业赋能",
      basic: [["数智赋能概况", "overview"], ["专业群建设", "majors"], ["实训基地", "training"]],
      coop: [["校企合作项目", "cooperation"], ["产教融合成果", "achievements"]],
      story: [["课程成果", "masters"], ["学生项目", "students"], ["技能竞赛", "competitions"], ["荣誉资质", "honors"]],
      video: "数智赋能专题宣传片"
    },
    "campus-culture": {
      slogan: "同心育人 · 校园文化 · 学生成长 · 服务地方",
      basic: [["校园文化概况", "overview"], ["专业群建设", "majors"], ["实训基地", "training"]],
      coop: [["校企合作项目", "cooperation"], ["产教融合成果", "achievements"]],
      story: [["课程成果", "masters"], ["学生项目", "students"], ["技能竞赛", "competitions"], ["荣誉资质", "honors"]],
      video: "校园文化专题宣传片"
    }
  };
  function topicShowcaseConfig(id) {
    var cfg = TOPIC_SHOWCASE[id] || {};
    return {
      slogan: cfg.slogan || (TOPIC_SUMMARY[id] || "产教融合 · 数字赋能 · 服务地方"),
      basic: cfg.basic || [
        ["专题概况", "overview"],
        ["专业群布局", "majors"],
        ["实训场景", "training"]
      ],
      coop: cfg.coop || [
        ["校企合作项目", "cooperation"],
        ["专题成果", "achievements"]
      ],
      story: cfg.story || [
        ["名师名匠", "masters"],
        ["优秀学生", "students"],
        ["技能大赛", "competitions"],
        ["荣誉资质", "honors"]
      ],
      video: cfg.video || ""
    };
  }

  function renderTopicShowcaseOverview(data) {
    var id = data.id || "";
    var cfg = topicShowcaseConfig(id);
    var editMode = INLINE_EDIT.enabled;
    var overviewTexts = sectionTexts(data, "overview");
    var majorTexts = sectionTexts(data, "majors");
    var trainingTexts = sectionTexts(data, "training");
    var cooperationTexts = sectionTexts(data, "cooperation");
    var achievementTexts = sectionTexts(data, "achievements");
    var basicCards = cfg.basic.map(function (item, index) {
      var text = item[0], secId = item[1];
      var textForCard = secId === "overview"
        ? (overviewTexts[0] || data.summary)
        : secId === "majors"
          ? (majorTexts[0] || majorTexts[1] || overviewTexts[1])
          : (trainingTexts[0] || trainingTexts[1] || overviewTexts[2]);
      var img = sectionImages(data, secId)[0] || null;
      var cardTextBlock = sectionTextBlocks(data, secId)[0] || null;
      var cardText = INLINE_EDIT.enabled && cardTextBlock ? cardTextBlock.content : compactParagraph(textForCard, 96);
      return '<section class="topic-showcase-mini" data-section-id="' + esc(secId) + '" tabindex="0" role="button" aria-label="查看' + esc(text) + '完整资料">' +
        '<strong>' + esc(text) + '</strong>' +
        topicPhotoFigure(img, "", "photo-" + index) +
        '<p data-block-text-idx="0">' + esc(cardText) + '</p>' +
        '</section>';
    }).join("");
    var storyItems = cfg.story.map(function (item, index) {
      var title = item[0], secId = item[1];
      var textForStory = secId === "masters"
        ? (majorTexts[2] || majorTexts[0])
        : secId === "students"
          ? (trainingTexts[2] || trainingTexts[0])
          : secId === "competitions"
            ? (achievementTexts[0] || achievementTexts[1])
            : (cooperationTexts[0] || cooperationTexts[1]);
      var img = sectionImages(data, secId)[0] || null;
      var src = (img && img.src) || "";
      return {
        title: title,
        body: clipText(textForStory || "", 62),
        imageUrl: src,
        caption: (img && img.caption) || title,
        lightbox: src,
        sectionId: secId
      };
    });
    var achievementCarousel = renderTopicCoverflowCarousel(storyItems, { fallbackImage: "", title: "教学与创新成果" });
    var mediaImages = sectionImages(data, "media");
    var mediaSection = firstSectionById(data, "media");
    var mediaVideo = null;
    if (mediaSection) {
      mediaVideo = (mediaSection.blocks || []).find(function (b) { return b.type === "video" && (b.src || b.poster); }) || null;
    }
    var videoPoster = mediaImages[0] || null;
    var videoPosterSrc = (videoPoster && videoPoster.src) || "";
    var videoTitle = cfg.video || (data.name + "宣传片");
    var videoHtml;
    if (mediaVideo) {
      videoHtml = '<div class="topic-showcase-video-box topic-showcase-video-real" data-section-id="media">' +
        renderVideo(mediaVideo) +
        (editMode ? '<button type="button" class="inline-edit-media-button inline-edit-control topic-showcase-video-upload" data-upload-video="media">更换视频</button>' : "") +
        '</div>';
    } else if (videoPosterSrc) {
      videoHtml = '<div class="topic-showcase-video-box photo-frame" data-section-id="media" tabindex="0" role="button" aria-label="查看视频资源完整资料" data-lightbox="' + esc(videoPosterSrc) + '" data-caption="' + esc((videoPoster && videoPoster.caption) || data.name) + '">' +
        '<img src="' + esc(videoPosterSrc) + '" alt="' + esc((videoPoster && videoPoster.caption) || data.name) + '" loading="lazy">' +
        '<span class="topic-showcase-play" aria-hidden="true"></span><div class="topic-showcase-controls" aria-hidden="true"><span></span><em>00:00 / 03:45</em><i></i><em>全屏</em></div>' +
        (editMode ? '<button type="button" class="inline-edit-media-button inline-edit-control topic-showcase-video-upload" data-upload-video="media">上传视频</button>' : "") +
        '</div>';
    } else {
      videoHtml = '<div class="topic-showcase-video-box topic-showcase-video-empty" data-section-id="media">' +
        '<span class="topic-showcase-coop-empty">' + (editMode ? "点击下方按钮上传视频（mp4 / webm）" : "视频资源待上传") + '</span>' +
        (editMode ? '<button type="button" class="inline-edit-media-button inline-edit-control topic-showcase-video-upload" data-upload-video="media">上传视频</button>' : "") +
        '</div>';
    }
    return '<section class="topic-showcase-page" aria-label="' + esc(data.name) + '专题展示页" style="--topic-bg-image:url(\'/static/blueprint/' + esc(id) + '-bg.png\')">' +
      '<header class="topic-showcase-header">' +
      '<div class="topic-showcase-brand topic-only-brand">' +
      '<div class="topic-showcase-title-kicker">TOPIC SHOWCASE <span>/ 专题展区</span></div>' +
      '<div class="topic-showcase-title-row"><strong>' + esc(data.name || "专题") + '</strong></div>' +
      '<p>' + esc(cfg.slogan) + '</p></div>' +
      '</header>' +
      '<div class="topic-showcase-content">' +
      '<article class="topic-showcase-panel topic-showcase-basic">' + topicPanelTitle("基本情况", "专题概览") +
      '<div class="topic-showcase-basic-grid">' + basicCards + '</div></article>' +
      '<article class="topic-showcase-panel topic-showcase-coop">' + topicPanelTitle("产教融合校企合作成果", "合作展示") +
      renderTopicCoopPanel(data, cooperationTexts) + '</article>' +
      '<article class="topic-showcase-panel topic-showcase-achievement">' + topicPanelTitle("教学与创新成果", "轮播图") + achievementCarousel + '</article>' +
      '<article class="topic-showcase-panel topic-showcase-video">' +
      '<div class="topic-showcase-panel-head"><h3><span aria-hidden="true"></span>视频资源</h3>' +
      '<em data-video-more="1" role="button" tabindex="0" aria-label="查看全部视频">更多</em></div>' +
      videoHtml +
      '<div class="topic-showcase-video-copy"><strong>' + esc(videoTitle) + '</strong><p>' + compactParagraph(data.summary || overviewTexts[0], 94) + '</p></div></article>' +
      '</div>' +
      renderTopicExperienceActions(data) +
      '<div class="topic-showcase-pager" aria-label="分页"><button type="button" aria-label="上一页">‹</button><span>1&nbsp;&nbsp;/&nbsp;&nbsp;1</span><button type="button" aria-label="下一页">›</button><em>刷新 ↻</em></div>' +
      '</section>';
  }

  /* ---------- 产教融合校企合作成果（简洁数据驱动） ---------- */
  function renderTopicCoopPanel(data, cooperationTexts) {
    var editMode = INLINE_EDIT.enabled;
    var coopSection = firstSectionById(data, "cooperation") || {};
    var coopImages = sectionImages(data, "cooperation");
    var coopImg = coopImages[0] || null;
    var title = String(coopSection.title || "").trim();
    var bodyBlocks = (coopSection.blocks || []).filter(function (b) {
      return b.type === "text" && String(b.content || "").trim();
    });
    var bodyTexts = bodyBlocks.map(function (b) { return String(b.content || "").trim(); });
    var photoHtml = coopImg && coopImg.src
      ? '<img src="' + esc(coopImg.src) + '" alt="' + esc(coopImg.caption || "产教融合合作场景") + '" loading="lazy">'
      : '<span class="topic-showcase-coop-empty">' + (editMode ? "点击换图补充合作场景图" : "合作场景图待补充") + '</span>';
    var titleHtml = title
      ? esc(title)
      : '<span class="topic-showcase-coop-empty">' + (editMode ? "输入合作成果标题…" : "合作成果标题待补充") + '</span>';
    var bodyHtml = bodyTexts.length
      ? bodyTexts.map(function (t) { return "<p>" + esc(t) + "</p>"; }).join("")
      : '<p class="topic-showcase-coop-empty">' + (editMode ? "输入合作成果正文…" : "合作成果正文待补充") + '</p>';
    return '<div class="topic-showcase-coop-layout" data-coop-section="cooperation" data-coop-enter="1">' +
      '<figure class="topic-showcase-coop-photo photo-frame">' + photoHtml + '</figure>' +
      '<div class="topic-showcase-coop-info">' +
      '<div class="topic-showcase-coop-title">' + titleHtml + '</div>' +
      '<div class="topic-showcase-coop-body">' + bodyHtml + '</div>' +
      (editMode
        ? '<div class="topic-showcase-coop-manage-row"><button type="button" class="topic-showcase-coop-manage" data-coop-enter="1">管理项目 ›</button></div>'
        : '<div class="topic-showcase-coop-enter">点击进入详情管理 ›</div>') +
      '</div></div>';
  }

  /* ---------- 一级页 ---------- */
  function renderHome() {
    setPortalDocumentTitle("学校门户");
    document.body.dataset.portalKind = "home";
    document.body.dataset.topic = "";
    var grid = $("fusionGrid");
    grid.innerHTML = "";
    var cards = HOME_CARDS.length ? HOME_CARDS.filter(function (card) { return !card.hidden; }) : ORDER.topics.map(function (id) {
      return { kind: "topics", id: id };
    });
    cards.forEach(function (cardConfig) {
      var kind = cardConfig.kind === "departments" ? "departments" : "topics";
      var id = cardConfig.id;
      var t = (kind === "departments" ? DATA.departments : DATA.topics)[id];
      if (!t) return;
      var card = t.homeCard || cardConfig || {};
      var article = document.createElement("article");
      article.className = "fusion-card";
      article.tabIndex = 0;
      article.setAttribute("role", "button");
      article.setAttribute("aria-label", "进入" + t.name + "专题页");
      if (card.projectId) article.dataset.editProjectId = card.projectId;
      article.dataset.editSlug = id;
      article.innerHTML =
        '<img class="fusion-photo" src="' + esc(card.cover || t.cover) + '" alt="" loading="lazy">' +
        '<div class="fusion-shade"></div>' +
        '<div class="fusion-copy">' +
        '<span class="fusion-label">' + esc(card.label || "创新育人专题") + '</span>' +
        '<h3>' + esc(t.name) + '</h3>' +
        '<p>' + esc(card.summary || TOPIC_SUMMARY[id] || t.summary) + '</p>' +
        '<div class="fusion-depts" hidden></div>' +
        '</div>' +
        '<span class="fusion-arrow" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></span>';
      var go = function () { openDetail(kind, id, 0); };
      article.addEventListener("click", function (e) {
        // 编辑模式下仅拦截编辑字段/控件点击；卡片空白处仍可进入专题页
        if (INLINE_EDIT.enabled && e.target.closest("[data-inline-edit-field], .inline-edit-control")) return;
        if (e.target.closest(".dept-chip")) return;
        go();
      });
      article.addEventListener("keydown", function (e) {
        if (INLINE_EDIT.enabled) return;
        if (e.key === "Enter" || e.key === " ") { e.preventDefault(); go(); }
      });
      Array.prototype.forEach.call(article.querySelectorAll(".dept-chip"), function (chip) {
        chip.addEventListener("click", function (e) {
          e.stopPropagation();
          openDetail(chip.dataset.goKind || "departments", chip.dataset.goId, 0);
        });
      });
      var photo = article.querySelector(".fusion-photo");
      if (photo) photo.addEventListener("error", function () { photo.style.display = "none"; }, { once: true });
      grid.appendChild(article);
    });
    activateInlineEditIfNeeded();
    prepareAdaptiveMedia(screenHome);

    screenDetail.hidden = true;
    screenHome.hidden = false;
    screenHome.classList.remove("show");
    void screenHome.offsetWidth;
    screenHome.classList.add("show");
    if (location.pathname !== "/departments" && !/^\/(departments|topics)/.test(location.pathname)) {
      history.replaceState(null, "", "/departments");
    }
  }

  /* ---------- 二级页 ---------- */
  function openDetail(kind, id, section, options) {
    options = options || {};
    var d = (kind === "departments" ? DATA.departments : DATA.topics)[id];
    if (!d) return;
    setPortalDocumentTitle((kind === "departments" ? "系部门户 · " : "专题门户 · ") + d.name);
    state.kind = kind; state.id = id; state.sections = sectionsForPortal(kind, d);
    state.section = Math.max(0, Math.min(section, state.sections.length - 1));
    document.body.dataset.portalKind = kind;
    document.body.dataset.topic = kind === "topics" ? id : "";
    screenDetail.classList.toggle("department-showcase-mode", kind === "departments");
    screenDetail.classList.toggle("topic-loop-mode", kind === "topics");
    screenDetail.dataset.topic = kind === "topics" ? id : "";
    setTopicLoopPaused(false);
    syncDepartmentSwitch(kind, id);

    $("detailMeta").textContent = d.name;
    $("backHomeText").textContent = "返回学校门户";
    var nav = $("chapterNav");
    nav.innerHTML = "";
    state.sections.forEach(function (s, i) {
      var btn = document.createElement("button");
      btn.className = "chapter-tab" + (i === state.section ? " active" : "");
      btn.textContent = displaySectionTitle(s);
      btn.tabIndex = 0;
      btn.addEventListener("click", function () { goSection(i); });
      nav.appendChild(btn);
    });
    if (!options.skipHistory) {
      if (options.replaceHistory) history.replaceState(null, "", urlFor(kind, id, state.section));
      else history.pushState(null, "", urlFor(kind, id, state.section));
    }
    screenHome.hidden = true;
    screenDetail.hidden = false;
    if (kind === "departments") renderDepartmentDetail();
    else renderChapter(false);
    resetIdle();
  }

  function goSection(i, options) {
    options = options || {};
    if (i === state.section) return;
    var backward = i < state.section;
    state.section = i;
    document.querySelectorAll(".chapter-tab").forEach(function (b, k) {
      b.classList.toggle("active", k === i);
    });
    if (!options.skipHistory) {
      if (options.replaceHistory) history.replaceState(null, "", urlFor(state.kind, state.id, i));
      else history.pushState(null, "", urlFor(state.kind, state.id, i));
    }
    if (state.kind === "departments") {
      renderDepartmentDetail();
      resetIdle();
      return;
    }
    renderChapter(backward);
    resetIdle();
  }

  function renderChapter(backward) {
    var sec = state.sections[state.section];
    if (!sec) return;
    var data = getData();
    var page = $("chapterPage");
    stopTopicMediaCarousels();
    stopTopicCoverflowCarousels();
    page.style.animation = "none";
    void page.offsetWidth;
    page.style.animation = "";

    var isTopicShowcaseOverview = state.kind === "topics" && sec.id === "overview";
    screenDetail.classList.toggle("modern-agriculture-showcase-mode", isTopicShowcaseOverview);
    screenDetail.classList.toggle("topic-loop-mode", state.kind === "topics" && !isTopicShowcaseOverview);
    page.innerHTML = isTopicShowcaseOverview ? renderTopicShowcaseOverview(data) : renderTopicLoopPage(data);
    if (isTopicShowcaseOverview) {
      prepareAdaptiveMedia(page);
      startTopicCoverflowCarousels(page);
      $("progressLabel").textContent = "01 / 01";
      $("prevChapter").disabled = true;
      $("nextChapter").disabled = true;
      applyInlineDetailControls();
      return;
    }
    startTopicMediaCarousels(page);
    startTopicCoverflowCarousels(page);
    prepareAdaptiveMedia(page, function () { prepareTopicLoop(page); });
    $("progressLabel").textContent =
      String(state.section + 1).padStart(2, "0") + " / " +
      String(state.sections.length).padStart(2, "0");
    $("prevChapter").disabled = state.section === 0;
    $("nextChapter").disabled = state.section === state.sections.length - 1;
    prepareTopicLoop(page);
    applyInlineDetailControls();
  }

  function renderDepartmentDetail() {
    var data = getData();
    var page = $("chapterPage");
    stopTopicMediaCarousels();
    stopTopicCoverflowCarousels();
    page.style.animation = "none";
    void page.offsetWidth;
    page.style.animation = "";
    screenDetail.classList.remove("topic-loop-mode");
    screenDetail.classList.remove("modern-agriculture-showcase-mode");
    page.innerHTML = renderDepartmentShowcase(data);
    prepareAdaptiveMedia(page);
    $("progressLabel").textContent = "";
    $("prevChapter").disabled = true;
    $("nextChapter").disabled = true;
    applyInlineDetailControls();
  }

  function getData() {
    return (state.kind === "departments" ? DATA.departments : DATA.topics)[state.id] || {};
  }

  function orderedTopicSections() {
    var sections = state.sections || [];
    if (!sections.length) return [];
    return sections.slice(state.section).concat(sections.slice(0, state.section));
  }

  function topicSectionModel(section) {
    var blocks = (section.blocks || []).map(function (sourceBlock) {
      return normalizeTopicBlock(sourceBlock, section);
    });
    var mediaBlocks = blocks.filter(function (b) {
      return (b.type === "image" && b.src) || (b.type === "video" && (b.poster || b.src));
    });
    var allTextBlocks = (section.blocks || []).filter(function (b) {
      return b.type === "text";
    });
    var textBlocks = allTextBlocks.filter(function (b) {
      return String(b.content || "").trim();
    });
    var texts = textBlocks.map(function (b) { return String(b.content || "").trim(); });
    var first = texts[0] || "";
    var useInlineTitle = Boolean(texts.length) && first.length <= 34;
    var title = useInlineTitle ? first : displaySectionTitle(section);
    var leadIndex = useInlineTitle ? 1 : 0;
    var leadBlock = textBlocks[leadIndex] || textBlocks[0] || allTextBlocks[0] || null;
    var leadPos = leadBlock ? allTextBlocks.indexOf(leadBlock) : -1;
    var pointTextBlocks = leadPos >= 0 ? allTextBlocks.slice(leadPos + 1) : allTextBlocks;
    return {
      title: title,
      lead: texts[leadIndex] || first,
      points: pointTextBlocks.map(function (b) { return String(b.content || "").trim(); }),
      textBlocks: textBlocks,
      titleTextBlock: useInlineTitle ? textBlocks[0] : null,
      leadTextBlock: leadBlock,
      pointTextBlocks: pointTextBlocks,
      leadIndex: leadIndex,
      media: mediaBlocks,
      externalLinks: section.externalLinks || []
    };
  }

  function renderExperienceLinks(links, compact, inert) {
    var list = (links || []).filter(function (link) { return link && link.href; });
    if (!list.length) return "";
    return '<div class="experience-links' + (compact ? " is-compact" : "") + '">' + list.map(function (link) {
      return '<a class="experience-link" href="' + esc(link.href) + '"' + (inert ? ' tabindex="-1"' : "") + '>' +
        '<span>' + esc(link.label || "打开体验系统") + '</span>' +
        '<em>打开</em>' +
        '</a>';
    }).join("") + '</div>';
  }

  function topicExternalLinks(data) {
    var links = [];
    (data.sections || []).forEach(function (section) {
      (section.externalLinks || []).forEach(function (link) {
        links.push({
          label: link.label,
          href: link.href,
          sourceTitle: link.sourceTitle || displaySectionTitle(section),
          description: link.description || "",
          sectionId: section.id || ""
        });
      });
    });
    return uniqueExternalLinks(links);
  }

  function topicExperienceKind(link) {
    var text = [link.label, link.sourceTitle, link.description].join(" ");
    return /资源|案例库|素材|课程|作品/.test(text) ? "resources" : "systems";
  }

  function renderTopicExperienceMenu(group, kind) {
    if (!group.length) return "";
    var isResource = kind === "resources";
    var label = isResource ? "数字资源" : "体验系统";
    var eyebrow = isResource ? "DIGITAL RESOURCES" : "INTERACTIVE SYSTEMS";
    var icon = isResource
      ? '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v16H6.5A2.5 2.5 0 0 0 4 21.5v-16Z M4 5.5v16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'
      : '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 4h8M9 2v2m6-2v2M6 8h12a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2Zm2 5h.01M16 13h.01M9 17h6" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>';
    var menuId = "topicExperience-" + kind;
    var links = group.map(function (link, index) {
      return '<a class="topic-experience-item experience-link" href="' + esc(link.href) + '" target="_blank" rel="noopener noreferrer">' +
        '<span class="topic-experience-index">' + String(index + 1).padStart(2, "0") + '</span>' +
        '<span class="topic-experience-copy"><strong>' + esc(link.label || "打开特色体验") + '</strong>' +
        '<small>' + esc(link.sourceTitle || (isResource ? "专题数字资源" : "专题互动体验")) + '</small></span>' +
        '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 16 16 8m-6 0h6v6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></a>';
    }).join("");
    return '<div class="topic-experience-action ' + (isResource ? "is-resource" : "is-system") + '">' +
      '<button class="topic-experience-trigger" type="button" aria-expanded="false" aria-controls="' + menuId + '">' +
      '<span class="topic-experience-icon">' + icon + '</span><strong>' + label + '</strong><em>' + group.length + ' 项</em></button>' +
      '<section class="topic-experience-menu" id="' + menuId + '" hidden aria-label="' + label + '入口">' +
      '<header><span><small>' + eyebrow + '</small><strong>' + label + '</strong></span>' +
      '<button class="topic-experience-close" type="button" aria-label="关闭' + label + '入口">×</button></header>' +
      '<div class="topic-experience-list">' + links + '</div></section></div>';
  }

  function renderTopicExperienceActions(data) {
    var links = topicExternalLinks(data);
    if (!links.length) return "";
    var systems = links.filter(function (link) { return topicExperienceKind(link) === "systems"; });
    var resources = links.filter(function (link) { return topicExperienceKind(link) === "resources"; });
    return '<nav class="topic-showcase-actions" aria-label="特色体验入口">' +
      renderTopicExperienceMenu(systems, "systems") +
      renderTopicExperienceMenu(resources, "resources") + '</nav>';
  }

  function renderTopicExperienceDock(data) {
    return renderTopicExperienceActions(data);
  }

  function renderTopicLoopPage(data) {
    var section = state.sections[state.section];
    if (!section) return "";
    var model = topicSectionModel(section);
    var indexLabel = String(state.section + 1).padStart(2, "0") + " / " +
      String(state.sections.length).padStart(2, "0");
    var statHtml = (data.stats || []).slice(0, 4).map(function (s) {
      return '<div class="topic-section-stat"><b>' + esc(s.value) + '</b><span>' + esc(s.label) + '</span></div>';
    }).join("");
    var editMode = INLINE_EDIT.enabled;
    var pointList = editMode ? model.pointTextBlocks : model.pointTextBlocks.filter(function (b) { return String(b.content || "").trim(); });
    var points = pointList.slice(0, editMode ? undefined : 4).map(function (block, i) {
      var text = editMode ? (String(block.content || "").trim() || "点击输入要点…") : compactText(block.content, 92);
      return '<li class="topic-point-item"><span data-block-text-idx="' + i + '">' + esc(text) + '</span>' +
        (editMode ? '<button type="button" class="inline-edit-point-remove" data-point-idx="' + i + '" aria-label="删除要点">×</button>' : '') +
        '</li>';
    }).join("");
    var prevIndex = state.section > 0 ? state.section - 1 : state.sections.length - 1;
    var nextIndex = state.section < state.sections.length - 1 ? state.section + 1 : 0;
    return '<section class="topic-section-page topic-theme-' + esc(data.id) + '" style="--topic-section-bg:url(\'/static/blueprint/' + esc(data.id) + '-bg.png\')">' +
      '<header class="topic-section-hero">' +
      '<div class="topic-section-heading"><span>' + esc(data.name || "专题门户") + ' · ' + indexLabel + '</span>' +
      '<h2>' + esc(displaySectionTitle(section)) + '</h2>' +
      '<p>' + esc(data.summary || TOPIC_SUMMARY[data.id] || "围绕重点专业群、成果资源和展示素材组织专题内容。") + '</p></div>' +
      '<div class="topic-section-stats">' + statHtml + '</div>' +
      '</header>' +
      '<div class="topic-section-content">' +
      '<article class="topic-section-story">' +
      '<div class="topic-section-kicker"><span>' + esc(SECTION_EN[section.id] || "SECTION") + '</span><em>章节摘要</em></div>' +
      '<h3' + (model.titleTextBlock ? ' data-block-text-idx="0"' : '') + '>' + esc(model.title || displaySectionTitle(section)) + '</h3>' +
      '<p class="topic-section-lead"' + (model.leadTextBlock ? ' data-block-text-idx="' + model.leadIndex + '"' : '') + '>' +
      (editMode && !model.lead ? '<span class="inline-edit-placeholder">点击输入章节正文…</span>' : esc(editMode ? model.lead : compactText(model.lead, 260))) + '</p>' +
      (points ? '<ul class="topic-section-points">' + points + '</ul>' : '') +
      (editMode ? '<button type="button" class="inline-edit-add-point">＋ 添加要点</button>' : '') +
      '<button type="button" class="topic-section-open" data-section-id="' + esc(section.id) + '">' +
      '<span>查看完整资料</span><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M14 7l5 5-5 5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></button>' +
      '</article>' +
      '<aside class="topic-section-media" aria-label="' + esc(displaySectionTitle(section)) + '图片资料" data-section-media="' + esc(section.id) + '">' +
      '<div class="topic-section-media-head"><span>影像资料</span><em>' + model.media.length + ' 项</em></div>' +
      renderTopicLoopMedia(model.media, data, section) +
      '</aside></div>' +
      '<footer class="topic-section-footer">' +
      '<button type="button" data-section-index="' + prevIndex + '"><span>上一章节</span><strong>' + esc(displaySectionTitle(state.sections[prevIndex])) + '</strong></button>' +
      '<p>点击上方章节标签可快速切换内容</p>' +
      '<button type="button" data-section-index="' + nextIndex + '"><span>下一章节</span><strong>' + esc(displaySectionTitle(state.sections[nextIndex])) + '</strong></button>' +
      '</footer>' +
      '</section>';
  }

  function renderTopicLoopSection(section, originalIndex, clone) {
    var data = getData();
    var model = topicSectionModel(section);
    var label = String(originalIndex + 1).padStart(2, "0") + " / " + esc(SECTION_EN[section.id] || "SECTION");
    var pointItems = model.points.slice(0, 3);
    var points = pointItems.length ? '<ul class="topic-loop-points">' + pointItems.map(function (text) {
      return '<li>' + esc(compactText(text, 64)) + '</li>';
    }).join("") + '</ul>' : "";
    return '<article class="topic-loop-card" data-section-id="' + esc(section.id) + '"' +
      (clone ? ' tabindex="-1"' : ' tabindex="0" role="button" aria-label="查看' + esc(displaySectionTitle(section)) + '完整资料"') + '>' +
      '<div class="topic-loop-copy"><span>' + label + '</span><h3>' + esc(displaySectionTitle(section)) + '</h3>' +
      '<p>' + esc(compactText(model.lead, 170)) + '</p>' + points + '</div>' +
      renderTopicLoopMedia(model.media, data, section) +
      '</article>';
  }

  function renderTopicLoopMediaLegacy(mediaBlocks, data, section) {
    var list = mediaBlocks.length ? mediaBlocks : [{ type: "image", src: data.cover || "", caption: data.name || displaySectionTitle(section) }];
    return '<div class="topic-loop-media legacy-unused">' + list.map(function (b) {
      if (b.type === "video") {
        var poster = b.poster || data.cover || "";
        return '<figure class="topic-loop-video">' +
          (poster ? '<img src="' + esc(poster) + '" alt="' + esc(b.title || displaySectionTitle(section)) + '" loading="lazy">' : '') +
          '<span class="topic-video-mark" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M8 5.5v13l10-6.5-10-6.5z" fill="currentColor"/></svg></span>' +
          '<figcaption>' + esc(b.title || "视频资源") + '</figcaption></figure>';
      }
      return '<figure class="photo-frame topic-loop-image" tabindex="0" data-lightbox="' + esc(b.src) + '" data-caption="' + esc(b.caption || data.name || displaySectionTitle(section)) + '">' +
        '<img src="' + esc(b.src) + '" alt="' + esc(b.caption || data.name || displaySectionTitle(section)) + '" loading="lazy">' +
        (b.caption ? '<figcaption>' + esc(b.caption) + '</figcaption>' : "") +
        '</figure>';
    }).join("") + '</div>';
  }

  function renderTopicLoopMedia(mediaBlocks, data, section) {
    var list = (mediaBlocks || []).filter(function (b) {
      if (!b) return false;
      if (b.type === "video") return !!(b.poster || b.src);
      return !!b.src;
    });
    if (!list.length) list = [];
    var items = list.map(function (b) {
      if (b.type === "video") {
        var poster = b.poster || "";
        return { title: b.title || displaySectionTitle(section), body: "", imageUrl: poster, caption: b.title || "视频资源", lightbox: "", video: true };
      }
      return { title: b.caption || displaySectionTitle(section), body: "", imageUrl: b.src, caption: b.caption || "", lightbox: b.src };
    });
    return '<div class="topic-loop-media">' + renderTopicCoverflowCarousel(items, { fallbackImage: "", title: displaySectionTitle(section) }) + '</div>';
  }

  function renderTopicLoopSlide(b, data, section, index) {
    var active = index === 0 ? " is-active" : "";
    if (b.type === "video") {
      var poster = b.poster || data.cover || "";
      return '<figure class="topic-loop-slide topic-loop-video' + active + '" data-slide-index="' + index + '">' +
        (poster ? '<img src="' + esc(poster) + '" alt="' + esc(b.title || displaySectionTitle(section)) + '" loading="lazy">' : '') +
        '<span class="topic-video-mark" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M8 5.5v13l10-6.5-10-6.5z" fill="currentColor"/></svg></span>' +
        '<figcaption>' + esc(b.title || "Video") + '</figcaption></figure>';
    }
    var caption = b.caption || data.name || displaySectionTitle(section);
    return '<figure class="topic-loop-slide topic-loop-image' + active + '" data-slide-index="' + index + '">' +
      '<img src="' + esc(b.src) + '" alt="' + esc(caption) + '" loading="lazy">' +
      (b.caption ? '<figcaption>' + esc(b.caption) + '</figcaption>' : "") +
      '</figure>';
  }

  function openTopicLoopSection(sectionId) {
    if (state.kind !== "topics") return;
    var section = (state.sections || []).find(function (item) { return item.id === sectionId; });
    if (!section) return;
    openDrawer(renderTopicFullSection(section));
    if (INLINE_EDIT.enabled) {
      initInlineEdit().then(function () { applyDrawerSectionControls(section); });
    } else {
      applyDrawerSectionControls(section);
    }
  }

  function applyDrawerSectionControls(section) {
    var body = $("drawerBody");
    if (!body || $("drawer").hidden) return;
    var data = getData();
    var project = detailProjectFor(data);
    body.querySelectorAll(".section-manager-item[data-item-id]").forEach(function (card) {
      if (card.dataset.inlineBound) return;
      card.dataset.inlineBound = "1";
      card.addEventListener("click", function (e) {
        e.preventDefault();
        e.stopPropagation();
        var items = (data.sectionItems && data.sectionItems[section.id]) || [];
        var item = items.find(function (it) { return String(it.id) === String(card.dataset.itemId); });
        if (item) itemDetailOverlay(item, section, project);
      });
    });
    if (!INLINE_EDIT.enabled || !INLINE_EDIT.ready) return;
    var titleNode = body.querySelector(".section-manager-title");
    if (titleNode) bindInlineSectionTitle(titleNode, section, project);
    var bodyNode = body.querySelector(".section-manager-body");
    if (bodyNode) bindInlineCoopBody(bodyNode, project, section);
    body.querySelectorAll("[data-section-add-item]").forEach(function (btn) {
      if (btn.dataset.inlineBound) return;
      btn.dataset.inlineBound = "1";
      btn.addEventListener("click", function (e) {
        e.preventDefault();
        e.stopPropagation();
        itemAddOverlay(section, project);
      });
    });
  }

  function itemAddOverlay(section, project) {
    var existing = document.querySelector(".item-editor-overlay");
    if (existing) existing.remove();
    var overlay = document.createElement("div");
    overlay.className = "item-editor-overlay";
    overlay.innerHTML =
      '<div class="item-editor-panel" role="dialog" aria-label="添加项目">' +
      '<header><strong>添加项目</strong><button type="button" class="item-editor-close" aria-label="关闭">×</button></header>' +
      '<label class="item-editor-field"><span>项目图片</span>' +
      '<div class="item-editor-image-box">' +
      '<img class="item-editor-preview" hidden alt="图片预览">' +
      '<button type="button" class="item-editor-upload">选择图片上传</button>' +
      '<input class="item-editor-url" placeholder="或直接粘贴图片地址 /uploads/...">' +
      '</div></label>' +
      '<label class="item-editor-field"><span>文字说明</span>' +
      '<textarea class="item-editor-summary" rows="3" placeholder="一小段文字说明"></textarea></label>' +
      '<div class="item-editor-actions"><span class="item-editor-status"></span>' +
      '<button type="button" class="item-editor-save primary">确定添加</button></div>' +
      '</div>';
    document.body.appendChild(overlay);
    var statusNode = overlay.querySelector(".item-editor-status");
    var setStatus = function (message, kind) {
      statusNode.textContent = message || "";
      statusNode.dataset.kind = kind || "";
    };
    overlay.querySelector(".item-editor-close").addEventListener("click", function () { overlay.remove(); });
    overlay.addEventListener("click", function (event) { if (event.target === overlay) overlay.remove(); });
    var pendingUrl = "";
    var previewImg = overlay.querySelector(".item-editor-preview");
    overlay.querySelector(".item-editor-upload").addEventListener("click", function () {
      var input = document.createElement("input");
      input.type = "file";
      input.accept = "image/*";
      input.style.cssText = "position:fixed;left:-9999px;top:0;width:1px;height:1px;opacity:0;pointer-events:none;";
      document.body.appendChild(input);
      input.addEventListener("change", function () {
        var file = input.files && input.files[0];
        if (!file) return;
        setStatus("正在上传图片...", "warn");
        fileToDataUrl(file)
          .then(function (dataUrl) {
            return inlineEditApi("/api/assets", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ filename: file.name, dataUrl: dataUrl })
            });
          })
          .then(function (payload) {
            var url = payload.url || (payload.asset && payload.asset.url) || "";
            if (!url) throw new Error("上传成功但未返回图片地址");
            pendingUrl = url;
            previewImg.src = url;
            previewImg.hidden = false;
            setStatus("图片已上传，填写说明后点确定", "ok");
          })
          .catch(function (error) { setStatus(error.message || "上传失败", "error"); });
      });
      input.click();
    });
    overlay.querySelector(".item-editor-save").addEventListener("click", function () {
      var summary = String(overlay.querySelector(".item-editor-summary").value || "").trim();
      var url = String(pendingUrl || overlay.querySelector(".item-editor-url").value || "").trim();
      if (!url) { setStatus("请先上传或填写项目图片", "error"); return; }
      if (!summary) { setStatus("请填写文字说明", "error"); return; }
      setStatus("正在保存...", "warn");
      inlineEditApi("/api/projects/" + encodeURIComponent(project.id) + "/content-items", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          moduleKey: section.id,
          contentType: "article",
          title: summary.slice(0, 24),
          summary: summary,
          assets: [{ url: url, role: "cover" }],
          enabled: true
        })
      }).then(function () {
        overlay.remove();
        inlineEditStatus("已添加，刷新中…", "ok");
        reloadPortalDetail().then(function () { openTopicLoopSection(section.id); });
      }).catch(function (error) { setStatus(error.message || "保存失败", "error"); });
    });
  }

  function bodyHtmlFromContentItem(item) {
    var blocks = Array.isArray(item && item.bodyJson) ? item.bodyJson : [];
    var parts = blocks.map(function (b) {
      if (!b) return "";
      if (b.type === "html") return String(b.html || "");
      if (b.type === "paragraph") return "<p>" + esc(String(b.text || "")) + "</p>";
      if (b.type === "heading") return "<h3>" + esc(String(b.text || "")) + "</h3>";
      return "";
    });
    return parts.join("");
  }

  function sanitizeDisplayHtml(html) {
    var doc = new DOMParser().parseFromString(String(html || ""), "text/html");
    doc.querySelectorAll("script, iframe, object, embed, style, link, meta").forEach(function (node) { node.remove(); });
    doc.querySelectorAll("*").forEach(function (node) {
      Array.prototype.slice.call(node.attributes || []).forEach(function (attr) {
        if (/^on/i.test(attr.name)) node.removeAttribute(attr.name);
      });
      if (node.tagName === "A") {
        var href = node.getAttribute("href") || "";
        if (!/^(https?:|mailto:|#|\/)/i.test(href)) node.setAttribute("href", "#");
      }
    });
    return doc.body.innerHTML;
  }

  function openVideoList() {
    openDrawer(renderTopicVideoList(getData()));
    if (INLINE_EDIT.enabled) {
      initInlineEdit().then(bindVideoListControls);
    } else {
      bindVideoListControls();
    }
  }

  function renderTopicVideoList(data) {
    var mediaSection = firstSectionById(data, "media") || { blocks: [] };
    var videos = (mediaSection.blocks || []).filter(function (b) { return b.type === "video" && (b.src || b.poster); });
    var editMode = INLINE_EDIT.enabled;
    var listHtml = videos.length
      ? videos.map(function (v, i) {
        var thumb = v.poster
          ? '<span class="video-manager-thumb"><img src="' + esc(v.poster) + '" alt="' + esc(v.title || "视频") + '" loading="lazy"><span class="video-manager-play" aria-hidden="true"></span></span>'
          : '<span class="video-manager-thumb video-manager-thumb-empty"><span class="video-manager-play" aria-hidden="true"></span></span>';
        return '<li class="video-manager-item" data-video-index="' + i + '" tabindex="0" role="button" aria-label="播放' + esc(v.title || "视频") + '">' +
          thumb +
          '<span class="video-manager-copy"><strong>' + esc(v.title || "未命名视频") + '</strong></span>' +
          (editMode ? '<button type="button" class="video-manager-delete" data-video-delete="' + i + '" aria-label="删除视频">删除</button>' : '') +
          '</li>';
      }).join("")
      : '<li class="section-manager-empty">' + (editMode ? "点击“添加视频”上传视频和文字描述" : "暂无视频") + '</li>';
    return '<article class="topic-display-panel section-manager">' +
      '<div class="topic-display-meta"><p class="topic-display-category">' + esc(data.name || "专题门户") + '</p></div>' +
      '<h1 class="section-manager-title">视频资源</h1>' +
      '<div class="section-manager-items">' +
      '<div class="section-manager-items-head"><strong>全部视频</strong><em>' + videos.length + ' 个</em>' +
      (editMode ? '<button type="button" class="section-manager-add" data-video-add="1">＋ 添加视频</button>' : '') +
      '</div>' +
      '<ul class="video-manager-list">' + listHtml + '</ul>' +
      '</div>' +
      '<footer class="topic-display-footer"><span>学校大屏展示内容</span><span>扫码进入子级展示页</span></footer>' +
      '</article>';
  }

  function bindVideoListControls() {
    var body = $("drawerBody");
    if (!body || $("drawer").hidden) return;
    var data = getData();
    var project = detailProjectFor(data);
    var mediaSection = firstSectionById(data, "media");
    if (!mediaSection) {
      mediaSection = { id: "media", title: "", blocks: [], contentType: "article" };
      data.sections = data.sections || [];
      data.sections.push(mediaSection);
    }
    var videos = (mediaSection.blocks || []).filter(function (b) { return b.type === "video" && (b.src || b.poster); });
    body.querySelectorAll("[data-video-index]").forEach(function (li) {
      if (li.dataset.inlineBound) return;
      li.dataset.inlineBound = "1";
      li.addEventListener("click", function (e) {
        e.preventDefault();
        e.stopPropagation();
        var v = videos[parseInt(li.dataset.videoIndex, 10)];
        if (v) videoDetailOverlay(v);
      });
    });
    body.querySelectorAll("[data-video-delete]").forEach(function (btn) {
      if (btn.dataset.inlineBound) return;
      btn.dataset.inlineBound = "1";
      btn.addEventListener("click", function (e) {
        e.preventDefault();
        e.stopPropagation();
        var v = videos[parseInt(btn.dataset.videoDelete, 10)];
        if (!v) return;
        if (!confirm("确定删除该视频？")) return;
        mediaSection.blocks = (mediaSection.blocks || []).filter(function (b) { return b !== v; });
        markPageDirty(project.id, mediaSection.id, pagePayloadForSection(mediaSection));
        openVideoList();
      });
    });
    body.querySelectorAll("[data-video-add]").forEach(function (btn) {
      if (btn.dataset.inlineBound) return;
      btn.dataset.inlineBound = "1";
      btn.addEventListener("click", function (e) {
        e.preventDefault();
        e.stopPropagation();
        videoAddOverlay(project, mediaSection);
      });
    });
  }

  function videoAddOverlay(project, section) {
    var existing = document.querySelector(".item-editor-overlay");
    if (existing) existing.remove();
    var overlay = document.createElement("div");
    overlay.className = "item-editor-overlay";
    overlay.innerHTML =
      '<div class="item-editor-panel" role="dialog" aria-label="添加视频">' +
      '<header><strong>添加视频</strong><button type="button" class="item-editor-close" aria-label="关闭">×</button></header>' +
      '<label class="item-editor-field"><span>视频文件（mp4 / webm）</span>' +
      '<div class="item-editor-image-box">' +
      '<video class="item-editor-video-preview" controls hidden></video>' +
      '<button type="button" class="item-editor-upload">选择视频上传</button>' +
      '</div></label>' +
      '<label class="item-editor-field"><span>文字描述</span>' +
      '<textarea class="item-editor-summary" rows="3" placeholder="一小段视频描述"></textarea></label>' +
      '<div class="item-editor-actions"><span class="item-editor-status"></span>' +
      '<button type="button" class="item-editor-save primary">确定添加</button></div>' +
      '</div>';
    document.body.appendChild(overlay);
    var statusNode = overlay.querySelector(".item-editor-status");
    var setStatus = function (message, kind) {
      statusNode.textContent = message || "";
      statusNode.dataset.kind = kind || "";
    };
    overlay.querySelector(".item-editor-close").addEventListener("click", function () { overlay.remove(); });
    overlay.addEventListener("click", function (event) { if (event.target === overlay) overlay.remove(); });
    var pendingUrl = "";
    var previewVideo = overlay.querySelector(".item-editor-video-preview");
    overlay.querySelector(".item-editor-upload").addEventListener("click", function () {
      var input = document.createElement("input");
      input.type = "file";
      input.accept = "video/mp4,video/webm";
      input.style.cssText = "position:fixed;left:-9999px;top:0;width:1px;height:1px;opacity:0;pointer-events:none;";
      document.body.appendChild(input);
      input.addEventListener("change", function () {
        var file = input.files && input.files[0];
        if (!file) return;
        setStatus("正在上传视频，请稍候…", "warn");
        fileToDataUrl(file)
          .then(function (dataUrl) {
            return inlineEditApi("/api/assets", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ filename: file.name, dataUrl: dataUrl })
            });
          })
          .then(function (payload) {
            var url = payload.url || (payload.asset && payload.asset.url) || "";
            if (!url) throw new Error("上传成功但未返回视频地址");
            pendingUrl = url;
            previewVideo.src = url;
            previewVideo.hidden = false;
            setStatus("视频已上传，填写描述后点确定", "ok");
          })
          .catch(function (error) { setStatus(error.message || "上传失败", "error"); });
      });
      input.click();
    });
    overlay.querySelector(".item-editor-save").addEventListener("click", function () {
      var title = String(overlay.querySelector(".item-editor-summary").value || "").trim();
      if (!pendingUrl) { setStatus("请先上传视频", "error"); return; }
      if (!title) { setStatus("请填写文字描述", "error"); return; }
      var blocks = section.blocks || [];
      var poster = "";
      for (var i = 0; i < blocks.length; i++) {
        if (blocks[i].type === "image" && blocks[i].src) { poster = blocks[i].src; break; }
      }
      blocks.push({ type: "video", src: pendingUrl, poster: poster, title: title });
      section.blocks = blocks;
      markPageDirty(project.id, section.id, pagePayloadForSection(section));
      overlay.remove();
      inlineEditStatus("视频已添加，待保存", "warn");
      openVideoList();
    });
  }

  function videoDetailOverlay(video) {
    var existing = document.querySelector(".item-detail-overlay");
    if (existing) existing.remove();
    var overlay = document.createElement("div");
    overlay.className = "item-detail-overlay";
    overlay.innerHTML =
      '<div class="item-detail-panel video-detail-panel">' +
      '<button type="button" class="item-detail-close" aria-label="关闭">×</button>' +
      '<div class="video-detail-stage">' + renderVideo(video) + '</div>' +
      (video.title ? '<div class="video-detail-copy">' + esc(video.title) + '</div>' : '') +
      '</div>';
    document.body.appendChild(overlay);
    overlay.querySelector(".item-detail-close").addEventListener("click", function () { overlay.remove(); });
    overlay.addEventListener("click", function (event) { if (event.target === overlay) overlay.remove(); });
    bindVideos(overlay);
  }

  function itemDetailOverlay(item, section, project) {
    var existing = document.querySelector(".item-detail-overlay");
    if (existing) existing.remove();
    var editMode = INLINE_EDIT.enabled;
    var bodyHtml = sanitizeDisplayHtml(item.bodyHtml);
    if (!bodyHtml) {
      var parts = [];
      if (item.imageUrl) parts.push('<p style="text-align:center"><img src="' + esc(item.imageUrl) + '" alt="' + esc(item.title || "项目图片") + '" style="max-width:100%"></p>');
      if (item.summary) parts.push("<p>" + esc(item.summary) + "</p>");
      bodyHtml = parts.join("");
    }
    var overlay = document.createElement("div");
    overlay.className = "item-detail-overlay";
    overlay.innerHTML =
      '<div class="item-detail-panel" role="dialog" aria-label="项目详情">' +
      '<button type="button" class="item-detail-close" aria-label="关闭">×</button>' +
      '<h3 class="item-detail-heading">' + esc(item.title || "未命名项目") + '</h3>' +
      (editMode
        ? '<div class="item-detail-toolbar">' +
          '<button type="button" data-richtext="bold" title="加粗"><b>B</b></button>' +
          '<button type="button" data-richtext="italic" title="斜体"><i>I</i></button>' +
          '<button type="button" data-richtext="underline" title="下划线"><u>U</u></button>' +
          '<span class="item-detail-toolbar-sep"></span>' +
          '<button type="button" data-richtext-block="h3" title="小标题">标题</button>' +
          '<button type="button" data-richtext-block="p" title="正文">正文</button>' +
          '<span class="item-detail-toolbar-sep"></span>' +
          '<button type="button" data-richtext="insertUnorderedList" title="无序列表">• 列表</button>' +
          '<button type="button" data-richtext="insertOrderedList" title="有序列表">1. 列表</button>' +
          '<span class="item-detail-toolbar-sep"></span>' +
          '<button type="button" data-richtext-image title="插入图片">图片</button>' +
          '<button type="button" data-richtext="removeFormat" title="清除格式">清除</button>' +
          '</div>'
        : "") +
      '<div class="item-detail-editor" contenteditable="' + (editMode ? "true" : "false") + '">' + bodyHtml + '</div>' +
      (editMode
        ? '<div class="item-detail-actions">' +
          '<span class="item-detail-status"></span>' +
          '<button type="button" class="item-detail-delete">删除该项目</button>' +
          '<button type="button" class="item-detail-save primary">保存</button>' +
          '</div>'
        : '<div class="item-detail-actions"><button type="button" class="item-detail-close-bottom">关闭</button></div>') +
      '</div>';
    document.body.appendChild(overlay);
    var statusNode = overlay.querySelector(".item-detail-status");
    var setStatus = function (message, kind) {
      if (!statusNode) return;
      statusNode.textContent = message || "";
      statusNode.dataset.kind = kind || "";
    };
    overlay.querySelector(".item-detail-close").addEventListener("click", function () { overlay.remove(); });
    overlay.querySelectorAll(".item-detail-close-bottom").forEach(function (btn) {
      btn.addEventListener("click", function () { overlay.remove(); });
    });
    var dragStartPoint = null;
    document.addEventListener("mousedown", function (event) {
      dragStartPoint = { x: event.clientX, y: event.clientY };
    }, true);
    overlay.addEventListener("click", function (event) {
      if (event.target !== overlay) return;
      if (dragStartPoint && Math.abs(event.clientX - dragStartPoint.x) + Math.abs(event.clientY - dragStartPoint.y) > 8) return;
      overlay.remove();
    });
    var editor = overlay.querySelector(".item-detail-editor");
    if (editor && editMode) {
      editor.addEventListener("keydown", function (event) {
        if (event.key === "Tab") {
          event.preventDefault();
          document.execCommand("insertHTML", false, "&nbsp;&nbsp;&nbsp;&nbsp;");
        }
      });
      var richHandles = [];
      var clearRichSelection = function () {
        editor.querySelectorAll(".rich-img-active").forEach(function (n) { n.classList.remove("rich-img-active"); });
        richHandles.forEach(function (h) { h.remove(); });
        richHandles.length = 0;
      };
      var positionRichHandles = function (img) {
        var or = overlay.getBoundingClientRect();
        var r = img.getBoundingClientRect();
        if (richHandles.length === 2) {
          richHandles[0].style.left = (r.right - or.left - 11) + "px";
          richHandles[0].style.top = (r.bottom - or.top - 11) + "px";
          richHandles[1].style.left = (r.right - or.left - 15) + "px";
          richHandles[1].style.top = (r.top - or.top - 15) + "px";
        }
      };
      var selectRichImage = function (img) {
        clearRichSelection();
        img.classList.add("rich-img-active");
        var resizeHandle = document.createElement("div");
        resizeHandle.className = "rich-img-handle rich-img-resize";
        resizeHandle.title = "拖拽调整大小";
        var rotateHandle = document.createElement("div");
        rotateHandle.className = "rich-img-handle rich-img-rotate";
        rotateHandle.title = "点击旋转 90°";
        rotateHandle.textContent = "↻";
        overlay.appendChild(resizeHandle);
        overlay.appendChild(rotateHandle);
        richHandles = [resizeHandle, rotateHandle];
        positionRichHandles(img);
        var cancel = function (e) {
          if (e.target !== img && !e.target.closest(".rich-img-handle")) {
            clearRichSelection();
            document.removeEventListener("mousedown", cancel);
            editor.removeEventListener("scroll", positionRichHandles);
          }
        };
        editor.addEventListener("scroll", positionRichHandles);
        document.addEventListener("mousedown", cancel);
        resizeHandle.addEventListener("mousedown", function (e) {
          e.preventDefault();
          e.stopPropagation();
          var startX = e.clientX;
          var startW = img.getBoundingClientRect().width;
          var move = function (ev) {
            var w = Math.max(40, startW + (ev.clientX - startX));
            img.style.width = w + "px";
            positionRichHandles(img);
          };
          var up = function () {
            document.removeEventListener("mousemove", move);
            document.removeEventListener("mouseup", up);
          };
          document.addEventListener("mousemove", move);
          document.addEventListener("mouseup", up);
        });
        rotateHandle.addEventListener("mousedown", function (e) { e.preventDefault(); e.stopPropagation(); });
        rotateHandle.addEventListener("click", function (e) {
          e.preventDefault();
          e.stopPropagation();
          var cur = 0;
          var m = /rotate\((-?[\d.]+)deg\)/.exec(img.style.transform || "");
          if (m) cur = parseFloat(m[1]);
          img.style.transform = "rotate(" + (cur + 90) + "deg)";
          positionRichHandles(img);
        });
      };
      editor.addEventListener("click", function (e) {
        var img = e.target.closest("img");
        if (img && editor.contains(img)) selectRichImage(img);
      });
      overlay.querySelectorAll("[data-richtext]").forEach(function (btn) {
        btn.addEventListener("click", function (e) {
          e.preventDefault();
          e.stopPropagation();
          editor.focus();
          document.execCommand(btn.dataset.richtext, false, null);
        });
      });
      overlay.querySelectorAll("[data-richtext-block]").forEach(function (btn) {
        btn.addEventListener("click", function (e) {
          e.preventDefault();
          e.stopPropagation();
          editor.focus();
          document.execCommand("formatBlock", false, btn.dataset.richtextBlock);
        });
      });
      var imageBtn = overlay.querySelector("[data-richtext-image]");
      if (imageBtn) {
        imageBtn.addEventListener("click", function (e) {
          e.preventDefault();
          e.stopPropagation();
          var input = document.createElement("input");
          input.type = "file";
          input.accept = "image/*";
          input.style.cssText = "position:fixed;left:-9999px;top:0;width:1px;height:1px;opacity:0;pointer-events:none;";
          document.body.appendChild(input);
          input.addEventListener("change", function () {
            var file = input.files && input.files[0];
            if (!file) return;
            setStatus("正在上传图片...", "warn");
            fileToDataUrl(file)
              .then(function (dataUrl) {
                return inlineEditApi("/api/assets", {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify({ filename: file.name, dataUrl: dataUrl })
                });
              })
              .then(function (payload) {
                var url = payload.url || (payload.asset && payload.asset.url) || "";
                if (!url) throw new Error("上传成功但未返回图片地址");
                editor.focus();
                document.execCommand("insertImage", false, url);
                setStatus("图片已插入，记得保存", "ok");
              })
              .catch(function (error) { setStatus(error.message || "上传失败", "error"); });
          });
          input.click();
        });
      }
      var deleteBtn = overlay.querySelector(".item-detail-delete");
      if (deleteBtn) {
        deleteBtn.addEventListener("click", function () {
          if (!confirm("确定删除该项目？")) return;
          inlineEditApi("/api/projects/" + encodeURIComponent(project.id) + "/content-items/" + encodeURIComponent(item.id), { method: "DELETE" })
            .then(function () {
              overlay.remove();
              inlineEditStatus("项目已删除", "ok");
              reloadPortalDetail().then(function () { openTopicLoopSection(section.id); });
            })
            .catch(function (error) { alert(error.message || "删除失败"); });
        });
      }
      var saveBtn = overlay.querySelector(".item-detail-save");
      if (saveBtn) {
        saveBtn.addEventListener("click", function () {
          var html = sanitizeDisplayHtml(editor.innerHTML);
          setStatus("正在保存...", "warn");
          inlineEditApi("/api/projects/" + encodeURIComponent(project.id) + "/content-items/" + encodeURIComponent(item.id), {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ body: html, title: item.title || "", summary: item.summary || "" })
          }).then(function () {
            overlay.remove();
            inlineEditStatus("详情已保存", "ok");
            reloadPortalDetail().then(function () { openTopicLoopSection(section.id); });
          }).catch(function (error) { setStatus(error.message || "保存失败", "error"); });
        });
      }
    }
  }

  function renderTopicFullSection(section) {
    var data = getData();
    var blocks = (section.blocks || []).map(function (sourceBlock) {
      return normalizeTopicBlock(sourceBlock, section);
    });
    var code = section.backendPageCode || (data.id ? data.id + "-" + section.id : section.id);
    var updated = formatTopicDisplayDate(section.backendUpdatedAt);
    var contentType = normalizeContentType(section.contentType || defaultContentTypeForSection(section.id));
    var editMode = INLINE_EDIT.enabled;
    var textBlocks = blocks.filter(function (b) { return b.type === "text" && String(b.content || "").trim(); });
    var bodyHtml = textBlocks.length
      ? textBlocks.map(function (b) { return "<p>" + esc(String(b.content || "").trim()) + "</p>"; }).join("")
      : '<p class="section-manager-empty">' + (editMode ? "输入板块正文…" : "板块正文待补充") + '</p>';
    var items = (data.sectionItems && data.sectionItems[section.id]) || [];
    var itemHtml = items.length
      ? items.map(function (item) {
        var thumb = item.imageUrl
          ? '<span class="section-manager-item-photo"><img src="' + esc(item.imageUrl) + '" alt="' + esc(item.title || "项目图片") + '" loading="lazy"></span>'
          : '<span class="section-manager-item-photo section-manager-item-photo-empty" aria-hidden="true">' + esc((item.title || "?").slice(0, 1)) + '</span>';
        return '<li class="section-manager-item" data-item-id="' + esc(item.id) + '" tabindex="0" role="button" aria-label="查看' + esc(item.title || "项目") + '详情">' +
          thumb +
          '<span class="section-manager-item-copy">' +
          '<strong>' + esc(item.summary || item.title || "未命名项目") + '</strong>' +
          '</span></li>';
      }).join("")
      : '<li class="section-manager-empty">' + (editMode ? "点击“添加项目”上传图片和说明" : "项目列表待补充") + '</li>';
    return '<article class="topic-display-panel content-type-' + esc(contentType) + ' section-manager">' +
      '<div class="topic-display-meta">' +
      '<p class="topic-display-category">' + esc(data.name || "专题门户") + '</p>' +
      '<div class="topic-display-source">' +
      (updated ? '<span>' + esc(updated) + '</span>' : '') +
      '<span>' + esc(CONTENT_TYPE_LABELS[contentType] || "普通图文") + '</span>' +
      '<span>' + esc(data.name || "学校展示") + '</span>' +
      '</div></div>' +
      '<span class="topic-display-code">编号 ' + esc(code) + '</span>' +
      '<h1 class="section-manager-title">' + esc(section.backendPageTitle || displaySectionTitle(section)) + '</h1>' +
      '<div class="section-manager-body">' + bodyHtml + '</div>' +
      '<div class="section-manager-items">' +
      '<div class="section-manager-items-head"><strong>项目列表</strong><em>' + items.length + ' 项</em>' +
      (editMode ? '<button type="button" class="section-manager-add" data-section-add-item="' + esc(section.id) + '">＋ 添加项目</button>' : '') +
      '</div>' +
      '<ul class="section-manager-item-list">' + itemHtml + '</ul>' +
      '</div>' +
      '<footer class="topic-display-footer"><span>学校大屏展示内容</span><span>扫码进入子级展示页</span></footer>' +
      '</article>';
  }

  function formatTopicDisplayDate(value) {
    var text = String(value || "").trim();
    if (!text) return "";
    var date = new Date(text);
    if (Number.isNaN(date.getTime())) return text.slice(0, 10);
    return date.getFullYear() + "年" +
      String(date.getMonth() + 1).padStart(2, "0") + "月" +
      String(date.getDate()).padStart(2, "0") + "日";
  }

  function renderTypedFullBlockSequence(blocks, title, contentType) {
    var type = normalizeContentType(contentType);
    if (type === "person") return renderPersonFullSequence(blocks, title);
    if (type === "attachment") return renderAttachmentFullSequence(blocks, title);
    return renderEntryFullSequence(blocks, title, type);
  }

  /* ---------- 通用条目分组:列表 → 详情 两级展示 ---------- */
  function groupSectionEntries(blocks, title, contentType) {
    var entries = [];
    var current = null;
    function pushEntry(t) {
      current = { title: t || "", texts: [], images: [], videos: [] };
      entries.push(current);
    }
    (blocks || []).forEach(function (b) {
      if (!b) return;
      if (b.type === "video" && (b.src || b.poster)) {
        var ve = { title: b.title || "视频资源", texts: [], images: [], videos: [b] };
        entries.push(ve);
        current = null;
        return;
      }
      if (b.type === "image" && b.src) {
        if (!current) pushEntry(b.caption || "图片资料");
        current.images.push(b);
        return;
      }
      if (b.type === "text") {
        var text = blockText(b);
        if (!text) return;
        if (!current) {
          if (isTopicDisplayHeading(text)) pushEntry(text);
          else { pushEntry(title || "资料"); current.texts.push(text); }
          return;
        }
        if (isTopicDisplayHeading(text) && (current.texts.length || current.images.length || current.videos.length)) {
          pushEntry(text);
          return;
        }
        current.texts.push(text);
      }
    });
    var filtered = [];
    entries.forEach(function (e) {
      var hasContent = e.texts.length + e.images.length + e.videos.length > 0;
      if (!hasContent) {
        if (filtered.length) filtered[filtered.length - 1].title += " " + e.title;
        else filtered.push(e);
        return;
      }
      filtered.push(e);
    });
    return filtered;
  }

  function renderEntryList(entries, title, leadTexts) {
    var leadHtml = (leadTexts && leadTexts.length)
      ? '<div class="topic-entry-lead">' + leadTexts.map(function (t) { return '<p>' + esc(t).replace(/\n/g, "<br>") + '</p>'; }).join("") + '</div>'
      : "";
    if (!entries.length) {
      return leadHtml || '<p>资料正在整理中。</p>';
    }
    var cards = entries.map(function (entry, index) {
      var src = (entry.images[0] && entry.images[0].src) || (entry.videos[0] && entry.videos[0].poster) || "";
      return '<button type="button" class="topic-person-card topic-entry-card" data-entry-index="' + index + '" tabindex="0" aria-label="查看' + esc(entry.title) + '的详细资料">' +
        (src
          ? '<span class="topic-person-card-photo photo-frame" tabindex="-1">' +
            '<img src="' + esc(src) + '" alt="' + esc(entry.title) + '" loading="lazy">' +
            '</span>'
          : '<span class="topic-person-card-photo topic-person-card-photo-empty" aria-hidden="true">' + esc((entry.title || "?").slice(0, 1)) + '</span>') +
        '<strong>' + esc(entry.title) + '</strong>' +
        '<em>查看详情</em>' +
        '</button>';
    }).join("");
    return leadHtml + '<section class="topic-person-grid" aria-label="' + esc(title) + '列表">' +
      '<p class="topic-person-grid-hint">共 ' + entries.length + ' 项,点击卡片查看详情</p>' +
      cards + '</section>';
  }

  function renderEntryDetail(entry, title) {
    var copy = renderTopicTextFlow((entry.texts || []).map(function (t) { return { content: t }; }));
    var photoHtml = entry.images.length
      ? renderTopicDisplayCarousel(entry.images, entry.title || title)
      : "";
    var videoHtml = entry.videos.map(function (b) { return '<div class="topic-display-video">' + renderVideo(b) + '</div>'; }).join("");
    return '<div class="topic-person-detail" data-entry-detail>' +
      '<button type="button" class="topic-person-back" data-entry-back aria-label="返回' + esc(title) + '列表">← 返回列表</button>' +
      '<h2 class="topic-person-name">' + esc(entry.title || title) + '</h2>' +
      (copy ? '<section class="topic-video-copy">' + copy + '</section>' : "") +
      photoHtml + videoHtml +
      '</div>';
  }

  function renderEntryFullSequence(blocks, title, contentType) {
    var all = groupSectionEntries(blocks, title, contentType);
    if (!all.length) return '<p>资料正在整理中。</p>';
    var leadTexts = [];
    var entries = all;
    var first = all[0];
    if (all.length > 1 && (!isTopicDisplayHeading(first.title) || first.title === (title || ""))) {
      leadTexts = first.texts.slice();
      entries = all.slice(1);
    }
    entryDrawerContext = { entries: entries, title: title };
    return renderEntryList(entries, title, leadTexts);
  }

  function splitTopicBlocks(blocks) {
    blocks = blocks || [];
    return {
      texts: blocks.filter(function (b) { return b.type === "text" && String(b.content || "").trim(); }),
      images: blocks.filter(function (b) { return b.type === "image" && b.src; }),
      videos: blocks.filter(function (b) { return b.type === "video" && (b.src || b.poster); }),
      attachments: blocks.filter(function (b) { return b.type === "attachment" && b.href; })
    };
  }

  function renderTopicTextFlow(textBlocks) {
    var html = "";
    (textBlocks || []).forEach(function (block) {
      var text = blockText(block);
      if (!text) return;
      if (isTopicDisplayHeading(text)) html += '<h2>' + esc(text) + '</h2>';
      else html += '<p>' + esc(text).replace(/\n/g, "<br>") + '</p>';
    });
    return html;
  }

  function renderPersonFullSequence(blocks, title) {
    var people = groupPersonBlocks(blocks);
    personDrawerContext = { people: people, title: title };
    if (!people.length) return '<p>人物资料正在整理中。</p>';
    return renderPersonList(people, title);
  }

  function renderPersonList(people, title) {
    var cards = people.map(function (person, index) {
      var src = person.portrait ? person.portrait.src : "";
      return '<button type="button" class="topic-person-card" data-person-index="' + index + '" tabindex="0" aria-label="查看' + esc(person.name) + '的详细资料">' +
        (src
          ? '<span class="topic-person-card-photo photo-frame" tabindex="-1">' +
            '<img src="' + esc(src) + '" alt="' + esc(person.name) + '" loading="lazy">' +
            '</span>'
          : '<span class="topic-person-card-photo topic-person-card-photo-empty" aria-hidden="true">' + esc((person.name || "?").slice(0, 1)) + '</span>') +
        '<strong>' + esc(person.name) + '</strong>' +
        '<em>查看详情</em>' +
        '</button>';
    }).join("");
    return '<section class="topic-person-grid" aria-label="' + esc(title) + '列表">' +
      '<p class="topic-person-grid-hint">共 ' + people.length + ' 位,点击卡片查看详情</p>' +
      cards + '</section>';
  }

  function groupPersonBlocks(blocks) {
    var people = [];
    var current = null;
    function isPersonNameText(text, cur) {
      var t = String(text || "").trim();
      if (!t || t.length > 40) return false;
      if (cur.portrait == null && cur.texts.length === 0) return false;
      if (t.indexOf("——") !== -1) return true;
      return true;
    }
    (blocks || []).forEach(function (b) {
      if (!b) return;
      if (b.type === "video") {
        if (!current) {
          current = { name: b.title || "视频", portrait: null, images: [], texts: [], videos: [] };
          people.push(current);
        }
        current.videos.push(b);
        return;
      }
      if (b.type === "image") {
        if (!current) {
          current = { name: b.caption || "", portrait: null, images: [], texts: [], videos: [] };
          people.push(current);
        }
        if (!current.portrait) {
          current.portrait = b;
          if (!current.name && b.caption) current.name = b.caption;
        } else {
          current.images.push(b);
        }
        return;
      }
      var content = String(b.content || "").trim();
      if (!content) return;
      if (!current) {
        current = { name: content, portrait: null, images: [], texts: [], videos: [] };
        people.push(current);
        return;
      }
      if (isPersonNameText(content, current)) {
        current = { name: content, portrait: null, images: [], texts: [], videos: [] };
        people.push(current);
      } else {
        current.texts.push(content);
      }
    });
    return people;
  }

  function renderPersonDetail(person, title) {
    var copy = renderTopicTextFlow((person.texts || []).map(function (t) { return { content: t }; })) || '<p>人物资料正在整理中。</p>';
    var portrait = person.portrait;
    var portraitHtml = portrait
      ? '<figure class="photo-frame topic-person-portrait" tabindex="0" data-lightbox="' + esc(portrait.src) + '" data-caption="' + esc(portrait.caption || person.name) + '">' +
        '<img src="' + esc(portrait.src) + '" alt="' + esc(portrait.caption || person.name) + '" loading="lazy">' +
        (portrait.caption ? '<figcaption>' + esc(portrait.caption) + '</figcaption>' : "") +
        '</figure>'
      : "";
    var restPhotos = person.images;
    var restPhotoHtml = restPhotos.length
      ? renderTopicDisplayCarousel(restPhotos, person.name || title, "topic-person-gallery")
      : "";
    var videoHtml = person.videos.map(function (b) { return '<div class="topic-display-video">' + renderVideo(b) + '</div>'; }).join("");
    return '<div class="topic-person-detail" data-person-detail>' +
      '<button type="button" class="topic-person-back" data-person-back aria-label="返回' + esc(title) + '列表">← 返回列表</button>' +
      '<h2 class="topic-person-name">' + esc(person.name || title) + '</h2>' +
      '<section class="topic-person-layout">' + portraitHtml +
      '<div class="topic-person-copy">' + copy + '</div></section>' + restPhotoHtml + videoHtml +
      '</div>';
  }

  function renderHonorFullSequence(blocks, title) {
    var grouped = splitTopicBlocks(blocks);
    var photoHtml = grouped.images.length
      ? renderTopicDisplayCarousel(grouped.images, title, "topic-honor-gallery")
      : "";
    var copy = renderTopicTextFlow(grouped.texts) || '<p>荣誉资料正在整理中。</p>';
    var videoHtml = grouped.videos.map(function (b) { return '<div class="topic-display-video">' + renderVideo(b) + '</div>'; }).join("");
    return '<section class="topic-honor-layout">' + photoHtml +
      '<div class="topic-honor-copy">' + copy + '</div></section>' + videoHtml;
  }

  function renderVideoFullSequence(blocks, title) {
    var grouped = splitTopicBlocks(blocks);
    var videoHtml = grouped.videos.map(function (b) { return '<div class="topic-display-video">' + renderVideo(b) + '</div>'; }).join("");
    var copy = renderTopicTextFlow(grouped.texts);
    var photoHtml = grouped.images.length
      ? renderTopicDisplayCarousel(grouped.images, title)
      : "";
    return videoHtml + (copy ? '<section class="topic-video-copy">' + copy + '</section>' : "") + photoHtml || '<p>视频资料正在整理中。</p>';
  }

  function renderAttachmentFullSequence(blocks, title) {
    var grouped = splitTopicBlocks(blocks);
    var copy = renderTopicTextFlow(grouped.texts);
    var attachmentHtml = grouped.attachments.length
      ? '<div class="topic-attachment-list">' + grouped.attachments.map(function (b, index) {
        return renderTopicAttachmentItem(b, index);
      }).join("") + '</div>'
      : '<p>附件资料正在整理中。</p>';
    return (copy ? '<section class="topic-video-copy">' + copy + '</section>' : "") + attachmentHtml;
  }

  function renderTopicAttachmentItem(b, index) {
    return '<a class="topic-attachment-item" href="' + esc(b.href) + '">' +
      '<span>附件 ' + String(index + 1).padStart(2, "0") + '</span>' +
      '<strong>' + esc(b.title || b.href || "查看附件") + '</strong>' +
      '<em>' + esc(b.href || "") + '</em>' +
      '</a>';
  }

  function renderFullBlockSequence(blocks, title) {
    var html = "";
    var photoGroup = [];
    var attachmentIndex = 0;
    var i = 0;
    var flushPhotos = function () {
      if (!photoGroup.length) return;
      html += renderTopicDisplayCarousel(photoGroup, title);
      photoGroup = [];
    };

    blocks = blocks || [];
    while (i < blocks.length) {
      if (isTopicDisplayFeatureStart(blocks, i)) {
        flushPhotos();
        var heading = blockText(blocks[i]);
        var image = blocks[i + 1];
        var paragraphs = [];
        i += 2;
        while (i < blocks.length && !isTopicDisplayFeatureStart(blocks, i)) {
          var next = blocks[i];
          if (next.type === "text") {
            var nextText = blockText(next);
            if (nextText) paragraphs.push(nextText);
            i += 1;
            continue;
          }
          break;
        }
        html += renderTopicDisplayFeatureCard(heading, image, paragraphs, title);
        continue;
      }

      var b = blocks[i];
      if (b.type === "text") {
        var text = String(b.content || "").trim();
        if (text) {
          flushPhotos();
          if (isTopicDisplayHeading(text)) html += '<h2>' + esc(text) + '</h2>';
          else html += '<p>' + esc(text).replace(/\n/g, "<br>") + '</p>';
        }
      } else if (b.type === "image" && b.src) {
        photoGroup.push(b);
      } else if (b.type === "video" && (b.src || b.poster)) {
        flushPhotos();
        html += '<div class="topic-display-video">' + renderVideo(b) + '</div>';
      } else if (b.type === "attachment" && b.href) {
        flushPhotos();
        html += '<div class="topic-attachment-list">' + renderTopicAttachmentItem(b, attachmentIndex) + '</div>';
        attachmentIndex += 1;
      }
      i += 1;
    }
    flushPhotos();
    return html || '<p>资料正在整理中。</p>';
  }

  function blockText(block) {
    return String(block && block.content || "").trim();
  }

  function isTopicDisplayHeading(text) {
    var t = String(text || "").trim();
    return t.length > 0 && t.length <= 34 && !/[。！？；;：:]/.test(t);
  }

  function isTopicDisplayFeatureStart(blocks, index) {
    var current = blocks[index];
    var next = blocks[index + 1];
    return current && next &&
      current.type === "text" &&
      next.type === "image" &&
      next.src &&
      isTopicDisplayHeading(blockText(current));
  }

  function renderTopicDisplayFeatureCard(heading, image, paragraphs, fallbackTitle) {
    var caption = image.caption || heading || fallbackTitle || "图片资料";
    return '<section class="topic-display-feature-card">' +
      '<figure class="photo-frame topic-display-feature-image" tabindex="0" data-lightbox="' + esc(image.src) + '" data-caption="' + esc(caption) + '">' +
      '<img src="' + esc(image.src) + '" alt="' + esc(caption) + '" loading="lazy"></figure>' +
      '<div class="topic-display-feature-copy"><h2>' + esc(heading) + '</h2>' +
      (paragraphs || []).map(function (text) { return '<p>' + esc(text).replace(/\n/g, "<br>") + '</p>'; }).join("") +
      '</div></section>';
  }

  function renderTopicDisplayFigure(b, title, index) {
    var caption = b.caption || "";
    var lightboxCaption = caption || title || ("图片资料 " + index);
    return '<figure class="photo-frame topic-display-photo" tabindex="0" ' +
      'data-lightbox="' + esc(b.src) + '" data-caption="' + esc(lightboxCaption) + '">' +
      '<img src="' + esc(b.src) + '" alt="' + esc(lightboxCaption) + '" loading="lazy">' +
      (caption ? '<figcaption>' + esc(caption) + '</figcaption>' : "") +
      '</figure>';
  }

  function renderTopicDisplayCarousel(images, title, extraClass) {
    var list = (images || []).filter(function (b) { return b && b.src; });
    if (!list.length) return "";
    var count = list.length;
    return '<div class="topic-display-carousel ' + (extraClass ? esc(extraClass) + " " : "") +
      (count > 1 ? 'has-carousel' : 'is-single') +
      '" data-detail-carousel data-media-count="' + count + '">' +
      '<div class="topic-display-carousel-stage">' + list.map(function (b, index) {
        return renderTopicDisplayCarouselSlide(b, title, index);
      }).join("") + '</div>' +
      (count > 1 ? '<div class="topic-loop-counter topic-display-carousel-counter" aria-hidden="true"><span data-carousel-current>1</span><em>/</em><span>' + count + '</span></div>' : '') +
      '</div>';
  }

  function renderTopicDisplayCarouselSlide(b, title, index) {
    var caption = b.caption || "";
    var lightboxCaption = caption || title || ("图片资料 " + (index + 1));
    return '<figure class="photo-frame topic-display-photo topic-display-carousel-slide' +
      (index === 0 ? " is-active" : "") + '" tabindex="0" data-slide-index="' + index + '" ' +
      'data-lightbox="' + esc(b.src) + '" data-caption="' + esc(lightboxCaption) + '">' +
      '<img src="' + esc(b.src) + '" alt="' + esc(lightboxCaption) + '" loading="lazy">' +
      (caption ? '<figcaption>' + esc(caption) + '</figcaption>' : "") +
      '</figure>';
  }

  function stopCarouselTimers(timers) {
    timers.forEach(function (timer) { window.clearInterval(timer); });
    timers.length = 0;
  }

  function startMediaCarousels(root, timers, carouselSelector, slideSelector, baseDelay) {
    stopCarouselTimers(timers);
    if (!root) return;
    root.querySelectorAll(carouselSelector).forEach(function (carousel, carouselIndex) {
      var slides = Array.prototype.slice.call(carousel.querySelectorAll(slideSelector));
      var current = carousel.querySelector("[data-carousel-current]");
      if (slides.length <= 1) return;
      var active = 0;
      var setActive = function (next) {
        active = next % slides.length;
        slides.forEach(function (slide, index) {
          slide.classList.toggle("is-active", index === active);
        });
        if (current) current.textContent = String(active + 1);
      };
      setActive(0);
      var delay = baseDelay + (carouselIndex % 4) * 420;
      timers.push(window.setInterval(function () { setActive(active + 1); }, delay));
    });
  }

  function stopTopicMediaCarousels() {
    stopCarouselTimers(topicMediaCarouselTimers);
  }

  function startTopicMediaCarousels(root) {
    startMediaCarousels(root, topicMediaCarouselTimers, "[data-topic-carousel]", ".topic-loop-slide", 3400);
  }

  function stopDrawerMediaCarousels() {
    stopCarouselTimers(drawerMediaCarouselTimers);
  }

  function startDrawerMediaCarousels(root) {
    startMediaCarousels(root, drawerMediaCarouselTimers, "[data-detail-carousel]", ".topic-display-carousel-slide", 3200);
  }

  function prepareTopicLoop(page) {
    var stageEl = page.querySelector("[data-topic-loop]");
    if (!stageEl) return;
    var track = stageEl.querySelector(".topic-loop-track");
    var sequence = stageEl.querySelector(".topic-loop-sequence");
    var mask = stageEl.querySelector(".topic-loop-mask");
    if (!track || !sequence || !mask) return;
    var measure = function () {
      var gap = parseFloat(getComputedStyle(track).rowGap || "0") || 0;
      var distance = sequence.getBoundingClientRect().height + gap;
      var viewport = mask.getBoundingClientRect().height;
      track.style.setProperty("--topic-loop-distance", distance + "px");
      track.style.setProperty("--topic-loop-shift", "-" + distance + "px");
      track.style.setProperty("--topic-loop-duration", Math.max(36, Math.min(150, Math.round(distance / 24))) + "s");
      stageEl.classList.toggle("is-static", distance <= viewport + 16);
    };
    window.requestAnimationFrame(function () {
      measure();
      window.setTimeout(measure, 420);
    });
    stageEl.querySelectorAll("img").forEach(function (img) {
      if (img.complete) return;
      img.addEventListener("load", measure, { once: true });
      img.addEventListener("error", measure, { once: true });
    });
  }

  function setTopicLoopPaused(paused) {
    screenDetail.classList.toggle("topic-loop-paused", !!paused);
  }

  /* ---------- 块渲染 ---------- */
  function renderBlocks(blocks, section) {
    var preparedBlocks = (blocks || []).map(function (sourceBlock) {
      return normalizeTopicBlock(sourceBlock, section);
    });
    if (state.kind === "topics" && shouldCondenseTopicBlocks(preparedBlocks)) {
      return renderTopicSectionSummary(preparedBlocks, section);
    }
    return renderBlockSequence(preparedBlocks);
  }

  function renderBlockSequence(blocks) {
    var html = "";
    var photoGroup = [];
    var flushPhotos = function () {
      if (!photoGroup.length) return;
      html += '<div class="photo-row">' + photoGroup.map(function (b) {
        return '<figure class="photo-frame' + (photoGroup.length === 1 ? " single" : "") + '" tabindex="0" ' +
          'data-lightbox="' + esc(b.src) + '" data-caption="' + esc(b.caption) + '">' +
          '<img src="' + esc(b.src) + '" alt="' + esc(b.caption) + '" loading="lazy">' +
          (b.caption ? '<figcaption>' + esc(b.caption) + '</figcaption>' : "") +
          '</figure>';
      }).join("") + '</div>';
      photoGroup = [];
    };

    blocks.forEach(function (b) {
      if (b.type === "image") {
        photoGroup.push(b);
        return;
      }
      flushPhotos();
      if (b.type === "text") html += renderText(b.content);
      else if (b.type === "video") html += renderVideo(b);
    });
    flushPhotos();
    return html;
  }

  function shouldCondenseTopicBlocks(blocks) {
    var texts = (blocks || []).filter(function (b) { return b.type === "text" && String(b.content || "").trim(); });
    var total = texts.reduce(function (sum, b) { return sum + String(b.content || "").trim().length; }, 0);
    return texts.length >= 3 || total > 560;
  }

  function compactText(text, limit) {
    text = String(text || "").replace(/\s+/g, " ").trim();
    if (text.length <= limit) return text;
    return text.slice(0, limit) + "...";
  }

  function renderTopicSectionSummary(blocks, section) {
    var texts = blocks.filter(function (b) { return b.type === "text" && String(b.content || "").trim(); })
      .map(function (b) { return String(b.content || "").trim(); });
    var first = texts[0] || displaySectionTitle(section);
    var title = first.length <= 80 ? first : displaySectionTitle(section);
    var rest = title === first ? texts.slice(1) : texts;
    var lead = rest[0] || first;
    var points = rest.slice(1, 5);
    var mediaBlocks = blocks.filter(function (b) { return b.type !== "text"; });
    var fullHtml = '<article class="topic-full-copy"><h2>' + esc(displaySectionTitle(section)) + '</h2>' +
      texts.map(function (text) { return '<p>' + esc(text) + '</p>'; }).join("") +
      '</article>';

    var pointHtml = points.length ? '<ul class="topic-copy-points">' + points.map(function (text) {
      return '<li>' + esc(compactText(text, 96)) + '</li>';
    }).join("") + '</ul>' : "";

    return '<section class="topic-copy-panel">' +
      '<div class="topic-copy-eyebrow">资料摘要</div>' +
      '<div class="topic-copy-head"><h3>' + esc(title) + '</h3>' +
      '<button class="more-btn topic-copy-action" data-full="' + esc(fullHtml) + '">查看完整资料</button></div>' +
      '<p class="topic-copy-lead">' + esc(compactText(lead, 280)) + '</p>' +
      pointHtml +
      '</section>' +
      renderBlockSequence(mediaBlocks);
  }

  function renderText(content) {
    var t = String(content || "").trim();
    if (!t) return "";
    var cls = "text-block";
    if (t.length <= 60) cls += " lead";
    var inner = esc(t).replace(/\n/g, "<br>");
    if (t.length > LONG_TEXT_LIMIT) {
      var brief = esc(t.slice(0, LONG_TEXT_LIMIT)) + "…";
      var full = inner;
      return '<div class="' + cls + '"><span class="tb-brief">' + brief + '</span>' +
        '<button class="more-btn" data-full="' + esc(full) + '">阅读全文 <span aria-hidden="true">→</span></button></div>';
    }
    return '<div class="' + cls + '">' + inner + "</div>";
  }

  function renderVideo(b) {
    return '<div class="video-player" data-vsrc="' + esc(b.src) + '" data-poster="' + esc(b.poster || "") + '">' +
      '<video preload="metadata" playsinline muted loop></video>' +
      '<div class="video-poster">' +
      (b.poster ? '<img src="' + esc(b.poster) + '" alt="' + esc(b.title) + '">' : "") +
      '<div class="v-overlay">' +
      '<div class="v-play" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z" fill="currentColor"/></svg></div>' +
      '<div class="v-info"><div class="v-title">' + esc(b.title || "视频资源") + '</div>' +
      (b.duration ? '<div class="v-duration">时长 ' + esc(b.duration) + '</div>' : "") +
      '</div></div></div>' +
      '<div class="video-controls">' +
      '<button class="vc-btn vc-toggle" aria-label="播放/暂停">' +
      '<svg class="ic-play" viewBox="0 0 24 24"><path d="M8 5v14l11-7z" fill="currentColor"/></svg>' +
      '<svg class="ic-pause" viewBox="0 0 24 24" hidden><path d="M6 5h4v14H6zM14 5h4v14h-4z" fill="currentColor"/></svg></button>' +
      '<div class="vc-progress" role="slider" aria-label="播放进度" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0"><div class="vc-fill"></div></div>' +
      '<span class="vc-time">0:00 / 0:00</span>' +
      '<button class="vc-btn vc-mute" aria-label="静音/取消静音">' +
      '<svg class="ic-vol" viewBox="0 0 24 24"><path d="M3 9v6h4l5 5V4L7 9H3z" fill="currentColor"/><path d="M16 8a5 5 0 010 8M18.5 5.5a9 9 0 010 13" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg></button>' +
      '<button class="vc-btn vc-full" aria-label="全屏">' +
      '<svg viewBox="0 0 24 24"><path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></button>' +
      '</div></div>';
  }

  /* ---------- 视频播放器逻辑 ---------- */
  function bindVideos(root) {
    root.querySelectorAll(".video-player").forEach(function (box) {
      var video = box.querySelector("video");
      var poster = box.querySelector(".video-poster");
      var toggle = box.querySelector(".vc-toggle");
      var progress = box.querySelector(".vc-progress");
      var fill = box.querySelector(".vc-fill");
      var timeEl = box.querySelector(".vc-time");
      var mute = box.querySelector(".vc-mute");
      var full = box.querySelector(".vc-full");
      video.src = box.dataset.vsrc;
      video.poster = box.dataset.poster || "";

      var fmt = function (s) {
        if (!isFinite(s)) return "0:00";
        var m = Math.floor(s / 60), sec = Math.floor(s % 60);
        return m + ":" + String(sec).padStart(2, "0");
      };
      var update = function () {
        if (video.duration) {
          fill.style.width = (video.currentTime / video.duration * 100) + "%";
          timeEl.textContent = fmt(video.currentTime) + " / " + fmt(video.duration);
          progress.setAttribute("aria-valuenow", Math.round(video.currentTime / video.duration * 100));
        }
      };
      var play = function () {
        state.playingVideo = true;
        box.classList.add("playing");
        poster.hidden = true;
        video.play().catch(function () {});
      };
      var pause = function () {
        state.playingVideo = false;
        box.classList.remove("playing");
        video.pause();
      };

      poster.addEventListener("click", play);
      toggle.addEventListener("click", function () {
        if (video.paused) play(); else pause();
      });
      video.addEventListener("timeupdate", update);
      video.addEventListener("ended", function () {
        state.playingVideo = false;
        box.classList.remove("playing");
        poster.hidden = false;
        video.currentTime = 0;
      });
      video.addEventListener("pause", function () { state.playingVideo = false; box.classList.remove("playing"); });
      video.addEventListener("play", function () { state.playingVideo = true; box.classList.add("playing"); });

      progress.addEventListener("click", function (e) {
        var r = progress.getBoundingClientRect();
        if (video.duration) video.currentTime = (e.clientX - r.left) / r.width * video.duration;
      });
      mute.addEventListener("click", function () { video.muted = !video.muted; });
      full.addEventListener("click", function () {
        if (document.fullscreenElement) document.exitFullscreen();
        else if (box.requestFullscreen) box.requestFullscreen();
      });
      video.addEventListener("click", function () {
        if (video.paused) play(); else pause();
      });
      // 播放中暂停空闲计时
      video.addEventListener("play", resetIdle);
      video.addEventListener("pause", resetIdle);
    });
  }

  /* ---------- 灯箱 ---------- */
  function openLightbox(src, caption) {
    var figures = Array.prototype.slice.call(document.querySelectorAll(".photo-frame[data-lightbox]"));
    lbImages = figures.map(function (f) {
      return { src: f.dataset.lightbox, caption: f.dataset.caption || "" };
    });
    lbIndex = Math.max(0, lbImages.findIndex(function (f) { return f.src === src; }));
    showLightbox();
  }
  function showLightbox() {
    var img = $("lbImage");
    img.src = lbImages[lbIndex].src;
    $("lbCaption").textContent = lbImages[lbIndex].caption;
    $("lightbox").hidden = false;
    setTopicLoopPaused(true);
    pauseDrawerAutoLoop(120000);
    $("lbClose").focus();
    resetIdle();
  }
  function closeLightbox() {
    $("lightbox").hidden = true;
    setTopicLoopPaused(!$("drawer").hidden);
    pauseDrawerAutoLoop(500);
  }

  /* ---------- 抽屉 ---------- */
  function drawerLoopContent(fullHtml) {
    return fullHtml;
  }

  function stopDrawerAutoLoop() {
    if (drawerLoopTimer) window.clearInterval(drawerLoopTimer);
    drawerLoopTimer = null;
    drawerLoopLastAt = 0;
    drawerLoopCycle = 0;
    drawerLoopPauseUntil = 0;
    if ($("drawerBody")) $("drawerBody").classList.remove("drawer-loop-static");
  }

  function measureDrawerLoop() {
    var body = $("drawerBody");
    var track = body && body.querySelector("[data-drawer-loop-track]");
    var sequence = body && body.querySelector("[data-drawer-loop-sequence]");
    if (!body || !track || !sequence) return 0;
    var gap = parseFloat(window.getComputedStyle(track).rowGap || "0") || 0;
    drawerLoopCycle = sequence.getBoundingClientRect().height + gap;
    var isStatic = drawerLoopCycle <= body.clientHeight + 24;
    body.classList.toggle("drawer-loop-static", isStatic);
    if (isStatic) body.scrollTop = 0;
    return drawerLoopCycle;
  }

  function pauseDrawerAutoLoop(ms) {
    drawerLoopPauseUntil = Date.now() + (ms || DRAWER_LOOP_RESUME_MS);
    drawerLoopLastAt = 0;
  }

  function startDrawerAutoLoop() {
    var body = $("drawerBody");
    if (!body) return;
    body.scrollTop = 0;
    drawerLoopLastAt = 0;
    drawerLoopPauseUntil = Date.now() + 900;
    window.requestAnimationFrame(function () {
      measureDrawerLoop();
      window.setTimeout(measureDrawerLoop, 420);
      body.querySelectorAll("img").forEach(function (img) {
        if (img.complete) return;
        img.addEventListener("load", measureDrawerLoop, { once: true });
        img.addEventListener("error", measureDrawerLoop, { once: true });
      });
    });
  }

  function stepDrawerAutoLoop() {
    var body = $("drawerBody");
    if (!body || $("drawer").hidden) {
      stopDrawerAutoLoop();
      return;
    }
    if (!drawerLoopCycle) measureDrawerLoop();
    var now = Date.now();
    if (!drawerLoopLastAt) drawerLoopLastAt = now;
    var delta = Math.min(80, now - drawerLoopLastAt) / 1000;
    drawerLoopLastAt = now;

    if (drawerLoopCycle > body.clientHeight + 24 && now >= drawerLoopPauseUntil && !state.playingVideo && $("lightbox").hidden) {
      var next = body.scrollTop + delta * DRAWER_LOOP_SPEED;
      while (next >= drawerLoopCycle) next -= drawerLoopCycle;
      body.scrollTop = next;
    }
  }

  function closeDrawer() {
    $("drawer").hidden = true;
    stopDrawerAutoLoop();
    stopDrawerMediaCarousels();
    setTopicLoopPaused(false);
  }

  function openDrawer(fullHtml) {
    stopDrawerAutoLoop();
    stopDrawerMediaCarousels();
    var isTopicDrawer = state.kind === "topics";
    $("drawer").classList.toggle("topic-reader-drawer", isTopicDrawer);
    $("drawerBody").classList.toggle("drawer-loop-static", isTopicDrawer);
    $("drawerBody").innerHTML = isTopicDrawer ? fullHtml : drawerLoopContent(fullHtml);
    $("drawerBody").scrollTop = 0;
    bindVideos($("drawerBody"));
    prepareAdaptiveMedia($("drawerBody"), measureDrawerLoop);
    $("drawer").hidden = false;
    setTopicLoopPaused(true);
    startDrawerMediaCarousels($("drawerBody"));
    if (!isTopicDrawer) startDrawerAutoLoop();
    $("drawerClose").focus();
  }

  /* ---------- 空闲返回 ---------- */
  function resetIdle() {
    clearTimeout(idleTimer);
    if (screenHome.hidden && !state.playingVideo && state.kind !== "topics") {
      idleTimer = setTimeout(goHome, IDLE_MS);
    }
  }
  function goHome(options) {
    options = options || {};
    if (state.playingVideo) { resetIdle(); return; }
    stopTopicMediaCarousels();
    stopTopicCoverflowCarousels();
    screenDetail.classList.remove("department-showcase-mode");
    screenDetail.classList.remove("topic-loop-mode", "topic-loop-paused");
    syncDepartmentSwitch("home", "");
    renderHome();
    if (!options.skipHistory && location.pathname !== "/departments") {
      if (options.pushHistory) history.pushState(null, "", "/departments");
      else history.replaceState(null, "", "/departments");
    }
  }

  /* ---------- SSE 扫码联动 ---------- */
  function connectSse() {
    if (!window.EventSource) return;
    var es = new EventSource("/api/display/events");
    es.addEventListener("scan", function (ev) {
      var scan;
      try { scan = JSON.parse(ev.data); } catch (e) { return; }
      state.lastScanAt = Date.now();
      var url = (scan && (scan.url || scan.displayUrl || "")) || "";
      // 兼容相对与绝对 URL（二维码扫码得到绝对 URL）
      var u;
      try { u = new URL(url, location.origin); } catch (e) { return; }
      var m = u.pathname.match(/^\/(departments|topics)\/([a-z0-9-]+)/);
      if (!m) return;
      var kind = m[1], id = m[2];
      var list = kind === "departments" ? DATA.departments : DATA.topics;
      if (!list[id]) return;
      var secIdx = 0;
      var sec = u.searchParams.get("section");
      if (sec) {
        var idx = list[id].sections.findIndex(function (s) { return s.id === sec; });
        if (idx >= 0) secIdx = idx;
      }
      // 已在该页且同章节则不做动作
      if (state.kind === kind && state.id === id && state.section === secIdx) return;
      openDetail(kind, id, secIdx);
    });
    es.onerror = function () { /* 自动重连 */ };
  }

  /* ---------- 键盘 ---------- */
  function bindKeys() {
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") {
        var openExperience = document.querySelector(".topic-experience-action.is-open");
        if (openExperience) { setTopicExperienceMenu(openExperience, false); return; }
        if (!$("lightbox").hidden) { closeLightbox(); return; }
        if (!$("drawer").hidden) { closeDrawer(); return; }
        if (!screenHome.hidden) return;
        goHome();
        return;
      }
      if (screenDetail.hidden) return;
      var tag = (e.target && e.target.tagName) || "";
      if (tag === "INPUT" || tag === "TEXTAREA") return;
      if (e.key === "ArrowRight") { e.preventDefault(); goSection(Math.min(state.section + 1, state.sections.length - 1)); }
      if (e.key === "ArrowLeft") { e.preventDefault(); goSection(Math.max(state.section - 1, 0)); }
    });
  }

  /* ---------- 事件委托 ---------- */
  function bindDelegates() {
    $("backHome").addEventListener("click", function (e) { e.preventDefault(); goHome(); });
    $("departmentSwitch").addEventListener("change", function (e) {
      var id = e.target.value;
      var kind = e.target.dataset.kind || "departments";
      if (id && (id !== state.id || kind !== state.kind)) openDetail(kind, id, 0);
    });
    $("prevChapter").addEventListener("click", function () { goSection(Math.max(state.section - 1, 0)); });
    $("nextChapter").addEventListener("click", function () { goSection(Math.min(state.section + 1, state.sections.length - 1)); });

    $("chapterPage").addEventListener("click", function (e) {
      var experienceClose = e.target.closest(".topic-experience-close");
      if (experienceClose) {
        setTopicExperienceMenu(experienceClose.closest(".topic-experience-action"), false);
        return;
      }
      var experienceTrigger = e.target.closest(".topic-experience-trigger");
      if (experienceTrigger) {
        var action = experienceTrigger.closest(".topic-experience-action");
        var willOpen = experienceTrigger.getAttribute("aria-expanded") !== "true";
        closeTopicExperienceMenus(action);
        setTopicExperienceMenu(action, willOpen);
        return;
      }
      var more = e.target.closest(".more-btn");
      if (more) { openDrawer(more.dataset.full); return; }
      var showCard = e.target.closest(".showcase-card[data-full]");
      if (showCard) { openDepartmentModule(showCard.dataset.module || "overview"); return; }
      var moduleButton = e.target.closest("[data-module]");
      if (moduleButton) { openDepartmentModule(moduleButton.dataset.module); return; }
      var rail = e.target.closest("[data-go-kind][data-go-id]");
      if (rail) { openDetail(rail.dataset.goKind, rail.dataset.goId, 0); return; }
      if (e.target.closest(".experience-link")) return;
      var topicSectionOpen = e.target.closest(".topic-section-open[data-section-id]");
      if (topicSectionOpen) { openTopicLoopSection(topicSectionOpen.dataset.sectionId); return; }
      var coopEnter = e.target.closest("[data-coop-enter]");
      if (coopEnter) { openTopicLoopSection("cooperation"); return; }
      var coopPhotoEdit = e.target.closest(".topic-showcase-coop-photo .inline-edit-media-button");
      if (coopPhotoEdit) return;
      var videoMore = e.target.closest("[data-video-more]");
      if (videoMore) { openVideoList(); return; }
      var topicSectionJump = e.target.closest("[data-section-index]");
      if (topicSectionJump) { goSection(Number(topicSectionJump.dataset.sectionIndex)); return; }
      var topicLoopCard = e.target.closest(".topic-loop-card[data-section-id]");
      if (topicLoopCard) { openTopicLoopSection(topicLoopCard.dataset.sectionId); return; }
      var showcaseMini = e.target.closest(".topic-showcase-mini[data-section-id]");
      if (showcaseMini) { openTopicLoopSection(showcaseMini.dataset.sectionId); return; }
      var showcaseSection = e.target.closest(".topic-showcase-partner[data-section-id], .topic-showcase-video-box[data-section-id]");
      if (showcaseSection) { openTopicLoopSection(showcaseSection.dataset.sectionId); return; }
      var frame = e.target.closest(".photo-frame[data-lightbox]");
      if (frame) openLightbox(frame.dataset.lightbox, frame.dataset.caption);
    });
    document.addEventListener("click", function (e) {
      if (!e.target.closest(".topic-experience-action")) closeTopicExperienceMenus();
    });
    $("chapterPage").addEventListener("keydown", function (e) {
      if ((e.key === "Enter" || e.key === " ") && e.target.classList.contains("topic-loop-card")) {
        e.preventDefault();
        openTopicLoopSection(e.target.dataset.sectionId);
        return;
      }
      if ((e.key === "Enter" || e.key === " ") && e.target.classList.contains("topic-showcase-mini")) {
        e.preventDefault();
        openTopicLoopSection(e.target.dataset.sectionId);
        return;
      }
      if ((e.key === "Enter" || e.key === " ") &&
          (e.target.classList.contains("topic-showcase-partner") || e.target.classList.contains("topic-showcase-video-box"))) {
        e.preventDefault();
        openTopicLoopSection(e.target.dataset.sectionId);
        return;
      }
      if ((e.key === "Enter" || e.key === " ") && e.target.classList.contains("photo-frame")) {
        e.preventDefault();
        openLightbox(e.target.dataset.lightbox, e.target.dataset.caption);
      }
    });
    // 章节渲染后绑定视频
    var mo = new MutationObserver(function () { bindVideos($("chapterPage")); });
    mo.observe($("chapterPage"), { childList: true });

    $("lbClose").addEventListener("click", closeLightbox);
    $("lbPrev").addEventListener("click", function () { lbIndex = (lbIndex - 1 + lbImages.length) % lbImages.length; showLightbox(); });
    $("lbNext").addEventListener("click", function () { lbIndex = (lbIndex + 1) % lbImages.length; showLightbox(); });
    $("lightbox").addEventListener("click", function (e) { if (e.target === this) closeLightbox(); });
    $("drawerClose").addEventListener("click", closeDrawer);
    $("drawer").addEventListener("click", function (e) {
      if (e.target === this) closeDrawer();
    });
    $("drawerBody").addEventListener("click", function (e) {
      var personCard = e.target.closest(".topic-person-card[data-person-index]");
      if (personCard && personDrawerContext) {
        var person = personDrawerContext.people[Number(personCard.dataset.personIndex)];
        if (person) openDrawer(renderPersonDetail(person, personDrawerContext.title));
        return;
      }
      var personBack = e.target.closest("[data-person-back]");
      if (personBack && personDrawerContext) {
        openDrawer(renderPersonList(personDrawerContext.people, personDrawerContext.title));
        return;
      }
      var entryCard = e.target.closest(".topic-entry-card[data-entry-index]");
      if (entryCard && entryDrawerContext) {
        var entry = entryDrawerContext.entries[Number(entryCard.dataset.entryIndex)];
        if (entry) openDrawer(renderEntryDetail(entry, entryDrawerContext.title));
        return;
      }
      var entryBack = e.target.closest("[data-entry-back]");
      if (entryBack && entryDrawerContext) {
        openDrawer(renderEntryList(entryDrawerContext.entries, entryDrawerContext.title));
        return;
      }
      var frame = e.target.closest(".photo-frame[data-lightbox]");
      if (frame) openLightbox(frame.dataset.lightbox, frame.dataset.caption);
    });
    ["wheel", "pointerdown", "keydown"].forEach(function (evt) {
      $("drawerBody").addEventListener(evt, function () { pauseDrawerAutoLoop(); }, { passive: true });
    });

    // 全局触摸/键盘重置空闲
    ["pointerdown", "keydown", "wheel"].forEach(function (evt) {
      document.addEventListener(evt, resetIdle, { passive: true });
    });
  }

  function setTopicExperienceMenu(action, open) {
    if (!action) return;
    var trigger = action.querySelector(".topic-experience-trigger");
    var menu = action.querySelector(".topic-experience-menu");
    if (!trigger || !menu) return;
    trigger.setAttribute("aria-expanded", open ? "true" : "false");
    action.classList.toggle("is-open", open);
    menu.hidden = !open;
    if (open) {
      var firstLink = menu.querySelector("a");
      if (firstLink) firstLink.focus({ preventScroll: true });
    } else if (menu.contains(document.activeElement)) {
      trigger.focus({ preventScroll: true });
    }
  }

  function closeTopicExperienceMenus(except) {
    document.querySelectorAll(".topic-experience-action.is-open").forEach(function (action) {
      if (action !== except) setTopicExperienceMenu(action, false);
    });
  }

  /* ---------- 启动 ---------- */
  function fitCanvas() {
    // DESIGN.md 4.3: 1920×1080 基准画布等比缩放居中，窗口比例不一致时不重新布局
    var s = Math.min(window.innerWidth / 1920, window.innerHeight / 1080);
    stage.style.setProperty("--bp-scale", String(Math.max(0.4, s)));
  }
  function boot() {
    fitCanvas();
    window.addEventListener("resize", fitCanvas);
    loadData().then(loadPortalHome).then(loadPortalContent).then(loadPortalChrome).then(function () {
      applyPortalChrome();
      bindUnityStartLink();
      initDepartmentSwitch();
      bindDelegates();
      bindKeys();
      connectSse();
      var route = parsePath();
      if (route.kind === "home") {
        renderHome();
        renderSchoolQr($("homeQr"));
      } else {
        openDetail(route.kind, route.id, route.section, { replaceHistory: true });
      }
      window.addEventListener("popstate", function () {
        var r = parsePath();
        if (r.kind === "home") goHome({ skipHistory: true });
        else if (r.id && (r.id !== state.id || r.kind !== state.kind)) openDetail(r.kind, r.id, r.section, { skipHistory: true });
        else if (r.id) goSection(r.section, { skipHistory: true });
      });
      window.addEventListener("pagehide", function () {
        stopTopicMediaCarousels();
        stopTopicCoverflowCarousels();
        stopDrawerMediaCarousels();
        stopDrawerAutoLoop();
      });
      window.addEventListener("pageshow", function (event) {
        if (!event.persisted) return;
        restoreRouteFromCache();
      });
    });
  }

  function restoreRouteFromCache() {
    fitCanvas();
    loadPortalHome().then(loadPortalContent).then(loadPortalChrome)
      .catch(function () { /* keep cached data */ })
      .then(function () {
        applyPortalChrome();
        var route = parsePath();
        if (route.kind === "home") {
          goHome({ skipHistory: true });
          renderSchoolQr($("homeQr"));
        } else if (route.id) {
          openDetail(route.kind, route.id, route.section, { skipHistory: true });
        }
      });
  }
  boot();
})();
