import logging
import time
from datetime import datetime
import requests
from google.protobuf.timestamp_pb2 import Timestamp
from opentelemetry.proto.metrics.v1.metrics_pb2 import (
    ResourceMetrics,
    ScopeMetrics,
    Metric,
    Gauge as OtelGauge,
    NumberDataPoint,
)

logging.basicConfig(level=logging.DEBUG)

# Custom timestamp (2025-03-03 12:00:00 UTC)
custom_timestamp_ns = int(datetime(2025, 3, 3, 12, 0, 0).timestamp() * 1_000_000_000)

# Create OTLP metric
ts = Timestamp()
ts.FromNanoseconds(custom_timestamp_ns)

data_point = NumberDataPoint(
    value=42,
    time_unix_nano=custom_timestamp_ns
)

metric = Metric(
    name="test_metric",
    description="A test metric",
    unit="1",
    gauge=OtelGauge(data_points=[data_point])
)

scope_metrics = ScopeMetrics(
    scope={"name": "test-meter"},
    metrics=[metric]
)

resource_metrics = ResourceMetrics(
    resource={"attributes": [{"key": "service.name", "value": {"string_value": "test-service"}}]},
    scope_metrics=[scope_metrics]
)

# Serialize to protobuf
payload = resource_metrics.SerializeToString()

# Send to otel-collector
headers = {"Content-Type": "application/x-protobuf"}
response = requests.post("http://otel-collector:4318/v1/metrics", data=payload, headers=headers)

logging.debug(f"Sent metric with timestamp: {custom_timestamp_ns} ({datetime.fromtimestamp(custom_timestamp_ns / 1_000_000_000)} UTC)")
logging.debug(f"Response: {response.status_code} {response.text}")

time.sleep(5)  # Allow processing