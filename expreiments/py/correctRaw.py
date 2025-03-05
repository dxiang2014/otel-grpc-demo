import logging
import time
from datetime import datetime
import requests

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Custom timestamp (2025-03-03 12:00:00 UTC)
custom_timestamp_ns = int(datetime(2025, 3, 3, 12, 0, 0).timestamp() * 1_000_000_000)

# Raw bytes for OTLP Metrics payload
payload = bytes.fromhex(
    "0a69"  # resource_metrics list, len=105
    "0a20"  # resource, len=32
    "0a1e"  # attributes, len=30
    "0a0c736572766963652e6e616d65"  # key="service.name"
    "120e"  # value, len=14
    "0a0c746573742d73657276696365"  # string_value="test-service"
    "1245"  # scope_metrics, len=69
    "0a0c"  # scope, len=12
    "0a0a746573742d6d65746572"  # name="test-meter"
    "1235"  # metrics, len=53
    "0a0b746573745f6d6574726963"  # name="test_metric"
    "120d"  # description, len=13
    "412074657374206d6574726963"  # "A test metric"
    "1a01"  # unit, len=1
    "31"    # unit="1"
    "2a14"  # gauge, len=20
    "0a12"  # data_points, len=18
    "19"    # as_int=42 (varint)
    "300929d1ccd42918"  # time_unix_nano=1741003200000000000
    "312a00000000000000"  # truncated start_time_unix_nano (ignored)
)

# Log the payload
logging.debug(f"Payload (hex): {payload.hex()}")

# Send to otel-collector
headers = {"Content-Type": "application/x-protobuf"}
response = requests.post("http://otel-collector:4318/v1/metrics", data=payload, headers=headers)

logging.debug(f"Sent metric with timestamp: {custom_timestamp_ns} ({datetime.fromtimestamp(custom_timestamp_ns / 1_000_000_000)} UTC)")
logging.debug(f"Response: {response.status_code} {response.text}")

time.sleep(5)  # Allow processing