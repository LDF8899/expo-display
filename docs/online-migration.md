# 线上化改造说明

这个项目原来按展会现场单机运行设计：Python 服务监听本机、SQLite 文件保存数据、上传资源写入本机 `uploads/`。多人在线版本建议改成：

```text
浏览器
  -> HTTPS / Nginx
  -> Python 后端服务
  -> MySQL：用户、项目、页面、审核、扫码、日志
  -> 对象存储：图片、视频、附件
  -> CDN：公开展示资源加速
```

## 已完成的基础改造

- 服务配置改为环境变量，默认仍兼容本地启动。
- Cookie 支持 HTTPS `Secure` 开关。
- CORS 不再默认对所有来源开放，需要显式配置允许的来源。
- 上传接口增加请求体大小、文件大小和 MIME 类型限制。
- 默认禁止 SVG 上传，避免脚本型 SVG 被当作站内资源访问。
- 新增 MySQL 初始化脚本：`database/mysql_schema.sql`。
- 新增数据库适配层：默认使用 SQLite，配置 `DATABASE_BACKEND=mysql` 后使用 PyMySQL 连接 MySQL。
- 新增资源存储适配层：默认写本地 `uploads/`，配置 `ASSET_STORAGE_BACKEND=s3` 后可上传到 S3 兼容对象存储。
- 新增上传资源元数据表 `assets`，记录上传人、文件名、存储 key、URL、MIME 和大小，后台可按账号隔离查看和删除；已被项目、页面或待审核草稿引用的资源会拒绝删除。
- 页面正文保存前增加服务端富文本净化，剥离脚本、事件属性和危险 URL。
- 服务端和 Nginx 模板都加入基础安全响应头和 CSP。
- 新增部署模板：`deploy/nginx/expo-display.conf`、`deploy/systemd/expo-display.service`、`deploy/expo-display.env.example`。
- 线上模式会拒绝使用默认管理员密码 `123456` 启动，除非临时设置 `ALLOW_DEFAULT_ADMIN_PASSWORD=1`。
- 账号创建、CSV 导入、管理员重置密码和用户改密码会统一校验密码强度，不再自动回退到 `123456`。
- 登录和上传接口增加内存限流，降低公网暴力尝试和上传滥用风险。
- 后台 POST/PUT/DELETE 接口增加 CSRF token 校验；登录和硬件扫码接口放行。
- 审核列表会返回当前版、待审核版和字段差异；管理员可通过带登录态的草稿预览查看未发布内容。
- 内容部署前会检查勾选页面是否已审核且启用、是否属于当前项目、是否引用缺失的本地上传资源；欢迎页部署会拒绝待审核的项目配置。
- 后台首页会集中显示 ready 状态、数据库/资源存储健康、运行模式、当前部署项目、待审核数量和资源数量。
- 后台首页会显示上线配置审计结果，标出 PUBLIC_BASE_URL、HTTPS Cookie、MySQL、对象存储、密码策略、限流和反代配置风险。
- 后台首页可导出上线验收报告 JSON，包含 ready、配置审计、部署状态、发布检查、待审核数量和资源统计，不包含密码或密钥。

