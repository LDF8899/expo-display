const form = document.getElementById("loginForm");
const username = document.getElementById("username");
const password = document.getElementById("password");
const statusText = document.getElementById("status");
const submitButton = form.querySelector("button[type='submit']");
const params = new URLSearchParams(window.location.search);
const nextUrl = params.get("next") || "";

username.value = "admin";

function safeRedirectUrl(value) {
  if (!value || !value.startsWith("/") || value.startsWith("//")) return "";
  return value;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  statusText.textContent = "";
  statusText.removeAttribute("data-state");
  submitButton.disabled = true;
  submitButton.textContent = "登录中...";

  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 10000);
    const res = await fetch("/api/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      signal: controller.signal,
      body: JSON.stringify({
        username: username.value.trim(),
        password: password.value,
      }),
    });
    clearTimeout(timeout);

    const data = await res.json();
    if (!data.ok) {
      statusText.textContent = data.error || "登录失败";
      return;
    }

    statusText.dataset.state = "success";
    statusText.textContent = "登录成功，正在进入工作台...";
    window.location.href = safeRedirectUrl(nextUrl) || data.redirectUrl || "/admin";
  } catch (err) {
    statusText.textContent = err.name === "AbortError"
      ? "登录请求超时，请确认本地服务正常运行后重试"
      : "网络连接异常，请确认服务已启动";
  } finally {
    submitButton.disabled = false;
    submitButton.textContent = "进入后台";
  }
});
