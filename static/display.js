const app = document.getElementById("app");
const idleView = document.getElementById("idleView");
const marketView = document.getElementById("marketView");
const pageView = document.getElementById("pageView");

const brandLogo = document.getElementById("brandLogo");
const heroCopy = document.querySelector(".hero-copy");
const heroLabel = document.getElementById("heroLabel");
const heroTitle = document.getElementById("heroTitle");
const heroSubtitle = document.getElementById("heroSubtitle");
const heroTags = document.getElementById("heroTags");
const scanTitle = document.getElementById("scanTitle");
const scanCopy = document.getElementById("scanCopy");
const scanImage = document.getElementById("scanImage");
const scanCard = document.querySelector(".scan-card");
const qrMark = document.querySelector(".qr-mark");
const summaryLabel = document.getElementById("summaryLabel");
const summaryTitle = document.getElementById("summaryTitle");
const summaryCopy = document.getElementById("summaryCopy");
const summaryTags = document.getElementById("summaryTags");
const summaryPanel = document.querySelector(".glass-panel");
const mainStage = document.getElementById("mainStage");
const carouselPanel = document.querySelector(".carousel-panel");
const carouselStage = document.getElementById("carouselStage");
const carouselScanSlot = document.getElementById("carouselScanSlot");
const carouselPagination = document.getElementById("carouselPagination");
const progressBar = document.getElementById("progressBar");
const prevSlide = document.getElementById("prevSlide");
const nextSlide = document.getElementById("nextSlide");
const connectionState = document.getElementById("connectionState");
const projectState = document.getElementById("projectState");
const clockTime = document.getElementById("clockTime");
const metricProject = document.getElementById("metricProject");
const footerProject = document.getElementById("footerProject");
const footerStatus = document.getElementById("footerStatus");
const footerTime = document.getElementById("footerTime");

const detailImage = document.getElementById("detailImage");
const detailCode = document.getElementById("detailCode");
const detailMediaTitle = document.getElementById("detailMediaTitle");
const detailCategory = document.getElementById("detailCategory");
const detailDate = document.getElementById("detailDate");
const detailSource = document.getElementById("detailSource");
const detailTitle = document.getElementById("detailTitle");
const detailSubtitle = document.getElementById("detailSubtitle");
const detailBody = document.getElementById("detailBody");
const detailContentPanel = document.querySelector(".content-panel");
const returnHome = document.getElementById("returnHome");
const returnMarketHome = document.getElementById("returnMarketHome");
const marketLabel = document.getElementById("marketLabel");
const marketTitle = document.getElementById("marketTitle");
const marketIntro = document.getElementById("marketIntro");
const marketCategoryNav = document.getElementById("marketCategoryNav");
const marketItems = document.getElementById("marketItems");

const defaultDisplayConfig = {
  // 学校标识与官网二维码写死为数字门户展厅同款素材
  logoImageUrl: "/static/blueprint/school-logo.png",
  schoolName: "毕节职业技术学院",
  schoolMeta: "欢迎来到校园 · 同心特色校园文化",
  badgeText: "欢迎到校",
  summaryLabel: "WELCOME OVERVIEW",
  summaryTitle: "从学校形象到展项内容，形成完整参观动线。",
  summaryCopy: "这版首页减少普通网页式卡片，改为发布会级舞台视觉：大图沉浸、少量状态信息、清晰扫码引导，更适合远距离观看。",
  summaryTags: ["远距可读", "实时扫码", "项目部署"],
  scanTitle: "扫码访问学校官网",
  scanCopy: "扫码即可访问学校官方网站，了解更多校园信息。",
  scanImageUrl: "/static/blueprint/school-qr.jpg",
  sideTitle: "欢迎页方向",
  sideCopy: "这版更像学校官网入口和大厅欢迎屏：先介绍学校，再用图片轮播建立校园印象。",
  brandColor: "#28539c",
  brandDeepColor: "#20468b",
  accent2: "#47b7ff",
  slides: [
    {
      label: "校园入口与主楼",
      meta: "WELCOME 01",
      title: "学校形象",
      body: "用校门、主楼、展馆空间或学校标识作为第一视觉，让观众在远处就能识别当前展示主题。",
      imageUrl: "",
      visual: "gate",
    },
    {
      label: "成果导览",
      meta: "WELCOME 02",
      title: "成果导览",
      body: "观众扫码后进入具体编号内容，系统继续保留项目、编号、来源和更新时间等关键上下文。",
      imageUrl: "",
      visual: "library",
    },
    {
      label: "现场节奏",
      meta: "WELCOME 03",
      title: "现场节奏",
      body: "自动轮播在无人操作时维持画面流动，人工控制按钮承担上一张与下一张浏览。",
      imageUrl: "",
      visual: "students",
    },
  ],
};
const marketThemeMap = {
  masters: { label: "名匠名师", color: "#7030A0" },
  alumni: { label: "优秀校友", color: "#0070C0" },
  students: { label: "优秀学生", color: "#30C0B4" },
  teaching: { label: "教学科研", color: "#75BD42" },
  competitions: { label: "技能大赛", color: "#EFBB1F" },
  honors: { label: "荣誉资质", color: "#FB9236" },
};
const marketThemeAliases = {
  innovation: "teaching",
  achievements: "teaching",
  research: "teaching",
};

function marketThemeForContent(content = {}) {
  const rawKey = String(content.marketCategoryKey || content.categoryKey || "").trim();
  const directKey = marketThemeAliases[rawKey] || rawKey;
  if (marketThemeMap[directKey]) return { key: directKey, ...marketThemeMap[directKey] };
  const label = String(content.marketCategoryLabel || content.categoryLabel || content.category || "").trim();
  const matched = Object.entries(marketThemeMap).find(([, theme]) => theme.label === label);
  if (matched) return { key: matched[0], ...matched[1] };
  if (/校友|毕业生|就业典型/.test(label)) return { key: "alumni", ...marketThemeMap.alumni };
  if (/竞赛|大赛|比赛|赛项|技能/.test(label)) return { key: "competitions", ...marketThemeMap.competitions };
  if (/学生|学生风采/.test(label)) return { key: "students", ...marketThemeMap.students };
  if (/名师|名匠|教师|大师/.test(label)) return { key: "masters", ...marketThemeMap.masters };
  if (/荣誉|资质|证书|奖项/.test(label)) return { key: "honors", ...marketThemeMap.honors };
  if (/教学|科研|成果|案例|创新|项目/.test(label)) return { key: "teaching", ...marketThemeMap.teaching };
  return null;
}

function applyDetailMarketTheme(content = {}) {
  if (!pageView) return;
  const theme = marketThemeForContent(content);
  if (!theme) {
    delete pageView.dataset.marketTheme;
    pageView.style.removeProperty("--detail-theme");
    document.documentElement.style.removeProperty("--detail-theme");
    return;
  }
  const color = content.marketColor || content.color || theme.color;
  pageView.dataset.marketTheme = theme.key;
  pageView.style.setProperty("--detail-theme", color);
  document.documentElement.style.setProperty("--detail-theme", color);
  document.documentElement.style.setProperty("--accent", color);
}

let activeProject = null;
let lastRenderedScanAt = "";
let homeResetAt = 0;
let carouselTimer = 0;
let carouselIndex = 0;
let carouselSlides = [];
let touchStartX = 0;
let detailScrollFrame = 0;
let detailScrollTimer = 0;
let detailLoopRefreshTimer = 0;
let detailScrollDirection = 1;
let detailScrollLastTs = 0;
let detailScrollPosition = 0;
let detailLoopDistance = 0;
let scannerKeyBuffer = "";
let scannerKeyTimer = 0;
let scannerLastKeyAt = 0;
const initialParams = new URLSearchParams(window.location.search);
const previewMode = initialParams.get("preview") || "";
const DISPLAY_EDIT = {
  enabled: initialParams.get("edit") === "1" && !initialParams.get("code") && !initialParams.get("market"),
  ready: false,
  csrfToken: "",
  draft: null,
  original: null,
  dirty: false,
  uploadTarget: "",
  uploadIndex: -1,
  toolbar: null,
  statusNode: null,
  saveButton: null,
  fileInput: null,
};
const DETAIL_EDIT = {
  enabled: initialParams.get("edit") === "1" && Boolean(initialParams.get("code")),
  ready: false,
  csrfToken: "",
  itemId: "",
  draft: null,
  dirty: false,
  toolbar: null,
  statusNode: null,
  saveButton: null,
  fileInput: null,
  uploadTarget: "",
  selectedBodyImage: null,
  savedRange: null,
  savedRichRange: null,
  activeRichEditor: null,
  imageTools: null,
  coverTools: null,
  editorOverlay: null,
  editorPanel: null,
  titleInput: null,
  subtitleInput: null,
  bodyEditor: null,
  contentClickBound: false,
};
const MARKET_EDIT = {
  enabled: initialParams.get("edit") === "1" && Boolean(initialParams.get("market")) && !initialParams.get("code"),
  ready: false,
  data: null,
  activeKey: "",
  items: [],
  toolbar: null,
};
let activeDetailPage = null;

function setText(element, value) {
  if (element) element.textContent = value || "";
}

