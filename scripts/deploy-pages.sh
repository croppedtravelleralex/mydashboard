#!/usr/bin/env bash
set -euo pipefail

PROJECT_NAME="alexstudio-web"
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
COLLECTOR_JSON="${ROOT_DIR}/collector/openai-usage.latest.json"
SAMPLE_JSON="${ROOT_DIR}/collector/openai-usage.latest.sample.json"
TARGET_JSON="${ROOT_DIR}/public/api/openai-usage.json"

cd "$ROOT_DIR"

if ! command -v wrangler >/dev/null 2>&1; then
  echo "ERROR: wrangler not found"
  exit 1
fi

if [ -z "${CLOUDFLARE_API_TOKEN:-}" ]; then
  echo "ERROR: CLOUDFLARE_API_TOKEN is not set"
  exit 1
fi

if [ -f "$COLLECTOR_JSON" ]; then
  cp "$COLLECTOR_JSON" "$TARGET_JSON"
  echo "[deploy] copied real collector JSON -> public/api/openai-usage.json"
elif [ -f "$SAMPLE_JSON" ]; then
  cp "$SAMPLE_JSON" "$TARGET_JSON"
  echo "[deploy] collector JSON missing, using sample JSON"
else
  echo "ERROR: no collector JSON available"
  exit 1
fi

wrangler pages deploy public --project-name "$PROJECT_NAME"
