import logging
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider, Counter
from opentelemetry.sdk.metrics.export import MetricExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.metrics.export import MetricRecord

logging.basicConfig(level=logging.DEBUG)

# Custom timestamp (2025-03-03 12:00:00 UTC)
custom_timestamp_ns = int(datetime(2025, 3, 3, 12, 0, 0).timestamp() * 1_000_000_000)

# Define the resource and meter provider
resource = Resource(attributes={SERVICE_NAME: "test-service"})
meter_provider = MeterProvider(resource=resource)
metrics.set_meter_provider(meter_provider)

# Create the meter and counter metric
meter = metrics.get_meter("test-meter")
counter = meter.create_counter("test_counter", description="A test counter", unit="1")

# Set the custom timestamp for the counter increment
counter.add(42, timestamp=custom_timestamp_ns)

# Export function (to simulate exporting the metrics)
class CustomMetricExporter(MetricExporter):
    def export(self, metric_records):
        # Assuming metric_records is a list of MetricRecord
        for record in metric_records:
            for data_point in record.points:
                logging.debug(f"Exporting metric: {data_point}")
        return True  # Indicating successful export

# Create and configure the exporter
exporter = CustomMetricExporter()

# Wrap the counter into a MetricRecord
metric_record = MetricRecord(
    metric=counter,  # The counter itself
    points=[{
        "value": 42,
        "timestamp": custom_timestamp_ns
    }]
)

# Export the metric record
exporter.export(metric_records=[metric_record])

import time
time.sleep(5)  # Allow export to complete