function cssUrl(value) {
  const safe = String(value || "").replace(/\\/g, "\\\\").replace(/"/g, '\\"');
  return `url("${safe}")`;
}

function escapeHtml(value) {
  return String(value || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

const mediaRatioClasses = ["media-tall", "media-portrait", "media-square", "media-landscape", "media-wide"];
const richFontSizeMap = {
  "1": "0.75em",
  "2": "0.875em",
  "3": "1em",
  "4": "1.15em",
  "5": "1.35em",
  "6": "1.6em",
  "7": "2em",
};
const allowedRichFontFamilies = new Map([
  ["arial", "Arial"],
  ["kaiti", "KaiTi"],
  ["microsoft yahei", "\"Microsoft YaHei\""],
  ["microsoft yahei ui", "\"Microsoft YaHei UI\""],
  ["sans-serif", "sans-serif"],
  ["serif", "serif"],
  ["simhei", "SimHei"],
  ["simsun", "SimSun"],
]);
const richTextStyleTags = new Set(["P", "DIV", "SPAN", "H2", "H3", "H4", "LI", "STRONG", "B", "EM", "I", "U"]);

function classifyMediaRatio(ratio) {
  if (ratio < 0.62) return "media-tall";
  if (ratio < 0.86) return "media-portrait";
  if (ratio > 1.9) return "media-wide";
  if (ratio > 1.18) return "media-landscape";
  return "media-square";
}

function adaptiveMediaTarget(img) {
  return img.closest(".detail-media, figure, .profile-card") || img;
}

function applyAdaptiveMediaClass(img) {
  const target = adaptiveMediaTarget(img);
  const nodes = [img, target].filter(Boolean);
  nodes.forEach((node) => {
    mediaRatioClasses.forEach((name) => node.classList.remove(name));
    node.classList.remove("media-ready", "media-error");
    node.style.removeProperty("--media-ratio");
  });
  const apply = () => {
    const w = img.naturalWidth || 0;
    const h = img.naturalHeight || 0;
    if (!w || !h) return;
    const ratio = w / h;
    const cls = classifyMediaRatio(ratio);
    nodes.forEach((node) => {
      mediaRatioClasses.forEach((name) => node.classList.remove(name));
      node.classList.add("media-ready", cls);
      node.style.setProperty("--media-ratio", ratio.toFixed(4));
    });
  };
  if (img.complete && img.naturalWidth) apply();
  else {
    img.addEventListener("load", apply, { once: true });
    img.addEventListener("error", () => nodes.forEach((node) => node.classList.add("media-error")), { once: true });
  }
}

function hydrateAdaptiveMedia(root) {
  if (!root) return;
  root.querySelectorAll(".detail-media img, figure img, .profile-card img").forEach(applyAdaptiveMediaClass);
}

function textToRichHtml(value) {
  return String(value || "")
    .split(/\n{2,}/)
    .map((item) => item.trim())
    .filter(Boolean)
    .map((item) => `<p>${escapeHtml(item).replaceAll("\n", "<br>")}</p>`)
    .join("");
}

function safeRichFontFamily(value) {
  const keep = [];
  String(value || "").split(",").forEach((part) => {
    const name = part.trim().replace(/^['"]|['"]$/g, "").toLowerCase();
    const family = allowedRichFontFamilies.get(name);
    if (family && !keep.includes(family)) keep.push(family);
  });
  return keep.join(", ");
}

function safeRichFontSize(value) {
  const text = String(value || "").trim().toLowerCase();
  if (richFontSizeMap[text]) return richFontSizeMap[text];
  if (/^(\d+(\.\d+)?(px|em|rem|%)|xx-small|x-small|small|medium|large|x-large|xx-large)$/.test(text)) return text;
  return "";
}

function safeRichInlineStyle(node, value) {
  const keep = [];
  String(value || "").split(";").forEach((part) => {
    if (!part.includes(":")) return;
    const [rawProp, ...rawValueParts] = part.split(":");
    const prop = String(rawProp || "").trim().toLowerCase();
    const rawValue = rawValueParts.join(":").trim();
    const valueText = rawValue.toLowerCase();
    if (prop === "transform" && node.tagName === "IMG") {
      const match = valueText.match(/^rotate\((-?\d+(?:\.\d+)?)deg\)\s+scale\((\d+(?:\.\d+)?)\)$/);
      if (!match) return;
      const rotate = Math.max(-360, Math.min(360, Number(match[1]) || 0));
      const scale = Math.max(0.5, Math.min(2.5, Number(match[2]) || 1));
      keep.push(`transform: rotate(${rotate}deg) scale(${scale})`);
      return;
    }
    if (prop === "font-family" && richTextStyleTags.has(node.tagName)) {
      const family = safeRichFontFamily(rawValue);
      if (family) keep.push(`font-family: ${family}`);
      return;
    }
    if (prop === "font-size" && richTextStyleTags.has(node.tagName)) {
      const size = safeRichFontSize(rawValue);
      if (size) keep.push(`font-size: ${size}`);
      return;
    }
    if (prop === "text-align" && ["P", "DIV", "SPAN", "H2", "H3", "H4", "LI"].includes(node.tagName) && /^(left|center|right)$/.test(valueText)) {
      keep.push(`text-align: ${valueText}`);
      return;
    }
    if (node.tagName === "IMG" && prop === "width" && /^\d+(\.\d+)?px$/.test(valueText)) {
      keep.push(`width: ${valueText}`);
      return;
    }
    if (node.tagName === "IMG" && prop === "max-width" && /^(\d+(\.\d+)?px|100%)$/.test(valueText)) {
      keep.push(`max-width: ${valueText}`);
    }
  });
  return keep.join("; ");
}

function normalizeLegacyFontTags(root) {
  Array.from(root.querySelectorAll("font")).forEach((node) => {
    const span = document.createElement("span");
    const styles = [];
    const family = safeRichFontFamily(node.getAttribute("face"));
    const size = safeRichFontSize(node.getAttribute("size"));
    const inlineStyle = safeRichInlineStyle(span, node.getAttribute("style"));
    if (family) styles.push(`font-family: ${family}`);
    if (size) styles.push(`font-size: ${size}`);
    if (inlineStyle) styles.push(inlineStyle);
    if (styles.length) span.setAttribute("style", styles.join("; "));
    while (node.firstChild) span.appendChild(node.firstChild);
    node.replaceWith(span);
  });
}

function sanitizeRichHtml(html) {
  const allowedTags = new Set([
    "A",
    "B",
    "BLOCKQUOTE",
    "BR",
    "DIV",
    "EM",
    "FIGCAPTION",
    "FIGURE",
    "H2",
    "H3",
    "H4",
    "HR",
    "I",
    "IMG",
    "LI",
    "OL",
    "P",
    "SECTION",
    "SPAN",
    "STRONG",
    "U",
    "UL",
  ]);
  const template = document.createElement("template");
  template.innerHTML = String(html || "");
  normalizeLegacyFontTags(template.content);
  Array.from(template.content.querySelectorAll("script, style, iframe, object, embed")).forEach((node) => node.remove());
  Array.from(template.content.querySelectorAll("*")).forEach((node) => {
    if (!allowedTags.has(node.tagName)) {
      node.replaceWith(document.createTextNode(node.textContent || ""));
      return;
    }
    Array.from(node.attributes).forEach((attribute) => {
      const name = attribute.name.toLowerCase();
      const value = attribute.value || "";
      if (name.startsWith("on")) {
        node.removeAttribute(attribute.name);
        return;
      }
      if (name === "style") {
        const style = safeRichInlineStyle(node, value);
        if (style) node.setAttribute("style", style);
        else node.removeAttribute(attribute.name);
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
        if (name === "src" && !/^(https?:|\/|data:image\/)/i.test(value)) {
          node.removeAttribute(attribute.name);
        }
        return;
      }
      if (name.startsWith("data-") && ["data-template", "data-template-field"].includes(name)) {
        return;
      }
      if (name !== "class") {
        node.removeAttribute(attribute.name);
      }
    });
  });
  return template.innerHTML.trim();
}

function normalizeRichBody(value) {
  const raw = String(value || "").trim();
  if (!raw) return "";
  return /<[a-z][\s\S]*>/i.test(raw) ? sanitizeRichHtml(raw) : textToRichHtml(raw);
}

function formatDate(value) {
  const text = String(value || "").trim();
  if (!text) return "";
  const date = new Date(text);
  if (Number.isNaN(date.getTime())) return text;
  return `${date.getFullYear()}年${String(date.getMonth() + 1).padStart(2, "0")}月${String(date.getDate()).padStart(2, "0")}日`;
}

function normalizeTags(value) {
  if (Array.isArray(value)) {
    const tags = value.map((item) => String(item || "").trim()).filter(Boolean);
    return tags;
  }
  const tags = String(value || "")
    .split(/[\n,，、]+/)
    .map((item) => item.trim())
    .filter(Boolean);
  return tags;
}

function normalizeDisplayConfig(config) {
  const source = config && typeof config === "object" ? config : {};
  const merged = {
    ...defaultDisplayConfig,
    ...source,
    summaryTags: source.summaryTags === undefined ? defaultDisplayConfig.summaryTags : normalizeTags(source.summaryTags),
    // 学校标识与官网二维码固定写死，不受项目配置影响
    logoImageUrl: defaultDisplayConfig.logoImageUrl,
    scanImageUrl: defaultDisplayConfig.scanImageUrl,
    scanTitle: defaultDisplayConfig.scanTitle,
    scanCopy: defaultDisplayConfig.scanCopy,
  };
  const slides = Array.isArray(source.slides) ? source.slides : defaultDisplayConfig.slides;
  merged.slides = slides.length ? slides : defaultDisplayConfig.slides;
  return merged;
}

function wrapIndex(index) {
  if (!carouselSlides.length) return 0;
  return (index + carouselSlides.length) % carouselSlides.length;
}

function shortestOffset(index, active) {
  let offset = index - active;
  const half = carouselSlides.length / 2;
  if (offset > half) offset -= carouselSlides.length;
  if (offset < -half) offset += carouselSlides.length;
  return offset;
}

function showSlide(index) {
  if (!carouselSlides.length) return;
  carouselIndex = wrapIndex(index);
  const slideNodes = Array.from(carouselStage.querySelectorAll(".slide"));
  slideNodes.forEach((slide, idx) => {
    const offset = shortestOffset(idx, carouselIndex);
    const abs = Math.abs(offset);
    const x = offset * 230;
    const rotateY = offset * -46;
    const depth = abs * -116;
    const scale = idx === carouselIndex ? 1.04 : Math.max(0.76, 1 - abs * 0.16);
    slide.classList.toggle("is-active", idx === carouselIndex);
    slide.setAttribute("aria-hidden", idx === carouselIndex ? "false" : "true");
    slide.style.zIndex = String(10 - abs);
    slide.style.opacity = abs > 1.5 ? "0" : "1";
    slide.style.pointerEvents = abs > 1.5 ? "none" : "auto";
    slide.style.transform = `translate3d(calc(-50% + ${x}px), 0, ${depth}px) rotateY(${rotateY}deg) scale(${scale})`;
  });

  if (progressBar) {
    progressBar.style.width = `${100 / carouselSlides.length}%`;
    progressBar.style.transform = `translateX(${carouselIndex * 100}%)`;
  }
  carouselPagination.querySelectorAll(".carousel-dot").forEach((dot, idx) => {
    dot.classList.toggle("is-active", idx === carouselIndex);
    dot.setAttribute("aria-current", idx === carouselIndex ? "true" : "false");
  });
}

function restartCarousel() {
  window.clearTimeout(carouselTimer);
  if (DISPLAY_EDIT.enabled || DETAIL_EDIT.enabled) return;
  if (carouselSlides.length > 1) {
    carouselTimer = window.setTimeout(() => {
      showSlide(carouselIndex + 1);
      restartCarousel();
    }, 4200);
  }
}

function stopDetailAutoScroll() {
  window.cancelAnimationFrame(detailScrollFrame);
  window.clearTimeout(detailScrollTimer);
  window.clearTimeout(detailLoopRefreshTimer);
  detailScrollFrame = 0;
  detailScrollTimer = 0;
  detailLoopRefreshTimer = 0;
  detailScrollLastTs = 0;
  detailScrollPosition = 0;
  detailLoopDistance = 0;
}

function detailCanScroll() {
  if (!detailContentPanel || !detailLoopDistance) return false;
  return detailContentPanel.scrollHeight - detailContentPanel.clientHeight > 8;
}

function removeElementIds(node) {
  if (node.nodeType !== Node.ELEMENT_NODE) return;
  node.removeAttribute("id");
  node.querySelectorAll("[id]").forEach((item) => item.removeAttribute("id"));
}

function ensureDetailLoopTrack() {
  let track = detailContentPanel.querySelector(".detail-loop-track");
  if (track) {
    track.querySelectorAll(".detail-loop-copy.is-clone").forEach((node) => node.remove());
    return track;
  }

  const primary = document.createElement("div");
  primary.className = "detail-loop-copy";
  while (detailContentPanel.firstChild) {
    primary.appendChild(detailContentPanel.firstChild);
  }

  track = document.createElement("div");
  track.className = "detail-loop-track";
  track.appendChild(primary);
  detailContentPanel.appendChild(track);
  return track;
}

function setupDetailScrollLoop() {
  if (!detailContentPanel) return;
  const track = ensureDetailLoopTrack();
  const primary = track.querySelector(".detail-loop-copy:not(.is-clone)");
  detailContentPanel.scrollTop = 0;
  detailLoopDistance = 0;
  if (!primary || detailContentPanel.scrollHeight - detailContentPanel.clientHeight <= 8) return;

  const clone = primary.cloneNode(true);
  clone.classList.add("is-clone");
  clone.setAttribute("aria-hidden", "true");
  removeElementIds(clone);
  track.appendChild(clone);

  detailLoopDistance = clone.offsetTop - primary.offsetTop;
}

function runDetailAutoScroll(timestamp) {
  if (!detailCanScroll() || pageView.hidden) return;

  if (!detailScrollLastTs) {
    detailScrollLastTs = timestamp;
    detailScrollPosition = detailContentPanel.scrollTop;
  }
  const deltaSeconds = Math.min((timestamp - detailScrollLastTs) / 1000, 0.05);
  detailScrollLastTs = timestamp;

  const speed = 24;
  detailScrollPosition += speed * deltaSeconds;
  const primary = detailContentPanel.querySelector(".detail-loop-copy:not(.is-clone)");
  const clone = detailContentPanel.querySelector(".detail-loop-copy.is-clone");
  if (primary && clone) {
    const liveDistance = clone.offsetTop - primary.offsetTop;
    if (liveDistance > detailContentPanel.clientHeight) {
      detailLoopDistance = liveDistance;
    }
  }
  if (detailScrollPosition >= detailLoopDistance) {
    detailScrollPosition -= detailLoopDistance;
  }
  detailContentPanel.scrollTop = detailScrollPosition;

  detailScrollFrame = window.requestAnimationFrame(runDetailAutoScroll);
}

function startDetailAutoScroll() {
  stopDetailAutoScroll();
  if (!detailContentPanel) return;
  setupDetailScrollLoop();
  detailContentPanel.scrollTop = 0;
  detailScrollPosition = 0;
  detailScrollDirection = 1;
  detailLoopRefreshTimer = window.setTimeout(() => {
    if (!pageView.hidden) setupDetailScrollLoop();
  }, 700);
  detailScrollTimer = window.setTimeout(() => {
    if (detailCanScroll() && !pageView.hidden) {
      detailScrollFrame = window.requestAnimationFrame(runDetailAutoScroll);
    }
  }, 1800);
}

function renderCarousel(slides, preferredIndex = 0) {
  carouselSlides = slides.length ? slides : defaultDisplayConfig.slides;
  carouselIndex = Math.max(0, Math.min(Number(preferredIndex) || 0, carouselSlides.length - 1));
  carouselStage.innerHTML = "";
  carouselPagination.innerHTML = "";

  const uploadedSlideImage = carouselSlides.map((item) => item.imageUrl).find(Boolean) || "";
  const fallbackImage = uploadedSlideImage || activeProject?.defaultImageUrl || "/static/expo-stage.png";

  carouselSlides.forEach((slide, index) => {
    const article = document.createElement("article");
    article.className = "slide";
    article.dataset.slide = String(index);
    article.style.setProperty("--slide-image", cssUrl(slide.imageUrl || fallbackImage));

    const caption = document.createElement("p");
    caption.className = "caption";
    caption.textContent = String(slide.meta ?? `WELCOME ${String(index + 1).padStart(2, "0")}`);
    caption.dataset.displayEditText = "meta";
    caption.dataset.placeholder = "顶部标识（可留空）";

    const title = document.createElement("h3");
    title.textContent = slide.title || "";
    title.dataset.displayEditText = "title";
    title.dataset.placeholder = "标题（可留空）";

    const body = document.createElement("p");
    body.textContent = slide.body || slide.label || "";
    body.dataset.displayEditText = "body";
    body.dataset.placeholder = "图片说明（可留空）";

    if (caption.textContent || DISPLAY_EDIT.enabled) article.appendChild(caption);
    if (title.textContent || DISPLAY_EDIT.enabled) article.appendChild(title);
    if (body.textContent || DISPLAY_EDIT.enabled) article.appendChild(body);
    article.addEventListener("click", () => {
      if (index !== carouselIndex) {
        showSlide(index);
        restartCarousel();
      }
    });
    carouselStage.appendChild(article);

    const dot = document.createElement("button");
    dot.type = "button";
    dot.className = "carousel-dot";
    dot.setAttribute("aria-label", `切换到第 ${index + 1} 张`);
    dot.addEventListener("click", () => {
      showSlide(index);
      restartCarousel();
    });
    carouselPagination.appendChild(dot);
  });

  showSlide(carouselIndex);
  decorateDisplayEditSlides();
  restartCarousel();
}

function marketItemUrl(item) {
  return item.qrPath || `/display?project=${encodeURIComponent(item.projectId)}&code=${encodeURIComponent(item.code)}&source=achievement-market`;
}

function normalizedMarketKey(key = "") {
  const rawKey = String(key || "").trim();
  return marketThemeAliases[rawKey] || rawKey;
}

function marketCategoryEditUrl(categoryKey = "", topicSlug = "") {
  const params = new URLSearchParams();
  const key = normalizedMarketKey(categoryKey);
  if (!key) return "";
  if (key) params.set("market", key);
  const topic = String(topicSlug || "").trim();
  if (topic) params.set("topic", topic);
  params.set("edit", "1");
  return `/display?${params.toString()}`;
}

function currentMarketCategoryEditUrl(fallbackCategoryKey = "") {
  const categoryKey = initialParams.get("market") || fallbackCategoryKey || "";
  const topicSlug = initialParams.get("topic") || "";
  if (!categoryKey) return "";
  return marketCategoryEditUrl(categoryKey, topicSlug);
}

function marketItemEditUrl(item, topicSlug = "", fallbackCategoryKey = "") {
  const url = new URL(marketItemUrl(item), window.location.origin);
  if (!url.searchParams.get("project") && item.projectId) url.searchParams.set("project", item.projectId);
  if (!url.searchParams.get("code") && item.code) url.searchParams.set("code", item.code);
  if (!url.searchParams.get("source")) url.searchParams.set("source", "achievement-market");
  url.searchParams.set("edit", "1");
  if (item.id !== undefined && item.id !== null && item.id !== "") url.searchParams.set("marketItem", item.id);
  const categoryKey = normalizedMarketKey(item.categoryKey || fallbackCategoryKey || initialParams.get("market") || "");
  if (categoryKey) url.searchParams.set("market", categoryKey);
  const topic = String(topicSlug || initialParams.get("topic") || "").trim();
  if (topic) url.searchParams.set("topic", topic);
  return `${url.pathname}${url.search}`;
}

function renderMarketHomeLinks(categories) {
  if (!carouselScanSlot || !categories || !categories.length) return;
  let links = carouselScanSlot.querySelector(".market-home-links");
  if (!links) {
    links = document.createElement("div");
    links.className = "market-home-links";
    carouselScanSlot.appendChild(links);
  }
  links.innerHTML = categories.map((category) => `
    <a style="--color:${category.color || "#47b7ff"}" href="/display?market=${encodeURIComponent(category.key)}">
      <span>${escapeHtml(category.label)}</span>
      <strong>${Number(category.count || 0)}</strong>
    </a>
  `).join("");
}

function applyMarketWelcomeConfig(config = {}, preferredIndex = 0) {
  const mainImage = String(config.welcomeImageUrl || "").trim();
  const fallbackMainImage = activeProject?.defaultImageUrl || "/static/expo-stage.png";
  document.documentElement.style.setProperty("--project-image", cssUrl(mainImage || fallbackMainImage));

  const welcomeTitle = String(config.welcomeTitle || "");
  const welcomeSubtitle = String(config.welcomeSubtitle || "");
  const welcomeIntro = String(config.welcomeIntro || "");
  setText(heroLabel, welcomeTitle);
  setText(heroTitle, welcomeSubtitle);
  setText(heroSubtitle, welcomeIntro);
  if (heroLabel) heroLabel.hidden = true;
  if (heroTitle) heroTitle.hidden = true;
  if (heroSubtitle) heroSubtitle.hidden = true;
  if (heroCopy) heroCopy.hidden = true;
  if (config.welcomeNote) setText(footerStatus, config.welcomeNote);

  const slides = resolveMarketCarouselSlides(config);
  if (!slides.length) {
    if (DISPLAY_EDIT.enabled) {
      renderCarousel(normalizeDisplayConfig(activeProject?.displayConfig).slides, preferredIndex);
    }
    return;
  }
  renderCarousel(slides, preferredIndex);
}

function marketCarouselDefaultCopy(config, index) {
  const projectSlides = normalizeDisplayConfig(activeProject?.displayConfig).slides;
  const source = projectSlides[index % projectSlides.length] || {};
  return {
    meta: source.meta || `WELCOME ${String(index + 1).padStart(2, "0")}`,
    title: source.title || config.welcomeTitle || "校园成果展示",
    body: source.body || config.welcomeSubtitle || "欢迎进入校园成果展示现场",
  };
}

function resolveMarketCarouselSlides(config = {}) {
  const rawSlides = Array.isArray(config.welcomeCarouselSlides) && config.welcomeCarouselSlides.length
    ? config.welcomeCarouselSlides
    : (Array.isArray(config.welcomeCarouselImages) ? config.welcomeCarouselImages : []);
  const seen = new Set();
  const slides = [];
  rawSlides.forEach((item, index) => {
    const source = item && typeof item === "object" ? item : { imageUrl: item };
    const imageUrl = String(source.imageUrl || source.url || "").trim();
    if (!imageUrl || seen.has(imageUrl) || slides.length >= 30) return;
    seen.add(imageUrl);
    const fallback = marketCarouselDefaultCopy(config, index);
    const customText = source.customText === true || (source.customText === undefined && ["meta", "title", "body"].some((key) => Object.hasOwn(source, key)));
    slides.push({
      imageUrl,
      meta: customText ? String(source.meta ?? "") : fallback.meta,
      title: customText ? String(source.title ?? "") : fallback.title,
      body: customText ? String(source.body ?? "") : fallback.body,
      customText,
    });
  });
  return slides;
}

function cleanDisplayEditImages(images) {
  return Array.from(new Set((Array.isArray(images) ? images : [])
    .map((url) => String(url || "").trim())
    .filter(Boolean))).slice(0, 30);
}

function normalizeDisplayEditConfig(config = {}) {
  const welcomeCarouselSlides = resolveMarketCarouselSlides(config);
  return {
    welcomeTitle: String(config.welcomeTitle || ""),
    welcomeSubtitle: String(config.welcomeSubtitle || ""),
    welcomeIntro: String(config.welcomeIntro || ""),
    welcomeImageUrl: String(config.welcomeImageUrl || "").trim(),
    welcomeCarouselImages: welcomeCarouselSlides.map((slide) => slide.imageUrl),
    welcomeCarouselSlides,
    welcomeNote: String(config.welcomeNote || ""),
  };
}

function cloneDisplayEditValue(value) {
  return JSON.parse(JSON.stringify(value));
}

function displayEditStatus(message, kind = "") {
  if (!DISPLAY_EDIT.statusNode) return;
  DISPLAY_EDIT.statusNode.textContent = message || "";
  DISPLAY_EDIT.statusNode.dataset.kind = kind;
}

async function displayEditApi(url, options = {}) {
  const requestOptions = { ...options };
  const method = String(requestOptions.method || "GET").toUpperCase();
  if (method !== "GET" && DISPLAY_EDIT.csrfToken) {
    requestOptions.headers = { ...(requestOptions.headers || {}), "X-CSRF-Token": DISPLAY_EDIT.csrfToken };
  }
  const response = await fetch(url, requestOptions);
  const payload = await response.json().catch(() => ({}));
  if (!response.ok || payload.ok === false) {
    throw new Error(payload.error || (response.status === 401 ? "登录已失效，请重新登录后台" : "操作失败"));
  }
  return payload;
}

function fileToDataUrl(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = () => reject(new Error("图片读取失败"));
    reader.readAsDataURL(file);
  });
}

function createDisplayEditToolbar() {
  if (DISPLAY_EDIT.toolbar) return;
  const toolbar = document.createElement("div");
  toolbar.className = "display-edit-toolbar";
  toolbar.innerHTML = `
    <strong>成果超市欢迎页可视化编辑</strong>
    <span data-display-edit-status>正在校验管理员身份…</span>
    <button type="button" data-display-edit-save disabled>保存修改</button>
    <a href="/admin?view=deploy">返回成果超市管理</a>
    <a href="/display">退出编辑</a>
    <input type="file" accept="image/*" data-display-edit-file hidden />
  `;
  document.body.appendChild(toolbar);
  DISPLAY_EDIT.toolbar = toolbar;
  DISPLAY_EDIT.statusNode = toolbar.querySelector("[data-display-edit-status]");
  DISPLAY_EDIT.saveButton = toolbar.querySelector("[data-display-edit-save]");
  DISPLAY_EDIT.fileInput = toolbar.querySelector("[data-display-edit-file]");
  DISPLAY_EDIT.saveButton.addEventListener("click", saveDisplayEdits);
  DISPLAY_EDIT.fileInput.addEventListener("change", uploadDisplayEditImages);
}

function updateDisplayEditCount() {
  const count = DISPLAY_EDIT.draft ? DISPLAY_EDIT.draft.welcomeCarouselSlides.length : 0;
  const node = document.querySelector("[data-display-edit-count]");
  if (node) node.textContent = `${count} / 30 张`;
}

function markDisplayEditDirty(message = "有未保存修改") {
  DISPLAY_EDIT.dirty = true;
  if (DISPLAY_EDIT.saveButton) DISPLAY_EDIT.saveButton.disabled = false;
  displayEditStatus(message, "warn");
  updateDisplayEditCount();
}

const editablePlaceholderTexts = new Set([
  "顶部标识（可留空）",
  "标题（可留空）",
  "摘要（可留空）",
  "图片说明（可留空）",
  "可直接编辑，允许留空",
  "点击填写项目摘要",
  "点击修改图片说明，可留空",
]);

function cleanEditableTextValue(value, node = null) {
  const text = String(value || "").trim();
  const placeholder = String(node?.dataset?.placeholder || "").trim();
  if (!text) return "";
  if ((placeholder && text === placeholder) || editablePlaceholderTexts.has(text)) return "";
  return text;
}

function displayEditTextValue(node, multiline = false) {
  if (!node) return "";
  return cleanEditableTextValue(multiline ? node.innerText : node.textContent, node);
}

function clearEditablePlaceholderText(node, multiline = false) {
  if (!node) return "";
  const value = displayEditTextValue(node, multiline);
  if (!value && String(multiline ? node.innerText : node.textContent).trim()) node.textContent = "";
  updateDisplayEditEmptyState(node, value);
  return value;
}

function updateDisplayEditEmptyState(node, value) {
  node.dataset.editEmpty = value ? "0" : "1";
}

function bindDisplayEditText(node, onChange, options = {}) {
  if (!node || node.dataset.displayEditBound === "1") return;
  const multiline = Boolean(options.multiline);
  node.dataset.displayEditBound = "1";
  node.contentEditable = "true";
  node.spellcheck = false;
  const initialValue = displayEditTextValue(node, multiline);
  node.dataset.displayEditLast = initialValue;
  updateDisplayEditEmptyState(node, initialValue);
  node.addEventListener("click", (event) => event.stopPropagation());
  node.addEventListener("keydown", (event) => {
    event.stopPropagation();
    if (!multiline && event.key === "Enter") {
      event.preventDefault();
      node.blur();
    }
  });
  const syncText = () => {
    const value = displayEditTextValue(node, multiline);
    updateDisplayEditEmptyState(node, value);
    if (node.dataset.displayEditLast === value) return;
    node.dataset.displayEditLast = value;
    onChange(value);
  };
  node.addEventListener("input", syncText);
  node.addEventListener("blur", syncText);
}

function selectDisplayEditFiles(target, index = -1, multiple = false) {
  if (!DISPLAY_EDIT.ready || !DISPLAY_EDIT.fileInput) return;
  if (target === "carousel-add" && DISPLAY_EDIT.draft.welcomeCarouselSlides.length >= 30) {
    displayEditStatus("轮播图最多可添加 30 张", "error");
    return;
  }
  DISPLAY_EDIT.uploadTarget = target;
  DISPLAY_EDIT.uploadIndex = index;
  DISPLAY_EDIT.fileInput.multiple = multiple;
  DISPLAY_EDIT.fileInput.value = "";
  DISPLAY_EDIT.fileInput.click();
}

function ensureDisplayEditControls() {
  if (!DISPLAY_EDIT.ready) return;
  if (heroCopy) heroCopy.hidden = true;
  [heroLabel, heroTitle, heroSubtitle].forEach((node) => {
    if (!node) return;
    node.hidden = true;
    delete node.dataset.displayEditText;
    delete node.dataset.placeholder;
  });
  if (mainStage && !mainStage.querySelector(".display-edit-main-button")) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "display-edit-main-button display-edit-control";
    button.textContent = "更换左侧大图";
    button.addEventListener("click", (event) => {
      event.preventDefault();
      event.stopPropagation();
      selectDisplayEditFiles("main");
    });
    mainStage.appendChild(button);
  }
  if (carouselPanel && !carouselPanel.querySelector(".display-edit-carousel-tools")) {
    const tools = document.createElement("div");
    tools.className = "display-edit-carousel-tools display-edit-control";
    tools.innerHTML = `
      <span>轮播图片 <strong data-display-edit-count>0 / 30 张</strong></span>
      <button type="button" data-display-edit-add>添加轮播图</button>
    `;
    tools.querySelector("[data-display-edit-add]").addEventListener("click", (event) => {
      event.preventDefault();
      event.stopPropagation();
      selectDisplayEditFiles("carousel-add", -1, true);
    });
    carouselPanel.appendChild(tools);
  }
  updateDisplayEditCount();
  decorateDisplayEditSlides();
}

function applyDisplayEditDraft(preferredIndex = 0) {
  if (!DISPLAY_EDIT.draft) return;
  DISPLAY_EDIT.draft.welcomeCarouselSlides = resolveMarketCarouselSlides(DISPLAY_EDIT.draft);
  DISPLAY_EDIT.draft.welcomeCarouselImages = DISPLAY_EDIT.draft.welcomeCarouselSlides.map((slide) => slide.imageUrl);
  applyMarketWelcomeConfig(DISPLAY_EDIT.draft, preferredIndex);
  ensureDisplayEditControls();
}

function handleDisplayEditSlideAction(action, index) {
  if (!DISPLAY_EDIT.ready || !DISPLAY_EDIT.draft) return;
  const slides = DISPLAY_EDIT.draft.welcomeCarouselSlides;
  if (action === "replace") {
    selectDisplayEditFiles("carousel-replace", index);
    return;
  }
  if (action === "remove") {
    slides.splice(index, 1);
    markDisplayEditDirty("已删除轮播图，保存后生效");
    applyDisplayEditDraft(Math.min(index, Math.max(0, slides.length - 1)));
    return;
  }
  if (action === "up" && index > 0) {
    [slides[index - 1], slides[index]] = [slides[index], slides[index - 1]];
    markDisplayEditDirty("已调整轮播顺序，保存后生效");
    applyDisplayEditDraft(index - 1);
  }
  if (action === "down" && index < slides.length - 1) {
    [slides[index + 1], slides[index]] = [slides[index], slides[index + 1]];
    markDisplayEditDirty("已调整轮播顺序，保存后生效");
    applyDisplayEditDraft(index + 1);
  }
}

function decorateDisplayEditSlides() {
  if (!DISPLAY_EDIT.ready || !DISPLAY_EDIT.draft || !carouselStage) return;
  const slides = DISPLAY_EDIT.draft.welcomeCarouselSlides || [];
  Array.from(carouselStage.querySelectorAll(".slide")).forEach((slide, index) => {
    if (index >= slides.length || slide.querySelector(".display-edit-slide-controls")) return;
    const controls = document.createElement("div");
    controls.className = "display-edit-slide-controls display-edit-control";
    controls.innerHTML = `
      <button type="button" data-display-slide-action="replace">更换</button>
      <button type="button" data-display-slide-action="up" ${index === 0 ? "disabled" : ""}>上移</button>
      <button type="button" data-display-slide-action="down" ${index === slides.length - 1 ? "disabled" : ""}>下移</button>
      <button type="button" class="danger" data-display-slide-action="remove">删除</button>
    `;
    controls.addEventListener("click", (event) => {
      const button = event.target.closest("[data-display-slide-action]");
      if (!button || button.disabled) return;
      event.preventDefault();
      event.stopPropagation();
      handleDisplayEditSlideAction(button.dataset.displaySlideAction, index);
    });
    slide.appendChild(controls);
    slide.querySelectorAll("[data-display-edit-text]").forEach((node) => {
      const field = node.dataset.displayEditText;
      bindDisplayEditText(node, (value) => {
        slides[index][field] = value;
        slides[index].customText = true;
        markDisplayEditDirty("轮播图文字已修改，保存后生效");
      }, { multiline: field === "body" });
    });
  });
}

async function uploadDisplayEditImages(event) {
  const files = Array.from(event.target.files || []).filter((file) => String(file.type || "").startsWith("image/"));
  if (!files.length || !DISPLAY_EDIT.ready || !DISPLAY_EDIT.draft) return;
  const target = DISPLAY_EDIT.uploadTarget;
  const index = DISPLAY_EDIT.uploadIndex;
  const available = target === "carousel-add"
    ? Math.max(0, 30 - DISPLAY_EDIT.draft.welcomeCarouselSlides.length)
    : 1;
  const selected = files.slice(0, available);
  if (!selected.length) {
    displayEditStatus("轮播图最多可添加 30 张", "error");
    return;
  }
  document.body.classList.add("display-edit-busy");
  if (DISPLAY_EDIT.saveButton) DISPLAY_EDIT.saveButton.disabled = true;
  try {
    for (let fileIndex = 0; fileIndex < selected.length; fileIndex += 1) {
      const file = selected[fileIndex];
      displayEditStatus(`正在上传 ${fileIndex + 1} / ${selected.length}：${file.name}`, "warn");
      const dataUrl = await fileToDataUrl(file);
      const payload = await displayEditApi("/api/assets", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ filename: file.name, dataUrl }),
      });
      const url = payload.url || payload.asset?.url || "";
      if (!url) throw new Error("上传成功但未返回图片地址");
      if (target === "main") DISPLAY_EDIT.draft.welcomeImageUrl = url;
      if (target === "carousel-replace" && index >= 0) DISPLAY_EDIT.draft.welcomeCarouselSlides[index].imageUrl = url;
      if (target === "carousel-add") {
        const copy = marketCarouselDefaultCopy(DISPLAY_EDIT.draft, DISPLAY_EDIT.draft.welcomeCarouselSlides.length);
        DISPLAY_EDIT.draft.welcomeCarouselSlides.push({ imageUrl: url, ...copy, customText: false });
      }
    }
    const preferredIndex = target === "carousel-replace"
      ? index
      : target === "carousel-add"
      ? DISPLAY_EDIT.draft.welcomeCarouselSlides.length - 1
      : carouselIndex;
    markDisplayEditDirty(selected.length > 1 ? `已添加 ${selected.length} 张轮播图，记得保存` : "图片已上传，记得保存");
    applyDisplayEditDraft(preferredIndex);
  } catch (error) {
    displayEditStatus(error.message || "图片上传失败", "error");
    if (DISPLAY_EDIT.dirty) applyDisplayEditDraft(carouselIndex);
  } finally {
    document.body.classList.remove("display-edit-busy");
    if (DISPLAY_EDIT.saveButton) DISPLAY_EDIT.saveButton.disabled = !DISPLAY_EDIT.dirty;
    event.target.value = "";
  }
}

