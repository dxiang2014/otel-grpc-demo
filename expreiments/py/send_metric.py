import logging
import time
from datetime import datetime
import requests
from opentelemetry.proto.resource.v1.resource_pb2 import Resource
from opentelemetry.proto.common.v1.common_pb2 import KeyValue, AnyValue, InstrumentationScope
from opentelemetry.proto.metrics.v1.metrics_pb2 import (
    ResourceMetrics,
    ScopeMetrics,
    Metric,
    Gauge as OtelGauge,
    NumberDataPoint,
    MetricsData,
)

logging.basicConfig(level=logging.DEBUG)

# List of custom timestamps (2025-03-01 to 2025-03-06 12:00:00 UTC)
timestamps = [
    int(datetime(2025, 2, 7, 12, 0, 0).timestamp() * 1_000_000_000),
    int(datetime(2025, 2, 8, 12, 0, 0).timestamp() * 1_000_000_000),
    int(datetime(2025, 2, 9, 12, 0, 0).timestamp() * 1_000_000_000),
    int(datetime(2025, 2, 10, 12, 0, 0).timestamp() * 1_000_000_000),
    int(datetime(2025, 2, 11, 12, 0, 0).timestamp() * 1_000_000_000),
    int(datetime(2025, 2, 12, 12, 0, 0).timestamp() * 1_000_000_000),
]

for custom_timestamp_ns in timestamps:
    # Create OTLP metric
    data_point = NumberDataPoint()
    data_point.as_int = 12
    data_point.time_unix_nano = custom_timestamp_ns
    data_point.ClearField("start_time_unix_nano")  # Explicitly clear

    metric = Metric(
        name="test_metric",
        description="A test metric",
        unit="1",
        gauge=OtelGauge(data_points=[data_point])
    )

    scope_metrics = ScopeMetrics(
        scope=InstrumentationScope(name="test-meter"),
        metrics=[metric]
    )

    resource_metrics = ResourceMetrics(
        resource=Resource(
            attributes=[
                KeyValue(key="service.name", value=AnyValue(string_value="test-service"))
            ]
        ),
        scope_metrics=[scope_metrics]
    )

    # Wrap in MetricsData
    metrics_data = MetricsData(resource_metrics=[resource_metrics])

    # Serialize to protobuf
    payload = metrics_data.SerializeToString()

    # Log the payload for debugging
    logging.debug(f"Payload (hex): {payload.hex()}")

    # Send to otel-collector
    headers = {"Content-Type": "application/x-protobuf"}
    response = requests.post("http://otel-collector:4318/v1/metrics", data=payload, headers=headers)

    logging.debug(f"Sent metric with timestamp: {custom_timestamp_ns} ({datetime.fromtimestamp(custom_timestamp_ns / 1_000_000_000)} UTC)")
    logging.debug(f"Response: {response.status_code} {response.text}")

    time.sleep(2)  # Allow processing between sends

time.sleep(5)  # Final wait
