# ThinkAI 图片素材生成配置说明

这份说明用于在其他电脑上配置同一套图片素材生成能力。配置完成后，可以通过脚本调用 ThinkAI 图片生成接口，用于生成背景图、UI 素材、视觉概念图等。

## 1. 准备 API Key

先拿到你的 ThinkAI API Key，格式通常类似：

```text
sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

不要把真实密钥提交到 Git、文档、聊天记录截图或共享文件里。建议只保存到本机环境变量。

## 2. Windows 配置

打开 PowerShell，执行：

```powershell
[Environment]::SetEnvironmentVariable("THINKAI_API_KEY", "你的API_KEY", "User")
```

关闭并重新打开 PowerShell，然后检查是否配置成功：

```powershell
[bool][Environment]::GetEnvironmentVariable("THINKAI_API_KEY", "User")
```

如果返回 `True`，说明配置成功。

## 3. macOS / Linux 配置

如果使用 zsh：

```bash
echo 'export THINKAI_API_KEY="你的API_KEY"' >> ~/.zshrc
source ~/.zshrc
```

如果使用 bash：

```bash
echo 'export THINKAI_API_KEY="你的API_KEY"' >> ~/.bashrc
source ~/.bashrc
```

检查是否配置成功：

```bash
test -n "$THINKAI_API_KEY" && echo OK
```

## 4. 推荐脚本位置

建议把生成脚本放在用户级工具目录，方便所有项目复用。

Windows 推荐路径：

```text
C:\Users\你的用户名\.codex\tools\generate_thinkai_image.ps1
```

项目内也可以放一份：

```text
tools\generate_thinkai_image.ps1
```

## 5. Windows PowerShell 生成脚本

新建文件 `generate_thinkai_image.ps1`，内容如下：

```powershell
param(
  [Parameter(Mandatory = $true)]
  [string]$Prompt,

  [string]$Size = "3840x2160",
  [ValidateSet("low", "medium", "high")]
  [string]$Quality = "medium",
  [int]$N = 1,
  [string]$Model = "gpt-image-2-4k",
  [string]$OutputDir = "outputs",
  [string]$OutputPrefix = "thinkai-image"
)

$ErrorActionPreference = "Stop"

$apiKey = $env:THINKAI_API_KEY
if ([string]::IsNullOrWhiteSpace($apiKey)) {
  $apiKey = [Environment]::GetEnvironmentVariable("THINKAI_API_KEY", "User")
}

if ([string]::IsNullOrWhiteSpace($apiKey)) {
  throw "THINKAI_API_KEY is not set. Set it as a user environment variable before running this script."
}

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

$body = @{
  model = $Model
  prompt = $Prompt
  size = $Size
  quality = $Quality
  n = $N
} | ConvertTo-Json -Depth 8

$headers = @{
  Authorization = "Bearer $apiKey"
  "Content-Type" = "application/json"
}

$response = Invoke-RestMethod `
  -Method Post `
  -Uri "https://www.thinkai.tv/v1/images/generations" `
  -Headers $headers `
  -Body $body

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$saved = @()
$index = 0

foreach ($item in $response.data) {
  $index += 1
  $baseName = "{0}-{1}-{2}" -f $OutputPrefix, $timestamp, $index

  if ($item.b64_json) {
    $outputPath = Join-Path $OutputDir "$baseName.png"
    [IO.File]::WriteAllBytes($outputPath, [Convert]::FromBase64String($item.b64_json))
    $saved += (Resolve-Path $outputPath).Path
    continue
  }

  if ($item.url) {
    $outputPath = Join-Path $OutputDir "$baseName.png"
    Invoke-WebRequest -Uri $item.url -OutFile $outputPath
    $saved += (Resolve-Path $outputPath).Path
    continue
  }

  $jsonPath = Join-Path $OutputDir "$baseName.response.json"
  $item | ConvertTo-Json -Depth 10 | Set-Content -Path $jsonPath -Encoding UTF8
  $saved += (Resolve-Path $jsonPath).Path
}

$metaPath = Join-Path $OutputDir "$OutputPrefix-$timestamp.metadata.json"
$metadata = @{
  model = $Model
  size = $Size
  quality = $Quality
  n = $N
  saved = $saved
  createdAt = (Get-Date).ToString("s")
}
$metadata | ConvertTo-Json -Depth 8 | Set-Content -Path $metaPath -Encoding UTF8

