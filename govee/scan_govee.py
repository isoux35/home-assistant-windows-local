"""Read nearby H5105 advertisements using Windows Bluetooth, without pairing."""
import argparse
import asyncio
import json
from pathlib import Path

from bleak import BleakScanner
from govee_ble import GoveeBluetoothDeviceData
from home_assistant_bluetooth import BluetoothServiceInfo


async def scan(seconds: int) -> None:
    decoders = {}
    found = {}
    advertisement_count = 0

    def received(device, advertisement):
        nonlocal advertisement_count
        advertisement_count += 1
        name = advertisement.local_name or device.name or ""
        if "H5105" not in name.upper():
            return
        decoder = decoders.setdefault(device.address, GoveeBluetoothDeviceData())
        info = BluetoothServiceInfo.from_advertisement(device, advertisement, "windows")
        update = decoder.update(info)
        readings = {
            key.key: value.native_value
            for key, value in update.entity_values.items()
            if value.native_value is not None
        }
        record = {"address": device.address, "name": name, "rssi": advertisement.rssi, "readings": readings}
        if found.get(device.address) != record:
            print(json.dumps(record), flush=True)
        found[device.address] = record

    print("Listening for Govee H5105 Bluetooth broadcasts...", flush=True)
    async with BleakScanner(detection_callback=received, scanning_mode="active"):
        await asyncio.sleep(seconds)
    result = {"total_advertisements": advertisement_count, "devices": list(found.values())}
    runtime = Path(__file__).with_name("runtime")
    runtime.mkdir(exist_ok=True)
    (runtime / "scan-result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seconds", type=int, default=30)
    asyncio.run(scan(parser.parse_args().seconds))
