$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true

$repositoryRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $repositoryRoot ".venv\Scripts\python.exe"
$authRoot = Join-Path $PSScriptRoot "allianceauth"
$manage = Join-Path $authRoot "manage.py"
$env:DJANGO_SETTINGS_MODULE = "local_auth.settings.local"

if (-not (Test-Path $python)) {
    throw "Missing .venv. Create it with: py -3.12 -m venv .venv"
}

$environmentFile = Join-Path $PSScriptRoot ".env"
if (-not (Test-Path $environmentFile)) {
    Copy-Item (Join-Path $PSScriptRoot ".env.example") $environmentFile
}

docker compose -f (Join-Path $PSScriptRoot "compose.yml") up -d

& $python -m pip install --editable $repositoryRoot
Push-Location $authRoot
try {
    & $python $manage migrate
    $seedScript = Join-Path $PSScriptRoot "seed_allianceauth.py"
    & $python $manage shell --command "exec(open(r'$seedScript').read())"
    & $python $manage check
}
finally {
    Pop-Location
}

Write-Host ""
Write-Host "Local validation environment is ready."
Write-Host "Alliance Auth: http://localhost:8000"
Write-Host "Wiki.js:       http://localhost:3000"
Write-Host ""
Write-Host "Run dev\start-auth.ps1 to start Alliance Auth."
Write-Host "Complete the Wiki.js setup wizard, create a Full Access API key, then set:"
Write-Host "  Copy dev\.env.example to dev\.env and add the key."