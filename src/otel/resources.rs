use opentelemetry_sdk::Resource;
use opentelemetry::KeyValue;

pub fn new() -> Resource {
    Resource::new(vec![
        KeyValue::new(
            opentelemetry_semantic_conventions::resource::DEVICE_ID,
            "r12f-dev",
        ),
        KeyValue::new(
            opentelemetry_semantic_conventions::resource::DEVICE_MANUFACTURER,
            "r12f",
        ),
        KeyValue::new(
            opentelemetry_semantic_conventions::resource::DEVICE_MODEL_NAME,
            "devbox",
        ),
        KeyValue::new(
            opentelemetry_semantic_conventions::resource::SERVICE_NAME,
            "otel-grpc-demo",
        ),
        KeyValue::new(
            opentelemetry_semantic_conventions::resource::SERVICE_INSTANCE_ID,
            "0",
        ),
        KeyValue::new(
            opentelemetry_semantic_conventions::resource::CONTAINER_IMAGE_NAME,
            "demo",
        ),
        KeyValue::new(
            opentelemetry_semantic_conventions::resource::CONTAINER_IMAGE_ID,
            "202411.0",
        ),
        KeyValue::new(
            opentelemetry_semantic_conventions::resource::HOST_IP,
            "1.2.3.4",
        ),
    ])
}