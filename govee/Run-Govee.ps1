$ErrorActionPreference = 'Stop'
$receiverPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $receiverPython)) { throw 'Create govee/.venv and install requirements first.' }
& $receiverPython -u (Join-Path $PSScriptRoot 'bridge.py')
if ($LASTEXITCODE -ne 0) { throw 'The Govee receiver stopped unexpectedly. Check govee/runtime/bridge.log.' }
