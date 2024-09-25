use once_cell::sync::OnceCell;
use opentelemetry::{metrics::{Counter, Gauge, MetricsError}, KeyValue};
use opentelemetry_otlp::{ExportConfig, WithExportConfig};
use opentelemetry_sdk::{runtime, Resource};
use opentelemetry::global;

#[derive(Debug)]
pub struct MetricStore {
    meter_provider: opentelemetry_sdk::metrics::SdkMeterProvider,

    // Counters
    port_rx_bytes: Counter<u64>,
    queue_watermark: Gauge<u64>,
}

static METRIC_STORE: OnceCell<MetricStore> = OnceCell::new();

impl MetricStore {
    pub fn init(resource: Resource) {
        let metric_store = MetricStore::new(resource).unwrap();
        METRIC_STORE.set(metric_store).unwrap();
    }

    pub fn uninit() {
        tracing::info!("MetricStore shutting down");
        METRIC_STORE.get().unwrap().shutdown();
    }

    pub fn get() -> &'static MetricStore {
        METRIC_STORE.get().unwrap()
    }

    fn new(resource: Resource) -> Result<MetricStore, MetricsError> {
        let export_config = ExportConfig {
            endpoint: "http://localhost:4317".to_string(),
            // endpoint: "http://localhost:9090/api/v1/otlp/v1/metrics".to_string(),
            protocol: opentelemetry_otlp::Protocol::Grpc,
            ..ExportConfig::default()
        };

        let meter_provider = opentelemetry_otlp::new_pipeline()
            .metrics(runtime::Tokio)
            .with_exporter(
                opentelemetry_otlp::new_exporter()
                    .tonic()
                    .with_export_config(export_config),
            )
            .with_resource(resource)
            .build()?;

        global::set_meter_provider(meter_provider.clone());

        let meter = global::meter_with_version(
            env!("CARGO_PKG_NAME"),
            Some(env!("CARGO_PKG_VERSION")),
            Some(opentelemetry_semantic_conventions::SCHEMA_URL),
            None);

        let metric_store = MetricStore {
            meter_provider,

            port_rx_bytes: meter
                .u64_counter("port.rx_bytes")
                .init(),

            queue_watermark: meter
                .u64_gauge("queue.watermark")
                .init(),
        };

        Ok(metric_store)
    }

    fn shutdown(&self) {
        self.meter_provider.shutdown().unwrap();
    }

    pub fn log_port_rx_bytes(&self, id: u64, value: u64) {
        let labels = vec![KeyValue::new("port.id", id.to_string())];
        self.port_rx_bytes.add(value, &labels);
    }

    pub fn log_queue_watermark(&self, id: u64, value: u64) {
        let labels = vec![KeyValue::new("queue.id", id.to_string())];
        self.queue_watermark.record(value, &labels);
    }
}