## 运行环境变量

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `HOST` | `127.0.0.1` | 本地保持默认；线上容器或服务器内可设为 `0.0.0.0` |
| `PORT` | `8000` | 后端监听端口 |
| `DB_PATH` | `expo.db` | 当前 SQLite 路径，正式接 MySQL 后会被替换 |
| `DATABASE_BACKEND` | `sqlite` | 可选 `sqlite` 或 `mysql` |
| `DATABASE_URL` | 空 | MySQL 连接串，例如 `mysql+pymysql://user:pass@host:3306/expo_display` |
| `MYSQL_HOST` | `127.0.0.1` | 未配置 `DATABASE_URL` 时使用 |
| `MYSQL_PORT` | `3306` | 未配置 `DATABASE_URL` 时使用 |
| `MYSQL_USER` | `root` | 未配置 `DATABASE_URL` 时使用 |
| `MYSQL_PASSWORD` | 空 | 未配置 `DATABASE_URL` 时使用 |
| `MYSQL_DATABASE` | `expo_display` | 未配置 `DATABASE_URL` 时使用 |
| `MYSQL_SCHEMA_PATH` | `database/mysql_schema.sql` | MySQL 自动建表脚本路径 |
| `UPLOAD_DIR` | `uploads` | 当前本地上传目录，正式接对象存储后会被替换 |
| `ADMIN_USERNAME` | `admin` | 初始管理员账号 |
| `ADMIN_PASSWORD` | `123456` | 初始管理员密码；线上必须通过环境变量覆盖 |
| `CSRF_SECRET` | 空 | CSRF token 签名密钥；线上建议配置一段随机长字符串 |
| `PASSWORD_MIN_LENGTH` | `10` | 老师/管理员账号新密码最短长度；线上预检要求不低于 `10` |
| `ALLOW_WEAK_USER_PASSWORDS` | `0` | 是否允许弱用户密码；线上预检要求保持关闭 |
| `ADMIN_SESSION_SECONDS` | `43200` | 登录有效期，单位秒 |
| `PUBLIC_BASE_URL` | 空 | 线上公网地址，例如 `https://expo.example.com` |
| `SESSION_COOKIE_SECURE` | 根据 `PUBLIC_BASE_URL` 是否 HTTPS 推断 | HTTPS 上线建议显式设为 `1` |
| `TRUST_PROXY_HEADERS` | `0` | 通过 Nginx 反代上线时设为 `1`，服务才会信任 `X-Forwarded-For` / `X-Real-IP` |
| `ALLOWED_ORIGINS` | 空 | 允许跨域来源，多个用英文逗号分隔；同域部署不需要配置 |
| `MAX_JSON_BYTES` | `8388608` | JSON 请求体上限 |
| `MAX_UPLOAD_BYTES` | `5242880` | 解码后的单张图片大小上限 |
| `ALLOW_SVG_UPLOADS` | `0` | 是否允许 SVG 上传；线上建议保持关闭 |
| `LOGIN_RATE_LIMIT` | `10` | 登录窗口内允许尝试次数，设为 `0` 可关闭 |
| `LOGIN_RATE_WINDOW_SECONDS` | `300` | 登录限流窗口秒数 |
| `UPLOAD_RATE_LIMIT` | `120` | 上传窗口内允许次数，设为 `0` 可关闭 |
| `UPLOAD_RATE_WINDOW_SECONDS` | `3600` | 上传限流窗口秒数 |
| `ASSET_STORAGE_BACKEND` | `local` | 可选 `local` 或 `s3` |
| `ASSET_PUBLIC_BASE_URL` | 空 | local 模式下返回的公开资源前缀；为空则返回 `/uploads/...` |
| `ASSET_KEY_PREFIX` | 空 | 上传到存储里的 key 前缀，例如 `expo-assets` |
| `S3_BUCKET` | 空 | S3/兼容对象存储 bucket |
| `S3_ENDPOINT_URL` | 空 | 兼容对象存储 endpoint，例如 COS/MinIO endpoint |
| `S3_REGION` | `auto` | S3 region |
| `S3_ACCESS_KEY_ID` | 兼容 `AWS_ACCESS_KEY_ID` | 对象存储 access key |
| `S3_SECRET_ACCESS_KEY` | 兼容 `AWS_SECRET_ACCESS_KEY` | 对象存储 secret key |
| `S3_PUBLIC_BASE_URL` | 空 | CDN 或对象存储公开访问前缀 |
| `S3_ACL` | 空 | 可选 ACL，例如 `public-read`；很多云厂商推荐用 bucket policy/CDN 控制公开访问 |

本地启动仍可以：

```powershell
python .\start_expo.py
```

线上后端服务示例：

```powershell
pip install -r .\requirements-online.txt
$env:HOST="0.0.0.0"
$env:PORT="8000"
$env:PUBLIC_BASE_URL="https://expo.example.com"
$env:SESSION_COOKIE_SECURE="1"
$env:TRUST_PROXY_HEADERS="1"
$env:ADMIN_PASSWORD="<use-a-strong-random-password>"
$env:CSRF_SECRET="<use-a-long-random-secret>"
python .\server.py
```

Linux 服务部署可参考：

```bash
sudo useradd --system --create-home --home-dir /opt/expo-display expo
sudo mkdir -p /opt/expo-display /etc/expo-display
sudo cp -r . /opt/expo-display
sudo cp deploy/expo-display.env.example /etc/expo-display/expo-display.env
sudo cp deploy/systemd/expo-display.service /etc/systemd/system/expo-display.service
sudo cp deploy/nginx/expo-display.conf /etc/nginx/conf.d/expo-display.conf
sudo chown -R expo:expo /opt/expo-display
cd /opt/expo-display
python3 -m venv .venv
sudo -u expo .venv/bin/pip install -r requirements-online.txt
sudo systemctl daemon-reload
sudo systemctl enable --now expo-display
sudo nginx -t && sudo systemctl reload nginx
```

上线前需要编辑：

```text
/etc/expo-display/expo-display.env
/etc/nginx/conf.d/expo-display.conf
```

把域名、证书路径、MySQL 账号、对象存储参数和管理员初始密码替换成真实值。

S3 兼容对象存储示例：

