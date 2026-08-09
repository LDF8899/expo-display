  (function () {
    function esc(s) {
      return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
        return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
      });
    }
    var DATA = window.AGRI_DATA || { groups: [] };
    var level2 = document.getElementById("level2");
    var itemGrid = document.getElementById("itemGrid");
    var level2Title = document.getElementById("level2Title");
    var level2Tagline = document.getElementById("level2Tagline");
    var level2Count = document.getElementById("level2Count");
    var modal = document.getElementById("itemModal");
    var modalBody = document.getElementById("modalBody");
    var currentItems = [];

    function flatItems(group) {
      var out = [];
      (group.sections || []).forEach(function (s) {
        (s.items || []).forEach(function (it) {
          out.push({ sec: s.title, item: it });
        });
      });
      return out;
    }

    function openGroup(index) {
      var group = DATA.groups[index];
      if (!group) return;
      currentItems = flatItems(group);
      level2Title.textContent = group.title;
      level2Tagline.textContent = "现代农业 · 全部事件与新闻";
      level2Count.textContent = currentItems.length + " 条内容";
      itemGrid.innerHTML = currentItems.map(function (x, i) {
        var cover = x.item.imgs && x.item.imgs.length
          ? '<div class="item-photo" style="background-image:url(\'' + esc(x.item.imgs[0]) + '\')"></div>'
          : '<div class="item-photo empty"><span>' + esc(x.sec) + '</span></div>';
        return '<article class="item-card" data-i="' + i + '" tabindex="0" role="button" aria-label="查看' + esc(x.item.title) + '详情">' +
          cover +
          '<div class="item-body">' +
          '<h4>' + esc(x.item.title) + '</h4>' +
          '<div class="item-meta"><span class="item-sec">' + esc(x.sec) + '</span>' +
          '<em>查看详情 →</em></div>' +
          '</div></article>';
      }).join("");
      document.querySelector(".page > .header").style.display = "none";
      document.querySelector(".page > .content").style.display = "none";
      document.querySelector(".page > .side-actions").style.display = "none";
      document.querySelector(".page > .pager").style.display = "none";
      level2.classList.add("active");
      history.replaceState(null, "", location.pathname + "#g=" + index);
    }

    function closeGroup() {
      if (location.hash) history.replaceState(null, "", location.pathname);
      level2.classList.remove("active");
      document.querySelector(".page > .header").style.display = "";
      document.querySelector(".page > .content").style.display = "";
      document.querySelector(".page > .side-actions").style.display = "";
      document.querySelector(".page > .pager").style.display = "";
    }

    function openDetail(index) {
      var x = currentItems[index];
      if (!x) return;
      var imgs = (x.item.imgs || []).map(function (src) {
        return '<img src="' + esc(src) + '" alt="" loading="lazy" onerror="this.style.display=\'none\'">';
      }).join("");
      var paras = (x.item.body || []).map(function (t) { return '<p>' + esc(t) + '</p>'; }).join("");
      modalBody.innerHTML =
        '<span class="modal-sec">' + esc(x.sec) + ' · 编号 ' + String(index + 1).padStart(3, "0") + '</span>' +
        '<h3 class="modal-title">' + esc(x.item.title) + '</h3>' +
        (x.item.summary ? '<p class="modal-summary">' + esc(x.item.summary) + '</p>' : '') +
        (imgs ? '<div class="modal-imgs">' + imgs + '</div>' : '') +
        (paras ? '<div class="modal-body">' + paras + '</div>' : '');
      modal.classList.add("active");
    }

    function closeDetail() { modal.classList.remove("active"); }

    var initialHash = (location.hash || "").match(/^#g=(\d+)$/);
    if (initialHash) openGroup(Number(initialHash[1]));

    document.querySelectorAll(".panel[data-group]").forEach(function (p) {
      p.addEventListener("click", function () { openGroup(Number(p.dataset.group)); });
      p.addEventListener("keydown", function (e) {
        if (e.key === "Enter" || e.key === " ") { e.preventDefault(); openGroup(Number(p.dataset.group)); }
      });
    });
    itemGrid.addEventListener("click", function (e) {
      var card = e.target.closest(".item-card[data-i]");
      if (card) openDetail(Number(card.dataset.i));
    });
    itemGrid.addEventListener("keydown", function (e) {
      if ((e.key === "Enter" || e.key === " ") && e.target.classList.contains("item-card")) {
        e.preventDefault(); openDetail(Number(e.target.dataset.i));
      }
    });
    document.getElementById("level2Back").addEventListener("click", closeGroup);
    document.getElementById("level2FootBack").addEventListener("click", closeGroup);
    document.getElementById("modalClose").addEventListener("click", closeDetail);
    modal.addEventListener("click", function (e) { if (e.target === modal) closeDetail(); });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") {
        if (modal.classList.contains("active")) closeDetail();
        else if (level2.classList.contains("active")) closeGroup();
      }
    });
  })();
