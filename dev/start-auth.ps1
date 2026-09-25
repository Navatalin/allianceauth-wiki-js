param([switch]$RequireEveSso)

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

if ($RequireEveSso -and (
	[string]::IsNullOrWhiteSpace($env:AA_ESI_CLIENT_ID) -or
	[string]::IsNullOrWhiteSpace($env:AA_ESI_CLIENT_SECRET) -or
	$env:AA_ESI_CLIENT_ID -eq "local-development" -or
	$env:AA_ESI_CLIENT_SECRET -eq "local-development")) {
	throw "Set real AA_ESI_CLIENT_ID and AA_ESI_CLIENT_SECRET in dev\.env for EVE SSO. Register http://localhost:8000/sso/callback with your EVE developer app."
}

Push-Location $authRoot
try {
	& $python $manage runserver 0.0.0.0:8000
}
finally {
	Pop-Location
}