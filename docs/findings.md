# Tested findings

Recorded 2026-10-19. These are observations from one Windows PC, one H5105, two Kasa bulbs and one Wyze Cam OG. Versions and model details matter; broader device support and long-term reliability are not established.

## Govee

- Windows BLE advertisements were decoded into temperature, humidity, battery and signal strength with Bleak 3.0.2 and `govee-ble` 1.5.1 on Python 3.12.
- The PC's Intel Bluetooth adapter remained owned by Windows and continued serving existing peripherals. No pairing, GATT, cloud account, USBIP, or Bluetooth adapter passthrough was used for the sensor.
- Local MQTT discovery produced the expected sensors in Home Assistant. Fresh measurements were observed after stopping and restarting the receiver.
- Stopping a scheduled PowerShell task alone left a child Python process holding the Bluetooth receiver lock. The stop script therefore targets Python processes containing this installation's exact absolute script path.
- The installed scheduler workaround initially cloned a working local task. The public installer instead generates new XML from the current identity so no exported personal task metadata is distributed. Its XML is syntax-checked; live registration of this generalized installer has not been tested on a clean PC.

## Kasa KL125

- Enabling Third-Party Compatibility in the Kasa app resolved the local integration setup problem encountered here.
- Home Assistant's official TP-Link integration discovered and exposed both bulbs after direct device connection. The tested bulbs were hardware version 4 with firmware 1.1.1.
- No outage test or physical on/off test was performed, so those results are not claimed. Use the [official integration instructions](https://www.home-assistant.io/integrations/tplink/) for your firmware rather than assuming identical authentication behavior.
- Automatic discovery did not cross this installation's router boundary. Looking up the device on the modem/router and using its LAN address solved identification. The public project contains no original IP/MAC addresses or network names.

## Wyze Cam OG

- Firmware 1.0.98 streamed through the Gwell path when model overrides and the full API device identifier → LAN IP mapping were supplied.
- A continuous decode test processed 2,353 frames over approximately 120 seconds. This verifies a short successful stream, not an uptime guarantee.
- Correct software-decoded still frames coexisted with corrupted browser live video. The local baseline-H.264 re-encode wrapper corrected the visible browser live view.
- The wrapper produced Constrained Baseline H.264, level 4.0, 1920×1080 at 20 fps. One brief container sample showed approximately 18% of one CPU core and 108 MB memory; these are machine-specific observations, not sizing requirements.
- With internet denied to the bridge processes only, existing video continued, but a Gwell sidecar restart could not obtain a fresh cloud token. The camera's internet was never blocked. Do not label this fully offline.
- Normal connectivity and streaming were restored after the temporary test. The public project deliberately does not include privileged cgroup/firewall diagnostic scripts or personal packet captures.

## Existing work and useful upstream contributions

H5105 support already exists in [Home Assistant](https://www.home-assistant.io/integrations/govee_ble/) and the upstream [decoder library](https://github.com/Bluetooth-Devices/govee-ble). Another [Windows-compatible reader](https://github.com/NHaag87/govee-api) also exists. Our contribution is the integration of Windows scanning, MQTT discovery, local configuration and startup/stop behavior for Home Assistant inside WSL.

Wyze Gwell support and model overrides already exist in [Wyze Bridge](https://github.com/IDisposable/docker-wyze-bridge). Related reports include [OG classification #110](https://github.com/IDisposable/docker-wyze-bridge/issues/110), [OG stream availability #154](https://github.com/IDisposable/docker-wyze-bridge/issues/154), and [Window Cam browser decoding #157](https://github.com/IDisposable/docker-wyze-bridge/issues/157). A useful future contribution would be a minimal, sanitized OG-specific reproduction and optional transcoding configuration. No upstream issue or PR was submitted as part of publishing this repository.