async function saveDisplayEdits() {
  if (!DISPLAY_EDIT.ready || !DISPLAY_EDIT.draft) return;
  if (!DISPLAY_EDIT.dirty) {
    displayEditStatus("当前没有需要保存的修改", "ok");
    return;
  }
  if (DISPLAY_EDIT.saveButton) DISPLAY_EDIT.saveButton.disabled = true;
  displayEditStatus("正在保存成果超市欢迎页…", "warn");
  try {
    const payload = await displayEditApi("/api/achievement-market/config", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(DISPLAY_EDIT.draft),
    });
    DISPLAY_EDIT.draft = normalizeDisplayEditConfig(payload.config || DISPLAY_EDIT.draft);
    DISPLAY_EDIT.original = cloneDisplayEditValue(DISPLAY_EDIT.draft);
    DISPLAY_EDIT.dirty = false;
    applyDisplayEditDraft(carouselIndex);
    displayEditStatus("已保存，前台展示已更新", "ok");
  } catch (error) {
    displayEditStatus(error.message || "保存失败", "error");
  } finally {
    if (DISPLAY_EDIT.saveButton) DISPLAY_EDIT.saveButton.disabled = !DISPLAY_EDIT.dirty;
  }
}

async function initDisplayEdit(config = {}) {
  if (!DISPLAY_EDIT.enabled) return;
  createDisplayEditToolbar();
  try {
    const session = await displayEditApi("/api/session");
    if (!session.authenticated || !(session.permissions || []).includes("admin")) {
      throw new Error("请先登录管理员账号，再进入成果超市可视化编辑");
    }
    DISPLAY_EDIT.csrfToken = session.csrfToken || "";
    DISPLAY_EDIT.draft = normalizeDisplayEditConfig(config);
    DISPLAY_EDIT.original = cloneDisplayEditValue(DISPLAY_EDIT.draft);
    DISPLAY_EDIT.ready = true;
    document.body.classList.add("display-edit-mode");
    ensureDisplayEditControls();
    applyDisplayEditDraft(carouselIndex);
    displayEditStatus("点击左侧大图或轮播图上的按钮进行修改", "ok");
  } catch (error) {
    displayEditStatus(error.message || "编辑模式不可用", "error");
  }
}