```powershell
$env:ASSET_STORAGE_BACKEND="s3"
$env:S3_BUCKET="expo-display-assets"
$env:S3_ENDPOINT_URL="https://s3.example.com"
$env:S3_REGION="auto"
$env:S3_ACCESS_KEY_ID="your-access-key"
$env:S3_SECRET_ACCESS_KEY="your-secret-key"
$env:S3_PUBLIC_BASE_URL="https://cdn.example.com/expo-display-assets"
$env:ASSET_KEY_PREFIX="uploads"
python .\server.py
```

## MySQL 初始化

拿到建库权限后执行：

```sql
SOURCE database/mysql_schema.sql;
```

如果 MySQL 版本低于 8.0，`utf8mb4_0900_ai_ci` 可能不可用，把脚本里的排序规则替换为：

```sql
utf8mb4_unicode_ci
```

应用已经有基础数据库适配层。默认仍使用 SQLite；配置 MySQL 后，启动时会连接 `MYSQL_DATABASE` 指定的库，并执行 `mysql_schema.sql` 里的建表语句。脚本中的 `CREATE DATABASE` 和 `USE` 主要给 DBA 手工初始化使用，应用自动初始化时会跳过这两句。

MySQL 运行示例：

```powershell
$env:DATABASE_BACKEND="mysql"
$env:MYSQL_HOST="127.0.0.1"
$env:MYSQL_PORT="3306"
$env:MYSQL_USER="expo_user"
$env:MYSQL_PASSWORD="<mysql-user-password>"
$env:MYSQL_DATABASE="expo_display"
$env:HOST="0.0.0.0"
$env:PUBLIC_BASE_URL="https://expo.example.com"
$env:SESSION_COOKIE_SECURE="1"
python .\server.py
```

本机已有 Docker MySQL 时，可以单独建库，不要复用其他业务库：

```powershell
$env:MYSQL_HOST="127.0.0.1"
$env:MYSQL_PORT="3307"
$env:MYSQL_USER="expo_user"
$env:MYSQL_PASSWORD="<mysql-user-password>"
$env:MYSQL_DATABASE="expo_display"
python .\server.py
```

迁移现有 `expo.db` 数据到 MySQL：

```powershell
$env:MYSQL_HOST="127.0.0.1"
$env:MYSQL_PORT="3306"
$env:MYSQL_USER="expo_user"
$env:MYSQL_PASSWORD="<mysql-user-password>"
$env:MYSQL_DATABASE="expo_display"
python .\scripts\migrate_sqlite_to_mysql.py --sqlite-db .\expo.db --truncate
```

## 健康检查

进程存活检查：

```text
GET /api/health
```

返回服务时间和当前 SSE 客户端数量，适合用作最轻量的进程探活。

就绪检查：

```text
GET /api/ready
```

返回数据库、资源存储和运行配置状态。数据库或上传存储不可用时会返回 `503`，适合给监控或发布流程判断服务是否可接流量。

## 下一步改造顺序

1. 拿到 MySQL 权限后，用迁移脚本导入现有 `expo.db` 并用 MySQL 模式启动做完整页面回归。
2. 拿到对象存储参数后，用 `ASSET_STORAGE_BACKEND=s3` 做上传回归，确认返回 URL 可被大屏访问。
3. 上线前运行 `python scripts/asset_management_test.py`，确认老师只能管理自己的资源，且使用中的资源不能被删除。
4. 上线前运行 `python scripts/review_diff_test.py`，确认审核对比和草稿预览可用。
5. 上线前运行 `python scripts/deploy_precheck_test.py`，确认发布前检查能拦截无效页面和缺失资源。
6. 上线前运行 `python scripts/operations_dashboard_test.py`，确认后台运维面板能显示 ready、部署和资源状态。
7. 上线前运行 `python scripts/operations_config_audit_test.py`，确认后台能标出关键上线配置风险。
8. 上线前运行 `python scripts/acceptance_report_test.py`，确认验收报告导出可用且不泄露敏感配置。
9. 前面接 Nginx 和 HTTPS，只暴露 `/display`、`/login`、`/admin`、`/api/*`。
4. 增加备份策略：MySQL 每日备份，对象存储生命周期和防误删。
5. 增加线上日志：访问日志、错误日志、管理员操作日志分开保存。
6. 把硬件扫码 Agent 和线上后台拆成独立部署模式，避免公网服务依赖现场 USB 硬件。

## 当前保留的本地模式

扫码硬件 Agent 仍然按本机现场模式工作，`start_expo.py` 和批处理脚本没有改动。后续如果同一个系统既要支持现场大屏，又要支持公网教师上传，建议拆成两个运行模式：

- 线上后台：用户上传、审核、发布。
- 现场大屏：只读取已发布内容，继续连接扫码硬件。
