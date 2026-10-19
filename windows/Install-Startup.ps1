param(
    [ValidateSet('HomeAssistant', 'Govee')][string]$Component,
    [string]$Distribution = 'Ubuntu-24.04'
)
$ErrorActionPreference = 'Stop'
$projectDirectory = Split-Path $PSScriptRoot -Parent
if (-not $Component) { throw 'Specify -Component HomeAssistant or -Component Govee.' }
if ($Distribution -notmatch '^[A-Za-z0-9_.-]+$') { throw 'Unsupported WSL distribution name.' }
if ($Component -eq 'Govee') {
    $runner = Join-Path $projectDirectory 'govee\Run-Govee.ps1'
    $taskName = 'HA Local Guide - Govee'
    $delay = 'PT35S'
    $extraArguments = ''
} else {
    $runner = Join-Path $PSScriptRoot 'Run-HomeAssistant.ps1'
    $taskName = 'HA Local Guide - Home Assistant'
    $delay = 'PT30S'
    $extraArguments = ' -Distribution "' + $Distribution + '"'
}
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existingTask -and (@($existingTask.Actions.Arguments | Where-Object { $_ -like ('*' + $runner + '*') }).Count -eq 0)) {
    throw 'Another installation owns this task name. Remove or rename it yourself before continuing.'
}
# Build task XML from the current identity. No exported user SID/account is stored in this repository.
$taskSid = [System.Security.Principal.WindowsIdentity]::GetCurrent().User.Value
$taskShell = "$env:WINDIR\System32\WindowsPowerShell\v1.0\powershell.exe"
$taskArguments = '-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File "' + $runner + '"' + $extraArguments
$xmlEscape = { param($text) [System.Security.SecurityElement]::Escape($text) }
$taskXml = @"
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo><Description>Local Home Assistant guide: $Component at sign-in.</Description></RegistrationInfo>
  <Triggers><LogonTrigger><Enabled>true</Enabled><UserId>$taskSid</UserId><Delay>$delay</Delay></LogonTrigger></Triggers>
  <Principals><Principal id="Author"><UserId>$taskSid</UserId><LogonType>InteractiveToken</LogonType><RunLevel>LeastPrivilege</RunLevel></Principal></Principals>
  <Settings><MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy><DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries><StopIfGoingOnBatteries>false</StopIfGoingOnBatteries><StartWhenAvailable>true</StartWhenAvailable><ExecutionTimeLimit>PT0S</ExecutionTimeLimit><Enabled>true</Enabled></Settings>
  <Actions Context="Author"><Exec><Command>$(& $xmlEscape $taskShell)</Command><Arguments>$(& $xmlEscape $taskArguments)</Arguments><WorkingDirectory>$(& $xmlEscape $projectDirectory)</WorkingDirectory></Exec></Actions>
</Task>
"@
Register-ScheduledTask -TaskName $taskName -Xml $taskXml -Force | Out-Null
Start-ScheduledTask -TaskName $taskName
Write-Output "$Component starts now and at this user's next sign-in."