function normalizeDetailImageTransform(value = {}) {
  const source = value && typeof value === "object" ? value : {};
  return {
    scale: Math.max(0.5, Math.min(2.5, Number(source.scale) || 1)),
    rotate: Math.max(-360, Math.min(360, Number(source.rotate) || 0)),
  };
}

function applyDetailImageTransform(value = {}) {
  if (!detailImage) return;
  const transform = normalizeDetailImageTransform(value);
  detailImage.style.transform = `rotate(${transform.rotate}deg) scale(${transform.scale})`;
  detailImage.style.transformOrigin = "center center";
}

function detailPublicUrl() {
  const url = new URL(window.location.href);
  url.searchParams.delete("edit");
  url.searchParams.delete("marketItem");
  return `${url.pathname}${url.search}`;
}

function detailEditExitUrl() {
  return currentMarketCategoryEditUrl() || detailPublicUrl();
}

function detailEditStatus(message, kind = "") {
  if (!DETAIL_EDIT.statusNode) return;
  DETAIL_EDIT.statusNode.textContent = message || "";
  DETAIL_EDIT.statusNode.dataset.kind = kind;
}

async function detailEditApi(url, options = {}) {
  const requestOptions = { ...options };
  const method = String(requestOptions.method || "GET").toUpperCase();
  if (method !== "GET" && DETAIL_EDIT.csrfToken) {
    requestOptions.headers = { ...(requestOptions.headers || {}), "X-CSRF-Token": DETAIL_EDIT.csrfToken };
  }
  const response = await fetch(url, requestOptions);
  const payload = await response.json().catch(() => ({}));
  if (!response.ok || payload.ok === false) throw new Error(payload.error || "操作失败");
  return payload;
}

function markDetailEditDirty(message = "有未保存修改") {
  DETAIL_EDIT.dirty = true;
  if (DETAIL_EDIT.saveButton) DETAIL_EDIT.saveButton.disabled = false;
  detailEditStatus(message, "warn");
}

function createDetailEditToolbar() {
  if (DETAIL_EDIT.toolbar) return;
  const frontEditReturnUrl = currentMarketCategoryEditUrl();
  const toolbar = document.createElement("div");
  toolbar.className = "detail-edit-toolbar";
  toolbar.innerHTML = `
    <div class="detail-edit-toolbar-main">
      <strong data-detail-edit-heading>成果项目可视化编辑</strong>
      <span data-detail-edit-status>正在校验管理员身份…</span>
      <button type="button" data-detail-open-editor>编辑正文</button>
      <button type="button" data-detail-edit-save disabled>保存修改</button>
      <a data-detail-edit-admin href="${frontEditReturnUrl || "/admin?view=deploy"}">${frontEditReturnUrl ? "返回分类编辑" : "返回成果超市管理"}</a>
      <a data-detail-edit-exit href="${frontEditReturnUrl ? detailPublicUrl() : detailEditExitUrl()}">${frontEditReturnUrl ? "查看正式页" : "退出编辑"}</a>
    </div>
    <input type="file" accept="image/*" data-detail-edit-file hidden />
  `;
  document.body.appendChild(toolbar);
  DETAIL_EDIT.toolbar = toolbar;
  DETAIL_EDIT.statusNode = toolbar.querySelector("[data-detail-edit-status]");
  DETAIL_EDIT.saveButton = toolbar.querySelector("[data-detail-edit-save]");
  DETAIL_EDIT.fileInput = toolbar.querySelector("[data-detail-edit-file]");
  toolbar.querySelector("[data-detail-open-editor]").addEventListener("click", openDetailRichEditor);
  DETAIL_EDIT.saveButton.addEventListener("click", saveDetailEdits);
  DETAIL_EDIT.fileInput.addEventListener("change", uploadDetailEditImage);
}

function marketEditExitUrl() {
  const url = new URL(window.location.href);
  url.searchParams.delete("edit");
  return `${url.pathname}${url.search}`;
}

function createMarketCategoryEditToolbar() {
  if (MARKET_EDIT.toolbar) return;
  const toolbar = document.createElement("div");
  toolbar.className = "detail-edit-toolbar market-edit-toolbar";
  toolbar.innerHTML = `
    <div class="detail-edit-toolbar-main">
      <strong data-detail-edit-heading>成果分类前台编辑</strong>
      <span data-detail-edit-status>正在校验管理员身份…</span>
      <button type="button" data-detail-open-editor disabled>编辑正文</button>
      <button type="button" data-detail-edit-save disabled>保存修改</button>
      <a data-detail-edit-exit href="${marketEditExitUrl()}">退出编辑</a>
    </div>
    <input type="file" accept="image/*" data-detail-edit-file hidden />
  `;
  document.body.appendChild(toolbar);
  MARKET_EDIT.toolbar = toolbar;
  DETAIL_EDIT.toolbar = toolbar;
  DETAIL_EDIT.statusNode = toolbar.querySelector("[data-detail-edit-status]");
  DETAIL_EDIT.saveButton = toolbar.querySelector("[data-detail-edit-save]");
  DETAIL_EDIT.fileInput = toolbar.querySelector("[data-detail-edit-file]");
  toolbar.querySelector("[data-detail-open-editor]").addEventListener("click", openDetailRichEditor);
  DETAIL_EDIT.saveButton.addEventListener("click", saveDetailEdits);
  DETAIL_EDIT.fileInput.addEventListener("change", uploadDetailEditImage);
}

