# 用 Word COM 把 .doc 转换为 .docx（保持图片），失败退出码非 0
$ErrorActionPreference = 'Stop'
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {
    foreach ($src in $args) {
        $doc = $word.Documents.Open($src, $false, $true)  # ReadOnly
        $dst = [System.IO.Path]::ChangeExtension($src, '.converted.docx')
        $doc.SaveAs([ref]$dst, [ref]16)  # wdFormatXMLDocument = 16
        $doc.Close($false)
        Write-Output ("converted: {0}" -f $dst)
    }
} finally {
    $word.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
}
