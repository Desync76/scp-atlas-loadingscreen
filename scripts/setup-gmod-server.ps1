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

$exe = Join-Path $steamDir 'steamcmd.exe'

# Au tout premier lancement, SteamCMD se met a jour lui-meme, se relance, et
# ABANDONNE les commandes qu'on lui avait passees. On le lance donc une fois a
# vide pour absorber cette mise a jour avant de demander quoi que ce soit.
Write-Host "[2/3] Amorcage de SteamCMD..." -ForegroundColor Cyan
& $exe +quit | Out-Null

Write-Host "[3/3] Installation du serveur GMod (app 4020)..." -ForegroundColor Cyan
Write-Host "      Cela peut prendre un long moment la premiere fois." -ForegroundColor DarkGray

$srcds = Join-Path $srvDir 'srcds.exe'

# Une reprise suffit en general : SteamCMD coupe parfois sur une erreur reseau
# transitoire, et app_update reprend la ou il s'etait arrete.
foreach ($essai in 1..3) {
    if (Test-Path $srcds) { break }
    if ($essai -gt 1) { Write-Host "      Reprise ($essai/3)..." -ForegroundColor DarkGray }
    & $exe +force_install_dir $srvDir +login anonymous +app_update 4020 validate +quit
}

if (-not (Test-Path $srcds)) {
    Write-Host "Echec : srcds.exe introuvable dans $srvDir" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Serveur installe dans $srvDir" -ForegroundColor Green
Write-Host "Etape suivante : .\scripts\apply-loadingurl.ps1" -ForegroundColor Yellow
