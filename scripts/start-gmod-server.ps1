<#
  Demarre le serveur GMod local de test.
  Rejoindre ensuite depuis GMod : console -> connect 127.0.0.1:27015

  Usage : .\scripts\start-gmod-server.ps1 [-Map gm_construct] [-Gamemode sandbox]
#>
param(
    [string]$Map      = 'gm_construct',
    [string]$Gamemode = 'sandbox',
    # 27016 et pas 27015 : le client GMod occupe deja 27015 des qu'il tourne,
    # et le serveur ne peut alors pas s'y attacher — il s'arrete aussitot.
    [int]$Port        = 27016
)

$root  = Split-Path -Parent $PSScriptRoot
$srcds = Join-Path $root 'server\srcds.exe'

if (-not (Test-Path $srcds)) {
    Write-Host "Serveur introuvable. Lancez d'abord .\scripts\setup-gmod-server.ps1" -ForegroundColor Red
    exit 1
}

Write-Host "Demarrage : $Map / $Gamemode  -  connect 127.0.0.1:$Port" -ForegroundColor Green

# -console exige une VRAIE console interactive : lance depuis un flux redirige,
# srcds sort sur CTextConsoleWin32::GetLine et s'arrete. A garder au premier
# plan dans un vrai terminal, ou a lancer via Start-Process (fenetre propre).
& $srcds -console -condebug -game garrysmod `
    +map $Map `
    +gamemode $Gamemode `
    +maxplayers 8 `
    +sv_lan 1 `
    -port $Port
