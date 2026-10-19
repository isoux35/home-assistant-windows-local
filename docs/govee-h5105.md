# Govee H5105 over local Bluetooth

Home Assistant already supports the H5105 through its [Govee Bluetooth integration](https://www.home-assistant.io/integrations/govee_ble/). This receiver is useful when Home Assistant runs in WSL and Windows needs to keep its Bluetooth adapter for other devices.

It reads live BLE advertisements with Bleak and decodes them with the same upstream `govee-ble` library used by Home Assistant. It uses no Govee login, cloud API, pairing, or GATT connection. Historical samples stored inside the sensor are outside this receiver's scope.

## Install and identify your sensor

From the repository root in Windows PowerShell:

```powershell
py -3.12 -m venv govee/.venv
.\govee\.venv\Scripts\python.exe -m pip install -r govee/requirements.lock.txt
.\govee\.venv\Scripts\python.exe govee/scan_govee.py --seconds 30
Copy-Item govee/config.example.json govee/config.json
```

The lock file is a snapshot from the tested Windows Python 3.12 environment. `requirements.txt` lists the directly used libraries. The scanner prints only matching H5105 devices and writes its results to ignored `govee/runtime/scan-result.json`. Keep this output private: it includes local Bluetooth addresses.

Edit `govee/config.json` locally: replace the example address with your sensor's MAC and choose a device name. This file is ignored by Git. The receiver deliberately rejects the unchanged example MAC. Place the sensor within Bluetooth range and ensure Bluetooth is enabled in Windows. No USB passthrough or WSL Bluetooth setup is required.

## Connect Home Assistant

Start the root Compose stack first. In Home Assistant, add the MQTT integration with broker `127.0.0.1`, port `1883`, and no username/password for this loopback-only example. Start the receiver:

```powershell
.\govee\Run-Govee.ps1
```

After a fresh advertisement, Home Assistant should discover a Govee H5105 device with temperature, humidity and battery sensors, plus a disabled-by-default diagnostic signal-strength sensor. Changing the sensor address changes its stable IDs and creates a different device. The runtime log and latest status are under ignored `govee/runtime/`.

The receiver publishes retained MQTT discovery, republishes it when Home Assistant announces startup, and retries MQTT connections. It publishes changes or a heartbeat at most every 60 seconds when advertisements arrive. State expires after 180 seconds. A stale or absent sample is not advertised as online; the scanner retries after errors and restarts after 180 seconds without target advertisements. A local lock prevents duplicate receiver instances.

## Automatic startup and stop

After checking live readings, install the sign-in task:

```powershell
.\windows\Install-Startup.ps1 -Component Govee
```

It starts 35 seconds after sign-in. To stop it and its Python child processes:

```powershell
.\govee\Stop-Govee.ps1
```

Do not run a second receiver with the same sensor ID while an existing installation is publishing it. These scripts target one configured H5105. Multi-sensor support and prolonged unattended recovery have not been validated.
