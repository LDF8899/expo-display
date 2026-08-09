(function () {
  "use strict";

  var ARROW_LEFT = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 18l-6-6 6-6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>';
  var ARROW_RIGHT = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 18l6-6-6-6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>';
  var SEARCH_ICON = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7" fill="none" stroke="currentColor" stroke-width="2"/><path d="M16.2 16.2L21 21" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>';
  var PAGE_SIZE = 6;

  function esc(value) {
    return String(value == null ? "" : value).replace(/[&<>"']/g, function (char) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[char];
    });
  }

  function cleanText(value) {
    return String(value || "").replace(/\s+/g, " ").trim();
  }

  function extractUrl(value) {
    var match = String(value || "").match(/url\(["']?(.+?)["']?\)/i);
    return match ? match[1] : "";
  }

  function cssImage(url) {
    return url ? "url('" + String(url).replace(/'/g, "\\'") + "')" : "none";
  }

  function backgroundUrl(node) {
    if (!node) return "";
    return extractUrl(window.getComputedStyle(node).backgroundImage);
  }

  function firstImage(node) {
    if (!node) return "";
    var image = node.querySelector("img");
    if (image && image.currentSrc) return image.currentSrc;
    if (image && image.src) return image.src;
    var candidates = [node].concat(Array.prototype.slice.call(node.querySelectorAll(".photo, .video-box, [role='img']")));
    for (var i = 0; i < candidates.length; i += 1) {
      var url = backgroundUrl(candidates[i]);
      if (url) return url;
    }
    return "";
  }

  function pageIdentity(page) {
    var topicNode = page.querySelector(".topic");
    var taglineNode = page.querySelector(".tagline");
    var pageImage = backgroundUrl(document.body) || backgroundUrl(page) || firstImage(page);
    return {
      school: "毕节职业技术学院",
      topic: cleanText(topicNode ? topicNode.textContent : document.title.replace("毕节职业技术学院", "")) || "系部专题",
      tagline: cleanText(taglineNode ? taglineNode.textContent : "内容展示 · 实训实践 · 产教融合 · 创新成果"),
      pageImage: pageImage,
      homeHref: (page.querySelector(".pager a.refresh") || {}).href || "/departments"
    };
  }

  function normalizeRichGroups(rawGroups, pageImage) {
    return (rawGroups || []).map(function (group, groupIndex) {
      var sections = (group.sections || []).map(function (section, sectionIndex) {
        var sectionImage = section.cover || pageImage;
        var items = (section.items || []).map(function (item, itemIndex) {
          var images = (item.imgs || item.images || []).filter(Boolean);
          return {
            id: item.id || [groupIndex, sectionIndex, itemIndex].join("-"),
            title: cleanText(item.title) || "内容详情",
            summary: cleanText(item.summary || (item.body || [])[0]),
            body: (item.body || []).map(cleanText).filter(Boolean),
            images: images,
            image: images[0] || sectionImage,
            sectionTitle: cleanText(section.title) || "专题内容"
          };
        });
        return {
          title: cleanText(section.title) || "专题内容",
          items: items
        };
      });
      return {
        id: group.id || String(groupIndex),
        title: cleanText(group.title) || "专题内容",
        note: cleanText(group.note) || "内容中心",
        sections: sections
      };
    });
  }

  function fallbackItemFromNode(node, titleFallback, sectionTitle, pageImage, index) {
    var titleNode = node.querySelector(".card-title, h3, h4, strong");
    var roleImage = node.querySelector("[role='img']");
    var title = cleanText(titleNode ? titleNode.textContent : "") || cleanText(roleImage ? roleImage.getAttribute("aria-label") : "") || titleFallback;
    var paragraph = node.querySelector("p");
    var summary = cleanText(paragraph ? paragraph.textContent : "");
    return {
      id: "fallback-" + index,
      title: title,
      summary: summary,
      body: summary ? [summary] : [],
      images: [],
      image: firstImage(node) || pageImage,
      sectionTitle: sectionTitle
    };
  }

  function groupsFromPage(page, pageImage) {
    var panels = Array.prototype.slice.call(page.querySelectorAll(":scope > .content > .panel"));
    return panels.map(function (panel, groupIndex) {
      var titleNode = panel.querySelector(".panel-title");
      var noteNode = panel.querySelector(".panel-note");
      var title = cleanText(titleNode ? titleNode.textContent : "") || "专题内容";
      var note = cleanText(noteNode ? noteNode.textContent : "") || "内容展示";
      var cardNodes = Array.prototype.slice.call(panel.querySelectorAll(".mini-card, .partner-card, .story-card"));
      var items = cardNodes.map(function (card, itemIndex) {
        return fallbackItemFromNode(card, title + " " + (itemIndex + 1), title, pageImage, groupIndex + "-" + itemIndex);
      });
      Array.prototype.slice.call(panel.querySelectorAll(".result-item")).forEach(function (resultNode, resultIndex) {
        var resultTitle = cleanText(resultNode.textContent);
        if (!resultTitle || items.some(function (item) { return item.title === resultTitle; })) return;
        items.push({
          id: "result-" + groupIndex + "-" + resultIndex,
          title: resultTitle,
          summary: "查看该项成果的专题说明与展示内容。",
          body: ["该成果来自当前专题页面的已整理资料，可在后续内容管理流程中继续补充图文、视频与关联资源。"],
          images: [],
          image: firstImage(panel) || pageImage,
          sectionTitle: title
        });
      });
      if (!items.length) {
        var video = panel.querySelector(".video-box");
        items.push(fallbackItemFromNode(panel, cleanText(video ? video.getAttribute("aria-label") : "") || title, title, pageImage, groupIndex));
      }
      return {
        id: "panel-" + groupIndex,
        title: title,
        note: note,
        sections: [{ title: title, items: items }],
        sourcePanel: panel
      };
    }).filter(function (group) {
      return group.sections[0].items.length;
    });
  }

  function flatItems(group) {
    var result = [];
    (group.sections || []).forEach(function (section) {
      (section.items || []).forEach(function (item) { result.push(item); });
    });
    return result;
  }

  function groupCount(group) {
    return flatItems(group).length;
  }

  function createShell(page, identity) {
    var shell = document.createElement("section");
    shell.className = "department-detail-center";
    shell.hidden = true;
    shell.setAttribute("aria-label", "系部二级内容中心");
    shell.style.setProperty("--detail-page-image", cssImage(identity.pageImage));
    shell.innerHTML = [
      '<div class="detail-workspace">',
        '<header class="detail-topbar">',
          '<button class="detail-back" type="button" data-detail-back>' + ARROW_LEFT + '<span>返回专题首页</span></button>',
          '<div class="detail-school-name"><span class="detail-school-seal">BVC</span><span><strong>' + esc(identity.school) + '</strong><span>' + esc(identity.tagline) + '</span></span></div>',
          '<label class="detail-search">' + SEARCH_ICON + '<input type="search" data-detail-search placeholder="搜索专业、实训基地或成果" aria-label="搜索专题内容"></label>',
          '<div class="detail-resource-list">',
            '<button class="detail-resource" type="button" data-detail-resource="immersive"><span class="detail-resource-icon">VR</span><span><strong>VR 实训场景</strong></span></button>',
            '<button class="detail-resource" type="button" data-detail-resource="library"><span class="detail-resource-icon">库</span><span><strong>数字资源库</strong></span></button>',
          '</div>',
        '</header>',
        '<main class="detail-body">',
          '<div class="detail-heading-row"><div><h2 data-detail-title></h2><p data-detail-subtitle></p></div><span class="detail-total" data-detail-total></span></div>',
          '<section class="detail-overview">',
            '<article class="detail-feature" data-detail-feature></article>',
            '<aside class="detail-insight"><div class="detail-insight-head"><div><h3>内容概览</h3><small>按现有资料自动汇总</small></div><span class="detail-insight-total" data-detail-insight-total></span></div><div class="detail-bars" data-detail-bars></div></aside>',
          '</section>',
          '<div class="detail-controls"><div class="detail-filters" data-detail-filters></div><span class="detail-result-note" data-detail-result-note></span></div>',
          '<section class="detail-grid" data-detail-grid aria-live="polite"></section>',
          '<nav class="detail-pagination" aria-label="内容分页"><button class="detail-page-button" type="button" data-detail-prev aria-label="上一页">' + ARROW_LEFT + '</button><span class="detail-page-status" data-detail-page-status></span><button class="detail-page-button" type="button" data-detail-next aria-label="下一页">' + ARROW_RIGHT + '</button></nav>',
        '</main>',
      '</div>',
      '<div class="detail-toast" role="status" data-detail-toast></div>'
    ].join("");
    page.appendChild(shell);

    var modal = document.createElement("div");
    modal.className = "detail-modal";
    modal.hidden = true;
    modal.innerHTML = '<article class="detail-modal-panel" role="dialog" aria-modal="true" aria-label="内容详情"><button class="detail-modal-close" type="button" aria-label="关闭详情" data-detail-modal-close>×</button><div class="detail-modal-media" data-detail-modal-media></div><div class="detail-modal-copy" data-detail-modal-copy></div></article>';
    page.appendChild(modal);

    var immersive = document.createElement("div");
    immersive.className = "detail-immersive";
    immersive.hidden = true;
    immersive.innerHTML = '<section class="detail-immersive-panel" role="dialog" aria-modal="true" aria-label="VR实训场景"><button class="detail-immersive-close" type="button" aria-label="关闭场景" data-detail-immersive-close>×</button><div class="detail-immersive-scene" data-detail-scene></div><div data-detail-hotspots></div><div class="detail-immersive-copy"><h3>VR 实训场景</h3><p>移动指针环视场景，点击标记查看当前专题中的实训、专业与成果内容。</p></div></section>';
    page.appendChild(immersive);

    return { shell: shell, modal: modal, immersive: immersive };
  }

  function init() {
    var page = document.querySelector(".page");
    if (!page || page.dataset.detailCenterReady === "1") return;
    page.dataset.detailCenterReady = "1";

    var identity = pageIdentity(page);
    var pageGroups = groupsFromPage(page, identity.pageImage);
    var rawData = window.DEPARTMENT_DATA || window.AGRI_DATA;
    var richGroups = rawData && Array.isArray(rawData.groups)
      ? normalizeRichGroups(rawData.groups, identity.pageImage)
      : [];
    var groups = richGroups.length
      ? richGroups.map(function (group, index) {
          if (group.sections.some(function (section) { return section.items.length; })) return group;
          return pageGroups[index] || group;
        })
      : pageGroups;
    if (!groups.length) return;

    // 主页面卡片图片：用各板块数据里的真实图片替换占位背景（自适应展示）
    function applyPagePhotos() {
      var panels = Array.prototype.slice.call(page.querySelectorAll(":scope > .content > .panel"));
      panels.forEach(function (panel, panelIndex) {
        var group = groups[panelIndex];
        if (!group) return;
        var pool = [];
        flatItems(group).forEach(function (item) {
          if (item.image && pool.indexOf(item.image) === -1) pool.push(item.image);
          (item.images || []).forEach(function (img) {
            if (img && pool.indexOf(img) === -1) pool.push(img);
          });
        });
        var photos = panel.querySelectorAll(".photo");
        if (!pool.length) return;
        Array.prototype.forEach.call(photos, function (photo, i) {
          var src = pool[i % pool.length];
          photo.style.backgroundImage = "url('" + src.replace(/'/g, "\\'") + "')";
        });
      });
    }
    applyPagePhotos();

    var ui = createShell(page, identity);
    var shell = ui.shell;
    var state = {
      activeGroup: 0,
      filter: "全部",
      query: "",
      page: 1,
      toastTimer: 0,
      lastFocus: null
    };

    function node(selector, root) {
      return (root || shell).querySelector(selector);
    }

    function currentGroup() {
      return groups[state.activeGroup] || groups[0];
    }

    function sectionCounts(group) {
      return (group.sections || []).map(function (section) {
        return { title: section.title, count: section.items.length };
      }).filter(function (entry) { return entry.count > 0; });
    }

    function filteredItems() {
      var query = state.query.toLowerCase();
      return flatItems(currentGroup()).filter(function (item) {
        var matchesFilter = state.filter === "全部" || item.sectionTitle === state.filter;
        var haystack = [item.title, item.summary].concat(item.body || []).join(" ").toLowerCase();
        return matchesFilter && (!query || haystack.indexOf(query) !== -1);
      });
    }

    function toast(message) {
      var toastNode = node("[data-detail-toast]");
      toastNode.textContent = message;
      toastNode.classList.add("is-visible");
      window.clearTimeout(state.toastTimer);
      state.toastTimer = window.setTimeout(function () { toastNode.classList.remove("is-visible"); }, 2400);
    }

    function renderFeature(items) {
      var feature = items[0] || flatItems(currentGroup())[0];
      var container = node("[data-detail-feature]");
      if (!feature) {
        container.innerHTML = '<div class="detail-empty">当前分类暂无可展示内容</div>';
        return;
      }
      container.innerHTML = '<div class="detail-feature-media" style="--detail-image:' + cssImage(feature.image || identity.pageImage) + '"></div><div class="detail-feature-copy"><span class="detail-kicker">' + esc(feature.sectionTitle) + '</span><h3>' + esc(feature.title) + '</h3><p>' + esc(feature.summary || (feature.body || [])[0] || "查看该条目的完整图文资料与关联内容。") + '</p><button class="detail-open-button" type="button" data-detail-open-feature>阅读全文' + ARROW_RIGHT + '</button></div>';
      node("[data-detail-open-feature]").addEventListener("click", function () { openItem(feature); });
    }

    function renderInsight(group) {
      var counts = sectionCounts(group);
      var max = Math.max.apply(Math, counts.map(function (item) { return item.count; }).concat([1]));
      node("[data-detail-insight-total]").textContent = groupCount(group);
      node("[data-detail-bars]").innerHTML = counts.slice(0, 5).map(function (entry) {
        var width = Math.max(8, Math.round((entry.count / max) * 100));
        return '<div class="detail-bar-row"><span>' + esc(entry.title) + '</span><span class="detail-bar-track"><i style="--detail-bar-width:' + width + '%"></i></span><b>' + entry.count + '</b></div>';
      }).join("");
    }

    function renderFilters(group) {
      var filters = ["全部"].concat(sectionCounts(group).map(function (entry) { return entry.title; }));
      node("[data-detail-filters]").innerHTML = filters.map(function (filter) {
        return '<button class="detail-filter' + (filter === state.filter ? ' is-active' : '') + '" type="button" data-detail-filter="' + esc(filter) + '">' + esc(filter) + '</button>';
      }).join("");
    }

    function renderCards(items) {
      var totalPages = Math.max(1, Math.ceil(items.length / PAGE_SIZE));
      if (state.page > totalPages) state.page = totalPages;
      var start = (state.page - 1) * PAGE_SIZE;
      var pageItems = items.slice(start, start + PAGE_SIZE);
      var grid = node("[data-detail-grid]");
      grid.innerHTML = pageItems.length ? pageItems.map(function (item, index) {
        return '<article class="detail-card" role="button" tabindex="0" data-detail-item="' + (start + index) + '" aria-label="查看' + esc(item.title) + '"><div class="detail-card-media" style="--detail-image:' + cssImage(item.image || identity.pageImage) + '"></div><div class="detail-card-copy"><small>' + esc(item.sectionTitle) + '</small><h4>' + esc(item.title) + '</h4><p>' + esc(item.summary || (item.body || [])[0] || "查看完整内容") + '</p></div></article>';
      }).join("") : '<div class="detail-empty">没有找到匹配内容，请更换关键词或分类。</div>';
      grid._detailItems = items;
      node("[data-detail-result-note]").textContent = "当前显示 " + pageItems.length + " / " + items.length + " 条";
      node("[data-detail-page-status]").textContent = state.page + " / " + totalPages;
      node("[data-detail-prev]").disabled = state.page <= 1;
      node("[data-detail-next]").disabled = state.page >= totalPages;
    }

    function render() {
      var group = currentGroup();
      var items = filteredItems();
      node("[data-detail-title]").textContent = group.title;
      node("[data-detail-subtitle]").textContent = identity.topic + " · " + (group.note || "全部图文与资源");
      node("[data-detail-total]").textContent = groupCount(group) + " 条内容";
      renderFeature(items);
      renderInsight(group);
      renderFilters(group);
      renderCards(items);
    }

    function setGroup(index) {
      if (index < 0 || index >= groups.length) return;
      state.activeGroup = index;
      state.filter = "全部";
      state.query = "";
      state.page = 1;
      node("[data-detail-search]").value = "";
      render();
      node(".detail-body").scrollTop = 0;
    }

    function openGroup(index) {
      state.lastFocus = document.activeElement;
      setGroup(index);
      shell.hidden = false;
      shell.setAttribute("aria-hidden", "false");
      window.requestAnimationFrame(function () { node("[data-detail-back]").focus(); });
    }

    function closeCenter() {
      shell.hidden = true;
      shell.setAttribute("aria-hidden", "true");
      if (state.lastFocus && typeof state.lastFocus.focus === "function") state.lastFocus.focus();
    }

    function openItem(item) {
      if (!item) return;
      var paragraphs = (item.body || []).length ? item.body : [item.summary || "该条目暂无更长正文，可继续通过内容管理流程补充图文资料。"];
      var images = (item.images || []).filter(Boolean);
      node("[data-detail-modal-media]", ui.modal).style.setProperty("--detail-image", cssImage(item.image || identity.pageImage));
      node("[data-detail-modal-copy]", ui.modal).innerHTML = '<small>' + esc(item.sectionTitle) + '</small><h3>' + esc(item.title) + '</h3>' + paragraphs.map(function (paragraph) { return '<p>' + esc(paragraph) + '</p>'; }).join("") + (images.length > 1 ? '<div class="detail-modal-gallery">' + images.slice(1, 5).map(function (src) { return '<img src="' + esc(src) + '" alt="' + esc(item.title) + '">'; }).join("") + '</div>' : '');
      ui.modal.hidden = false;
      node("[data-detail-modal-close]", ui.modal).focus();
    }

    function closeModal() {
      ui.modal.hidden = true;
    }

    function openImmersive() {
      var candidates = flatItems(currentGroup()).filter(function (item) { return item.image; }).slice(0, 3);
      if (!candidates.length) candidates = flatItems(currentGroup()).slice(0, 3);
      node("[data-detail-hotspots]", ui.immersive).innerHTML = candidates.map(function (item, index) {
        return '<button class="detail-hotspot" type="button" data-detail-hotspot="' + index + '" aria-label="' + esc(item.title) + '">' + (index + 1) + '</button>';
      }).join("");
      node("[data-detail-hotspots]", ui.immersive)._detailItems = candidates;
      ui.immersive.hidden = false;
      node("[data-detail-immersive-close]", ui.immersive).focus();
    }

    function closeImmersive() {
      ui.immersive.hidden = true;
    }

    Array.prototype.slice.call(page.querySelectorAll(":scope > .content > .panel")).forEach(function (panel, index) {
      panel.dataset.detailGroup = String(index);
      panel.tabIndex = panel.tabIndex >= 0 ? panel.tabIndex : 0;
      panel.setAttribute("role", panel.getAttribute("role") || "button");
      panel.setAttribute("aria-label", "进入" + (groups[index] ? groups[index].title : "专题内容") + "二级页面");
      panel.addEventListener("click", function (event) {
        if (event.target.closest("button, a, input, video, dialog")) return;
        openGroup(index);
      });
      panel.addEventListener("keydown", function (event) {
        if ((event.key === "Enter" || event.key === " ") && event.target === panel) {
          event.preventDefault();
          openGroup(index);
        }
      });
    });

    shell.addEventListener("click", function (event) {
      var filter = event.target.closest("[data-detail-filter]");
      if (filter) { state.filter = filter.dataset.detailFilter; state.page = 1; render(); return; }
      var card = event.target.closest("[data-detail-item]");
      if (card) { openItem(node("[data-detail-grid]")._detailItems[Number(card.dataset.detailItem)]); return; }
      if (event.target.closest("[data-detail-back]")) { closeCenter(); return; }
      if (event.target.closest("[data-detail-prev]")) { state.page = Math.max(1, state.page - 1); renderCards(filteredItems()); return; }
      if (event.target.closest("[data-detail-next]")) { state.page += 1; renderCards(filteredItems()); return; }
      var resource = event.target.closest("[data-detail-resource]");
      if (resource) {
        if (resource.dataset.detailResource === "immersive") openImmersive();
        else {
          var videoIndex = groups.findIndex(function (group) { return /视频|资源/.test(group.title); });
          if (videoIndex >= 0) { setGroup(videoIndex); toast("已打开视频与数字资源栏目"); }
          else { state.filter = "全部"; state.query = ""; state.page = 1; render(); toast("已汇总当前专题全部数字资源"); }
        }
      }
    });

    shell.addEventListener("keydown", function (event) {
      var card = event.target.closest("[data-detail-item]");
      if (card && (event.key === "Enter" || event.key === " ")) {
        event.preventDefault();
        openItem(node("[data-detail-grid]")._detailItems[Number(card.dataset.detailItem)]);
      }
    });

    node("[data-detail-search]").addEventListener("input", function (event) {
      state.query = cleanText(event.target.value);
      state.page = 1;
      renderFeature(filteredItems());
      renderCards(filteredItems());
    });

    node("[data-detail-modal-close]", ui.modal).addEventListener("click", closeModal);
    ui.modal.addEventListener("click", function (event) { if (event.target === ui.modal) closeModal(); });
    node("[data-detail-immersive-close]", ui.immersive).addEventListener("click", closeImmersive);
    ui.immersive.addEventListener("click", function (event) {
      if (event.target === ui.immersive) { closeImmersive(); return; }
      var hotspot = event.target.closest("[data-detail-hotspot]");
      if (hotspot) {
        var items = node("[data-detail-hotspots]", ui.immersive)._detailItems || [];
        closeImmersive();
        openItem(items[Number(hotspot.dataset.detailHotspot)]);
      }
    });
    node("[data-detail-scene]", ui.immersive).addEventListener("pointermove", function (event) {
      var rect = event.currentTarget.getBoundingClientRect();
      var percent = Math.max(18, Math.min(82, ((event.clientX - rect.left) / rect.width) * 100));
      event.currentTarget.style.setProperty("--scene-x", percent + "%");
    });

    document.addEventListener("keydown", function (event) {
      if (event.key !== "Escape") return;
      if (!ui.modal.hidden) closeModal();
      else if (!ui.immersive.hidden) closeImmersive();
      else if (!shell.hidden) closeCenter();
    });

    render();
  }

  window.DepartmentDetailCenter = { init: init };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init, { once: true });
  else init();
})();
