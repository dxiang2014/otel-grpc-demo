import logging
import time
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

logging.basicConfig(level=logging.DEBUG)

# Resource configuration
resource = Resource(attributes={SERVICE_NAME: "test-service"})
reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(endpoint="http://otel-collector:4318/v1/metrics")
)
provider = MeterProvider(resource=resource, metric_readers=[reader])
metrics.set_meter_provider(provider)

# Create a meter and a counter metric
meter = metrics.get_meter("test-meter")
counter = meter.create_counter("test_counter", description="A test counter", unit="1")

# Increment the counter (you can only increase a counter)
counter.add(42)

# Log the current timestamp to verify
logging.debug(f"Sent counter with timestamp: {time.time()}")

time.sleep(5)  # Allow export
