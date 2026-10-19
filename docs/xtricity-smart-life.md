# Xtricity Smart Life power bar over local LAN

The tested Xtricity Wi-Fi power bar was enrolled in Smart Life and worked with [make-all/tuya-local](https://github.com/make-all/tuya-local), stable release **2026.9.2-rel** (integration version **2026.9.2**), on Home Assistant Container **2026.10.2**. This is Tuya Local (`tuya_local`); select that integration in Home Assistant.

Its LAN protocol was automatically detected as **3.3**. The existing upstream **Powerstrip (`multi_timer_powerstrip`)** profile matched the reported datapoints without modifying upstream device definitions.

The unit was initially described as a four-outlet/three-USB power bar, but Smart Life and the LAN response both exposed **three switch channels**. Do not infer independently switchable sockets from a retail description. No separate fourth channel or USB switch was reported, and the physical socket-to-channel mapping was not independently established. Other Xtricity hardware or firmware may need a different profile.

## Install the custom integration

HACS was not installed in the tested Container setup. Only `custom_components/tuya_local` from the pinned upstream release was copied into the existing configuration bind mount. HACS users can use the [upstream installation guide](https://github.com/make-all/tuya-local/tree/2026.9.2-rel#installation).

For a fresh checkout of this repository, run from its root in Windows PowerShell with Git installed. Both the source download and Home Assistant configuration directories are ignored by Git. The commands refuse to overwrite an existing source checkout or integration; review and back up an existing installation before upgrading it.

```powershell
$sourceDirectory = Join-Path $PWD 'runtime/upstream/tuya-local-2026.9.2'
$componentsDirectory = Join-Path $PWD 'config/custom_components'
$installedDirectory = Join-Path $componentsDirectory 'tuya_local'
if ((Test-Path -LiteralPath $sourceDirectory) -or
    (Test-Path -LiteralPath $installedDirectory)) {
    throw 'Source or integration already exists; review it before continuing.'
}
New-Item -ItemType Directory -Force -Path (Split-Path $sourceDirectory), $componentsDirectory | Out-Null
git clone --depth 1 --branch 2026.9.2-rel https://github.com/make-all/tuya-local.git $sourceDirectory
if ($LASTEXITCODE -ne 0) { throw 'Tuya Local download failed.' }
Copy-Item -LiteralPath (Join-Path $sourceDirectory 'custom_components/tuya_local') -Destination $installedDirectory -Recurse
```

Use the configuration directory mounted as `/config` by your existing Home Assistant. Adapt the paths if it is outside this checkout; do not start a second installation. Home Assistant installs the release's dependencies, `tinytuya==1.20.0` and `tuya-device-sharing-sdk~=0.2.4`, inside its container. Initial installation needs internet access.

With this repository's Compose stack already running, validate and restart only Home Assistant:

```powershell
wsl -d Ubuntu-24.04 --cd "$PWD" -- docker compose exec homeassistant python -m homeassistant --script check_config --config /config
if ($LASTEXITCODE -ne 0) { throw 'Home Assistant configuration check failed.' }
wsl -d Ubuntu-24.04 --cd "$PWD" -- docker compose restart homeassistant
if ($LASTEXITCODE -ne 0) { throw 'Home Assistant restart failed.' }
```

Use your own distribution name if it differs from `Ubuntu-24.04`.

## Retrieve the local key privately

The [cloud-assisted flow](https://github.com/make-all/tuya-local/tree/2026.9.2-rel#choose-your-configuration-path) retrieves connection information without a Tuya developer account. It uses Smart Life cloud during setup; routine commands then go directly to the device over LAN.

1. Leave the bar powered on and already enrolled in Smart Life. Do not reset or re-pair it just to add Home Assistant.
2. In Home Assistant, open **Settings → Devices & services → Add integration → Tuya Local** and choose **SmartLife cloud-assisted device setup**.
3. Find **User Code** in Smart Life **Settings → Account and Security**. Enter it directly into the local Home Assistant form. Scan the displayed QR code with Smart Life and approve the login on your phone. Do not share the code, QR image or resulting device key.
4. Select the power bar from the account's device list. A directly connected Wi-Fi bar uses **None** for gateway. In the tested setup it appeared under a generic power-strip product name; verify the correct device rather than selecting by branding alone.
5. Close Smart Life on the phone before local discovery and connection. Many Tuya devices support only one local client; competing phone apps, another local integration or a diagnostic tool can occupy it.
6. Let discovery search for the address. If it fails, find the bar's LAN IP in your router's connected-device/DHCP list and enter it privately. Keep the retrieved Device ID and local key unchanged. Start with protocol **auto**.
7. Inspect the reported controls and select the matching device profile. The tested unit selected **Powerstrip (`multi_timer_powerstrip`)** and saved protocol **3.3**. Do not force this profile onto a unit with a different datapoint response.
8. Choose a device name and finish. Three switch entities and three timer entities were active here; the optional fourth outlet/timer and unsupported features remained disabled.

Broadcast discovery failed across the tested router/subnet boundary, but a direct connection to the bar's known address succeeded. Discovery failure alone does not establish that LAN control is impossible. Home Assistant still needs a route to the device and permission to reach its local Tuya service (TCP port `6668` on this unit). A DHCP reservation on your own router can keep the address stable. Automatic rediscovery may remain ineffective across that router boundary.

## Reported channel mapping

These are protocol datapoint numbers, not device identifiers or captured personal readings:

| Datapoint | Type | Exposed entity |
| --- | --- | --- |
| `1` | Boolean | Outlet 1 switch |
| `2` | Boolean | Outlet 2 switch |
| `3` | Boolean | Outlet 3 switch |
| `9` | Integer, seconds | Timer 1 |
| `10` | Integer, seconds | Timer 2 |
| `11` | Integer, seconds | Timer 3 |

The mapping comes from the device response and the [upstream profile](https://github.com/make-all/tuya-local/blob/2026.9.2-rel/custom_components/tuya_local/devices/multi_timer_powerstrip.yaml). Home Assistant represents these countdown timers as time entities; the underlying values are durations in seconds, not scheduled wall-clock times. Timer operation was not tested.

## Verify control and startup

1. Compare the three Home Assistant controls with those in Smart Life, then close the phone app again.
2. Identify a safe test channel. Avoid interrupting a computer, router or other essential load. Briefly change its state, verify the response and restore its original state.
3. Add the three switches to Overview Favorites or a dashboard card.
4. Restart Home Assistant and confirm the switches return with their actual states and the dashboard entries persist.

The tested installation passed a brief on/off test of the initially-off second channel and restored it to off. A direct TCP connection from Home Assistant to the bar was confirmed, and local connection and all three switch states returned after restarting Home Assistant.

The [upstream setup guide](https://github.com/make-all/tuya-local/tree/2026.9.2-rel#choose-your-configuration-path) states that its temporary cloud authentication token is kept in memory and is not saved. The tested saved integration entry contained local connection information, not that cloud login token. A restart therefore checked reconnection after clearing the temporary login, while internet access remained available.

This is evidence of local control and restart recovery, not a complete internet-outage test. Neither Home Assistant's nor the bar's internet access was blocked. Tuya Local also does not prevent the bar itself from contacting Tuya cloud. No separate Windows bridge or startup task is needed; the integration loads with Home Assistant under the existing [startup arrangement](windows-setup.md#start-at-sign-in).

## Keep connection data private

The device ID and local key are stored in Home Assistant's ignored `config/` directory. Do not commit `.storage`, account exports, diagnostics or screenshots containing the setup form. This repository supplies no real device identifiers, LAN addresses, keys or cloud tokens.

Re-pairing the device changes its local key. If this happens, retrieve the new key through the private setup flow and reconfigure the integration. Do not publish the old or new key in an issue. See [upstream troubleshooting](https://github.com/make-all/tuya-local/tree/2026.9.2-rel) for protocol and connection problems.
