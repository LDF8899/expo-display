$apps = @('Word.Application','KWPS.Application','Kwps.Application','WPS.Application','WPS.Application.1')
foreach ($a in $apps) {
    try {
        $t = [Type]::GetTypeFromProgID($a)
        if ($t) { Write-Output ("{0} : available" -f $a) }
    } catch {}
}
