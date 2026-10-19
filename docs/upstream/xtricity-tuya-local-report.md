# Xtricity compatibility report for Tuya Local

**Status: prepared; not submitted upstream.** On 2026-10-19, Tuya Local restricted issue and pull-request creation to repository collaborators, and its Discussions page was unavailable. Recheck the contribution policy and search for an existing report before submitting this draft when contributions reopen. No automatic submission is configured.

Target: [make-all/tuya-local](https://github.com/make-all/tuya-local), using the [Product details / existing configuration match template](https://github.com/make-all/tuya-local/blob/main/.github/ISSUE_TEMPLATE/product-id.yml).

The report below includes the shared Tuya product/model ID requested by upstream. It excludes private per-device IDs, local keys, account data, network addresses, raw diagnostics, screenshots and current device readings. See the [setup guide](../xtricity-smart-life.md) for the installation procedure and [privacy notes](../privacy.md) for handling local configuration.

## Proposed issue title

Report a match for existing Powerstrip: Xtricity Wi-Fi power bar

## Proposed issue body

### Product ID

`rM6YG2U2W0QF88YM`

This is the shared cloud product/model ID from the Tuya Local setup message, not the private device ID. A local productKey was not obtained because broadcast discovery did not succeed.

### Manufacturer / Brand

Xtricity

### Model

Wi-Fi Smart Power Bar; exact model/SKU and device firmware version were not recorded. The cloud product label was `Smart Power Strip-3WiFi`.

### Existing configuration match

`multi_timer_powerstrip` (Powerstrip), unchanged from Tuya Local **2026.9.2** / release **2026.9.2-rel**. Setup reported a **100% match** and automatically detected Tuya protocol **3.3**. Home Assistant Container **2026.10.2**, running in WSL2 Ubuntu 24.04 on Windows.

Reported datapoints, with runtime values omitted:

| DP | Type | Entity from the existing profile |
| --- | --- | --- |
| 1 | Boolean | Outlet 1 |
| 2 | Boolean | Outlet 2 |
| 3 | Boolean | Outlet 3 |
| 9 | Integer | Timer 1 |
| 10 | Integer | Timer 2 |
| 11 | Integer | Timer 3 |

Three switches and three timer entities were active. The optional fourth outlet/timer and unsupported features remained disabled. Smart Life also showed three switch controls. No separate USB switch was reported. The retail description originally supplied mentioned four outlets and three USB ports, but the physical socket-to-channel mapping was not independently established; this report concerns the three channels actually returned.

### Verification

- Smart Life cloud-assisted QR setup retrieved the connection information. Manual LAN addressing worked when broadcast discovery failed across a router/subnet boundary.
- A brief on/off test of channel 2 succeeded and its original state was restored. A direct local TCP connection from Home Assistant to the bar was confirmed.
- After restarting Home Assistant, the local connection and all three switch states returned, and the saved dashboard controls persisted.
- Timers were exposed but timer operation was not tested. Internet access remained enabled: this was not an outage test and does not establish that the bar stops contacting Tuya cloud.

Could this shared product ID and Xtricity brand be associated with the existing profile? No mapping changes were needed for this unit. Raw diagnostics, account data, device identifiers, local keys, network addresses and screenshots are omitted for privacy.
