<#
  Ecrit gmod/server.cfg dans le serveur local et y injecte l'URL voulue.

  Usage :
    .\scripts\apply-loadingurl.ps1                       # URL GitHub Pages
    .\scripts\apply-loadingurl.ps1 -Local                # http://127.0.0.1:8080/index.html
    .\scripts\apply-loadingurl.ps1 -Url "https://..."    # URL libre
#>
param(
    [string]$Url,
    [switch]$Local
)
$ErrorActionPreference = 'Stop'

$root   = Split-Path -Parent $PSScriptRoot
$src    = Join-Path $root 'gmod\server.cfg'
$destDir= Join-Path $root 'server\garrysmod\cfg'
$dest   = Join-Path $destDir 'server.cfg'

$pagesUrl = 'https://desync76.github.io/scp-atlas-loadingscreen/'

if ($Local)          { $Url = 'http://127.0.0.1:8080/index.html' }
elseif (-not $Url)   { $Url = $pagesUrl }

if (-not (Test-Path $destDir)) {
    Write-Host "Serveur introuvable. Lancez d'abord .\scripts\setup-gmod-server.ps1" -ForegroundColor Red
    exit 1
}

$cfg = Get-Content $src -Raw
$cfg = [regex]::Replace($cfg, '(?m)^\s*sv_loadingurl\s+".*?"\s*$', "sv_loadingurl `"$Url`"")

# UTF-8 SANS BOM. Set-Content -Encoding utf8 en ajoute un sous PowerShell 5.1,
# et le moteur Source lit alors le marqueur comme une commande : la console
# affiche Unknown command "" et la premiere ligne du fichier est perdue.
[System.IO.File]::WriteAllText($dest, $cfg, (New-Object System.Text.UTF8Encoding($false)))

Write-Host "server.cfg ecrit : $dest" -ForegroundColor Green
Write-Host "sv_loadingurl -> $Url" -ForegroundColor Cyan
