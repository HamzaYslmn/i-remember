#!/usr/bin/env bash
set -euo pipefail

declare -a SERVICE_PIDS=()

wait_for_port() {
    local port="$1"
    printf 'Waiting for localhost:%s/status ' "$port"
    until curl -sf "http://localhost:${port}/status" >/dev/null 2>&1; do
        sleep 1
        printf '.'
    done
    echo " ready!"
}

start_service() {
    local name="$1" path="$2" port="$3"
    echo "Starting ${name} on port ${port} ..."
    (cd "$path" && uv run uvicorn xMain:app --host 0.0.0.0 --port "$port") &
    SERVICE_PIDS+=("$!")
    echo "${name} PID: $!"
    wait_for_port "$port"
}

start_nginx() {
    local port="$1"
    echo "Starting NGINX on port ${port} ..."
    nginx -g "daemon off;" &
    SERVICE_PIDS+=("$!")
    echo "NGINX PID: $!"
}

cleanup() {
    echo "Shutting down services ..."
    kill "${SERVICE_PIDS[@]}" 2>/dev/null || true
}
trap cleanup EXIT

start_service "BackEnd" "./BackEnd" 8001
start_nginx 8080

wait "${SERVICE_PIDS[@]}"