from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

resource = Resource(attributes={SERVICE_NAME: "test-service"})
reader = PeriodicExportingMetricReader(OTLPMetricExporter(endpoint="http://otel-collector:4318"))
provider = MeterProvider(resource=resource, metric_readers=[reader])
metrics.set_meter_provider(provider)

meter = metrics.get_meter("test-meter")
gauge = meter.create_gauge("test_metric", description="A test metric", unit="1")
gauge.set(42)

import time
time.sleep(5)  # Allow export