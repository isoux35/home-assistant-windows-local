$ErrorActionPreference = 'Stop'
$receiverTaskName = 'HA Local Guide - Govee'
$receiverScript = Join-Path $PSScriptRoot 'bridge.py'
$receiverTask = Get-ScheduledTask -TaskName $receiverTaskName -ErrorAction SilentlyContinue
if ($receiverTask) { Stop-ScheduledTask -TaskName $receiverTaskName }
# The venv launcher can leave a child Python process after the task is stopped.
# Match the absolute script path; do not stop unrelated Python processes.
$receiverProcesses = @(Get-CimInstance Win32_Process -Filter "Name='python.exe' OR Name='pythonw.exe'" | Where-Object {
    $_.CommandLine -and $_.CommandLine.Contains($receiverScript)
})
foreach ($receiverProcess in $receiverProcesses) { Stop-Process -Id $receiverProcess.ProcessId -ErrorAction SilentlyContinue }
