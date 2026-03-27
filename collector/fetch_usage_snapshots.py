#!/usr/bin/env python3
import json
import ssl
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNTIME = ROOT / 'collector' / 'private' / 'accounts_export.runtime.json'
OUTDIR = ROOT / 'collector' / 'snapshots'
URL = 'https://chatgpt.com/backend-api/wham/usage'
TIMEOUT = 30


def safe_name(text: str) -> str:
    return ''.join(c if c.isalnum() or c in ('-', '_', '.') else '-' for c in text)[:80]


def fetch_one(entry):
    workspace_id = (entry.get('workspace_id') or '').strip()
    access_token = (entry.get('access_token') or '').strip()
    name = (entry.get('email') or entry.get('account_id') or 'account').strip()
    headers = {
        'Authorization': f'Bearer {access_token}',
        'ChatGPT-Account-ID': workspace_id,
        'User-Agent': 'OpenClaw-Dashboard-Collector/1.0',
        'Accept': 'application/json,text/plain,*/*',
    }
    req = urllib.request.Request(URL, headers=headers, method='GET')
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT, context=ssl.create_default_context()) as resp:
            body = resp.read().decode('utf-8', errors='replace')
            status = getattr(resp, 'status', 200)
            ctype = resp.headers.get('content-type', '')
            data = json.loads(body)
            return {
                'ok': True,
                'status': status,
                'content_type': ctype,
                'data': data,
                'account': name,
                'workspace_id': workspace_id,
            }
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace') if hasattr(e, 'read') else ''
        return {
            'ok': False,
            'status': e.code,
            'error': 'http_error',
            'body_preview': body[:500],
            'account': name,
            'workspace_id': workspace_id,
        }
    except Exception as e:
        return {
            'ok': False,
            'status': None,
            'error': str(e),
            'account': name,
            'workspace_id': workspace_id,
        }


def main():
    entries = json.loads(RUNTIME.read_text(encoding='utf-8'))
    results = []
    OUTDIR.mkdir(parents=True, exist_ok=True)
    for idx, entry in enumerate(entries, start=1):
        result = fetch_one(entry)
        fname = f'{idx:03d}-{safe_name(entry.get("account_id") or entry.get("email") or "account")}.json'
        path = OUTDIR / fname
        path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        results.append({
            'file': str(path),
            'ok': result.get('ok'),
            'status': result.get('status'),
            'account': result.get('account'),
            'workspace_id': result.get('workspace_id'),
            'error': result.get('error'),
        })
    print(json.dumps(results, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