function currentMarketEditItem(id) {
  return (MARKET_EDIT.items || []).find((item) => String(item.id) === String(id)) || null;
}

function applyMarketSavedItem(item) {
  if (!item || !MARKET_EDIT.enabled) return;
  MARKET_EDIT.items = (MARKET_EDIT.items || []).map((entry) => String(entry.id) === String(item.id) ? { ...entry, ...item } : entry);
  if (MARKET_EDIT.data) {
    MARKET_EDIT.data.items = MARKET_EDIT.items;
    MARKET_EDIT.data.categories = (MARKET_EDIT.data.categories || []).map((category) => ({
      ...category,
      items: (category.items || []).map((entry) => String(entry.id) === String(item.id) ? { ...entry, ...item } : entry),
    }));
    renderMarketCategoryPage(MARKET_EDIT.data, MARKET_EDIT.activeKey);
  }
}

function applyMarketItemToDetailPreview(item) {
  if (!item) return;
  setText(detailTitle, item.title || "");
  const subtitle = item.subtitle || item.intro || "";
  setText(detailSubtitle, subtitle);
  detailSubtitle.hidden = !subtitle;
  detailBody.innerHTML = normalizeRichBody(item.body) || textToRichHtml(item.intro || item.subtitle || "");
  if (detailImage) {
    detailImage.src = item.imageUrl || activeProject?.defaultImageUrl || "/static/expo-stage.png";
    applyDetailImageTransform(normalizeDetailImageTransform(item.imageTransform));
  }
  hydrateAdaptiveMedia(detailBody);
}

function openMarketCategoryItemEditor(itemId) {
  if (!MARKET_EDIT.enabled) return;
  if (!MARKET_EDIT.ready) {
    detailEditStatus("请先登录管理员账号，或稍等身份校验完成", "error");
    return;
  }
  const item = currentMarketEditItem(itemId);
  if (!item) {
    detailEditStatus("未找到这个成果项目", "error");
    return;
  }
  closeDetailRichEditor();
  DETAIL_EDIT.ready = true;
  DETAIL_EDIT.itemId = String(item.id);
  DETAIL_EDIT.draft = { ...item, imageTransform: normalizeDetailImageTransform(item.imageTransform) };
  DETAIL_EDIT.dirty = false;
  applyMarketItemToDetailPreview(item);
  const openButton = DETAIL_EDIT.toolbar?.querySelector("[data-detail-open-editor]");
  if (openButton) openButton.disabled = false;
  if (DETAIL_EDIT.saveButton) DETAIL_EDIT.saveButton.disabled = true;
  detailEditStatus(`正在编辑：${item.title || item.code || "未命名成果"}`, "ok");
  openDetailRichEditor();
}

function closeDetailRichEditor() {
  if (DETAIL_EDIT.editorOverlay) DETAIL_EDIT.editorOverlay.remove();
  DETAIL_EDIT.editorOverlay = null;
  DETAIL_EDIT.editorPanel = null;
  DETAIL_EDIT.titleInput = null;
  DETAIL_EDIT.subtitleInput = null;
  DETAIL_EDIT.bodyEditor = null;
  DETAIL_EDIT.savedRichRange = null;
  DETAIL_EDIT.activeRichEditor = null;
  DETAIL_EDIT.selectedBodyImage = null;
  DETAIL_EDIT.imageTools = null;
}

function syncDetailEditorToPreview() {
  if (!DETAIL_EDIT.bodyEditor) return;
  const nextTitle = displayEditTextValue(DETAIL_EDIT.titleInput);
  const nextSubtitle = displayEditTextValue(DETAIL_EDIT.subtitleInput);
  DETAIL_EDIT.draft.title = nextTitle;
  DETAIL_EDIT.draft.subtitle = nextSubtitle;
  DETAIL_EDIT.draft.intro = nextSubtitle;
  setText(detailTitle, nextTitle || "展项内容已接入");
  setText(detailSubtitle, nextSubtitle);
  detailSubtitle.hidden = !nextSubtitle;
  detailBody.innerHTML = cleanDetailBodyClone(DETAIL_EDIT.bodyEditor).innerHTML.trim();
  hydrateAdaptiveMedia(detailBody);
}

function detailRichEditors() {
  return [DETAIL_EDIT.titleInput, DETAIL_EDIT.subtitleInput, DETAIL_EDIT.bodyEditor].filter(Boolean);
}

function detailEditorContains(editor, node) {
  if (!editor || !node) return false;
  const target = node.nodeType === Node.ELEMENT_NODE ? node : node.parentNode;
  return node === editor || (target && editor.contains(target));
}

function rememberDetailRichRange(preferredEditor = null) {
  const editors = detailRichEditors();
  const selection = window.getSelection();
  if (!selection || !selection.rangeCount) {
    if (preferredEditor) DETAIL_EDIT.activeRichEditor = preferredEditor;
    return;
  }
  const range = selection.getRangeAt(0);
  const editor = editors.find((node) => detailEditorContains(node, range.commonAncestorContainer)) || preferredEditor;
  if (!editor) return;
  DETAIL_EDIT.activeRichEditor = editor;
  DETAIL_EDIT.savedRichRange = range.cloneRange();
}

function currentDetailRichEditor() {
  const editors = detailRichEditors();
  const focused = editors.find((node) => detailEditorContains(node, document.activeElement));
  if (focused) return focused;
  if (DETAIL_EDIT.savedRichRange) {
    const ranged = editors.find((node) => detailEditorContains(node, DETAIL_EDIT.savedRichRange.commonAncestorContainer));
    if (ranged) return ranged;
  }
  return DETAIL_EDIT.activeRichEditor || DETAIL_EDIT.bodyEditor || editors[0] || null;
}

function restoreDetailRichRange(editor = currentDetailRichEditor()) {
  if (!editor) return null;
  editor.focus();
  const selection = window.getSelection();
  const range = DETAIL_EDIT.savedRichRange;
  if (selection && range && detailEditorContains(editor, range.commonAncestorContainer)) {
    selection.removeAllRanges();
    selection.addRange(range);
  }
  DETAIL_EDIT.activeRichEditor = editor;
  return editor;
}

function detailRichEditorLabel(editor) {
  if (editor === DETAIL_EDIT.titleInput) return "封面标题";
  if (editor === DETAIL_EDIT.subtitleInput) return "封面摘要";
  return "正文";
}

function runDetailRichCommand(command, value = null) {
  const editor = restoreDetailRichRange();
  if (!editor) return null;
  document.execCommand(command, false, value);
  rememberDetailRichRange(editor);
  return editor;
}

function bindDetailRichEditorControls(overlay) {
  const editor = DETAIL_EDIT.bodyEditor;
  const statusNode = overlay.querySelector(".item-detail-status");
  const setStatus = (message, kind) => {
    if (!statusNode) return;
    statusNode.textContent = message || "";
    statusNode.dataset.kind = kind || "";
  };
  overlay.querySelectorAll("[data-richtext]").forEach((button) => {
    button.addEventListener("mousedown", (event) => event.preventDefault());
    button.addEventListener("click", () => {
      const target = runDetailRichCommand(button.dataset.richtext);
      setStatus(`${detailRichEditorLabel(target)}格式已修改，记得保存。`, "warn");
    });
  });
  overlay.querySelectorAll("[data-richtext-font], [data-richtext-size]").forEach((select) => {
    select.addEventListener("mousedown", () => rememberDetailRichRange());
    select.addEventListener("change", () => {
      let target = currentDetailRichEditor();
      if (select.dataset.richtextFont !== undefined && select.value) target = runDetailRichCommand("fontName", select.value);
      if (select.dataset.richtextSize !== undefined && select.value) target = runDetailRichCommand("fontSize", select.value);
      select.value = "";
      setStatus(`${detailRichEditorLabel(target)}文字样式已修改，记得保存。`, "warn");
    });
  });
  overlay.querySelectorAll("[data-richtext-block]").forEach((button) => {
    button.addEventListener("mousedown", (event) => event.preventDefault());
    button.addEventListener("click", () => {
      const target = runDetailRichCommand("formatBlock", button.dataset.richtextBlock);
      setStatus(`${detailRichEditorLabel(target)}格式已修改，记得保存。`, "warn");
    });
  });
  overlay.querySelector("[data-detail-upload-body]").addEventListener("click", () => {
    captureDetailBodyRange();
    selectDetailEditFile("body-insert", true);
  });
  overlay.querySelector("[data-detail-editor-save]").addEventListener("click", async () => {
    syncDetailEditorToPreview();
    markDetailEditDirty("正文已更新，保存后生效");
    await saveDetailEdits();
    if (!DETAIL_EDIT.dirty) closeDetailRichEditor();
  });
  overlay.querySelector("[data-detail-editor-close]").addEventListener("click", closeDetailRichEditor);
  overlay.addEventListener("click", (event) => {
    if (event.target === overlay) closeDetailRichEditor();
  });
  [DETAIL_EDIT.titleInput, DETAIL_EDIT.subtitleInput, editor].forEach((node) => {
    if (!node) return;
    node.addEventListener("input", () => {
      rememberDetailRichRange(node);
      updateDisplayEditEmptyState(node, displayEditTextValue(node, node === editor));
      setStatus("有未保存修改。", "warn");
    });
    node.addEventListener("focus", () => rememberDetailRichRange(node));
    node.addEventListener("keyup", () => rememberDetailRichRange(node));
    node.addEventListener("mouseup", () => rememberDetailRichRange(node));
  });
  editor.addEventListener("keydown", (event) => {
    if (event.key === "Tab") {
      event.preventDefault();
      document.execCommand("insertHTML", false, "&nbsp;&nbsp;&nbsp;&nbsp;");
    }
  });
  editor.addEventListener("keyup", captureDetailBodyRange);
  editor.addEventListener("mouseup", captureDetailBodyRange);
  editor.addEventListener("click", (event) => {
    const image = event.target.closest("img");
    if (image && editor.contains(image)) {
      event.preventDefault();
      selectDetailBodyImage(image);
    }
  });
}

function openDetailRichEditor() {
  if (!DETAIL_EDIT.ready || DETAIL_EDIT.editorOverlay) return;
  const overlay = document.createElement("div");
  overlay.className = "item-detail-overlay detail-rich-editor-overlay";
  overlay.innerHTML = `
    <div class="item-detail-panel detail-rich-editor-panel" role="dialog" aria-label="项目详情">
      <button type="button" class="item-detail-close detail-rich-editor-close" data-detail-editor-close aria-label="关闭">×</button>
      <div class="item-detail-toolbar detail-rich-editor-toolbar" aria-label="正文格式工具">
        <select data-richtext-font title="字体">
          <option value="">字体</option>
          <option value="Microsoft YaHei UI">微软雅黑</option>
          <option value="SimSun">宋体</option>
          <option value="SimHei">黑体</option>
          <option value="KaiTi">楷体</option>
          <option value="Arial">Arial</option>
        </select>
        <select data-richtext-size title="字号">
          <option value="">字号</option>
          <option value="2">小</option>
          <option value="3">正文</option>
          <option value="4">大</option>
          <option value="5">特大</option>
          <option value="6">标题</option>
        </select>
        <span class="item-detail-toolbar-sep"></span>
        <button type="button" data-richtext="bold" title="加粗"><b>B</b></button>
        <button type="button" data-richtext="italic" title="斜体"><i>I</i></button>
        <button type="button" data-richtext="underline" title="下划线"><u>U</u></button>
        <span class="item-detail-toolbar-sep"></span>
        <button type="button" data-richtext-block="h3" title="小标题">标题</button>
        <button type="button" data-richtext-block="p" title="正文">正文</button>
        <span class="item-detail-toolbar-sep"></span>
        <button type="button" data-richtext="insertUnorderedList" title="无序列表">• 列表</button>
        <button type="button" data-richtext="insertOrderedList" title="有序列表">1. 列表</button>
        <span class="item-detail-toolbar-sep"></span>
        <button type="button" data-detail-upload-body title="插入图片">图片</button>
        <button type="button" data-richtext="removeFormat" title="清除格式">清除</button>
      </div>
      <label class="detail-editor-field detail-editor-title-field">
        <span class="detail-editor-label">封面标题</span>
        <small>显示在详情页主标题位置，也是项目对外展示的核心名称。</small>
        <h3 class="item-detail-heading" contenteditable="true" spellcheck="false" data-detail-editor-title></h3>
      </label>
      <label class="detail-editor-field">
        <span class="detail-editor-label">封面简介 / 摘要</span>
        <small>显示在封面标题下方，适合填写人物身份、项目概述等短介绍。</small>
        <p class="detail-editor-summary" contenteditable="true" spellcheck="false" data-detail-editor-subtitle></p>
      </label>
      <div class="detail-editor-body-head">
        <span class="detail-editor-label">详情正文</span>
        <small>下方大文本框用于维护完整介绍，可插入图片、分段和设置正文格式。</small>
      </div>
      <div class="item-detail-editor detail-rich-editor-body" contenteditable="true" spellcheck="false"></div>
      <div class="item-detail-actions detail-rich-editor-actions">
        <span class="item-detail-status">封面简介会显示在标题下方；详情正文显示在页面正文区域。</span>
        <button type="button" class="item-detail-close-bottom" data-detail-editor-close>取消</button>
        <button type="button" class="item-detail-save primary" data-detail-editor-save>保存</button>
      </div>
    </div>
  `;
  document.body.appendChild(overlay);
  DETAIL_EDIT.editorOverlay = overlay;
  DETAIL_EDIT.editorPanel = overlay.querySelector(".detail-rich-editor-panel");
  DETAIL_EDIT.titleInput = overlay.querySelector("[data-detail-editor-title]");
  DETAIL_EDIT.subtitleInput = overlay.querySelector("[data-detail-editor-subtitle]");
  DETAIL_EDIT.bodyEditor = overlay.querySelector(".detail-rich-editor-body");
  DETAIL_EDIT.titleInput.dataset.placeholder = "标题（可留空）";
  DETAIL_EDIT.subtitleInput.dataset.placeholder = "摘要（可留空）";
  DETAIL_EDIT.bodyEditor.dataset.placeholder = "正文（可留空）";
  DETAIL_EDIT.titleInput.textContent = cleanEditableTextValue(DETAIL_EDIT.draft?.title || "");
  DETAIL_EDIT.subtitleInput.textContent = cleanEditableTextValue(DETAIL_EDIT.draft?.subtitle || DETAIL_EDIT.draft?.intro || "");
  DETAIL_EDIT.bodyEditor.innerHTML = detailBody.innerHTML.trim();
  [DETAIL_EDIT.titleInput, DETAIL_EDIT.subtitleInput, DETAIL_EDIT.bodyEditor].forEach((node) => {
    updateDisplayEditEmptyState(node, displayEditTextValue(node, node === DETAIL_EDIT.bodyEditor));
  });
  createDetailBodyImageTools();
  bindDetailRichEditorControls(overlay);
  bindDetailTemplateFigureCaptions();
  hydrateAdaptiveMedia(DETAIL_EDIT.bodyEditor);
  DETAIL_EDIT.bodyEditor.focus();
}

