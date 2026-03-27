#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

python3 collector/parse_accounts_export.py /root/.openclaw/media/inbound/accounts_export_full---ac46c07e-c14c-4a2a-983d-6ce0ebcb0705.txt >/tmp/dashboard-parse.out
python3 collector/fetch_usage_snapshots.py >/tmp/dashboard-fetch.out
python3 collector/generate_usage_json.py >/tmp/dashboard-generate.out
bash scripts/deploy-pages.sh >/tmp/dashboard-deploy.out

echo "[collector] parse done"
echo "[collector] fetch done"
echo "[collector] generate done"
echo "[collector] deploy done"
