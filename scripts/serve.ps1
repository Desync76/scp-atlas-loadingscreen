<#
  Lance le loading screen en local sur http://127.0.0.1:8080
  Usage : .\scripts\serve.ps1  [-Port 8080]
#>
param([int]$Port = 8080)

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$url = "http://127.0.0.1:$Port/index.html?hostname=SCP+ATLAS+(local)&mapname=rp_scp_atlas&gamemode=scpatlas&maxplayers=64"

Write-Host ""
Write-Host "  Loading screen servi depuis : $root" -ForegroundColor Cyan
Write-Host "  URL : $url" -ForegroundColor Green
Write-Host "  Ctrl+C pour arreter." -ForegroundColor DarkGray
Write-Host ""

Start-Process $url
python -m http.server $Port --bind 127.0.0.1
