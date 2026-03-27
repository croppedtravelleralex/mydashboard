#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
mkdir -p logs
export CLOUDFLARE_API_TOKEN="$(cat private/cloudflare_api_token)"
nohup python3 scripts/collector_trigger_server.py > logs/collector-trigger.out 2>&1 &
echo $! > logs/collector-trigger.pid
sleep 1
cat logs/collector-trigger.out
