import logging
import time
from datetime import datetime
import requests
from opentelemetry.proto.metrics.v1.metrics_pb2 import (
    ResourceMetrics,
    ScopeMetrics,
    Metric,
    Gauge as OtelGauge,
    NumberDataPoint,
)
from opentelemetry.proto.resource.v1.resource_pb2 import Resource
from opentelemetry.proto.common.v1.common_pb2 import KeyValue, AnyValue
from opentelemetry.proto.metrics.v1.metrics_pb2 import InstrumentationScope  # <-- Added import

logging.basicConfig(level=logging.DEBUG)

# Custom timestamp (2025-03-03 12:00:00 UTC)
custom_timestamp_ns = int(datetime(2025, 3, 3, 12, 0, 0).timestamp() * 1_000_000_000)

# Simple Gauge Metric
metric = Metric(
    name="simple_test_metric",
    description="Simple test metric",
    unit="1",
    gauge=OtelGauge(data_points=[NumberDataPoint(as_int=42, time_unix_nano=custom_timestamp_ns)])
)

scope_metrics = ScopeMetrics(
    scope=InstrumentationScope(name="simple-meter"),
    metrics=[metric]
)

resource_metrics = ResourceMetrics(
    resource=Resource(
        attributes=[
            KeyValue(key="service.name", value=AnyValue(string_value="simple-service"))
        ]
    ),
    scope_metrics=[scope_metrics]
)

# Serialize to protobuf
payload = resource_metrics.SerializeToString()

# Set headers with explicit Content-Encoding
headers = {
    "Content-Type": "application/x-protobuf",
    "Content-Encoding": "identity"  # Ensure no compression is being applied
}

# Log payload details
logging.debug(f"Payload (bytes): {payload}")
logging.debug(f"Custom timestamp (ns): {custom_timestamp_ns}")
logging.debug(f"Converted timestamp: {datetime.utcfromtimestamp(custom_timestamp_ns * 1e-9)} UTC")

# Send to otel-collector
otel_endpoint = "http://otel-collector:4318/v1/metrics"  # Update if needed
try:
    response = requests.post(otel_endpoint, data=payload, headers=headers)
    logging.debug(f"Response: {response.status_code} {response.text}")
except requests.RequestException as e:
    logging.error(f"Failed to send metric: {e}")

time.sleep(5)  # Allow processing