function captureDetailBodyRange() {
  const selection = window.getSelection();
  if (!selection || !selection.rangeCount) return;
  const range = selection.getRangeAt(0);
  const editor = DETAIL_EDIT.bodyEditor || detailBody;
  if (editor && editor.contains(range.commonAncestorContainer)) DETAIL_EDIT.savedRange = range.cloneRange();
}

function bindDetailEditableText(node, field, options = {}) {
  if (!node) return;
  node.dataset.detailEditText = field;
  node.dataset.placeholder = options.placeholder || "可直接编辑，允许留空";
  bindDisplayEditText(node, (value) => {
    DETAIL_EDIT.draft[field] = value;
    markDetailEditDirty("文字已修改，保存后生效");
  }, { multiline: Boolean(options.multiline) });
}

function selectDetailEditFile(target, multiple = false) {
  if (!DETAIL_EDIT.ready || !DETAIL_EDIT.fileInput) return;
  DETAIL_EDIT.uploadTarget = target;
  DETAIL_EDIT.fileInput.multiple = multiple;
  DETAIL_EDIT.fileInput.value = "";
  DETAIL_EDIT.fileInput.click();
}

function updateDetailCoverTools() {
  if (!DETAIL_EDIT.coverTools || !DETAIL_EDIT.draft) return;
  const transform = normalizeDetailImageTransform(DETAIL_EDIT.draft.imageTransform);
  const label = DETAIL_EDIT.coverTools.querySelector("[data-detail-cover-value]");
  if (label) label.textContent = `${Math.round(transform.scale * 100)}% · ${transform.rotate}°`;
}

function adjustDetailCover(action) {
  if (!DETAIL_EDIT.draft) return;
  const transform = normalizeDetailImageTransform(DETAIL_EDIT.draft.imageTransform);
  if (action === "scale-down") transform.scale = Math.max(0.5, Number((transform.scale - 0.1).toFixed(2)));
  if (action === "scale-up") transform.scale = Math.min(2.5, Number((transform.scale + 0.1).toFixed(2)));
  if (action === "rotate-left") transform.rotate = Math.max(-360, transform.rotate - 15);
  if (action === "rotate-right") transform.rotate = Math.min(360, transform.rotate + 15);
  if (action === "reset") Object.assign(transform, { scale: 1, rotate: 0 });
  if (action === "remove") {
    DETAIL_EDIT.draft.imageUrl = "";
    detailImage.src = activeProject?.defaultImageUrl || "/static/expo-stage.png";
  }
  DETAIL_EDIT.draft.imageTransform = transform;
  applyDetailImageTransform(transform);
  updateDetailCoverTools();
  markDetailEditDirty(action === "remove" ? "封面已移除，保存后生效" : "封面显示效果已修改，保存后生效");
}

function createDetailCoverTools() {
  if (!detailImage?.parentElement || DETAIL_EDIT.coverTools) return;
  const tools = document.createElement("div");
  tools.className = "detail-edit-cover-tools detail-edit-control";
  tools.innerHTML = `
    <strong>封面</strong>
    <button type="button" data-detail-cover-action="upload">更换封面</button>
    <button type="button" class="danger" data-detail-cover-action="remove">移除</button>
  `;
  tools.addEventListener("click", (event) => {
    const button = event.target.closest("[data-detail-cover-action]");
    if (!button) return;
    event.preventDefault();
    event.stopPropagation();
    if (button.dataset.detailCoverAction === "upload") selectDetailEditFile("cover");
    else adjustDetailCover(button.dataset.detailCoverAction);
  });
  detailImage.parentElement.appendChild(tools);
  DETAIL_EDIT.coverTools = tools;
  updateDetailCoverTools();
}

function bodyImageTransform(image) {
  const match = String(image?.style?.transform || "").match(/rotate\((-?\d+(?:\.\d+)?)deg\)\s+scale\((\d+(?:\.\d+)?)\)/i);
  return normalizeDetailImageTransform(match ? { rotate: match[1], scale: match[2] } : {});
}

function applyBodyImageTransform(image, transform) {
  const value = normalizeDetailImageTransform(transform);
  image.style.transform = `rotate(${value.rotate}deg) scale(${value.scale})`;
  image.style.transformOrigin = "center center";
  return value;
}

function updateDetailBodyImageTools() {
  if (!DETAIL_EDIT.imageTools || !DETAIL_EDIT.selectedBodyImage) return;
  const transform = bodyImageTransform(DETAIL_EDIT.selectedBodyImage);
  const label = DETAIL_EDIT.imageTools.querySelector("[data-detail-body-image-value]");
  if (label) label.textContent = `${Math.round(transform.scale * 100)}% · ${transform.rotate}°`;
}

function selectDetailBodyImage(image) {
  if (DETAIL_EDIT.selectedBodyImage) DETAIL_EDIT.selectedBodyImage.classList.remove("detail-edit-selected-image");
  DETAIL_EDIT.selectedBodyImage = image;
  if (!image) {
    if (DETAIL_EDIT.imageTools) DETAIL_EDIT.imageTools.hidden = true;
    return;
  }
  image.classList.add("detail-edit-selected-image");
  if (DETAIL_EDIT.imageTools) {
    DETAIL_EDIT.imageTools.hidden = false;
    if (DETAIL_EDIT.bodyEditor && DETAIL_EDIT.editorPanel && !DETAIL_EDIT.editorPanel.contains(DETAIL_EDIT.imageTools)) {
      const actions = DETAIL_EDIT.editorPanel.querySelector(".detail-rich-editor-actions");
      DETAIL_EDIT.editorPanel.insertBefore(DETAIL_EDIT.imageTools, actions || null);
    }
  }
  updateDetailBodyImageTools();
}

function adjustDetailBodyImage(action) {
  const image = DETAIL_EDIT.selectedBodyImage;
  if (!image) return;
  const transform = bodyImageTransform(image);
  if (action === "scale-down") transform.scale = Math.max(0.5, Number((transform.scale - 0.1).toFixed(2)));
  if (action === "scale-up") transform.scale = Math.min(2.5, Number((transform.scale + 0.1).toFixed(2)));
  if (action === "rotate-left") transform.rotate = Math.max(-360, transform.rotate - 15);
  if (action === "rotate-right") transform.rotate = Math.min(360, transform.rotate + 15);
  if (action === "reset") Object.assign(transform, { scale: 1, rotate: 0 });
  if (action === "remove") {
    const target = image.closest("figure") || image;
    target.remove();
    selectDetailBodyImage(null);
    markDetailEditDirty("正文图片已删除，保存后生效");
    return;
  }
  applyBodyImageTransform(image, transform);
  updateDetailBodyImageTools();
  markDetailEditDirty("正文图片显示效果已修改，保存后生效");
}

function createDetailBodyImageTools() {
  if (DETAIL_EDIT.imageTools) return;
  const tools = document.createElement("div");
  tools.className = "detail-edit-body-image-tools detail-edit-control";
  tools.hidden = true;
  tools.innerHTML = `
    <strong>正文图片</strong>
    <span data-detail-body-image-value>100% · 0°</span>
    <button type="button" data-detail-body-image-action="replace">更换</button>
    <button type="button" data-detail-body-image-action="scale-down">缩小</button>
    <button type="button" data-detail-body-image-action="scale-up">放大</button>
    <button type="button" data-detail-body-image-action="rotate-left">左转</button>
    <button type="button" data-detail-body-image-action="rotate-right">右转</button>
    <button type="button" data-detail-body-image-action="reset">重置</button>
    <button type="button" class="danger" data-detail-body-image-action="remove">删除</button>
  `;
  tools.addEventListener("click", (event) => {
    const button = event.target.closest("[data-detail-body-image-action]");
    if (!button) return;
    event.preventDefault();
    event.stopPropagation();
    if (button.dataset.detailBodyImageAction === "replace") selectDetailEditFile("body-replace");
    else adjustDetailBodyImage(button.dataset.detailBodyImageAction);
  });
  if (DETAIL_EDIT.editorPanel) {
    const actions = DETAIL_EDIT.editorPanel.querySelector(".detail-rich-editor-actions");
    DETAIL_EDIT.editorPanel.insertBefore(tools, actions || null);
  } else {
    document.body.appendChild(tools);
  }
  DETAIL_EDIT.imageTools = tools;
}

function bindDetailTemplateFigureCaptions() {
  const editor = DETAIL_EDIT.bodyEditor || detailBody;
  if (!DETAIL_EDIT.ready || !editor) return;
  editor.querySelectorAll("figcaption").forEach((caption) => {
    caption.dataset.placeholder = caption.dataset.placeholder || "图片说明（可留空）";
    clearEditablePlaceholderText(caption);
    if (caption.dataset.detailCaptionBound === "1") return;
    caption.dataset.detailCaptionBound = "1";
    caption.contentEditable = "true";
    caption.spellcheck = false;
    caption.addEventListener("click", (event) => event.stopPropagation());
    caption.addEventListener("input", () => {
      updateDisplayEditEmptyState(caption, displayEditTextValue(caption));
      markDetailEditDirty("图片说明已修改，保存后生效");
    });
  });
}

function insertDetailBodyImage(url, keepInsertionPoint = false) {
  const editor = DETAIL_EDIT.bodyEditor || detailBody;
  if (!editor) return;
  const figure = document.createElement("figure");
  figure.className = "detail-edit-figure";
  const image = document.createElement("img");
  image.src = url;
  image.alt = "";
  applyBodyImageTransform(image, { scale: 1, rotate: 0 });
  const caption = document.createElement("figcaption");
  caption.dataset.placeholder = "图片说明（可留空）";
  caption.textContent = "";
  updateDisplayEditEmptyState(caption, "");
  figure.append(image, caption);
  const range = DETAIL_EDIT.savedRange;
  if (range && editor.contains(range.commonAncestorContainer)) {
    range.deleteContents();
    range.insertNode(figure);
  } else {
    editor.appendChild(figure);
  }
  if (keepInsertionPoint) {
    const nextRange = document.createRange();
    nextRange.setStartAfter(figure);
    nextRange.collapse(true);
    DETAIL_EDIT.savedRange = nextRange;
  } else {
    DETAIL_EDIT.savedRange = null;
  }
  selectDetailBodyImage(image);
  bindDetailTemplateFigureCaptions();
  hydrateAdaptiveMedia(figure);
  markDetailEditDirty("正文图片已插入，保存后生效");
}

