#!/usr/bin/env python3
import json, sys
from pathlib import Path
FIELDS = {'account_id','issuer','group_name','status','workspace_id','chatgpt_account_id','exported_at','access_token','id_token','refresh_token'}
def mask(value: str, keep=6):
    if not value: return ''
    if len(value) <= keep * 2: return value[:keep] + '...'
    return value[:keep] + '...' + value[-keep:]

def parse_blocks(text: str):
    blocks=[]; current=None
    for raw in text.splitlines():
        line=raw.strip()
        if not line: continue
        if line.startswith('[') and '] ' in line:
            if current: blocks.append(current)
            current={'label': line}
            try:
                current['email'] = line.split('] ', 1)[1].strip()
            except Exception:
                pass
            continue
        if current is None: continue
        if '=' in line:
            k,v=line.split('=',1)
            if k in FIELDS: current[k]=v
        elif '@' in line and 'email' not in current:
            current['email']=line
    if current: blocks.append(current)
    return blocks

def sanitize(block):
    return {
        'email': block.get('email'),
        'account_id': block.get('account_id'),
        'issuer': block.get('issuer'),
        'group_name': block.get('group_name'),
        'status': block.get('status'),
        'workspace_id': block.get('workspace_id'),
        'chatgpt_account_id': block.get('chatgpt_account_id'),
        'exported_at': block.get('exported_at'),
        'token_preview': {
            'access_token': mask(block.get('access_token','')),
            'id_token': mask(block.get('id_token','')),
            'refresh_token': mask(block.get('refresh_token','')),
        }
    }

def runtime_entry(block):
    return {
        'email': block.get('email'),
        'account_id': block.get('account_id'),
        'workspace_id': block.get('workspace_id'),
        'issuer': block.get('issuer'),
        'status': block.get('status'),
        'group_name': block.get('group_name'),
        'chatgpt_account_id': block.get('chatgpt_account_id'),
        'exported_at': block.get('exported_at'),
        'access_token': block.get('access_token'),
        'id_token': block.get('id_token'),
        'refresh_token': block.get('refresh_token'),
    }

def main():
    src=Path(sys.argv[1])
    text=src.read_text(encoding='utf-8')
    blocks=parse_blocks(text)
    root=Path(__file__).resolve().parent
    sanitized_path=root/'accounts_export.sanitized.json'
    runtime_path=root/'private'/'accounts_export.runtime.json'
    sanitized_path.write_text(json.dumps([sanitize(b) for b in blocks], ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    runtime_path.write_text(json.dumps([runtime_entry(b) for b in blocks], ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(f'parsed_accounts={len(blocks)}')
    print(f'sanitized={sanitized_path}')
    print(f'runtime={runtime_path}')
if __name__=='__main__': main()
