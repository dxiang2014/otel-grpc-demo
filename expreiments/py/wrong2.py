import logging
import time
from google.protobuf.json_format import MessageToJson
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader, MetricExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Custom metric exporter with logging
class LoggingOTLPMetricExporter(OTLPMetricExporter):
    def export(self, metrics_data, **kwargs):
        # Serialize the metric data to JSON for logging
        serialized_data = MessageToJson(metrics_data.to_protobuf())  # Convert to Protobuf JSON
        logging.debug(f"Exporting metrics: {serialized_data}")
        return super().export(metrics_data, **kwargs)

# Setup OpenTelemetry metric provider
resource = Resource(attributes={SERVICE_NAME: "test-service"})
exporter = LoggingOTLPMetricExporter(endpoint="http://otel-collector:4318/v1/metrics")
reader = PeriodicExportingMetricReader(exporter)
provider = MeterProvider(resource=resource, metric_readers=[reader])
metrics.set_meter_provider(provider)

# Create and set gauge metric
meter = metrics.get_meter("test-meter")
gauge = meter.create_gauge("test_metric", description="A test metric", unit="1")
gauge.set(42)

# Wait for export to happen
time.sleep(5)