async function uploadDetailEditImage(event) {
  const target = DETAIL_EDIT.uploadTarget;
  const images = Array.from(event.target.files || []).filter((file) => String(file.type || "").startsWith("image/"));
  const selected = target === "body-insert" ? images : images.slice(0, 1);
  if (!selected.length) {
    event.target.value = "";
    return;
  }
  document.body.classList.add("detail-edit-busy");
  if (DETAIL_EDIT.saveButton) DETAIL_EDIT.saveButton.disabled = true;
  try {
    for (let index = 0; index < selected.length; index += 1) {
      const file = selected[index];
      detailEditStatus(`正在上传 ${index + 1} / ${selected.length}：${file.name}`, "warn");
      const dataUrl = await fileToDataUrl(file);
      const payload = await detailEditApi("/api/assets", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ filename: file.name, dataUrl }),
      });
      const url = payload.url || payload.asset?.url || "";
      if (!url) throw new Error("上传成功但未返回图片地址");
      if (target === "cover") {
        DETAIL_EDIT.draft.imageUrl = url;
        detailImage.src = url;
        hydrateAdaptiveMedia(detailImage.parentElement);
      }
      if (target === "body-insert") insertDetailBodyImage(url, index < selected.length - 1);
      if (target === "body-replace" && DETAIL_EDIT.selectedBodyImage) {
        DETAIL_EDIT.selectedBodyImage.src = url;
      }
    }
    markDetailEditDirty(selected.length > 1 ? `已插入 ${selected.length} 张图片，记得保存` : "图片已上传，记得保存");
  } catch (error) {
    detailEditStatus(error.message || "图片上传失败", "error");
  } finally {
    document.body.classList.remove("detail-edit-busy");
    if (DETAIL_EDIT.saveButton) DETAIL_EDIT.saveButton.disabled = !DETAIL_EDIT.dirty;
    event.target.value = "";
  }
}

function cleanDetailBodyClone(source) {
  const clone = source.cloneNode(true);
  clone.querySelectorAll("figcaption").forEach((caption) => {
    const value = cleanEditableTextValue(caption.textContent, caption);
    if (!value) {
      caption.remove();
      return;
    }
    caption.textContent = value;
  });
  clone.querySelectorAll(".detail-edit-selected-image").forEach((node) => node.classList.remove("detail-edit-selected-image"));
  clone.querySelectorAll("[contenteditable], [data-detail-edit-text], [data-display-edit-bound], [data-detail-caption-bound], [data-edit-empty], [data-placeholder]").forEach((node) => {
    node.removeAttribute("contenteditable");
    node.removeAttribute("data-detail-edit-text");
    node.removeAttribute("data-display-edit-bound");
    node.removeAttribute("data-detail-caption-bound");
    node.removeAttribute("data-edit-empty");
    node.removeAttribute("data-placeholder");
  });
  return clone;
}

function detailBodyHtmlForSave() {
  const clone = cleanDetailBodyClone(detailBody);
  return clone.innerHTML.trim();
}

