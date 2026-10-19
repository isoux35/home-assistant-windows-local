# Tested findings

Recorded 2026-10-19. These are observations from one Windows PC, one H5105, two Kasa bulbs, one Wyze Cam OG, one Winix C909 and one Xtricity Smart Life power bar. Versions and model details matter; broader device support and long-term reliability are not established.

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

## Winix C909

- Community integration `iprak/winix` 1.7.0 loaded successfully on Home Assistant Container 2026.10.2. The tested C909 reported firmware 1.0.2.
- The integration requires Winix cloud authentication and polling. This installation allowed a cloud-dependent exception; local-only C909 control is not established.
- A fan entity, AQI, Filter Life, Air QValue and a maximum-filter-life diagnostic sensor were exposed. The fan and selected sensors were added to Overview Favorites and remained there after a dashboard reload.
- No purifier power/speed change or internet-outage test was performed. Live readings, account information and purifier identifiers are omitted from this repository.
- See the [Winix setup guide](winix-c909.md), including the upstream warning about concurrent phone-app/Home Assistant sessions.

## Xtricity Smart Life power bar

- `make-all/tuya-local` stable release 2026.9.2-rel (integration 2026.9.2) established a direct LAN connection using automatically detected protocol 3.3. The upstream `multi_timer_powerstrip` profile matched without changes.
- Smart Life QR sign-in supplied the device ID and local key during setup. Broadcast discovery failed across the router boundary; manually supplying the device's LAN address succeeded.
- The actual response contained switch datapoints 1, 2 and 3, and timer datapoints 9, 10 and 11. Smart Life also showed three controls. Retail descriptions did not establish a separately controllable fourth outlet or USB group, and the socket-to-channel mapping was not independently verified.
- An initially-off second channel passed a brief on/off test and was restored. Home Assistant maintained a direct local TCP connection to the bar on port 6668.
- After a Home Assistant restart cleared the temporary cloud login, the local connection and three switch states returned. The switches also remained in dashboard Favorites. Timer behavior was not tested.
- Internet access remained enabled throughout. This verifies LAN control and restart recovery, not a full outage test or prevention of the bar's own cloud traffic. See the [Xtricity local setup guide](xtricity-smart-life.md).

## Existing work and upstream contributions

H5105 support already exists in [Home Assistant](https://www.home-assistant.io/integrations/govee_ble/) and the upstream [decoder library](https://github.com/Bluetooth-Devices/govee-ble). Another [Windows-compatible reader](https://github.com/NHaag87/govee-api) also exists. Our contribution is the integration of Windows scanning, MQTT discovery, local configuration and startup/stop behavior for Home Assistant inside WSL.

Wyze Gwell support and model overrides already exist in [Wyze Bridge](https://github.com/IDisposable/docker-wyze-bridge). Related reports include [OG classification #110](https://github.com/IDisposable/docker-wyze-bridge/issues/110), [OG stream availability #154](https://github.com/IDisposable/docker-wyze-bridge/issues/154), and [Window Cam browser decoding #157](https://github.com/IDisposable/docker-wyze-bridge/issues/157). Sanitized OG findings were subsequently submitted as [issue #163](https://github.com/IDisposable/docker-wyze-bridge/issues/163), and a Windows BLE scanning example was submitted to `govee-ble` as [PR #296](https://github.com/Bluetooth-Devices/govee-ble/pull/296).
