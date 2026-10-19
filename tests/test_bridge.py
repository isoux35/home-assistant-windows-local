"""Configuration and MQTT behavior tests; no radio, broker, or real device used."""
import json
from pathlib import Path
import sys
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "govee"))
import bridge


class ConfigTests(unittest.TestCase):
    def load(self, settings):
        with patch.object(bridge.Path, "read_text", return_value=json.dumps(settings)):
            return bridge.load_settings("config.json")

    def test_normalizes_address_without_cloud_credentials(self):
        result = self.load({"address": "02-00-00-00-00-ab"})
        self.assertEqual(result["address"], "02:00:00:00:00:AB")
        self.assertEqual(result["mqtt_host"], "127.0.0.1")
        self.assertEqual(result["mqtt_port"], 1883)

    def test_rejects_missing_invalid_and_example_addresses(self):
        for address in ("", "invalid", "AA:BB:CC:DD:EE:FF"):
            with self.subTest(address=address), self.assertRaises(ValueError):
                self.load({"address": address})

    def test_rejects_nonloopback_anonymous_mqtt(self):
        with self.assertRaises(ValueError):
            self.load({"address": "02:00:00:00:00:01", "mqtt_host": "0.0.0.0"})

    def test_rejects_invalid_ports(self):
        for port in (0, 65536, True, "1883"):
            with self.subTest(port=port), self.assertRaises(ValueError):
                self.load({"address": "02:00:00:00:00:01", "mqtt_port": port})


class DiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.patcher = patch.object(bridge.mqtt, "Client")
        self.client = self.patcher.start().return_value
        self.addCleanup(self.patcher.stop)
        self.receiver = bridge.GoveeBridge({
            "address": "02:00:00:00:00:01", "name": "Test sensor",
            "mqtt_host": "127.0.0.1", "mqtt_port": 1883,
        })

    def test_discovery_has_four_retained_stable_sensors(self):
        self.receiver.discovery()
        calls = self.client.publish.call_args_list
        self.assertEqual(len(calls), 4)
        payloads = [json.loads(call.args[1]) for call in calls]
        self.assertEqual(len({item["unique_id"] for item in payloads}), 4)
        self.assertTrue(all(call.kwargs == {"qos": 1, "retain": True} for call in calls))
        self.assertTrue(all(item["expire_after"] == 180 for item in payloads))
        self.assertEqual(payloads[-1]["enabled_by_default"], False)
        self.assertTrue(all(item["device"]["name"] == "Test sensor" for item in payloads))

    def test_no_sample_publishes_offline_instead_of_online(self):
        self.receiver.connected.set()
        self.receiver.publish_current()
        self.client.publish.assert_called_once_with(
            self.receiver.base + "/availability", "offline", qos=1, retain=True)

    def test_stale_sample_stays_offline(self):
        self.receiver.connected.set()
        self.receiver.last_sample = {"temperature": 0}
        self.receiver.last_seen = time.monotonic() - 181
        self.receiver.publish_current()
        self.assertEqual(self.client.publish.call_args.args[1], "offline")
        self.assertEqual(self.client.publish.call_count, 1)

    def test_fresh_sample_publishes_state_before_online(self):
        self.receiver.connected.set()
        self.receiver.last_sample = {"temperature": 0}
        self.receiver.last_seen = time.monotonic()
        self.receiver.publish_current()
        calls = self.client.publish.call_args_list
        self.assertEqual(calls[0].args[0], self.receiver.base + "/state")
        self.assertEqual(calls[1].args[1], "online")

    def test_home_assistant_birth_reannounces_discovery(self):
        message = type("Message", (), {"topic": "homeassistant/status", "payload": b"online"})()
        self.receiver.on_message(self.client, None, message)
        self.assertEqual(self.client.publish.call_count, 4)


if __name__ == "__main__":
    unittest.main()
