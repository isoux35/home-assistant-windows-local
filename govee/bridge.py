"""Windows BLE -> local MQTT bridge for a Govee H5105.

Uses the same Govee advertisement decoder as Home Assistant. No cloud API,
pairing, GATT connections, or Bluetooth adapter passthrough is used.
"""
import argparse
import asyncio
from datetime import datetime, timezone
import json
import logging
from logging.handlers import RotatingFileHandler
import msvcrt
import re
from pathlib import Path
import threading
import time

from bleak import BleakScanner
from govee_ble import GoveeBluetoothDeviceData
from home_assistant_bluetooth import BluetoothServiceInfo
import paho.mqtt.client as mqtt

ROOT = Path(__file__).resolve().parent
def load_settings(path):
    settings = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    address = str(settings.get("address", "")).upper().replace("-", ":")
    if not re.fullmatch(r"(?:[0-9A-F]{2}:){5}[0-9A-F]{2}", address):
        raise ValueError("Set address to your sensor's Bluetooth MAC in config.json")
    if address == "AA:BB:CC:DD:EE:FF":
        raise ValueError("Replace the example Bluetooth address in config.json")
    host = settings.get("mqtt_host", "127.0.0.1")
    if host not in ("127.0.0.1", "localhost"):
        raise ValueError("This example uses a loopback-only MQTT broker")
    port = settings.get("mqtt_port", 1883)
    if isinstance(port, bool) or not isinstance(port, int) or not 1 <= port <= 65535:
        raise ValueError("mqtt_port must be an integer from 1 to 65535")
    return {"address": address, "name": str(settings.get("name", "Govee H5105")),
            "mqtt_host": host, "mqtt_port": port}


LOG = logging.getLogger("govee_local")


