import logging
import time
from datetime import datetime

logging.basicConfig(level=logging.DEBUG)

from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

resource = Resource(attributes={SERVICE_NAME: "test-service"})
reader = PeriodicExportingMetricReader(OTLPMetricExporter(endpoint="http://otel-collector:4318/v1/metrics"))
provider = MeterProvider(resource=resource, metric_readers=[reader])
metrics.set_meter_provider(provider)

meter = metrics.get_meter("test-meter")
gauge = meter.create_gauge("test_metric", description="A test metric", unit="1")

# Set the gauge value (timestamp will be set by the SDK)
gauge.set(42)

# Log the intended timestamp for reference (not sent to otel-collector)
custom_timestamp = int(datetime(2025, 3, 3, 12, 0, 0).timestamp() * 1_000_000_000)
logging.debug(f"Intended timestamp (not sent): {custom_timestamp} ({datetime.fromtimestamp(custom_timestamp / 1_000_000_000)} UTC)")

time.sleep(5)  # Allow export