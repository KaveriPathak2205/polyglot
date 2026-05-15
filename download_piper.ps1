$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
$models = Join-Path $root "models"
New-Item -ItemType Directory -Force -Path $models | Out-Null

Write-Host "Downloading piper.exe..."
$zip = Join-Path $env:TEMP "piper_win.zip"
$ext = Join-Path $env:TEMP "piper_win_extract"
Invoke-WebRequest -Uri "https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_windows_amd64.zip" -OutFile $zip -UseBasicParsing
if (Test-Path $ext) { Remove-Item -Recurse -Force $ext }
Expand-Archive -Path $zip -DestinationPath $ext -Force
$exe = Get-ChildItem -Path $ext -Recurse -Filter "piper.exe" | Select-Object -First 1
if (-not $exe) { throw "piper.exe not found" }
Copy-Item $exe.FullName (Join-Path $root "piper.exe") -Force
Get-ChildItem $exe.DirectoryName | Copy-Item -Destination $root -Recurse -Force
Write-Host "piper.exe OK"

$files = @{
    "en_US-amy-medium.onnx" = "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx"
    "en_US-amy-medium.onnx.json" = "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx.json"
    "hi_IN-rohan-medium.onnx" = "https://huggingface.co/rhasspy/piper-voices/resolve/main/hi/hi_IN/rohan/medium/hi_IN-rohan-medium.onnx"
    "hi_IN-rohan-medium.onnx.json" = "https://huggingface.co/rhasspy/piper-voices/resolve/main/hi/hi_IN/rohan/medium/hi_IN-rohan-medium.onnx.json"
    "es_ES-mls_9972-low.onnx" = "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/mls_9972/low/es_ES-mls_9972-low.onnx"
    "es_ES-mls_9972-low.onnx.json" = "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/mls_9972/low/es_ES-mls_9972-low.onnx.json"
}

foreach ($name in $files.Keys) {
    Write-Host "Downloading $name ..."
    $out = Join-Path $models $name
    Invoke-WebRequest -Uri $files[$name] -OutFile $out -UseBasicParsing
}

Write-Host "All done."
