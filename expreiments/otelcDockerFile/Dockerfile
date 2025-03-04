# Use a lightweight base image
FROM ubuntu:22.04

# Set working directory
WORKDIR /app

# Copy the otelcol-contrib binary from your local system
COPY otelcol-contrib /app/otelcol-contrib

# Copy the config file
COPY services/otel-collector-config.yaml /etc/otelcol-contrib/config.yaml

# Ensure the binary is executable
RUN chmod +x /app/otelcol-contrib

# Expose ports from your config (and extras from your Docker command)
EXPOSE 4317 4318 13133 1777 55679 9090 8889

# Set the entrypoint to run the collector with the config
ENTRYPOINT ["/app/otelcol-contrib", "--config", "/etc/otelcol-contrib/config.yaml"]
