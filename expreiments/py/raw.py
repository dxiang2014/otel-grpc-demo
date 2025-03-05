import logging
import time
from datetime import datetime
import requests
from google.protobuf import message

# Raw bytes for a minimal OTLP Metrics payload
# ResourceMetrics: service.name="test-service"
# ScopeMetrics: scope.name="test-meter"
# Metric: name="test_metric", Gauge, value=42, time_unix_nano=1741003200000000000
payload = bytes.fromhex(
    "0a20"  # resource, len=32
    "0a1e"  # attributes, len=30
    "0a0c736572766963652e6e616d65"  # key="service.name"
    "120e"  # value, len=14
    "0a0c746573742d73657276696365"  # string_value="test-service"
    "1233"  # scope_metrics, len=51
    "0a0c"  # scope, len=12
    "0a0a746573742d6d65746572"  # name="test-meter"
    "1223"  # metrics, len=35
    "0a0b746573745f6d6574726963"  # name="test_metric"
    "2a14"  # gauge, len=20
    "0a12"  # data_points, len=18
    "19"    # as_int=42 (varint)
    "110080d1a82f492918"  # time_unix_nano=1741003200000000000
)

logging.basicConfig(level=logging.DEBUG)

custom_timestamp_ns = int(datetime(2025, 3, 3, 12, 0, 0).timestamp() * 1_000_000_000)
logging.debug(f"Payload (hex): {payload.hex()}")

headers = {"Content-Type": "application/x-protobuf"}
response = requests.post("http://otel-collector:4318/v1/metrics", data=payload, headers=headers)

logging.debug(f"Sent metric with timestamp: {custom_timestamp_ns} ({datetime.fromtimestamp(custom_timestamp_ns / 1_000_000_000)} UTC)")
logging.debug(f"Response: {response.status_code} {response.text}")

time.sleep(5)  # Allow processing