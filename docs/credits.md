# Credits and licenses

This project packages original glue scripts and setup notes around existing projects. It does not claim authorship of Bluetooth decoders, camera protocols, Home Assistant, FFmpeg, or the bridge image.

- [Home Assistant](https://github.com/home-assistant/core): automation platform and native Govee/TP-Link/MQTT/Generic Camera integrations; Apache-2.0.
- [iprak/winix](https://github.com/iprak/winix): community Winix cloud integration, tested at 1.7.0; MIT. Its account/session behavior and sensor meanings inform the C909 guide.
- [make-all/tuya-local](https://github.com/make-all/tuya-local): community Tuya LAN integration and existing `multi_timer_powerstrip` device profile, tested at 2026.9.2; MIT. The Xtricity setup uses its existing profile without modifying or claiming authorship of it.
- [TinyTuya](https://github.com/jasonacox/tinytuya): local Tuya protocol library used by Tuya Local; MIT. The cloud-assisted setup dependency is declared by Tuya Local's upstream manifest.
- [Bluetooth-Devices/govee-ble](https://github.com/Bluetooth-Devices/govee-ble): the Govee advertisement decoder imported by the receiver; Apache-2.0 with notices for incorporated upstream work.
- [Bleak](https://github.com/hbldh/bleak): Windows Bluetooth scanning; MIT.
- [Eclipse Paho MQTT Python](https://github.com/eclipse-paho/paho.mqtt.python): MQTT client; EPL-2.0 / EDL-1.0.
- [Eclipse Mosquitto](https://github.com/eclipse-mosquitto/mosquitto): local broker; EPL-2.0 / EDL-1.0.
- [IDisposable/docker-wyze-bridge](https://github.com/IDisposable/docker-wyze-bridge): referenced bridge image/source; AGPL-3.0. Derived from the wider docker-wyze-bridge community, including [mrlt8/docker-wyze-bridge](https://github.com/mrlt8/docker-wyze-bridge).
- [wlatic/hacky-wyze-gwell](https://github.com/wlatic/hacky-wyze-gwell): upstream experimental Gwell work used by the bridge. Consult that project for its current license and provenance.
- [go2rtc](https://github.com/AlexxIT/go2rtc) and [FFmpeg](https://ffmpeg.org/): media components in the upstream bridge image. FFmpeg licensing depends on build options; the referenced image supplies the binary and libx264 support.

Related H5105 work: [NHaag87/govee-api](https://github.com/NHaag87/govee-api), forked from [Heckie75/govee-h5075-thermo-hygrometer](https://github.com/Heckie75/govee-h5075-thermo-hygrometer). This project's receiver imports `govee-ble`; it does not copy those readers.

The repository does not vendor upstream source trees or distribute container/binary artifacts. Its MIT license covers its original scripts and notes only; each referenced dependency retains its own terms and notices. The Wyze FFmpeg wrapper is a new shell launcher and does not copy the bridge's Go implementation.
