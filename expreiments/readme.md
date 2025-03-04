
# Set up influxdb

## 1. create the docker images
    docker pull mcr.microsoft.com/azurelinux/base/influxdb:2.7

REPOSITORY                                     TAG               IMAGE ID       CREATED         SIZE
my-otel-collector                              0.120.0           0029d73ca208  2 minutes ago   514MB
curlimages/curl                                latest            94e9e444bcba   2 weeks ago     41.7MB
mcr.microsoft.com/azurelinux/base/influxdb     2.7               a62c74c4ea47   3 weeks ago     421MB
otel-grpc-demo                                 latest            99125ba4a79d   4 months ago    20MB
otel/opentelemetry-collector-contrib           latest            85ac41c2db88   12 days ago     397MB
otel/opentelemetry-collector                   latest            fae9574bf0ec   4 months ago    143MB

## 2. Start otel-collector and influxDB on the same network

    docker network create monitoring
    docker run --network monitoring --name influxdb -p 8086:8086 a62c74c4ea47

    docker run --network monitoring --name otel-collector \
    -p 9090:9090 -p 8889:8889 -p 4317:4317 -p 4318:4318 \
    -v $(pwd)/services/otel-collector-config.yaml:/etc/otelcol-contrib/config.yaml \
    0029d73ca208

## 3. Set up user/password/token in influxDB
    docker exec -it influxdb /bin/bash
    influx setup
    influx auth list

    docker images


## 4. Set up the environment variables

    export INFLUX_TOKEN="9I3G2EyKnW4bEHwkV3Y7-dfubQD2VnXQ5x6PGMG47lQQsIAw8R0zf85-p15DOy1m-ZAIwOnODn3iwOeGuLcHqQ=="
    export INFLUX_ORG="pncm"
    export INFLUX_BUCKET="bucket1"
    export INFLUX_URL="http://localhost:8086"

## 5. Test the setup
    TIMESTAMP=$(date +%s)
    curl -XPOST "$INFLUX_URL/api/v2/write?org=$INFLUX_ORG&bucket=$INFLUX_BUCKET&precision=s"   --header "Authorization: Token $INFLUX_TOKEN"   --header "Content-Type: text/plain"   --data-binary "temperature,location=room1 value=223.5 $TIMESTAMP"

    TIMESTAMP=$(date +%s)
    echo "temperature,location=room1 value=23.5 $TIMESTAMP" | influx write \
    --org "$INFLUX_ORG" \
    --bucket "$INFLUX_BUCKET" \
    --precision s \
    --token "$INFLUX_TOKEN" \
    --host "$INFLUX_URL" \
    --format lp

    TIMESTAMP=$(date +%s)
    curl -XPOST "$INFLUX_URL/api/v2/write?org=$INFLUX_ORG&bucket=$INFLUX_BUCKET&precision=s" \
    --header "Authorization: Token $INFLUX_TOKEN" \
    --header "Content-Type: text/plain" \
    --data-binary "temperature,location=room1 value=123.5 $TIMESTAMP"

    curl -X POST http://localhost:8086/api/v2/query?org=pncm --data '{"query": "buckets()"}' --header "Authorization: Token $INFLUX_TOKEN" 
    curl -X POST http://localhost:8086/api/v2/query?org=pncm -d 'from(bucket: "bucket1") |> range(start: -1h)' --header "Authorization: Token $INFLUX_TOKEN"  --header "Content-Type: application/vnd.flux"

    curl -XPOST "http://localhost:8086/api/v2/query?org=pncm"  -H "Authorization: Token $INFLUX_TOKEN"  -d '{"query": "from(bucket:\"bucket1\") |> range(start: -10h)"}'

    curl -curl -X POST http://localhost:8086/api/v2/query?org=pncm  -H "Authorization: Token $INFLUX_TOKEN"   --data '{ "query": "from(bucket: \"bucket1\") |> range(start: -10h)"}'

##	6. Send metric to otel-collector
    docker run --rm --network monitoring -v $(pwd)/send_metric.py:/app/send_metric.py python:3.11 bash -c "pip install opentelemetry-proto==1.30.0 requests && python /app/send_metric.py"

//1.28 is more stable version, 1.30 is the latest version

    docker run --rm --network monitoring -v $(pwd)/send_metric.py:/app/send_metric.py python:3.11 bash -c "pip install opentelemetry-api==1.28.0 opentelemetry-sdk==1.28.0 opentelemetry-exporter-otlp-proto-http==1.28.0 opentelemetry-proto==1.28.0 requests  && python /app/send_metric.py"

##	7. Typical troubleshoot commands
    docker stats
    docker logs influxdb
    docker logs otel-collector
    docker inspect influxdb
    docker inspect otel-collector
    docker ps -a
    netstat -tulnp | grep 8889

