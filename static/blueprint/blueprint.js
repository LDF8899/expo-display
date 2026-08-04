/* ============================================================
   毕节职业技术学院数字门户展厅 · 蓝图展陈
   数据驱动 SPA: /departments 学校门户, /departments/<id> 与 /topics/<id> 二级门户
   ============================================================ */
(function () {
  "use strict";

  var DATA = { departments: {}, topics: {} };
  var PORTAL_CHROME = {
    logoImageUrl: "/uploads/acc2be26d71f4981b3c1f125390266a8.png",
    navText: "社会服务 · 国际交流 · 育人成果 · 名师名匠",
    schoolQrImageUrl: "/uploads/fad5544323334f97a45f6afcf1eac08c.jpg"
  };
  var ORDER = {
    departments: ["mining-construction", "finance", "information", "medical-nursing", "tourism"],
    topics: [
      "modern-agriculture",
      "digital-tourism",
      "smart-healthcare",
      "finance-commerce",
      "digital-intelligence",
      "smart-energy",
      "smart-manufacturing",
      "smart-construction",
      "campus-culture"
    ]
  };
  var DEPT_SUMMARY = {
    "mining-construction": "智慧矿山、智能制造与现代建造",
    "finance": "数字商贸、智慧物流与财务实践",
    "information": "人工智能、网络安全与数字技术",
    "medical-nursing": "临床护理、康养服务与急救教育",
    "tourism": "数字文旅、酒店运营与烹饪技艺"
  };
  var TOPIC_SUMMARY = {
    "modern-agriculture": "山地特色农业、乡村振兴与数字化生产服务",
    "digital-tourism": "数字文旅、酒店运营、烹饪技艺与服务场景",
    "smart-healthcare": "护理康养、急救教育、健康管理与服务运营",
    "smart-energy": "绿色能源、智能开采与化工安全",
    "smart-manufacturing": "智能装备、新能源汽车与无人机应用",
    "finance-commerce": "数字商贸、电商物流与产教融合",
    "digital-intelligence": "人工智能、网络安全、数据应用与跨专业赋能",
    "smart-construction": "现代建造、工程管理、测绘应用与绿色施工",
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
    "smart-construction": ["工矿建筑系", "电子信息工程系", "财政经济系"],
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
    video: "视频类"
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
  var idleTimer = null, lbImages = [], lbIndex = 0, topicMediaCarouselTimers = [];
  var drawerLoopTimer = null, drawerLoopLastAt = 0, drawerLoopCycle = 0, drawerLoopPauseUntil = 0;
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
    var base = "/" + kind + "/" + id;
    if (section != null) {
      var data = (kind === "departments" ? DATA.departments : DATA.topics)[id];
      var sec = sectionsForPortal(kind, data)[section];
      if (sec) base += "?section=" + encodeURIComponent(sec.id);
    }
    return base;
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

  /* ---------- 二维码 ---------- */
  function loadPortalContent() {
    var jobs = [];
    ["departments", "topics"].forEach(function (kind) {
      ORDER[kind].forEach(function (id) {
        jobs.push(fetch("/api/portal/" + kind + "/" + encodeURIComponent(id))
          .then(function (r) { return r.ok ? r.json() : null; })
          .then(function (payload) { mergePortalPayload(kind, id, payload); })
          .catch(function () { /* static blueprint data remains the fallback */ }));
      });
    });
    return Promise.all(jobs);
  }

  function mergePortalPayload(kind, id, payload) {
    if (!payload || !payload.ok || !payload.project || !payload.pages || !payload.pages.length) return;
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
        var link = node.querySelector("figcaption a[href]");
        var caption = node.querySelector("figcaption");
        var title = node.querySelector("strong, h2, h3");
        var href = link ? link.getAttribute("href") : "";
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
      if (/^(p|li|blockquote|h2|h3|h4)$/.test(tag)) {
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
      if (!block || (block.type !== "image" && block.type !== "video")) return true;
      var key = block.type + ":" + (block.src || "");
      if (!block.src || seen[key]) return false;
      seen[key] = true;
      return true;
    });
  }

  function loadPortalChrome() {
    return fetch("/api/display/project")
      .then(function (r) { return r.json(); })
      .then(function (payload) {
        var config = payload && payload.project && payload.project.displayConfig;
        if (!config) return;
        PORTAL_CHROME.logoImageUrl = String(config.logoImageUrl || PORTAL_CHROME.logoImageUrl).trim();
        PORTAL_CHROME.navText = String(config.schoolMeta || PORTAL_CHROME.navText).trim();
        PORTAL_CHROME.schoolQrImageUrl = String(config.scanImageUrl || PORTAL_CHROME.schoolQrImageUrl).trim();
      })
      .catch(function () { /* 使用本地默认配置 */ });
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
  }

  function bindUnityStartLink() {
    document.addEventListener("click", function (event) {
      var link = event.target.closest(".unity-test-link[data-unity-start]");
      if (!link) return;
      event.preventDefault();
      var target = window.open("about:blank", "_blank");
      var go = function (url) {
        if (target) target.location.href = url;
        else window.location.href = url;
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
    return '<button class="showcase-card' + (missing ? " is-missing" : "") + '" type="button" data-module="' + esc(moduleId) + '" data-full="' + full + '">' +
      '<span class="showcase-kicker">' + esc(kicker) + '<em>' + esc(status) + '</em></span>' +
      '<strong>' + esc(title) + '</strong>' +
      '<p>' + esc(body) + '</p></button>';
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
      '<div class="showcase-module-grid">' + moduleHtml + '</div></article>' +
      '<article class="showcase-panel teaching-panel"><div class="showcase-panel-head"><h3>图像资料</h3><span>代表场景</span></div>' +
      '<figure class="showcase-media photo-frame" tabindex="0" data-lightbox="' + esc(hero.src) + '" data-caption="' + esc(hero.caption || data.name) + '">' +
      (hero.src ? '<img src="' + esc(hero.src) + '" alt="' + esc(hero.caption || data.name) + '" loading="lazy">' : '<div class="showcase-slot">图片待放置</div>') +
      '<figcaption><h4>' + esc(hero.caption || "教学成果展示区") + '</h4><p>' + esc(clipText(achievements || overview, 68)) + '</p></figcaption></figure>' +
      galleryHtml + '</article>' +
      '<article class="showcase-panel video-panel"><div class="showcase-panel-head"><h3>视频资源</h3><span>播放区</span></div>' +
      videoHtml + '</article>' +
      '</div></section>';
  }

  /* ---------- 一级页 ---------- */
  function renderHome() {
    setPortalDocumentTitle("学校门户");
    var grid = $("fusionGrid");
    grid.innerHTML = "";
    ORDER.topics.forEach(function (id) {
      var t = DATA.topics[id];
      if (!t) return;
      var departments = TOPIC_DEPARTMENTS[id] || [];
      var chips = departments.map(function (name) {
        var deptId = departmentIdForName(name);
        if (!deptId) return "";
        return '<button type="button" class="dept-chip" data-go-id="' + esc(deptId) + '">' + esc(name) + '</button>';
      }).join("");
      var card = document.createElement("article");
      card.className = "fusion-card";
      card.tabIndex = 0;
      card.setAttribute("role", "button");
      card.setAttribute("aria-label", "进入" + t.name + "专题页");
      card.innerHTML =
        '<img class="fusion-photo" src="' + esc(t.cover) + '" alt="" loading="lazy">' +
        '<div class="fusion-shade"></div>' +
        '<div class="fusion-copy">' +
        '<span class="fusion-label">创新育人专题</span>' +
        '<h3>' + esc(t.name) + '</h3>' +
        '<p>' + esc(TOPIC_SUMMARY[id] || t.summary) + '</p>' +
        '<div class="fusion-depts">' + chips + '</div>' +
        '</div>' +
        '<span class="fusion-arrow" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></span>';
      var go = function () { openDetail("topics", id, 0); };
      card.addEventListener("click", function (e) {
        if (e.target.closest(".dept-chip")) return;
        go();
      });
      card.addEventListener("keydown", function (e) {
        if (e.key === "Enter" || e.key === " ") { e.preventDefault(); go(); }
      });
      Array.prototype.forEach.call(card.querySelectorAll(".dept-chip"), function (chip) {
        chip.addEventListener("click", function (e) {
          e.stopPropagation();
          openDetail("departments", chip.dataset.goId, 0);
        });
      });
      var photo = card.querySelector(".fusion-photo");
      if (photo) photo.addEventListener("error", function () { photo.style.display = "none"; }, { once: true });
      grid.appendChild(card);
    });
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
    screenDetail.classList.toggle("department-showcase-mode", kind === "departments");
    screenDetail.classList.toggle("topic-loop-mode", kind === "topics");
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
    page.style.animation = "none";
    void page.offsetWidth;
    page.style.animation = "";

    page.innerHTML = renderTopicLoopPage(data);
    startTopicMediaCarousels(page);
    prepareAdaptiveMedia(page, function () { prepareTopicLoop(page); });
    $("progressLabel").textContent =
      String(state.section + 1).padStart(2, "0") + " / " +
      String(state.sections.length).padStart(2, "0");
    $("prevChapter").disabled = state.section === 0;
    $("nextChapter").disabled = state.section === state.sections.length - 1;
    prepareTopicLoop(page);
  }

  function renderDepartmentDetail() {
    var data = getData();
    var page = $("chapterPage");
    stopTopicMediaCarousels();
    page.style.animation = "none";
    void page.offsetWidth;
    page.style.animation = "";
    screenDetail.classList.remove("topic-loop-mode");
    page.innerHTML = renderDepartmentShowcase(data);
    prepareAdaptiveMedia(page);
    $("progressLabel").textContent = "";
    $("prevChapter").disabled = true;
    $("nextChapter").disabled = true;
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
    var texts = blocks.filter(function (b) { return b.type === "text" && String(b.content || "").trim(); })
      .map(function (b) { return String(b.content || "").trim(); });
    var mediaBlocks = blocks.filter(function (b) {
      return (b.type === "image" && b.src) || (b.type === "video" && (b.poster || b.src));
    });
    var first = texts[0] || displaySectionTitle(section);
    var title = first.length <= 34 ? first : displaySectionTitle(section);
    var rest = title === first ? texts.slice(1) : texts;
    return {
      title: title,
      lead: rest[0] || first,
      points: rest.slice(1, 5),
      media: mediaBlocks
    };
  }

  function renderTopicLoopPage(data) {
    var sections = orderedTopicSections();
    var statHtml = (data.stats || []).slice(0, 4).map(function (s) {
      return '<div class="topic-loop-stat"><b>' + esc(s.value) + '</b><span>' + esc(s.label) + '</span></div>';
    }).join("");
    var sectionsHtml = sections.map(function (section) {
      var originalIndex = state.sections.indexOf(section);
      return renderTopicLoopSection(section, originalIndex, false);
    }).join("");
    var cloneHtml = sections.map(function (section) {
      var originalIndex = state.sections.indexOf(section);
      return renderTopicLoopSection(section, originalIndex, true);
    }).join("");
    return '<section class="topic-loop-stage" data-topic-loop>' +
      '<header class="topic-loop-hero">' +
      '<div class="topic-loop-title"><span>Topic Showcase</span><h2>' + esc(data.name || "专题门户") + '</h2>' +
      '<p>' + esc(data.summary || TOPIC_SUMMARY[data.id] || "围绕重点专业群、成果资源和展示素材组织专题内容。") + '</p></div>' +
      '<div class="topic-loop-stats">' + statHtml + '</div>' +
      '</header>' +
      '<div class="topic-loop-mask">' +
      '<div class="topic-loop-track">' +
      '<div class="topic-loop-sequence">' + sectionsHtml + '</div>' +
      '<div class="topic-loop-sequence topic-loop-clone" aria-hidden="true">' + cloneHtml + '</div>' +
      '</div>' +
      '</div>' +
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
    var fallback = [{ type: "image", src: data.cover || "", caption: data.name || displaySectionTitle(section) }];
    var list = (mediaBlocks.length ? mediaBlocks : fallback).filter(function (b) {
      if (!b) return false;
      if (b.type === "video") return !!(b.poster || b.src || data.cover);
      return !!b.src;
    });
    if (!list.length) list = fallback;
    var count = list.length;
    return '<div class="topic-loop-media' + (count > 1 ? ' has-carousel' : ' is-single') +
      '" data-topic-carousel data-media-count="' + count + '">' +
      '<div class="topic-loop-carousel">' + list.map(function (b, index) {
        return renderTopicLoopSlide(b, data, section, index);
      }).join("") + '</div>' +
      (count > 1 ? '<div class="topic-loop-counter" aria-hidden="true"><span data-carousel-current>1</span><em>/</em><span>' + count + '</span></div>' : '') +
      '</div>';
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
  }

  function renderTopicFullSection(section) {
    var data = getData();
    var blocks = (section.blocks || []).map(function (sourceBlock) {
      return normalizeTopicBlock(sourceBlock, section);
    });
    var intro = data.summary || TOPIC_SUMMARY[data.id] || "";
    var code = section.backendPageCode || (data.id ? data.id + "-" + section.id : section.id);
    var updated = formatTopicDisplayDate(section.backendUpdatedAt);
    var contentType = normalizeContentType(section.contentType || defaultContentTypeForSection(section.id));
    return '<article class="topic-display-panel content-type-' + esc(contentType) + '">' +
      '<div class="topic-display-meta">' +
      '<p class="topic-display-category">' + esc(data.name || "专题门户") + '</p>' +
      '<div class="topic-display-source">' +
      (updated ? '<span>' + esc(updated) + '</span>' : '') +
      '<span>' + esc(CONTENT_TYPE_LABELS[contentType] || "普通图文") + '</span>' +
      '<span>' + esc(data.name || "学校展示") + '</span>' +
      '</div></div>' +
      '<span class="topic-display-code">编号 ' + esc(code) + '</span>' +
      '<h1>' + esc(section.backendPageTitle || displaySectionTitle(section)) + '</h1>' +
      (intro ? '<p class="topic-display-subtitle">' + esc(intro) + '</p>' : '') +
      '<div class="topic-display-body">' + renderTypedFullBlockSequence(blocks, displaySectionTitle(section), contentType) + '</div>' +
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
    if (type === "honor") return renderHonorFullSequence(blocks, title);
    if (type === "video") return renderVideoFullSequence(blocks, title);
    return renderFullBlockSequence(blocks, title);
  }

  function splitTopicBlocks(blocks) {
    blocks = blocks || [];
    return {
      texts: blocks.filter(function (b) { return b.type === "text" && String(b.content || "").trim(); }),
      images: blocks.filter(function (b) { return b.type === "image" && b.src; }),
      videos: blocks.filter(function (b) { return b.type === "video" && (b.src || b.poster); })
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
    var grouped = splitTopicBlocks(blocks);
    var portrait = grouped.images[0];
    var copy = renderTopicTextFlow(grouped.texts) || '<p>人物资料正在整理中。</p>';
    var portraitHtml = portrait
      ? '<figure class="photo-frame topic-person-portrait" tabindex="0" data-lightbox="' + esc(portrait.src) + '" data-caption="' + esc(portrait.caption || title) + '">' +
        '<img src="' + esc(portrait.src) + '" alt="' + esc(portrait.caption || title) + '" loading="lazy">' +
        (portrait.caption ? '<figcaption>' + esc(portrait.caption) + '</figcaption>' : "") +
        '</figure>'
      : "";
    var restPhotos = grouped.images.slice(1);
    var restPhotoHtml = restPhotos.length
      ? '<div class="topic-display-photo-strip">' + restPhotos.map(function (b, index) { return renderTopicDisplayFigure(b, title, index + 1); }).join("") + '</div>'
      : "";
    var videoHtml = grouped.videos.map(function (b) { return '<div class="topic-display-video">' + renderVideo(b) + '</div>'; }).join("");
    return '<section class="topic-person-layout">' + portraitHtml +
      '<div class="topic-person-copy">' + copy + '</div></section>' + restPhotoHtml + videoHtml;
  }

  function renderHonorFullSequence(blocks, title) {
    var grouped = splitTopicBlocks(blocks);
    var photoHtml = grouped.images.length
      ? '<div class="topic-honor-gallery">' + grouped.images.map(function (b, index) { return renderTopicDisplayFigure(b, title, index + 1); }).join("") + '</div>'
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
      ? '<div class="topic-display-photo-strip">' + grouped.images.map(function (b, index) { return renderTopicDisplayFigure(b, title, index + 1); }).join("") + '</div>'
      : "";
    return videoHtml + (copy ? '<section class="topic-video-copy">' + copy + '</section>' : "") + photoHtml || '<p>视频资料正在整理中。</p>';
  }

  function renderFullBlockSequence(blocks, title) {
    var html = "";
    var photoGroup = [];
    var i = 0;
    var flushPhotos = function () {
      if (!photoGroup.length) return;
      html += '<div class="topic-display-photo-strip' + (photoGroup.length === 1 ? " single" : "") + '">' + photoGroup.map(function (b, index) {
        return renderTopicDisplayFigure(b, title, index + 1);
      }).join("") + '</div>';
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

  function stopTopicMediaCarousels() {
    topicMediaCarouselTimers.forEach(function (timer) { window.clearInterval(timer); });
    topicMediaCarouselTimers = [];
  }

  function startTopicMediaCarousels(root) {
    stopTopicMediaCarousels();
    if (!root) return;
    root.querySelectorAll("[data-topic-carousel]").forEach(function (carousel, carouselIndex) {
      var slides = Array.prototype.slice.call(carousel.querySelectorAll(".topic-loop-slide"));
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
      var delay = 3400 + (carouselIndex % 4) * 420;
      var timer = window.setInterval(function () { setActive(active + 1); }, delay);
      topicMediaCarouselTimers.push(timer);
    });
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
    return '<div class="drawer-loop-track" data-drawer-loop-track>' +
      '<div class="drawer-loop-sequence" data-drawer-loop-sequence>' + fullHtml + '</div>' +
      '<div class="drawer-loop-sequence drawer-loop-clone" aria-hidden="true">' + fullHtml + '</div>' +
      '</div>';
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
      drawerLoopTimer = window.setInterval(stepDrawerAutoLoop, 50);
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
    setTopicLoopPaused(false);
  }

  function openDrawer(fullHtml) {
    stopDrawerAutoLoop();
    $("drawerBody").innerHTML = drawerLoopContent(fullHtml);
    bindVideos($("drawerBody"));
    prepareAdaptiveMedia($("drawerBody"), measureDrawerLoop);
    $("drawer").hidden = false;
    setTopicLoopPaused(true);
    startDrawerAutoLoop();
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
    $("homeDepartmentSwitch").addEventListener("change", function (e) {
      var id = e.target.value;
      if (id) openDetail("departments", id, 0);
    });
    $("departmentSwitch").addEventListener("change", function (e) {
      var id = e.target.value;
      var kind = e.target.dataset.kind || "departments";
      if (id && (id !== state.id || kind !== state.kind)) openDetail(kind, id, 0);
    });
    $("prevChapter").addEventListener("click", function () { goSection(Math.max(state.section - 1, 0)); });
    $("nextChapter").addEventListener("click", function () { goSection(Math.min(state.section + 1, state.sections.length - 1)); });

    $("chapterPage").addEventListener("click", function (e) {
      var more = e.target.closest(".more-btn");
      if (more) { openDrawer(more.dataset.full); return; }
      var showCard = e.target.closest(".showcase-card[data-full]");
      if (showCard) { openDepartmentModule(showCard.dataset.module || "overview"); return; }
      var moduleButton = e.target.closest("[data-module]");
      if (moduleButton) { openDepartmentModule(moduleButton.dataset.module); return; }
      var rail = e.target.closest("[data-go-kind][data-go-id]");
      if (rail) { openDetail(rail.dataset.goKind, rail.dataset.goId, 0); return; }
      var topicLoopCard = e.target.closest(".topic-loop-card[data-section-id]");
      if (topicLoopCard) { openTopicLoopSection(topicLoopCard.dataset.sectionId); return; }
      var frame = e.target.closest(".photo-frame[data-lightbox]");
      if (frame) openLightbox(frame.dataset.lightbox, frame.dataset.caption);
    });
    $("chapterPage").addEventListener("keydown", function (e) {
      if ((e.key === "Enter" || e.key === " ") && e.target.classList.contains("topic-loop-card")) {
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

  /* ---------- 启动 ---------- */
  function fitCanvas() {
    // DESIGN.md 4.3: 1920×1080 基准画布等比缩放居中，窗口比例不一致时不重新布局
    var s = Math.min(window.innerWidth / 1920, window.innerHeight / 1080);
    stage.style.setProperty("--bp-scale", String(Math.max(0.4, s)));
  }
  function boot() {
    fitCanvas();
    window.addEventListener("resize", fitCanvas);
    Promise.all([loadData().then(loadPortalContent), loadPortalChrome()]).then(function () {
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
    });
  }
  boot();
})();
