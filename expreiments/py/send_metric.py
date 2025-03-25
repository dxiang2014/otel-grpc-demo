import logging
import time
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

# Run indefinitely, sending a sample every second
while True:
    # Use current timestamp in nanoseconds
    current_timestamp_ns = int(time.time() * 1_000_000_000)

    # Create OTLP metric
    data_point = NumberDataPoint()
    data_point.as_int = 12  # Sample value
    data_point.time_unix_nano = current_timestamp_ns
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
    try:
        response = requests.post(
            "http://otel-collector:4318/v1/metrics",
            data=payload,
            headers=headers,
            timeout=5  # Add timeout to avoid hanging
        )
        logging.debug(
            f"Sent metric with timestamp: {current_timestamp_ns} "
            f"({time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(current_timestamp_ns / 1_000_000_000))} UTC)"
        )
        logging.debug(f"Response: {response.status_code} {response.text}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to send metric: {e}")

    time.sleep(1)  # Send every second