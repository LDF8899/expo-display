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
