$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

$listener = Get-NetTCPConnection -LocalAddress 127.0.0.1 -LocalPort 8768 -State Listen -ErrorAction SilentlyContinue
if ($listener) {
    Stop-Process -Id $listener.OwningProcess -Force
}

$env:LEADGEN_SEARCH_PROVIDER = 'serpapi'
$secureKey = Read-Host 'Enter SerpApi key' -AsSecureString
$ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureKey)
try {
    $env:LEADGEN_SEARCH_API_KEY = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
}
finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
}
$env:LEADGEN_DISCOVERY_SOURCES = ''

$python = Join-Path $projectRoot '.venv\Scripts\python.exe'
if (-not (Test-Path $python)) {
    throw "LeadGen virtual environment not found: $python"
}

Start-Process -FilePath $python -WorkingDirectory $projectRoot -ArgumentList '-m','uvicorn','app.main:app','--host','127.0.0.1','--port','8768'
Start-Sleep -Milliseconds 800
Start-Process 'http://127.0.0.1:8768/discover/provider-check'
Write-Host 'LeadGen started on http://127.0.0.1:8768'
Write-Host 'Provider check opened. Do not run discovery until it reports HTTP status 200.'
