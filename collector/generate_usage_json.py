#!/usr/bin/env python3
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Optional, List

TZ = timezone(timedelta(hours=8))
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'collector' / 'openai-usage.latest.json'
SNAPSHOT_DIR = ROOT / 'collector' / 'snapshots'
SAMPLE_SNAPSHOT = ROOT / 'collector' / 'sample_usage_snapshot.json'
SANITIZED_ACCOUNTS = ROOT / 'collector' / 'accounts_export.sanitized.json'
TRIGGER_STATE = ROOT / 'logs' / 'collector-trigger-state.json'
TRIGGER_RUNS = ROOT / 'logs' / 'collector-trigger-runs.json'
PREVIOUS_OUT = ROOT / 'public' / 'api' / 'openai-usage.json'


def now_local() -> datetime:
    return datetime.now(TZ)


def iso_now() -> str:
    return now_local().isoformat(timespec='seconds')


def ts_to_iso(ts: Optional[float]) -> Optional[str]:
    if ts is None:
        return None
    try:
        return datetime.fromtimestamp(float(ts), TZ).isoformat(timespec='seconds')
    except Exception:
        return None


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def load_sanitized_accounts() -> List[Dict[str, Any]]:
    if SANITIZED_ACCOUNTS.exists():
        try:
            return json.loads(SANITIZED_ACCOUNTS.read_text(encoding='utf-8'))
        except Exception:
            return []
    return []


def get_nested(d: Dict[str, Any], *keys: str) -> Any:
    cur: Any = d
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return None
        cur = cur[k]
    return cur


def to_float(value: Any) -> Optional[float]:
    try:
        if value is None:
            return None
        return float(value)
    except Exception:
        return None


def compute_status(remain: Optional[float]) -> str:
    if remain is None:
        return 'warning'
    if remain <= 15:
        return 'danger'
    if remain <= 40:
        return 'warning'
    return 'healthy'


def build_quota_from_snapshot(snapshot_payload: Dict[str, Any]) -> Dict[str, Any]:
    raw = snapshot_payload.get('data', snapshot_payload)
    primary_used = to_float(get_nested(raw, 'rate_limit', 'primary_window', 'used_percent'))
    primary_reset = to_float(get_nested(raw, 'rate_limit', 'primary_window', 'reset_at') or get_nested(raw, 'rate_limit', 'primary_window', 'resets_at'))
    secondary_used = to_float(get_nested(raw, 'rate_limit', 'secondary_window', 'used_percent'))
    secondary_reset = to_float(get_nested(raw, 'rate_limit', 'secondary_window', 'reset_at') or get_nested(raw, 'rate_limit', 'secondary_window', 'resets_at'))

    primary_remain = None if primary_used is None else max(0.0, 100.0 - primary_used)
    secondary_remain = None if secondary_used is None else max(0.0, 100.0 - secondary_used)

    return {
        'window_5h': {
            'remaining_percent': None if primary_remain is None else round(primary_remain, 1),
            'used_percent': None if primary_used is None else round(primary_used, 1),
            'resets_at': ts_to_iso(primary_reset),
            'status': compute_status(primary_remain),
        },
        'window_7d': {
            'remaining_percent': None if secondary_remain is None else round(secondary_remain, 1),
            'used_percent': None if secondary_used is None else round(secondary_used, 1),
            'resets_at': ts_to_iso(secondary_reset),
            'status': compute_status(secondary_remain),
        },
    }


def summarize_account_state(remain_5h: Optional[float], remain_7d: Optional[float]) -> str:
    if (remain_5h is not None and remain_5h <= 15) or (remain_7d is not None and remain_7d <= 15):
        return 'danger'
    if (remain_5h is not None and remain_5h <= 40) or (remain_7d is not None and remain_7d <= 40):
        return 'warning'
    return 'ok'


