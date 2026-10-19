# Windows and Home Assistant setup

Tested baseline: Windows with WSL2 Ubuntu 24.04, Docker Engine 29.1.3 inside WSL, Docker Compose v2, Home Assistant Container 2026.10.2, and Python 3.12 on Windows. Docker Desktop was not used. This is a Home Assistant Container installation, so Supervisor apps/add-ons are not available.

## Prerequisites

- Install WSL2 and Ubuntu using [Microsoft's instructions](https://learn.microsoft.com/windows/wsl/install).
- Enable systemd in the distribution if needed using [Microsoft's systemd guide](https://learn.microsoft.com/windows/wsl/systemd).
- Install Docker Engine and the Compose plugin inside Ubuntu using [Docker's Ubuntu instructions](https://docs.docker.com/engine/install/ubuntu/).
- Install Python 3.12 on Windows for the optional BLE receiver.
- Place this repository in a directory that WSL can access, such as a Windows folder without unusual shell characters. Keep the checkout path stable once startup tasks are installed.

The Windows scripts default to the WSL distribution name `Ubuntu-24.04`; pass `-Distribution YOUR_DISTRO` if yours differs. They expect your WSL user to have permission to run Docker. Check this using `wsl -d Ubuntu-24.04 -- docker info` before continuing. Follow Docker's documented post-installation guidance for your chosen permission model.

## Start Home Assistant and MQTT

From the repository root in PowerShell:

```powershell
Copy-Item .env.example .env
# Optionally edit .env to select your timezone.
.\windows\Run-HomeAssistant.ps1
```

This stays running to keep WSL alive. Open [Home Assistant](http://localhost:8123), finish onboarding, then follow the device guides. State goes into the ignored `config/` directory and a Docker named volume for MQTT.

The example publishes MQTT only on `127.0.0.1:1883` in WSL. On the tested machine, WSL localhost forwarding made this reachable from the Windows receiver. If it fails on another WSL networking configuration, first check localhost forwarding; do not fix it by exposing the anonymous broker to the LAN.

Home Assistant uses Linux host networking, as in the tested installation. Check your machine's own reachability and firewall rules before assuming that the UI is confined to loopback.

## Start at sign-in

After manual startup succeeds, close the foreground runner and install a task:

```powershell
.\windows\Install-Startup.ps1 -Component HomeAssistant
```

The task runs hidden as the current interactive user with limited privileges, 30 seconds after sign-in. It does not store an account password. It starts Home Assistant/MQTT, starts Wyze if `wyze/.secrets.env` exists, and starts the Govee task if installed. It is a sign-in task, not a boot service: it requires the user session and does not promise operation after sign-out. Leave the PC powered on and prevent sleep during required automations.

To stop this installation:

```powershell
.\windows\Stop-HomeAssistant.ps1
```

To remove automatic startup without deleting data, stop the stack, then unregister the two `HA Local Guide - ...` tasks from Task Scheduler. This repository's startup scripts refuse to replace a task owned by a different script path.
