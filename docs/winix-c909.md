# Winix C909: cloud-dependent setup

The tested C909 uses the community [iprak/winix integration](https://github.com/iprak/winix), version **1.7.0**, with Home Assistant Container **2026.10.2**. The purifier reported firmware **1.0.2**. This setup requires a Winix account and internet access: the integration declares `cloud_polling`, and this guide establishes no local-only control method for the C909.

The tested installation explicitly allowed this cloud dependency. Skip this integration if every device must operate without a vendor cloud.

## Install the custom integration

Home Assistant Container does not provide Supervisor apps/add-ons. HACS was not installed in the tested setup; only the upstream integration directory was copied into the existing configuration bind mount. HACS users can follow upstream installation guidance instead.

For a fresh checkout of this repository, run the following from its root in Windows PowerShell. Git must be installed. Source downloads go into ignored `runtime/`; Home Assistant configuration goes into ignored `config/`. These commands refuse to replace an existing source checkout or installed integration. Back up an existing installation and follow upstream upgrade instructions rather than forcing an overwrite.

```powershell
$sourceDirectory = Join-Path $PWD 'runtime/upstream/winix-v1.7.0'
$componentsDirectory = Join-Path $PWD 'config/custom_components'
$installedDirectory = Join-Path $componentsDirectory 'winix'
if ((Test-Path -LiteralPath $sourceDirectory) -or
    (Test-Path -LiteralPath $installedDirectory)) {
    throw 'Source or integration already exists; review it before continuing.'
}
New-Item -ItemType Directory -Force -Path (Split-Path $sourceDirectory), $componentsDirectory | Out-Null
git clone --depth 1 --branch v1.7.0 https://github.com/iprak/winix.git $sourceDirectory
if ($LASTEXITCODE -ne 0) { throw 'Winix download failed.' }
Copy-Item -LiteralPath (Join-Path $sourceDirectory 'custom_components/winix') -Destination $installedDirectory -Recurse
```

Use the same `config/` directory that your running Home Assistant mounts as `/config`. If you already run Home Assistant elsewhere, adapt the paths to that installation instead of starting a second stack. The tested release's manifest requires `winix==0.3.0` and `pycryptodome==3.23.0`; Home Assistant installs these into its container when loading the integration. Do not install them into the Windows BLE receiver environment.

With this repository's Compose stack already running, check configuration and restart only Home Assistant:

```powershell
wsl -d Ubuntu-24.04 --cd "$PWD" -- docker compose exec homeassistant python -m homeassistant --script check_config --config /config
if ($LASTEXITCODE -ne 0) { throw 'Home Assistant configuration check failed.' }
wsl -d Ubuntu-24.04 --cd "$PWD" -- docker compose restart homeassistant
if ($LASTEXITCODE -ne 0) { throw 'Home Assistant restart failed.' }
```

Choose your own WSL distribution name if it differs. Initial dependency installation needs internet access.

## Sign in and verify

1. Confirm the purifier is already enrolled in the Winix phone app and that its account credentials work.
2. Open Home Assistant **Settings → Devices & services → Add integration → Winix**.
3. Enter the Winix account credentials directly in your local Home Assistant form. Keep passwords and account details out of Git, screenshots and shared logs. No credentials belong in this repository's YAML or example files.
4. Open the discovered purifier's device page. In the tested setup, Home Assistant exposed a fan entity, AQI, Filter Life and Air QValue sensors, plus a maximum-filter-life diagnostic sensor.
5. Add the fan, AQI and Filter Life entities to your dashboard or Overview Favorites. Reload the dashboard to confirm the choices persist.

According to the [upstream sensor documentation](https://github.com/iprak/winix/tree/v1.7.0#air-purifier), Winix AQI is a three-level category: `1` means good, `2` fair and `3` poor. It is not the US numeric AQI scale. Air QValue is a vendor reading whose precise interpretation is not established here; do not assume it is a particulate concentration. Sensor availability depends on the model.

Entity availability, reported state and dashboard persistence were verified on one C909. No physical power or speed-change test, internet-outage test, or long-term reliability test was performed. The integration loads with Home Assistant; it needs no separate Windows bridge or startup task.

## Login/session troubleshooting

The [upstream account guidance](https://github.com/iprak/winix/tree/v1.7.0#note) warns that signing into the Winix phone app and Home Assistant with the same account can invalidate the other session. If this occurs, use a separate Winix account for Home Assistant and share the purifier to it from the primary account using the app's device-sharing flow. Account creation, password changes and sharing remain actions you perform privately in Winix.

For an incorrect-credentials error, verify the account and password in Winix's own sign-in flow before changing Home Assistant configuration. Do not post raw configuration entries, authentication responses or diagnostics when requesting help.
