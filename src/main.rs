mod otel;

use std::error::Error;
use otel::metrics::MetricStore;
use tracing_subscriber::{EnvFilter, fmt, prelude::*};

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error + Send + Sync + 'static>> {
    tracing_subscriber::registry()
        .with(fmt::layer())
        .with(EnvFilter::from_default_env())
        .init();

    tracing::info!("Starting up");
    let otel_resources = otel::resources::new();
    MetricStore::init(otel_resources);

    for _ in 0..10 {
        tracing::info!("Logging metrics");

        MetricStore::get().log_port_rx_bytes(0, 10000);
        MetricStore::get().log_queue_watermark(3, 23456);

        tokio::time::sleep(std::time::Duration::from_secs(1)).await;
    }

    tracing::info!("Shutting down");
    MetricStore::uninit();

    Ok(())
}