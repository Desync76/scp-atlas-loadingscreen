<#
  Demarre le serveur GMod local de test.
  Rejoindre ensuite depuis GMod : console -> connect 127.0.0.1:27015

  Usage : .\scripts\start-gmod-server.ps1 [-Map gm_construct] [-Gamemode sandbox]
#>
param(
    [string]$Map      = 'gm_construct',
    [string]$Gamemode = 'sandbox'
)

$root  = Split-Path -Parent $PSScriptRoot
$srcds = Join-Path $root 'server\srcds.exe'

if (-not (Test-Path $srcds)) {
    Write-Host "Serveur introuvable. Lancez d'abord .\scripts\setup-gmod-server.ps1" -ForegroundColor Red
    exit 1
}

Write-Host "Demarrage : $Map / $Gamemode  -  connect 127.0.0.1:27015" -ForegroundColor Green

& $srcds -console -game garrysmod `
    +map $Map `
    +gamemode $Gamemode `
    +maxplayers 8 `
    +sv_lan 1 `
    -port 27015
