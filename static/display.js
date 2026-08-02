const app = document.getElementById("app");
const idleView = document.getElementById("idleView");
const pageView = document.getElementById("pageView");

const brandLogo = document.getElementById("brandLogo");
const brandFallback = document.getElementById("brandFallback");
const brandTitle = document.getElementById("brandTitle");
const brandKicker = document.getElementById("brandKicker");
const projectName = document.getElementById("projectName");
const schoolMeta = document.getElementById("schoolMeta");
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
const carouselStage = document.getElementById("carouselStage");
const carouselSummary = document.querySelector(".carousel-summary");
const carouselSummaryLabel = document.getElementById("carouselSummaryLabel");
const carouselSummaryTitle = document.getElementById("carouselSummaryTitle");
const carouselSummaryCopy = document.getElementById("carouselSummaryCopy");
const carouselSummaryTags = document.getElementById("carouselSummaryTags");
const carouselScanSlot = document.getElementById("carouselScanSlot");
const carouselPagination = document.getElementById("carouselPagination");
const progressBar = document.getElementById("progressBar");
const prevSlide = document.getElementById("prevSlide");
const nextSlide = document.getElementById("nextSlide");
const connectionState = document.getElementById("connectionState");
const projectState = document.getElementById("projectState");
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

const defaultDisplayConfig = {
  logoImageUrl: "",
  schoolName: "毕节职业技术学院",
  schoolMeta: "欢迎来到校园 · 同心特色校园文化",
  badgeText: "欢迎到校",
  summaryLabel: "WELCOME OVERVIEW",
  summaryTitle: "从学校形象到展项内容，形成完整参观动线。",
  summaryCopy: "这版首页减少普通网页式卡片，改为发布会级舞台视觉：大图沉浸、少量状态信息、清晰扫码引导，更适合远距离观看。",
  summaryTags: ["远距可读", "实时扫码", "项目部署"],
  scanTitle: "扫描展项二维码",
  scanCopy: "大屏将自动进入对应编号内容页，保留当前项目与扫码事件的实时联动。",
  scanImageUrl: "",
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

function textToRichHtml(value) {
  return String(value || "")
    .split(/\n{2,}/)
    .map((item) => item.trim())
    .filter(Boolean)
    .map((item) => `<p>${escapeHtml(item).replaceAll("\n", "<br>")}</p>`)
    .join("");
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
    "SPAN",
    "STRONG",
    "U",
    "UL",
  ]);
  const template = document.createElement("template");
  template.innerHTML = String(html || "");
  Array.from(template.content.querySelectorAll("script, style, iframe, object, embed")).forEach((node) => node.remove());
  Array.from(template.content.querySelectorAll("*")).forEach((node) => {
    if (!allowedTags.has(node.tagName)) {
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
        if (name === "src" && !/^(https?:|\/|data:image\/)/i.test(value)) {
          node.removeAttribute(attribute.name);
        }
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

function renderCarousel(slides) {
  carouselSlides = slides.length ? slides : defaultDisplayConfig.slides;
  carouselIndex = 0;
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
    caption.textContent = slide.meta || `WELCOME ${String(index + 1).padStart(2, "0")}`;

    const title = document.createElement("h3");
    title.textContent = slide.title || "";

    const body = document.createElement("p");
    body.textContent = slide.body || slide.label || "";

    article.append(caption, title, body);
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

  showSlide(0);
  restartCarousel();
}

function applyProject(project) {
  activeProject = project || {};
  const config = normalizeDisplayConfig(activeProject.displayConfig);
  const accent = activeProject.accent || "#f59a13";
  const image = activeProject.defaultImageUrl || "/static/expo-stage.png";
  const name = activeProject.name || "学校宣传大屏";
  const schoolDisplayName = String(config.schoolName ?? name).trim();
  const schoolMetaText = String(config.schoolMeta || "").trim();
  const logoUrl = String(config.logoImageUrl || "").trim();

  document.documentElement.style.setProperty("--accent", accent);
  document.documentElement.style.setProperty("--accent-2", config.accent2 || "#47b7ff");
  document.documentElement.style.setProperty("--brand-blue", config.brandColor || "#28539c");
  document.documentElement.style.setProperty("--brand-blue-deep", config.brandDeepColor || "#20468b");
  document.documentElement.style.setProperty("--project-image", cssUrl(image));

  setText(brandKicker, config.badgeText);
  brandKicker.hidden = !config.badgeText;
  const shouldShowName = !!schoolDisplayName;
  setText(projectName, schoolDisplayName || name);
  projectName.hidden = !shouldShowName;
  setText(schoolMeta, schoolMetaText);
  schoolMeta.hidden = !schoolMetaText;
  brandTitle.hidden = !shouldShowName && !schoolMetaText;

  if (logoUrl) {
    brandLogo.src = logoUrl;
    brandLogo.hidden = false;
    brandFallback.hidden = true;
    brandLogo.alt = `${schoolDisplayName || name}标识`;
  } else {
    brandLogo.removeAttribute("src");
    brandLogo.hidden = true;
    brandFallback.hidden = false;
    setText(brandFallback, (schoolDisplayName || name).slice(0, 1) || "校");
  }

  const tags = normalizeTags(config.summaryTags);

  if (heroLabel) heroLabel.hidden = true;
  if (heroTags) heroTags.hidden = true;
  setText(heroTitle, activeProject.idleTitle);
  heroTitle.hidden = !activeProject.idleTitle;
  setText(heroSubtitle, activeProject.idleCopy);
  heroSubtitle.hidden = !activeProject.idleCopy;
  if (heroCopy) heroCopy.hidden = !activeProject.idleTitle && !activeProject.idleCopy;

  setText(carouselSummaryLabel, config.summaryLabel);
  if (carouselSummaryLabel) carouselSummaryLabel.hidden = !config.summaryLabel;
  setText(carouselSummaryTitle, config.summaryTitle || config.summaryCopy);
  if (carouselSummaryTitle) carouselSummaryTitle.hidden = !config.summaryTitle && !config.summaryCopy;
  setText(carouselSummaryCopy, config.summaryTitle ? config.summaryCopy : "");
  if (carouselSummaryCopy) carouselSummaryCopy.hidden = !config.summaryTitle || !config.summaryCopy;
  if (carouselSummaryTags) {
    carouselSummaryTags.innerHTML = "";
    tags.forEach((tag) => {
      const pill = document.createElement("span");
      pill.className = "tag";
      pill.textContent = tag;
      carouselSummaryTags.appendChild(pill);
    });
    carouselSummaryTags.hidden = !tags.length;
  }
  if (carouselSummary) {
    carouselSummary.hidden = !config.summaryLabel && !config.summaryTitle && !config.summaryCopy && !tags.length;
  }
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
  pageView.hidden = view !== "page";

  const active = view === "idle" ? idleView : pageView;
  active.classList.remove("fade-in");
  void active.offsetWidth;
  active.classList.add("fade-in");
}

function goHome() {
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
  applyProject(project);

  const accent = page.accent || project.accent || "#f59a13";
  document.documentElement.style.setProperty("--accent", accent);

  const code = page.code || scan.code || "—";
  const category = page.category || "校园成果";
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
  setText(footerStatus, `正在展示编号 ${code}`);

  show("page");
  startDetailAutoScroll();
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

async function init() {
  if (carouselScanSlot && scanCard && scanCard.parentElement !== carouselScanSlot) {
    carouselScanSlot.appendChild(scanCard);
  }
  bindCarouselControls();
  bindKeyboardScannerFallback();
  try {
    await loadInitialProject();
  } catch {
    applyProject(null);
  }
  show("idle");
  if (previewMode) {
    if (connectionState) connectionState.textContent = "预览模式";
  } else {
    connect();
    setInterval(pollLatestScan, 1200);
  }
  loadInitialCode();
}

returnHome.addEventListener("click", goHome);

init();
