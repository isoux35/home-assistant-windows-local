# Privacy and local configuration

This repository is a fresh, selected export. It contains no original Home Assistant database/auth files, account credentials, exported scheduled tasks, local device identifiers, network names, camera images, recordings or diagnostic logs. Example configuration uses explicit placeholders. Commit author metadata uses a generic project identity.

Runtime configuration belongs only in ignored local files:

- Root `.env`: local timezone/settings.
- `govee/config.json`: Bluetooth address and chosen sensor name.
- `govee/runtime/`: local scan results, readings, lock and logs.
- `wyze/.secrets.env`: account/API credentials, local passwords and camera addressing.
- `wyze/state/`: session tokens and generated configuration.
- Root `config/`: Home Assistant authentication, database and configuration.

The GitHub repository owner remains visible as part of GitHub's normal account identity. The scripts do not embed a Windows username, real name, email address, home network address or location from the original installation.

The anonymous MQTT example is intended only for loopback access on the same PC. Do not publish it to a LAN or the internet without replacing that configuration with an appropriate authenticated setup. Wyze host-networked listeners have different exposure characteristics; see its guide.

`.gitignore` helps prevent accidental additions, but does not remove secrets already tracked. Review `git diff --cached` and the full file list before every push, and check generated output before sharing logs/screenshots. Live recordings and device scan results may be sensitive even when they contain no password.
