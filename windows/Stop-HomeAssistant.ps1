param([string]$Distribution = 'Ubuntu-24.04')
$ErrorActionPreference = 'Stop'
$projectDirectory = Split-Path $PSScriptRoot -Parent
& (Join-Path $projectDirectory 'govee\Stop-Govee.ps1')
$cameraDirectory = Join-Path $projectDirectory 'wyze'
if (Test-Path -LiteralPath (Join-Path $cameraDirectory '.secrets.env')) {
    & wsl.exe -d $Distribution --cd $cameraDirectory -- docker compose stop
    if ($LASTEXITCODE -ne 0) { Write-Warning 'Could not stop Wyze cleanly.' }
}
& wsl.exe -d $Distribution --cd $projectDirectory -- docker compose stop
if ($LASTEXITCODE -ne 0) { throw 'Could not stop Home Assistant and MQTT.' }
$startupTask = Get-ScheduledTask -TaskName 'HA Local Guide - Home Assistant' -ErrorAction SilentlyContinue
if ($startupTask) { Stop-ScheduledTask -TaskName $startupTask.TaskName }
