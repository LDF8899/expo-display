# 展会扫码展示系统

这是展会现场使用的扫码展示系统。扫码器由 C# Agent 调用硬件 DLL，Python 后端接收扫码结果并通过 SSE 推送给大屏展示页。

## 当前链路

```text
扫码器硬件
-> scanner-agent\vbar.dll
-> scanner-agent\Txq_csharp_sdk.exe --agent
-> POST http://127.0.0.1:8000/api/scan
-> Python server.py
-> GET /api/display/events
-> /display 大屏展示页更新
```

Python 不直接调用扫码器硬件，只负责启动和看护 C# Agent、接收扫码结果、维护展示内容。

## 正式启动

现场直接双击：

```text
启动展会系统.bat
```

启动后保持命令行窗口打开。该脚本会执行 `start_expo.py`，自动完成：

```text
1. 启动 C# 扫码 Agent
2. 启动 Python 展示后端
3. 自动打开大屏展示页
4. 定时检查 C# Agent，关闭后自动重新拉起
```

页面地址：

```text
大屏展示页：http://127.0.0.1:8000/display
后台管理页：http://127.0.0.1:8000/admin
```

不要在正式现场只运行：

```powershell
python .\server.py
```

这个命令只启动 Python 后端，不会启动扫码 Agent。

## 打包部署

推荐双击：

```text
打包展会系统.bat
```

它会在上一级目录生成：

```text
expo-display-deploy.zip
```

部署时也可以直接复制整个 `expo-display` 文件夹。现场运行至少需要保留：

```text
启动展会系统.bat
start_expo.py
server.py
expo.db
static
uploads
scanner-agent
```

`scanner-agent` 目录内必须包含：

```text
scanner-agent\Txq_csharp_sdk.exe
scanner-agent\Txq_csharp_sdk.exe.config
scanner-agent\vbar.dll
```

`Txq_csharp_sdk.exe` 和 `vbar.dll` 必须在同一个目录，且当前 DLL 对应 x64 版本。

启动项目前，如果系统里存在非当前项目目录下的同名 `Txq_csharp_sdk.exe`，启动器会先结束这些进程，只保留 `scanner-agent` 里的 Agent。

## 后台管理

后台地址：

```text
http://127.0.0.1:8000/admin
```

后台需要登录：

```text
账号：admin
密码：123456
```

当前支持：

- 新建展会项目
- 每个项目维护一套独立展项编号
- 编辑待机页和欢迎页文案
- 编辑项目默认图片和主题色
- 编辑编号展示页标题、副标题、正文和图片
- 部署项目，快速切换大屏和扫码使用的整套内容
- 模拟扫码

部署项目后，下一次扫码会使用该项目下的编号和展示内容。

前端设计说明：

```text
前端设计说明.md
```

## 数据库

项目使用 SQLite，数据库文件是：

```text
expo.db
```

当前业务表：

```text
admin_users      管理员账号和密码哈希
admin_sessions   管理员登录会话
projects         展会项目、待机页和欢迎页配置、当前部署状态
pages            展项展示内容
scans            扫码记录
```

## 接口测试

不用硬件时，可以直接模拟扫码：

```powershell
Invoke-RestMethod -Method Post `
  -Uri 'http://127.0.0.1:8000/api/scan' `
  -ContentType 'application/json' `
  -Body '{"url":"https://achievementexpo.siat.ac.cn/view/#/activePage/10100043"}'
```

健康检查：

```text
GET http://127.0.0.1:8000/api/health
```

其中 `clients` 大于 `0` 表示已有大屏展示页连接事件流。

## 调试环境变量

只启动 Python，不启动 Agent：

```powershell
$env:START_SCANNER_AGENT='0'
python .\start_expo.py
```

不自动打开浏览器：

```powershell
$env:OPEN_BROWSER='0'
python .\start_expo.py
```

启动时同时打开后台：

```powershell
$env:OPEN_ADMIN='1'
python .\start_expo.py
```

## 运行要求

```text
Windows
Python 3
.NET Framework 4.8
扫码器驱动/USB 连接正常
```

如果真实扫码没反应，先检查任务管理器里是否同时存在：

```text
python.exe
Txq_csharp_sdk.exe
```
