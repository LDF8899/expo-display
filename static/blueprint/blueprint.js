/* ============================================================
   毕节职业技术学院系部数字展厅 · 蓝图展陈
   数据驱动 SPA: /departments 一级页, /departments/<id> 与 /topics/<id> 二级页
   ============================================================ */
(function () {
  "use strict";

  var DATA = { departments: {}, topics: {} };
  var ORDER = {
    departments: ["mining-construction", "finance", "information", "medical-nursing", "tourism"],
    topics: ["smart-energy", "smart-manufacturing", "finance-commerce", "digital-tourism"]
  };
  var DEPT_SUMMARY = {
    "mining-construction": "智慧矿山、智能制造与现代建造",
    "finance": "数字商贸、智慧物流与财务实践",
    "information": "人工智能、网络安全与数字技术",
    "medical-nursing": "临床护理、康养服务与急救教育",
    "tourism": "数字文旅、酒店运营与烹饪技艺"
  };
  var TOPIC_SUMMARY = {
    "smart-energy": "绿色能源、智能开采与化工安全",
    "smart-manufacturing": "智能装备、新能源汽车与无人机应用",
    "finance-commerce": "数字商贸、电商物流与产教融合",
    "digital-tourism": "数字文旅、粤菜师傅与产教融合"
  };
  var SECTION_EN = {
    "overview": "OVERVIEW", "majors": "MAJORS", "training": "TRAINING",
    "cooperation": "COOPERATION", "achievements": "ACHIEVEMENTS",
    "competitions": "COMPETITIONS", "honors": "HONORS", "masters": "MASTERS",
    "alumni": "ALUMNI", "students": "STUDENTS", "media": "MEDIA",
    "faculty": "FACULTY", "orders": "ORDERS", "industry-school": "INDUSTRY"
  };
  var LONG_TEXT_LIMIT = 260;
  var IDLE_MS = 120000;

  var $ = function (id) { return document.getElementById(id); };
  var stage = $("bpStage"), screenHome = $("screenHome"), screenDetail = $("screenDetail");

  var state = { kind: null, id: null, section: 0, sections: [], lastScanAt: 0, playingVideo: false };
  var idleTimer = null, lbImages = [], lbIndex = 0;

  /* ---------- 工具 ---------- */
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
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
    var idx = list[id].sections.findIndex(function (s) { return s.id === section; });
    return { kind: kind, id: id, section: idx >= 0 ? idx : 0 };
  }
  function urlFor(kind, id, section) {
    var base = "/" + kind + "/" + id;
    if (section != null) {
      var sec = (kind === "departments" ? DATA.departments : DATA.topics)[id].sections[section];
      if (sec) base += "?section=" + encodeURIComponent(sec.id);
    }
    return base;
  }

  /* ---------- 数据加载 ---------- */
  function loadData() {
    var jobs = [];
    ["departments", "topics"].forEach(function (kind) {
      ORDER[kind].forEach(function (id) {
        jobs.push(fetch("/static/blueprint/data/" + kind + "/" + id + ".json")
          .then(function (r) { return r.json(); })
          .then(function (d) { DATA[kind][id] = d; })
          .catch(function () { console.warn("load failed:", id); }));
      });
    });
    return Promise.all(jobs);
  }

  /* ---------- 二维码 ---------- */
  function renderQr(box, text) {
    box.innerHTML = "";
    var img = document.createElement("img");
    img.alt = "二维码";
    img.onerror = function () {
      box.innerHTML = '<div class="qr-placeholder">扫描进入<br>数字展厅</div>';
    };
    img.src = "/api/qr-public?data=" + encodeURIComponent(text) + "&size=240";
    box.appendChild(img);
  }

  /* ---------- 一级页 ---------- */
  function renderHome() {
    var grid = $("deptGrid");
    grid.innerHTML = "";
    ORDER.departments.forEach(function (id, i) {
      var d = DATA.departments[id];
      if (!d) return;
      var card = document.createElement("article");
      card.className = "dept-card";
      card.tabIndex = 0;
      card.setAttribute("role", "button");
      card.setAttribute("aria-label", "进入" + d.name + "二级页面");
      card.innerHTML =
        '<img class="dept-photo" src="' + esc(d.cover) + '" alt="" loading="lazy" ' +
        'onerror="this.style.display=\'none\'">' +
        '<div class="shade"></div>' +
        '<div class="dept-copy"><h3 class="dept-name">' + esc(d.name) + '</h3>' +
        '<p class="dept-desc">' + esc(DEPT_SUMMARY[id] || d.summary) + '</p></div>' +
        '<span class="arrow" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></span>';
      var go = function () { openDetail("departments", id, 0); };
      card.addEventListener("click", go);
      card.addEventListener("keydown", function (e) {
        if (e.key === "Enter" || e.key === " ") { e.preventDefault(); go(); }
      });
      grid.appendChild(card);
    });

    var strip = $("topicStrip");
    strip.innerHTML = "";
    ORDER.topics.forEach(function (id) {
      var t = DATA.topics[id];
      if (!t) return;
      var card = document.createElement("article");
      card.className = "topic-card";
      card.tabIndex = 0;
      card.setAttribute("role", "button");
      card.setAttribute("aria-label", "进入" + t.name + "专题页");
      card.innerHTML =
        '<div><div class="t-name">' + esc(t.name) + '</div>' +
        '<div class="t-sub">' + esc(TOPIC_SUMMARY[id] || t.summary) + '</div></div>' +
        '<span class="t-arrow" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></span>';
      var go = function () { openDetail("topics", id, 0); };
      card.addEventListener("click", go);
      card.addEventListener("keydown", function (e) {
        if (e.key === "Enter" || e.key === " ") { e.preventDefault(); go(); }
      });
      strip.appendChild(card);
    });

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
  function openDetail(kind, id, section) {
    var d = (kind === "departments" ? DATA.departments : DATA.topics)[id];
    if (!d) return;
    state.kind = kind; state.id = id; state.sections = d.sections;
    state.section = Math.max(0, Math.min(section, d.sections.length - 1));

    $("detailMeta").textContent = d.name;
    var nav = $("chapterNav");
    nav.innerHTML = "";
    d.sections.forEach(function (s, i) {
      var btn = document.createElement("button");
      btn.className = "chapter-tab" + (i === state.section ? " active" : "");
      btn.textContent = s.title;
      btn.tabIndex = 0;
      btn.addEventListener("click", function () { goSection(i); });
      nav.appendChild(btn);
    });
    renderQr($("detailQr"), location.origin + urlFor(kind, id, null));

    history.pushState(null, "", urlFor(kind, id, state.section));
    screenHome.hidden = true;
    screenDetail.hidden = false;
    renderChapter(false);
    resetIdle();
  }

  function goSection(i) {
    if (i === state.section) return;
    var backward = i < state.section;
    state.section = i;
    document.querySelectorAll(".chapter-tab").forEach(function (b, k) {
      b.classList.toggle("active", k === i);
    });
    history.pushState(null, "", urlFor(state.kind, state.id, i));
    renderChapter(backward);
    resetIdle();
  }

  function renderChapter(backward) {
    var sec = state.sections[state.section];
    if (!sec) return;
    var page = $("chapterPage");
    // 章节切换统一正向淡入（chapterIn，480ms）：重启动画实现每次切换的过渡
    page.style.animation = "none";
    void page.offsetWidth;
    page.style.animation = "";

    var head = '<div class="chapter-head"><h2>' + esc(sec.title) + '</h2>' +
      '<span class="en">' + esc(SECTION_EN[sec.id] || "SECTION") + '</span></div>';
    page.innerHTML = head + renderBlocks(sec.blocks);

    $("progressLabel").textContent =
      String(state.section + 1).padStart(2, "0") + " / " +
      String(state.sections.length).padStart(2, "0");
    $("prevChapter").disabled = state.section === 0;
    $("nextChapter").disabled = state.section === state.sections.length - 1;

    var stats = getData().stats;
    if (state.section === 0 && stats && stats.length) {
      var grid = document.createElement("div");
      grid.className = "stat-grid";
      grid.style.marginBottom = "24px";
      stats.forEach(function (s) {
        var c = document.createElement("div");
        c.className = "stat-card";
        c.innerHTML = '<div class="value">' + esc(s.value) + '</div>' +
          '<div class="label">' + esc(s.label) + '</div>';
        grid.appendChild(c);
      });
      page.insertBefore(grid, page.firstChild.nextSibling);
    }
  }

  function getData() {
    return (state.kind === "departments" ? DATA.departments : DATA.topics)[state.id] || {};
  }

  /* ---------- 块渲染 ---------- */
  function renderBlocks(blocks) {
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
    $("lbClose").focus();
    resetIdle();
  }
  function closeLightbox() { $("lightbox").hidden = true; }

  /* ---------- 抽屉 ---------- */
  function openDrawer(fullHtml) {
    $("drawerBody").innerHTML = fullHtml;
    $("drawer").hidden = false;
    $("drawerClose").focus();
  }

  /* ---------- 空闲返回 ---------- */
  function resetIdle() {
    clearTimeout(idleTimer);
    if (screenHome.hidden && !state.playingVideo) {
      idleTimer = setTimeout(goHome, IDLE_MS);
    }
  }
  function goHome() {
    if (state.playingVideo) { resetIdle(); return; }
    renderHome();
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
        if (!$("drawer").hidden) { $("drawer").hidden = true; return; }
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
    $("prevChapter").addEventListener("click", function () { goSection(Math.max(state.section - 1, 0)); });
    $("nextChapter").addEventListener("click", function () { goSection(Math.min(state.section + 1, state.sections.length - 1)); });

    $("chapterPage").addEventListener("click", function (e) {
      var more = e.target.closest(".more-btn");
      if (more) { openDrawer(more.dataset.full); return; }
      var frame = e.target.closest(".photo-frame[data-lightbox]");
      if (frame) openLightbox(frame.dataset.lightbox, frame.dataset.caption);
    });
    $("chapterPage").addEventListener("keydown", function (e) {
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
    $("drawerClose").addEventListener("click", function () { $("drawer").hidden = true; });
    $("drawer").addEventListener("click", function (e) { if (e.target === this) this.hidden = true; });

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
    loadData().then(function () {
      bindDelegates();
      bindKeys();
      connectSse();
      var route = parsePath();
      if (route.kind === "home") {
        renderHome();
        renderQr($("homeQr"), location.origin + "/departments");
      } else {
        renderHome(); // 先确保数据就绪
        openDetail(route.kind, route.id, route.section);
      }
      window.addEventListener("popstate", function () {
        var r = parsePath();
        if (r.kind === "home") goHome();
        else if (r.id && r.id !== state.id) openDetail(r.kind, r.id, r.section);
        else if (r.id) goSection(r.section);
      });
    });
  }
  boot();
})();
