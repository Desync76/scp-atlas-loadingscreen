<#
  Installe un serveur dédié Garry's Mod local dans .\server\ via SteamCMD.
  A lancer UNE SEULE FOIS (~2-3 Go de téléchargement).

  Usage : .\scripts\setup-gmod-server.ps1
#>
$ErrorActionPreference = 'Stop'

$root     = Split-Path -Parent $PSScriptRoot
$steamDir = Join-Path $root 'steamcmd'
$srvDir   = Join-Path $root 'server'
$zip      = Join-Path $steamDir 'steamcmd.zip'

New-Item -ItemType Directory -Force -Path $steamDir | Out-Null
New-Item -ItemType Directory -Force -Path $srvDir   | Out-Null

if (-not (Test-Path (Join-Path $steamDir 'steamcmd.exe'))) {
    Write-Host "[1/2] Telechargement de SteamCMD..." -ForegroundColor Cyan
    Invoke-WebRequest -Uri 'https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip' -OutFile $zip
    Expand-Archive -Path $zip -DestinationPath $steamDir -Force
    Remove-Item $zip -Force
} else {
    Write-Host "[1/2] SteamCMD deja present." -ForegroundColor DarkGray
}

Write-Host "[2/2] Installation du serveur GMod (app 4020)..." -ForegroundColor Cyan
Write-Host "      Cela peut prendre un long moment la premiere fois." -ForegroundColor DarkGray

& (Join-Path $steamDir 'steamcmd.exe') `
    +force_install_dir $srvDir `
    +login anonymous `
    +app_update 4020 validate `
    +quit

if (-not (Test-Path (Join-Path $srvDir 'srcds.exe'))) {
    Write-Host "Echec : srcds.exe introuvable dans $srvDir" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Serveur installe dans $srvDir" -ForegroundColor Green
Write-Host "Etape suivante : .\scripts\apply-loadingurl.ps1" -ForegroundColor Yellow
