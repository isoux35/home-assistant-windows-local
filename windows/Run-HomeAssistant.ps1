param([string]$Distribution = 'Ubuntu-24.04')
$ErrorActionPreference = 'Stop'
$projectDirectory = Split-Path $PSScriptRoot -Parent
& wsl.exe -d $Distribution --user root -- systemctl start docker
if ($LASTEXITCODE -ne 0) { throw 'Could not start Docker Engine in WSL.' }
& wsl.exe -d $Distribution --cd $projectDirectory -- docker compose up -d
if ($LASTEXITCODE -ne 0) { throw 'Could not start Home Assistant and MQTT.' }
$cameraDirectory = Join-Path $projectDirectory 'wyze'
if (Test-Path -LiteralPath (Join-Path $cameraDirectory '.secrets.env')) {
    & wsl.exe -d $Distribution --cd $cameraDirectory -- docker compose up -d
    if ($LASTEXITCODE -ne 0) { Write-Warning 'Wyze failed to start; Home Assistant is still running.' }
}
$receiverTask = Get-ScheduledTask -TaskName 'HA Local Guide - Govee' -ErrorAction SilentlyContinue
if ($receiverTask) { Start-ScheduledTask -TaskName $receiverTask.TaskName }
# Keep a WSL process alive; task runs until explicitly stopped or sign-out.
& wsl.exe -d $Distribution --exec sleep infinity
throw 'The WSL keepalive session ended.'
