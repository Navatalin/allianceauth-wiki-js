$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true

$repositoryRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $repositoryRoot ".venv\Scripts\python.exe"
$authRoot = Join-Path $PSScriptRoot "allianceauth"
$manage = Join-Path $authRoot "manage.py"
$env:DJANGO_SETTINGS_MODULE = "local_auth.settings.local"

if (Test-Path (Join-Path $PSScriptRoot ".env")) {
	Get-Content (Join-Path $PSScriptRoot ".env") | ForEach-Object {
		if ($_ -match '^\s*([^#][^=]*)=(.*)$') {
			[Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim(), "Process")
		}
	}
}

Push-Location $authRoot
try {
	& $python $manage runserver 0.0.0.0:8000
}
finally {
	Pop-Location
}