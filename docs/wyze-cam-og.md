# Wyze Cam OG: experimental local video bridge

Tested camera: **Wyze Cam OG (`GW_GC1`), firmware 1.0.98**. Tested image: Wyze Bridge 4.5.0, revision `da56b956`, pinned by digest in `wyze/compose.yaml`.

The underlying work is [IDisposable/docker-wyze-bridge](https://github.com/IDisposable/docker-wyze-bridge) and its vendored [Gwell protocol implementation](https://github.com/wlatic/hacky-wyze-gwell). This project adds a setup example and an FFmpeg wrapper; it does not implement the camera protocol.

## Configure locally

1. Obtain your Wyze developer API ID/key through the [official developer API instructions](https://support.wyze.com/hc/en-us/articles/16129834216731-Creating-an-API-Key).
2. Confirm that email/password sign-in works. A Google-linked account may need a separate Wyze password through Wyze's own account flow. Never put your Google password into this configuration.
3. Copy `wyze/.secrets.env.example` to `wyze/.secrets.env` and edit it locally. All example values are placeholders. This ignored file contains credentials, local passwords, the camera API ID and camera LAN IP.
4. Use the full API identifier for `FILTER_MACS` and `GWELL_LAN_IPS`: the tested API returned `GW_GC1_` plus the device suffix, rather than only the physical MAC. Set a DHCP reservation in your own router if you want a stable camera IP.
5. Keep the example file's literal raw env-file syntax: do not wrap values in shell quotes. A current Docker Compose supporting `env_file: format: raw` is required.

Do not share the generated `state/` directory. It holds authentication/session data and generated stream configuration. There is no credential-entry GUI in this public project.

From Ubuntu, inside this repository's `wyze` directory:

```sh
chmod +x bin/ffmpeg
docker compose up -d
```

Do this once before enabling the Windows startup runner. View the bridge UI at [localhost:5080](http://localhost:5080) with username `localviewer` and your local bridge password. Find the actual stream path listed by the bridge; do not assume it matches the display name verbatim.

The image uses Linux host networking. Unlike the loopback-only MQTT publication, host-networked bridge listeners can be reachable through the host's interfaces depending on WSL/network/firewall behavior. Keep bridge/stream authentication enabled and do not forward these ports from your router. Same-host loopback RTSP was accepted without credentials in the tested bridge; do not assume those listeners are authenticated on every path.

## Add to Home Assistant

Add the **Generic Camera** integration. Set the stream source to:

```text
rtsp://127.0.0.1:8554/YOUR_ACTUAL_STREAM_PATH
```

In the tested same-WSL-host setup, username/password fields could be left blank for loopback. Use the stream credentials if your deployment requires them. Open the entity's live view and verify the real scene; a correct still image alone is insufficient. Add the camera entity to your dashboard or Favorites after confirming playback.

## Purple/pink browser video workaround

Our first stream decoded to a correct room image with CPU FFmpeg and snapshots, while Home Assistant's browser live player displayed a purple/pink corrupted view. The source was H.264 High profile, with a 15 fps hint despite approximately 20 fps arriving.

`bin/ffmpeg` intercepts only raw stdin → RTSP publishing and re-encodes as 1080p-compatible H.264 Constrained Baseline at 20 fps, no B frames, and regular keyframes. Other FFmpeg invocations pass through to `/usr/bin/ffmpeg`. No camera firmware is changed. This fixed the observed browser view but adds CPU use and another lossy encode. The input timing assumptions are specific to this tested OG stream; do not apply them blindly to other models or audio streams. Audio is disabled here.

This is a workaround, not a proven root-cause fix. Upstream [issue #157](https://github.com/IDisposable/docker-wyze-bridge/issues/157) describes related frame-rate/bitstream/browser problems on a **Window Cam**, a different model. Its proposed filter-only fix has not been tested on this OG setup.

To compare without the wrapper, remove the `PATH` override and the `./bin/ffmpeg` bind mount from a local copy of the Compose file and recreate only this bridge. Back up your local changes first.

## Offline limits

We confirmed direct video traffic to the camera's LAN address. During a separate test, only the bridge container's outbound connectivity was restricted: loopback and the camera LAN address stayed allowed, while internet access was denied. An already-running stream continued to decode. Restarting the Gwell sidecar under that restriction failed while requesting a new cloud camera token. Restoring connectivity and restarting recovered streaming.

The camera itself retained internet access throughout. This establishes neither camera operation with all internet removed nor reconnect after an outage. The tested bridge still depends on Wyze cloud for authentication/session setup. Cloud token caching and current upstream changes need separate investigation before making stronger claims.