def infer_display_name(snapshot_path: Path, accounts_meta: List[Dict[str, Any]], idx: int) -> str:
    if idx < len(accounts_meta):
        current = accounts_meta[idx]
        return current.get('email') or current.get('account_id') or snapshot_path.stem
    return snapshot_path.stem


def build_account_from_snapshot(snapshot_path: Path, accounts_meta: List[Dict[str, Any]], idx: int) -> Dict[str, Any]:
    snapshot_payload = load_json(snapshot_path)
    quota = build_quota_from_snapshot(snapshot_payload)
    remain_5h = quota['window_5h']['remaining_percent']
    remain_7d = quota['window_7d']['remaining_percent']
    name = infer_display_name(snapshot_path, accounts_meta, idx)
    account_meta = accounts_meta[idx] if idx < len(accounts_meta) else {}
    return {
        'id': f'account-{idx+1:03d}',
        'name': name,
        'status': summarize_account_state(remain_5h, remain_7d),
        'captured_at': iso_now(),
        'workspace_id': account_meta.get('workspace_id'),
        'quota': quota,
        'collector': {
            'status': 'ok' if snapshot_payload.get('ok', True) else 'warning',
            'message': 'parsed from real usage snapshot',
        },
    }


def summarize_accounts(accounts):
    def avg(vals):
        vals = [v for v in vals if isinstance(v, (int, float))]
        return round(sum(vals) / len(vals), 1) if vals else None
    avg5 = avg([a['quota']['window_5h']['remaining_percent'] for a in accounts])
    avg7 = avg([a['quota']['window_7d']['remaining_percent'] for a in accounts])
    return {
        'account_count': len(accounts),
        'available_count': sum(1 for a in accounts if a['status'] in ('ok', 'warning')),
        'warning_count': sum(1 for a in accounts if a['status'] == 'warning'),
        'danger_count': sum(1 for a in accounts if a['status'] == 'danger'),
        'avg_5h_remaining_percent': avg5,
        'avg_7d_remaining_percent': avg7,
    }



def load_optional_json(path: Path, default):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except Exception:
            return default
    return default


def build_recent_runs():
    runs = load_optional_json(TRIGGER_RUNS, [])
    if isinstance(runs, list) and runs:
        return runs[:10]
    return [{'id': 'collector-run-bootstrap', 'status': 'success', 'finished_at': iso_now()}]


def compute_change_summary(summary):
    prev = load_optional_json(PREVIOUS_OUT, {})
    prev_summary = prev.get('summary') if isinstance(prev, dict) else {}
    if not isinstance(prev_summary, dict) or not prev_summary:
        return {'changed': True, 'reason': 'first_comparison'}
    keys = ['account_count', 'available_count', 'warning_count', 'danger_count', 'avg_5h_remaining_percent', 'avg_7d_remaining_percent']
    diffs = {}
    for key in keys:
        if prev_summary.get(key) != summary.get(key):
            diffs[key] = {'before': prev_summary.get(key), 'after': summary.get(key)}
    return {'changed': bool(diffs), 'diffs': diffs}

def collect_snapshot_files():
    files = []
    if SNAPSHOT_DIR.exists():
        files.extend(sorted(SNAPSHOT_DIR.glob('*.json')))
    if not files and SAMPLE_SNAPSHOT.exists():
        files = [SAMPLE_SNAPSHOT]
    return files


def main():
    snapshot_files = collect_snapshot_files()
    accounts_meta = load_sanitized_accounts()
    accounts = [build_account_from_snapshot(path, accounts_meta, idx) for idx, path in enumerate(snapshot_files)]
    now = iso_now()
    summary = summarize_accounts(accounts)
    payload = {
        'ok': True,
        'source': 'ubuntu-collector-real-snapshots',
        'generated_at': now,
        'summary': summary,
        'change_summary': compute_change_summary(summary),
        'trigger_state': load_optional_json(TRIGGER_STATE, {}),
        'accounts': accounts,
        'recent_runs': build_recent_runs(),
        'errors': []
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Wrote {OUT}')
    print(json.dumps(payload['summary'], ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