class GoveeBridge:
    def __init__(self, settings):
        self.address = settings["address"]
        self.device_id = "govee_h5105_" + self.address.replace(":", "").lower()
        self.base = f"govee_local/{self.device_id}"
        self.name = settings["name"]
        self.mqtt_host = settings["mqtt_host"]
        self.mqtt_port = settings["mqtt_port"]
        self.decoder = GoveeBluetoothDeviceData()
        self.connected = threading.Event()
        self.last_sample = None
        self.last_seen = 0.0
        self.last_published = 0.0
        self.last_logged = 0.0
        self.last_values = None
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=self.device_id, protocol=mqtt.MQTTv5)
        self.client.will_set(f"{self.base}/availability", "offline", qos=1, retain=True)
        self.client.reconnect_delay_set(min_delay=1, max_delay=60)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message

    def discovery(self):
        fields = {
            "temperature": ("Temperature", "temperature", "°C"),
            "humidity": ("Humidity", "humidity", "%"),
            "battery": ("Battery", "battery", "%"),
            "signal_strength": ("Signal strength", "signal_strength", "dBm"),
        }
        for key, (name, device_class, unit) in fields.items():
            payload = {
                "name": name,
                "unique_id": f"{self.device_id}_{key}",
                "state_topic": f"{self.base}/state",
                "value_template": "{{ value_json." + key + " }}",
                "unit_of_measurement": unit,
                "device_class": device_class,
                "state_class": "measurement",
                "expire_after": 180,
                "availability_topic": f"{self.base}/availability",
                "qos": 1,
                "device": {
                    "identifiers": [self.device_id],
                    "name": self.name,
                    "manufacturer": "Govee",
                    "model": "H5105",
                    "connections": [["bluetooth", self.address]],
                },
                "origin": {"name": "Windows Govee local bridge", "sw_version": "1.0.0"},
            }
            if key in ("battery", "signal_strength"):
                payload["entity_category"] = "diagnostic"
            if key == "signal_strength":
                payload["enabled_by_default"] = False
            self.client.publish(f"homeassistant/sensor/{self.device_id}/{key}/config", json.dumps(payload), qos=1, retain=True)

    def publish_current(self):
        if not self.connected.is_set():
            return
        sample = self.last_sample
        if sample is None or time.monotonic() - self.last_seen >= 180:
            self.client.publish(f"{self.base}/availability", "offline", qos=1, retain=True)
            return
        self.client.publish(f"{self.base}/state", json.dumps(sample), qos=1, retain=True)
        self.client.publish(f"{self.base}/availability", "online", qos=1, retain=True)
        self.last_published = time.monotonic()

    def on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code.is_failure:
            LOG.error("Local MQTT connection failed: %s", reason_code)
            return
        self.connected.set()
        client.subscribe("homeassistant/status", qos=1)
        self.discovery()
        self.publish_current()
        LOG.info("Connected to local MQTT broker")

    def on_disconnect(self, client, userdata, flags, reason_code, properties):
        self.connected.clear()
        LOG.info("Local MQTT disconnected; reconnect will be automatic")

    def on_message(self, client, userdata, message):
        if message.topic == "homeassistant/status" and message.payload == b"online":
            self.discovery()
            self.publish_current()

    def received(self, device, advertisement):
        if device.address.upper() != self.address:
            return
        try:
            info = BluetoothServiceInfo.from_advertisement(device, advertisement, "windows")
            update = self.decoder.update(info)
            values = {key.key: value.native_value for key, value in update.entity_values.items()}
            if not all(isinstance(values.get(key), (int, float)) for key in ("temperature", "humidity", "battery")):
                return
            if not (-40 <= values["temperature"] <= 100 and 0 <= values["humidity"] <= 100 and 0 <= values["battery"] <= 100):
                return
            current = {key: values[key] for key in ("temperature", "humidity", "battery")}
            current["signal_strength"] = values.get("signal_strength", advertisement.rssi)
            self.last_seen = time.monotonic()
            self.last_sample = current | {"last_seen": datetime.now(timezone.utc).isoformat()}
            relevant = tuple(current[key] for key in ("temperature", "humidity", "battery"))
            if relevant != self.last_values or self.last_seen - self.last_published >= 60:
                self.publish_current()
                self.last_values = relevant
                temporary = ROOT / "runtime" / "status.json.tmp"
                temporary.write_text(json.dumps(self.last_sample, indent=2), encoding="utf-8")
                temporary.replace(ROOT / "runtime" / "status.json")
            if self.last_seen - self.last_logged >= 60:
                LOG.info("H5105: %.1f C, %.1f%% humidity, %s%% battery, RSSI %s", current["temperature"], current["humidity"], current["battery"], current["signal_strength"])
                self.last_logged = self.last_seen
        except Exception:
            LOG.exception("Unable to decode H5105 advertisement")

    async def run(self, duration=None):
        self.client.connect_async(self.mqtt_host, self.mqtt_port, keepalive=30)
        self.client.loop_start()
        deadline = time.monotonic() + duration if duration else None
        try:
            while deadline is None or time.monotonic() < deadline:
                try:
                    async with BleakScanner(detection_callback=self.received, scanning_mode="active"):
                        LOG.info("Listening to H5105 broadcasts using Windows Bluetooth")
                        scan_started = time.monotonic()
                        while deadline is None or time.monotonic() < deadline:
                            await asyncio.sleep(5)
                            if time.monotonic() - max(self.last_seen, scan_started) >= 180:
                                LOG.warning("No H5105 broadcasts for three minutes; restarting the Bluetooth scanner")
                                break
                except Exception:
                    LOG.exception("Bluetooth scanner stopped; retrying in 10 seconds")
                    await asyncio.sleep(10)
        finally:
            if self.connected.is_set():
                self.client.publish(f"{self.base}/availability", "offline", qos=1, retain=True).wait_for_publish(timeout=3)
            self.client.disconnect()
            self.client.loop_stop()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "config.json")
    parser.add_argument("--duration", type=int, help="Optional run duration in seconds")
    args = parser.parse_args()
    try:
        settings = load_settings(args.config)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    runtime = ROOT / "runtime"
    runtime.mkdir(exist_ok=True)
    handler = RotatingFileHandler(runtime / "bridge.log", maxBytes=1_000_000, backupCount=2, encoding="utf-8")
    logging.basicConfig(level=logging.INFO, handlers=[handler], format="%(asctime)s %(levelname)s %(message)s")
    lock_path = runtime / "bridge.lock"
    lock = lock_path.open("a+b")
    if lock_path.stat().st_size == 0:
        lock.write(b"0")
        lock.flush()
    lock.seek(0)
    try:
        msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
    except OSError:
        LOG.info("Receiver already running; exiting duplicate instance")
        lock.close()
        return
    LOG.info("Starting local Govee H5105 receiver")
    try:
        asyncio.run(GoveeBridge(settings).run(args.duration))
    except KeyboardInterrupt:
        pass
    finally:
        lock.close()


if __name__ == "__main__":
    main()
