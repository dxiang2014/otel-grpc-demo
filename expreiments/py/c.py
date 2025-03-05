import logging
import time
from datetime import datetime

logging.basicConfig(level=logging.DEBUG)

from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

# Define a custom timestamp in nanoseconds (e.g., 2025-03-03 12:00:00 UTC)
custom_timestamp = int(datetime(2025, 3, 3, 12, 0, 0).timestamp() * 1_000_000_000)

resource = Resource(attributes={SERVICE_NAME: "test-service"})
reader = PeriodicExportingMetricReader(OTLPMetricExporter(endpoint="http://otel-collector:4318/v1/metrics"))
provider = MeterProvider(resource=resource, metric_readers=[reader])
metrics.set_meter_provider(provider)

meter = metrics.get_meter("test-meter")

# Define a callback to provide the metric value with a custom timestamp
def observable_gauge_callback(options):
    return [metrics.Observation(value=42, timestamp=custom_timestamp)]

# Create an ObservableGauge
gauge = meter.create_observable_gauge(
    "test_metric",
    description="A test metric",
    unit="1",
    callbacks=[observable_gauge_callback]
)

# Log the timestamp for verification
logging.debug(f"Set observable gauge with timestamp: {custom_timestamp} ({datetime.fromtimestamp(custom_timestamp / 1_000_000_000)} UTC)")

time.sleep(5)  # Allow export