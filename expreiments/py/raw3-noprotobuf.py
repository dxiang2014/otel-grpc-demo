import logging
import time
from google.protobuf.json_format import MessageToJson
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.proto.metrics.v1.metrics_pb2 import MetricsData  # Import protobuf type

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Custom metric exporter with logging
class LoggingOTLPMetricExporter(OTLPMetricExporter):
    def export(self, metrics_data, **kwargs):
        if isinstance(metrics_data, MetricsData):  # Ensure it's a protobuf message
            serialized_data = MessageToJson(metrics_data)  # Convert to JSON
            logging.debug(f"Exporting metrics: {serialized_data}")
        else:
            logging.debug("Received non-protobuf metrics data")
        
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

# Allow time for metric export
time.sleep(5)
