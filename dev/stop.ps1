$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true

docker compose -f (Join-Path $PSScriptRoot "compose.yml") down