async function saveDetailEdits() {
  if (!DETAIL_EDIT.ready || !DETAIL_EDIT.draft) return;
  if (DETAIL_EDIT.bodyEditor) syncDetailEditorToPreview();
  if (!DETAIL_EDIT.dirty) {
    detailEditStatus("当前没有需要保存的修改", "ok");
    return;
  }
  DETAIL_EDIT.saveButton.disabled = true;
  detailEditStatus("正在保存项目详情…", "warn");
  try {
    const payload = await detailEditApi(`/api/achievement-market/items/${encodeURIComponent(DETAIL_EDIT.itemId)}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        title: DETAIL_EDIT.draft.title,
        subtitle: DETAIL_EDIT.draft.subtitle,
        intro: DETAIL_EDIT.draft.intro,
        imageUrl: DETAIL_EDIT.draft.imageUrl,
        imageTransform: normalizeDetailImageTransform(DETAIL_EDIT.draft.imageTransform),
        body: detailBodyHtmlForSave(),
        categoryKey: DETAIL_EDIT.draft.categoryKey,
        sortOrder: DETAIL_EDIT.draft.sortOrder,
        enabled: DETAIL_EDIT.draft.enabled,
      }),
    });
    DETAIL_EDIT.draft = { ...DETAIL_EDIT.draft, ...(payload.item || {}) };
    applyMarketSavedItem(payload.item || DETAIL_EDIT.draft);
    DETAIL_EDIT.dirty = false;
    detailEditStatus("项目详情已保存，正式展示已更新", "ok");
  } catch (error) {
    detailEditStatus(error.message || "保存失败", "error");
  } finally {
    DETAIL_EDIT.saveButton.disabled = !DETAIL_EDIT.dirty;
  }
}

function bindDetailEditCanvas() {
  document.body.classList.add("detail-edit-mode");
  stopDetailAutoScroll();
  detailSubtitle.hidden = false;
  if (!DETAIL_EDIT.contentClickBound && detailContentPanel) {
    DETAIL_EDIT.contentClickBound = true;
    detailContentPanel.addEventListener("click", (event) => {
      if (!DETAIL_EDIT.ready || DETAIL_EDIT.editorOverlay) return;
      if (event.target.closest("a, button, input, textarea, select, [contenteditable='true']")) return;
      openDetailRichEditor();
    });
  }
  createDetailCoverTools();
  createDetailBodyImageTools();
}

async function initDetailEdit() {
  if (!DETAIL_EDIT.enabled) return;
  createDetailEditToolbar();
  try {
    const session = await detailEditApi("/api/session");
    if (!session.authenticated || !(session.permissions || []).includes("admin")) {
      throw new Error("请先登录管理员账号，再进入项目可视化编辑");
    }
    DETAIL_EDIT.csrfToken = session.csrfToken || "";
    const projectId = initialParams.get("project") || activeProject?.id || 0;
    const payload = await detailEditApi(`/api/achievement-market?projectId=${encodeURIComponent(projectId)}`);
    const requestedId = initialParams.get("marketItem") || "";
    const code = initialParams.get("code") || activeDetailPage?.code || "";
    const item = (payload.items || []).find((entry) => requestedId ? String(entry.id) === String(requestedId) : String(entry.code) === String(code));
    if (!item) throw new Error("未找到对应的成果超市项目");
    DETAIL_EDIT.itemId = String(item.id);
    DETAIL_EDIT.draft = { ...item, imageTransform: normalizeDetailImageTransform(item.imageTransform) };
    DETAIL_EDIT.ready = true;
    DETAIL_EDIT.toolbar.querySelector("[data-detail-edit-heading]").textContent = `项目详情可视化编辑 · ${item.title || item.code}`;
    applyMarketItemToDetailPreview(item);
    const categoryKey = normalizedMarketKey(item.categoryKey || initialParams.get("market") || "teaching");
    const frontEditReturnUrl = (initialParams.get("market") || initialParams.get("topic"))
      ? currentMarketCategoryEditUrl(categoryKey)
      : "";
    const returnLink = DETAIL_EDIT.toolbar.querySelector("[data-detail-edit-admin]");
    if (returnLink) {
      returnLink.href = frontEditReturnUrl || `/admin?view=deploy&market=${encodeURIComponent(categoryKey || "teaching")}`;
      returnLink.textContent = frontEditReturnUrl ? "返回分类编辑" : "返回成果超市管理";
    }
    const exitLink = DETAIL_EDIT.toolbar.querySelector("[data-detail-edit-exit]");
    if (exitLink) {
      exitLink.href = frontEditReturnUrl ? detailPublicUrl() : detailEditExitUrl();
      exitLink.textContent = frontEditReturnUrl ? "查看正式页" : "退出编辑";
    }
    applyDetailMarketTheme(item);
    applyDetailImageTransform(DETAIL_EDIT.draft.imageTransform);
    bindDetailEditCanvas();
    detailEditStatus("封面可直接更换；正文请进入富文本编辑器维护", "ok");
  } catch (error) {
    detailEditStatus(error.message || "编辑模式不可用", "error");
  }
}

async function loadMarketSummary() {
  try {
    const res = await fetch("/api/achievement-market/public", { cache: "no-store" });
    if (!res.ok) return null;
    const data = await res.json();
    if (data.ok) {
      applyMarketWelcomeConfig(data.config || {});
      renderMarketHomeLinks(data.categories || []);
      return data;
    }
  } catch {
    // The display page remains usable even if the market layer is not configured yet.
  }
  return null;
}

function renderMarketCategoryPage(data, activeKey) {
  const config = data.config || {};
  const categories = data.categories || [];
  const category = categories[0] || marketThemeMap[activeKey] || {};
  const theme = marketThemeMap[category.key] || category || {};
  const color = category.color || theme.color || marketThemeMap.teaching.color;
  const topicSlug = String(data.topicSlug || initialParams.get("topic") || "").trim();
  const topicLabel = String(data.topicName || "").trim();
  const editMode = MARKET_EDIT.enabled;
  MARKET_EDIT.data = data;
  MARKET_EDIT.activeKey = activeKey;
  document.documentElement.style.setProperty("--accent", color);
  setText(marketLabel, topicSlug ? "专题成果超市" : (category.label || theme.label || "成果超市"));
  setText(marketTitle, category.label ? `${topicLabel ? `${topicLabel} · ` : ""}${category.label}展示页` : (config.welcomeTitle || "成果超市"));
  setText(marketIntro, editMode ? "前台编辑模式：点击卡片进入二级详情页，可编辑左侧封面和右侧富文本，保存后与成果超市后台同步。" : (category.description || config.welcomeIntro || "选择展示项目，扫码或点击进入详情页。"));
  marketCategoryNav.innerHTML = Object.entries(marketThemeMap).map(([key, item]) => `
    <a class="${key === activeKey ? "active" : ""}" style="--color:${item.color}" href="/display?market=${encodeURIComponent(key)}${topicSlug ? `&topic=${encodeURIComponent(topicSlug)}` : ""}${editMode ? "&edit=1" : ""}">${item.label}</a>
  `).join("");
  const items = data.items || [];
  MARKET_EDIT.items = items;
  marketItems.classList.toggle("is-editing", editMode);
  marketItems.innerHTML = items.length ? items.map((item) => {
    const itemUrl = marketItemUrl(item);
    const publicUrl = new URL(itemUrl, window.location.origin).toString();
    const qr = `/api/qr-public?data=${encodeURIComponent(publicUrl)}`;
    const detailHref = editMode ? marketItemEditUrl(item, topicSlug, category.key || activeKey) : itemUrl;
    return `
      <article class="market-card" style="--color:${item.color || color}">
        <a class="market-card-detail" href="${escapeHtml(detailHref)}">
          <figure>
            ${item.imageUrl ? `<img src="${escapeHtml(item.imageUrl)}" alt="" />` : `<span>${escapeHtml(item.categoryLabel || category.label || "成果")}</span>`}
            <figcaption>${escapeHtml(item.categoryLabel || category.label || "成果")}</figcaption>
          </figure>
          <div class="market-card-copy">
            <span>${escapeHtml(topicLabel || item.projectName || "成果超市")}</span>
            <h2>${escapeHtml(item.title || "")}</h2>
            <p>${escapeHtml(item.intro || item.subtitle || "")}</p>
          </div>
        </a>
        <div class="market-card-actions">
          <span class="market-card-code">${escapeHtml(item.code || "")}</span>
          ${editMode ? `<a class="market-card-edit-button" href="${escapeHtml(detailHref)}">编辑详情</a>` : ""}
          <a class="market-card-qr" href="${escapeHtml(detailHref)}" aria-label="打开${escapeHtml(item.title || "成果详情")}">
            <img src="${escapeHtml(qr)}" alt="" />
            <strong>扫码 / 点击详情</strong>
          </a>
        </div>
      </article>
    `;
  }).join("") : `<div class="market-empty">当前主题暂无已发布展示项目</div>`;
  show("market");
}

async function loadMarketCategory() {
  const activeKey = initialParams.get("market") || "";
  if (!activeKey) return false;
  const key = marketThemeAliases[activeKey] || activeKey;
  if (!marketThemeMap[key]) return false;
  const topicSlug = initialParams.get("topic") || "";
  const res = await fetch(`/api/achievement-market/public?category=${encodeURIComponent(key)}${topicSlug ? `&topic=${encodeURIComponent(topicSlug)}` : ""}`, { cache: "no-store" });
  if (!res.ok) return false;
  const data = await res.json();
  if (!data.ok) return false;
  renderMarketCategoryPage(data, key);
  return true;
}

async function initMarketCategoryEdit() {
  if (!MARKET_EDIT.enabled) return;
  createMarketCategoryEditToolbar();
  document.body.classList.add("market-edit-mode");
  try {
    const session = await detailEditApi("/api/session");
    if (!session.authenticated || !(session.permissions || []).includes("admin")) {
      throw new Error("请先登录管理员账号，再进入成果前台编辑");
    }
    DETAIL_EDIT.csrfToken = session.csrfToken || "";
    MARKET_EDIT.ready = true;
    DETAIL_EDIT.ready = true;
    detailEditStatus("点击任意成果卡片，进入二级详情页编辑封面和正文", "ok");
  } catch (error) {
    MARKET_EDIT.ready = false;
    DETAIL_EDIT.ready = false;
    detailEditStatus(error.message || "编辑模式不可用", "error");
  }
}

function applyProject(project) {
  activeProject = project || {};
  const config = normalizeDisplayConfig(activeProject.displayConfig);
  const accent = activeProject.accent || "#f59a13";
  const image = activeProject.defaultImageUrl || "/static/expo-stage.png";
  const name = activeProject.name || "学校宣传大屏";
  const schoolDisplayName = String(config.schoolName ?? name).trim();

  document.documentElement.style.setProperty("--accent", accent);
  document.documentElement.style.setProperty("--accent-2", config.accent2 || "#47b7ff");
  document.documentElement.style.setProperty("--brand-blue", config.brandColor || "#28539c");
  document.documentElement.style.setProperty("--brand-blue-deep", config.brandDeepColor || "#20468b");
  document.documentElement.style.setProperty("--project-image", cssUrl(image));

  // 顶部品牌区：仅保留居中的学校图标（素材写死）
  brandLogo.src = config.logoImageUrl;
  brandLogo.hidden = false;
  brandLogo.alt = `${schoolDisplayName || name}标识`;

  const tags = normalizeTags(config.summaryTags);

  if (heroLabel) heroLabel.hidden = true;
  if (heroTitle) heroTitle.hidden = true;
  if (heroSubtitle) heroSubtitle.hidden = true;
  if (heroCopy) heroCopy.hidden = true;
  if (heroTags) heroTags.hidden = true;

  setText(scanTitle, config.scanTitle);
  scanTitle.hidden = !config.scanTitle;
  setText(scanCopy, config.scanCopy);
  scanCopy.hidden = !config.scanCopy;
  if (scanCard) scanCard.hidden = !config.scanTitle && !config.scanCopy;
  const scanImageUrl = String(config.scanImageUrl || "").trim();
  if (scanImageUrl) {
    scanImage.src = scanImageUrl;
    scanImage.hidden = false;
    if (qrMark) qrMark.hidden = true;
  } else {
    scanImage.removeAttribute("src");
    scanImage.hidden = true;
    if (qrMark) qrMark.hidden = false;
  }
  setText(summaryLabel, config.summaryLabel);
  summaryLabel.hidden = !config.summaryLabel;
  setText(summaryTitle, config.summaryTitle);
  summaryTitle.hidden = !config.summaryTitle;
  setText(summaryCopy, config.summaryCopy);
  summaryCopy.hidden = !config.summaryCopy;
  setText(projectState, `当前部署项目 · ${name}`);
  setText(footerProject, name);
  setText(footerStatus, previewMode ? "预览模式" : "实时等待扫码内容");
  setText(footerTime, "Display Ready");
  setText(metricProject, String(activeProject.id || 1).padStart(2, "0").slice(-2));

  summaryTags.innerHTML = "";
  tags.forEach((tag) => {
    const pill = document.createElement("span");
    pill.className = "tag";
    pill.textContent = tag;
    summaryTags.appendChild(pill);
  });
  if (summaryPanel) {
    summaryPanel.hidden = !config.summaryLabel && !config.summaryTitle && !config.summaryCopy && !tags.length;
  }

  renderCarousel(config.slides);
}

function show(view) {
  if (view !== "page") stopDetailAutoScroll();
  app.className = `screen ${view}`;
  idleView.hidden = view !== "idle";
  marketView.hidden = view !== "market";
  pageView.hidden = view !== "page";

  const active = view === "idle" ? idleView : view === "market" ? marketView : pageView;
  active.classList.remove("fade-in");
  void active.offsetWidth;
  active.classList.add("fade-in");
}

function topicOverviewReturnUrl() {
  const topicSlug = String(initialParams.get("topic") || "")
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9-]+/g, "-")
    .replace(/-{2,}/g, "-")
    .replace(/^-|-$/g, "");
  if (topicSlug) return `/topics/${encodeURIComponent(topicSlug)}?section=overview`;

  const projectSlug = String(activeProject?.portalSlug || "")
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9-]+/g, "-")
    .replace(/-{2,}/g, "-")
    .replace(/^-|-$/g, "");
  return activeProject?.portalType === "topic" && projectSlug
    ? `/topics/${encodeURIComponent(projectSlug)}?section=overview`
    : "";
}

function goHome() {
  const topicUrl = topicOverviewReturnUrl();
  if (topicUrl) {
    window.location.assign(topicUrl);
    return;
  }
  homeResetAt = Date.now();
  show("idle");
  if (window.location.pathname === "/display" && window.location.search) {
    window.history.replaceState(null, "", "/display");
  }
}

function replaceDisplayUrl(url) {
  if (previewMode) return;
  if (!url || window.location.pathname !== "/display") return;
  const next = new URL(url, window.location.origin);
  if (next.origin === window.location.origin && next.pathname === "/display") {
    window.history.replaceState(null, "", `${next.pathname}${next.search}`);
  }
}

function renderPage(scan) {
  if (!scan?.page) return;
  if (scan.receivedAt && scan.receivedAt === lastRenderedScanAt) return;
  lastRenderedScanAt = scan.receivedAt || new Date().toISOString();
  replaceDisplayUrl(scan.localDisplayUrl || scan.displayUrl);

  const page = scan.page;
  const project = scan.project || activeProject || {};
  activeDetailPage = page;
  applyProject(project);

  const accent = page.accent || project.accent || "#f59a13";
  document.documentElement.style.setProperty("--accent", accent);
  applyDetailMarketTheme(page);

  const code = page.code || scan.code || "—";
  const category = page.marketCategoryLabel || page.category || "校园成果";
  const source = page.source || project.name || "学校展示";
  const publishDate = formatDate(page.publishedAt || page.updatedAt);

  setText(detailCode, `编号 ${code}`);
  setText(detailMediaTitle, category);
  setText(detailCategory, category);
  setText(detailSource, source);
  detailSource.hidden = !source;
  setText(detailDate, publishDate);
  detailDate.hidden = !publishDate;
  setText(detailTitle, page.title || "展项内容已接入");
  setText(detailSubtitle, page.subtitle || "扫码后，大屏直接切换到对应编号内容。");
  detailSubtitle.hidden = !page.subtitle;
  detailBody.innerHTML =
    normalizeRichBody(page.body) ||
    textToRichHtml("该编号内容已从当前部署项目读取。请在后台维护标题、图片和正文，以获得完整展示效果。");
  detailImage.src = page.imageUrl || project.defaultImageUrl || "/static/expo-stage.png";
  applyDetailImageTransform(page.imageTransform);
  hydrateAdaptiveMedia(pageView);
  setText(footerStatus, `正在展示编号 ${code}`);

  show("page");
  if (!DETAIL_EDIT.enabled) startDetailAutoScroll();
}

function handleScan(scan) {
  if (!scan) return;
  const receivedAtMs = Date.parse(scan.receivedAt || "");
  if (receivedAtMs && receivedAtMs <= homeResetAt) return;
  if (scan.receivedAt && scan.receivedAt === lastRenderedScanAt) return;
  if (scan.external && scan.displayUrl) {
    lastRenderedScanAt = scan.receivedAt || new Date().toISOString();
    window.location.href = scan.displayUrl;
    return;
  }
  renderPage(scan);
}

async function submitScannedText(text) {
  const value = String(text || "").trim();
  if (!value || previewMode) return;
  try {
    const res = await fetch("/api/scan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: value }),
    });
    if (!res.ok) return;
    const data = await res.json();
    if (data.ok && data.scan) handleScan(data.scan);
  } catch {
    // Hardware agent remains primary; keyboard wedge capture is a fallback.
  }
}

function flushScannerKeyBuffer() {
  window.clearTimeout(scannerKeyTimer);
  const value = scannerKeyBuffer.trim();
  scannerKeyBuffer = "";
  scannerLastKeyAt = 0;
  if (value.length >= 5) {
    submitScannedText(value);
  }
}

function bindKeyboardScannerFallback() {
  window.addEventListener("paste", (event) => {
    const value = event.clipboardData?.getData("text") || "";
    if (value.trim().length >= 5) {
      submitScannedText(value);
    }
  });

  window.addEventListener("keydown", (event) => {
    if (event.ctrlKey || event.altKey || event.metaKey) return;
    if (event.key === "Enter" || event.key === "Tab") {
      if (scannerKeyBuffer) {
        event.preventDefault();
        flushScannerKeyBuffer();
      }
      return;
    }
    if (event.key.length !== 1) return;

    const now = Date.now();
    if (scannerLastKeyAt && now - scannerLastKeyAt > 180) {
      scannerKeyBuffer = "";
    }
    scannerLastKeyAt = now;
    scannerKeyBuffer += event.key;
    window.clearTimeout(scannerKeyTimer);
    scannerKeyTimer = window.setTimeout(flushScannerKeyBuffer, 220);
  });
}

function connect() {
  const events = new EventSource("/api/display/events");
  if (connectionState) connectionState.textContent = "展示通道已连接";
  events.addEventListener("scan", (event) => {
    handleScan(JSON.parse(event.data));
  });
  events.onerror = () => {
    if (connectionState) connectionState.textContent = "展示通道重连中";
    events.close();
    setTimeout(connect, 1500);
  };
}

async function pollLatestScan() {
  try {
    const res = await fetch("/api/display/latest", { cache: "no-store" });
    if (!res.ok) return;
    const data = await res.json();
    if (data.ok && data.scan) {
      handleScan(data.scan);
    }
  } catch {
    // SSE remains primary; polling only fills in after transient disconnects.
  }
}

async function loadInitialCode() {
  const project = initialParams.get("project");
  const code = initialParams.get("code");
  const reviewVersion = initialParams.get("reviewVersion");
  if (!code) return;

  const apiUrl = reviewVersion
    ? `/api/reviews/pages/${encodeURIComponent(reviewVersion)}/preview`
    : project
    ? `/api/display/projects/${encodeURIComponent(project)}/pages/${encodeURIComponent(code)}`
    : `/api/pages/${encodeURIComponent(code)}`;
  const res = await fetch(apiUrl, { cache: "no-store" });
  if (!res.ok) return;

  const data = await res.json();
  if (data.ok && data.page) {
    if (data.project) applyProject(data.project);
    renderPage({
      code,
      project: data.project || activeProject,
      page: data.page,
      receivedAt: new Date().toISOString(),
    });
  }
}

async function loadInitialProject() {
  const project = initialParams.get("project");
  const apiUrl = project
    ? `/api/display/projects/${encodeURIComponent(project)}`
    : "/api/display/project";
  const res = await fetch(apiUrl, { cache: "no-store" });
  const data = await res.json();
  if (data.ok) applyProject(data.project);
}

function bindCarouselControls() {
  prevSlide.addEventListener("click", () => {
    showSlide(carouselIndex - 1);
    restartCarousel();
  });

  nextSlide.addEventListener("click", () => {
    showSlide(carouselIndex + 1);
    restartCarousel();
  });

  carouselStage.addEventListener(
    "touchstart",
    (event) => {
      touchStartX = event.touches[0].clientX;
      window.clearTimeout(carouselTimer);
    },
    { passive: true },
  );
  carouselStage.addEventListener("touchend", (event) => {
    const delta = event.changedTouches[0].clientX - touchStartX;
    if (Math.abs(delta) > 45) {
      showSlide(delta < 0 ? carouselIndex + 1 : carouselIndex - 1);
    }
    restartCarousel();
  });

  window.addEventListener("keydown", (event) => {
    if (event.key === "ArrowRight") {
      showSlide(carouselIndex + 1);
      restartCarousel();
    }
    if (event.key === "ArrowLeft") {
      showSlide(carouselIndex - 1);
      restartCarousel();
    }
  });
}

function updateClock() {
  if (!clockTime) return;
  const now = new Date();
  const pad = (value) => String(value).padStart(2, "0");
  clockTime.textContent = `${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`;
}

async function init() {
  // 扫码卡保留在主舞台（左侧），右侧 carouselScanSlot 仅承载成果超市分类入口
  bindCarouselControls();
  if (!DISPLAY_EDIT.enabled && !DETAIL_EDIT.enabled && !MARKET_EDIT.enabled) bindKeyboardScannerFallback();
  try {
    await loadInitialProject();
  } catch {
    applyProject(null);
  }
  if (DETAIL_EDIT.enabled) {
    await loadInitialCode();
    if (connectionState) connectionState.textContent = "项目详情编辑模式";
    await initDetailEdit();
    return;
  }
  if (DISPLAY_EDIT.enabled) {
    show("idle");
    const marketData = await loadMarketSummary();
    if (connectionState) connectionState.textContent = "可视化编辑模式";
    if (footerStatus) footerStatus.textContent = "成果超市欢迎页编辑中";
    await initDisplayEdit(marketData?.config || {});
    return;
  }
  const marketLoaded = await loadMarketCategory();
  if (!marketLoaded) {
    show("idle");
    loadMarketSummary();
  }
  if (MARKET_EDIT.enabled) {
    if (connectionState) connectionState.textContent = marketLoaded ? "成果分类前台编辑模式" : "编辑页面未找到分类";
    if (footerStatus) footerStatus.textContent = "成果超市数据前台编辑中";
    if (marketLoaded) await initMarketCategoryEdit();
    return;
  }
  if (previewMode) {
    if (connectionState) connectionState.textContent = "预览模式";
  } else {
    connect();
    setInterval(pollLatestScan, 1200);
  }
  if (!marketLoaded) loadInitialCode();
}

returnHome.addEventListener("click", goHome);
returnMarketHome.addEventListener("click", goHome);
marketItems.addEventListener("click", (event) => {
  const editTarget = event.target.closest("[data-market-edit-item]");
  if (!editTarget || !MARKET_EDIT.enabled) return;
  event.preventDefault();
  event.stopPropagation();
  openMarketCategoryItemEditor(editTarget.dataset.marketEditItem);
});
window.addEventListener("beforeunload", (event) => {
  if (!DISPLAY_EDIT.dirty && !DETAIL_EDIT.dirty) return;
  event.preventDefault();
  event.returnValue = "";
});

updateClock();
setInterval(updateClock, 1000);

init();
