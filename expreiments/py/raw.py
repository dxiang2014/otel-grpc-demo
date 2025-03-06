import logging
import time
from datetime import datetime
import requests
from google.protobuf import message

# Raw bytes for a minimal OTLP Metrics payload
# ResourceMetrics: service.name="test-service"
# ScopeMetrics: scope.name="test-meter"
# Metric: name="test_metric", Gauge, value=42, time_unix_nano=1741003200000000000
payload = bytes.fromhex("0a690a200a1e0a0c736572766963652e6e616d65120e0a0c746573742d7365727669636512450a0c0a0a746573742d6d6574657212350a0b746573745f6d6574726963120d412074657374206d65747269631a01312a140a1219300929d1ccd42918312a00000000000000")

logging.basicConfig(level=logging.DEBUG)

custom_timestamp_ns = int(datetime(2025, 3, 3, 12, 0, 0).timestamp() * 1_000_000_000)
logging.debug(f"Payload (hex): {payload.hex()}")

headers = {"Content-Type": "application/x-protobuf"}
response = requests.post("http://otel-collector:4318/v1/metrics", data=payload, headers=headers)

logging.debug(f"Sent metric with timestamp: {custom_timestamp_ns} ({datetime.fromtimestamp(custom_timestamp_ns / 1_000_000_000)} UTC)")
logging.debug(f"Response: {response.status_code} {response.text}")

time.sleep(5)  # Allow processing