$saved
```

## 6. 使用示例

在项目根目录执行：

```powershell
.\tools\generate_thinkai_image.ps1 `
  -Prompt "生成一张3840x2160横屏4K现代农业专题背景图，中间留白，边缘有乌蒙山、梯田、马铃薯和智慧农业元素，不要文字、不要按钮、不要卡片。" `
  -Size "3840x2160" `
  -Quality "medium" `
  -N 1 `
  -OutputPrefix "modern-agriculture-bg"
```

如果使用用户级脚本：

```powershell
& "$env:USERPROFILE\.codex\tools\generate_thinkai_image.ps1" `
  -Prompt "你的图片提示词" `
  -Size "3840x2160" `
  -Quality "medium" `
  -N 1 `
  -OutputPrefix "material"
```

生成结果默认保存在当前项目的 `outputs` 文件夹里。

## 7. 参数说明

| 参数 | 说明 | 示例 |
| --- | --- | --- |
| `-Prompt` | 图片提示词 | `"数字文旅背景图..."` |
| `-Size` | 图片尺寸 | `"3840x2160"` |
| `-Quality` | 质量，可选 `low`、`medium`、`high` | `"medium"` |
| `-N` | 生成数量 | `1` |
| `-OutputPrefix` | 输出文件名前缀 | `"digital-tourism-bg"` |
| `-OutputDir` | 输出目录 | `"outputs"` |

## 8. 常用尺寸

```text
1920x1080  常规横屏
3840x2160  4K 横屏
1024x1024  方图
1536x1024  横向概念图
1024x1536  竖向海报图
```

## 9. 注意事项

- 背景图用于叠加 UI 时，提示词里要写清楚“中间留白、只在边缘放主体元素”。
- 不希望模型生成文字时，明确写“不要文字、不要 logo、不要按钮、不要卡片、不要 UI 边框”。
- 密钥只放在环境变量里，不要写进脚本。
- 如果接口返回 URL，脚本会下载图片；如果返回 base64，脚本会直接保存为 PNG。

## 10. 双渠道与图片识别（本项目已配置）

本项目 `tools/` 目录下已内置三份脚本，两套生成渠道 + 一套识别能力并存：

| 脚本 | 渠道 | 用途 |
| --- | --- | --- |
| `tools/generate_thinkai_image.ps1` | ThinkAI `gpt-image-2-4k` | 图片生成（默认 3840×2160） |
| `tools/generate_zhipu_image.py` | 智谱 `cogview-4` | 图片生成（中文语义好，实测一次成功） |
| `tools/analyze_image.py` | 智谱 `glm-5v-turbo` | 图片识别/内容验证 |

### 智谱生成（cogview-4）

```bash
python tools/generate_zhipu_image.py --prompt "你的提示词" --size 1920x1088 --output-prefix my-bg
```

- 密钥：`ZHIPU_API_KEY`（用户级环境变量，已配置）
- 智谱尺寸限制：边长 512–2880px、宽高 16 的倍数、面积 ≤ 2^21 px，脚本会自动校验
- 合规且最接近 16:9 的最大尺寸是 `1920x1088`；需要 4K 时用 PIL 放大（`Image.LANCZOS`）
- 生成质量不稳定时建议用识别脚本验证内容

### 图片识别（glm-5v-turbo）

```bash
python tools/analyze_image.py --image "图片路径或URL" --prompt "请描述这张图片"
```

- 默认开启 thinking 模式（`--no-thinking` 关闭），与官方调用实例一致
- 支持本地图片路径（自动压缩转 base64）和 http(s) URL 直传
- 已验证 grounding 定位：`"Where is ...? Provide coordinates in [[xmin,ymin,xmax,ymax]] format"` 可返回坐标

### 渠道选择经验

- **ThinkAI `gpt-image-2-4k`**：原生支持 3840×2160，但渠道质量不稳定（曾连续两次生成与提示词无关的内容），生成后务必用 `analyze_image.py` 验证
- **智谱 `cogview-4`**：中文语义理解好，生成"乌蒙山、梯田、马铃薯"等本土场景更可靠；原生尺寸上限 1920×1088

