(function () {
  "use strict";

  var statusNode = document.getElementById("modelStatus");
  var statusChip = document.getElementById("modelStatusChip");
  var returnButton = document.getElementById("returnPortal");
  var restartButton = document.getElementById("restartModel");
  var modelStream = document.getElementById("modelStream");
  var modelWindow = document.querySelector(".model-window");
  var stopping = false;
  var preview = new URLSearchParams(window.location.search).has("preview");
  var streamStarted = false;
  var dragging = false;
  var lastMoveAt = 0;
  var dragPath = [];

  function setStatus(text, isError) {
    statusNode.textContent = text;
    statusNode.classList.toggle("is-error", !!isError);
    statusChip.textContent = isError ? "异常" : text.indexOf("已接入") >= 0 ? "串流中" : "启动中";
    statusChip.classList.toggle("is-ready", !isError && text.indexOf("已接入") >= 0);
    statusChip.classList.toggle("is-error", !!isError);
  }

  function requestJson(url) {
    return fetch(url, { cache: "no-store" }).then(function (response) {
      return response.json().catch(function () { return {}; }).then(function (payload) {
        if (!response.ok || !payload.ok) {
          throw new Error(payload.error || "请求失败");
        }
        return payload;
      });
    });
  }

  function startModel() {
    if (preview) {
      setStatus("预览模式：不会启动桌面模型窗口", false);
      statusChip.textContent = "预览";
      statusChip.classList.remove("is-ready", "is-error");
      return;
    }
    restartButton.disabled = true;
    setStatus("正在启动模型窗口...", false);
    requestJson("/api/homestay-model/start")
      .then(function (payload) {
        var pid = payload.pid || (payload.pids && payload.pids[0]) || "";
        setStatus(pid ? "模型窗口已启动，正在接入画面，PID " + pid : "模型窗口已启动，正在接入画面", false);
        startStream();
      })
      .catch(function (error) {
        setStatus(error.message || "模型启动失败", true);
      })
      .finally(function () {
        restartButton.disabled = false;
      });
  }

  function startStream() {
    if (streamStarted) return;
    streamStarted = true;
    modelStream.hidden = false;
    modelStream.src = "/api/homestay-model/stream?fps=14&quality=62&width=1280&ts=" + Date.now();
  }

  function stopModelThenReturn() {
    if (stopping) return;
    stopping = true;
    returnButton.disabled = true;
    restartButton.disabled = true;
    setStatus("正在关闭模型窗口...", false);
    requestJson("/api/homestay-model/stop")
      .catch(function () { return null; })
      .finally(function () {
        window.location.assign("/departments/tourism");
      });
  }

  function streamPoint(event) {
    var rect = modelStream.getBoundingClientRect();
    var naturalWidth = modelStream.naturalWidth || rect.width;
    var naturalHeight = modelStream.naturalHeight || rect.height;
    if (!rect.width || !rect.height || !naturalWidth || !naturalHeight) return null;

    var scale = Math.min(rect.width / naturalWidth, rect.height / naturalHeight);
    var drawWidth = naturalWidth * scale;
    var drawHeight = naturalHeight * scale;
    var offsetX = (rect.width - drawWidth) / 2;
    var offsetY = (rect.height - drawHeight) / 2;
    var x = (event.clientX - rect.left - offsetX) / drawWidth;
    var y = (event.clientY - rect.top - offsetY) / drawHeight;
    return {
      x: Math.min(1, Math.max(0, x)),
      y: Math.min(1, Math.max(0, y))
    };
  }

  function sendInput(type, point, extra) {
    if (preview || !point) return;
    extra = extra || {};
    var url = "/api/homestay-model/input?type=" + encodeURIComponent(type) +
      "&x=" + encodeURIComponent(point.x.toFixed(5)) +
      "&y=" + encodeURIComponent(point.y.toFixed(5));
    if (extra.dy != null) url += "&dy=" + encodeURIComponent(String(extra.dy));
    if (extra.key) url += "&key=" + encodeURIComponent(extra.key);
    if (extra.mode) url += "&mode=" + encodeURIComponent(extra.mode);
    fetch(url, { cache: "no-store" }).catch(function () {});
  }

  function pushDragPoint(point) {
    if (!point) return;
    var previous = dragPath.length ? dragPath[dragPath.length - 1] : null;
    if (previous && Math.abs(previous.x - point.x) + Math.abs(previous.y - point.y) < 0.008) return;
    dragPath.push(point);
    if (dragPath.length > 80) dragPath.shift();
  }

  function replayDragPath() {
    if (preview || !dragPath.length) return;
    var first = dragPath[0];
    var last = dragPath[dragPath.length - 1];
    var moved = Math.abs(first.x - last.x) + Math.abs(first.y - last.y) > 0.018;
    if (!moved) {
      sendInput("click", last, { mode: "foreground" });
      return;
    }
    var path = dragPath.map(function (point) {
      return point.x.toFixed(5) + "," + point.y.toFixed(5);
    }).join(";");
    fetch("/api/homestay-model/drag?path=" + encodeURIComponent(path), { cache: "no-store" }).catch(function () {});
  }

  returnButton.addEventListener("click", function (event) {
    event.preventDefault();
    stopModelThenReturn();
  });
  restartButton.addEventListener("click", startModel);

  modelStream.addEventListener("load", function () {
    modelWindow.classList.add("is-streaming");
    setStatus("模型画面已接入，可拖拽、滚轮和键盘操作", false);
  });
  modelStream.addEventListener("error", function () {
    streamStarted = false;
    modelWindow.classList.remove("is-streaming");
    setStatus("暂未捕获到模型画面，请确认模型窗口没有最小化", true);
  });

  modelStream.addEventListener("pointerdown", function (event) {
    if (preview) return;
    event.preventDefault();
    modelStream.focus({ preventScroll: true });
    dragging = true;
    dragPath = [];
    modelWindow.classList.add("is-dragging");
    modelStream.setPointerCapture(event.pointerId);
    pushDragPoint(streamPoint(event));
  });
  modelStream.addEventListener("pointermove", function (event) {
    if (!dragging) return;
    event.preventDefault();
    var now = performance.now();
    if (now - lastMoveAt < 28) return;
    lastMoveAt = now;
    pushDragPoint(streamPoint(event));
  });
  function finishPointer(event) {
    if (!dragging) return;
    event.preventDefault();
    dragging = false;
    modelWindow.classList.remove("is-dragging");
    pushDragPoint(streamPoint(event));
    replayDragPath();
  }
  modelStream.addEventListener("pointerup", finishPointer);
  modelStream.addEventListener("pointercancel", finishPointer);
  modelStream.addEventListener("lostpointercapture", function () {
    dragging = false;
    modelWindow.classList.remove("is-dragging");
  });
  modelStream.addEventListener("wheel", function (event) {
    event.preventDefault();
    sendInput("wheel", streamPoint(event), { dy: event.deltaY, mode: "foreground" });
  }, { passive: false });
  modelStream.addEventListener("contextmenu", function (event) {
    event.preventDefault();
  });

  window.addEventListener("keydown", function (event) {
    if (preview || event.target.closest("button,a,input,textarea,select")) return;
    var supported = ["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown", "w", "a", "s", "d", "W", "A", "S", "D", "Escape", "Enter", " "];
    if (supported.indexOf(event.key) < 0) return;
    event.preventDefault();
    sendInput("keydown", { x: 0.5, y: 0.5 }, { key: event.key });
  });
  window.addEventListener("keyup", function (event) {
    if (preview || event.target.closest("button,a,input,textarea,select")) return;
    sendInput("keyup", { x: 0.5, y: 0.5 }, { key: event.key });
  });

  window.addEventListener("pagehide", function () {
    if (!stopping && !preview) {
      fetch("/api/homestay-model/stop", { cache: "no-store", keepalive: true }).catch(function () {});
    }
  });

  startModel();
})();
