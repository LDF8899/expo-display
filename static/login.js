const form = document.getElementById("loginForm");
const username = document.getElementById("username");
const password = document.getElementById("password");
const statusText = document.getElementById("status");
const submitButton = form.querySelector("button[type='submit']");

username.value = "admin";

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  statusText.textContent = "";
  statusText.removeAttribute("data-state");
  submitButton.disabled = true;
  submitButton.textContent = "登录中...";

  try {
    const res = await fetch("/api/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username: username.value.trim(),
        password: password.value,
      }),
    });

    const data = await res.json();
    if (!data.ok) {
      statusText.textContent = data.error || "登录失败";
      return;
    }

    statusText.dataset.state = "success";
    statusText.textContent = "登录成功，正在进入工作台...";
    window.location.href = data.redirectUrl || "/admin";
  } catch {
    statusText.textContent = "网络连接异常，请确认服务已启动";
  } finally {
    submitButton.disabled = false;
    submitButton.textContent = "登录";
  }
});
