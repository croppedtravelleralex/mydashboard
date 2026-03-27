#!/usr/bin/env python3
import json
import os
import subprocess
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOKEN_FILE = ROOT / 'private' / 'collect-trigger.token'
LOG_DIR = ROOT / 'logs'
STATE_FILE = LOG_DIR / 'collector-trigger-state.json'
RUN_SCRIPT = ROOT / 'scripts' / 'run-collector-once.sh'
HOST = os.environ.get('DASHBOARD_TRIGGER_HOST', '127.0.0.1')
PORT = int(os.environ.get('DASHBOARD_TRIGGER_PORT', '18765'))

LOG_DIR.mkdir(parents=True, exist_ok=True)
LOCK = threading.Lock()
STATE = {
    'running': False,
    'last_started_at': None,
    'last_finished_at': None,
    'last_status': 'idle',
    'last_exit_code': None,
    'last_error': None,
    'last_stdout_tail': '',
    'last_stderr_tail': '',
}


def now_iso():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec='seconds')


def load_token():
    return TOKEN_FILE.read_text(encoding='utf-8').strip()


def persist_state():
    STATE_FILE.write_text(json.dumps(STATE, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def run_collect():
    with LOCK:
        if STATE['running']:
            return False
        STATE['running'] = True
        STATE['last_started_at'] = now_iso()
        STATE['last_status'] = 'running'
        STATE['last_error'] = None
        persist_state()

    try:
        env = os.environ.copy()
        proc = subprocess.run(
            [str(RUN_SCRIPT)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            env=env,
            timeout=1800,
        )
        with LOCK:
            STATE['running'] = False
            STATE['last_finished_at'] = now_iso()
            STATE['last_exit_code'] = proc.returncode
            STATE['last_stdout_tail'] = (proc.stdout or '')[-4000:]
            STATE['last_stderr_tail'] = (proc.stderr or '')[-4000:]
            STATE['last_status'] = 'success' if proc.returncode == 0 else 'failed'
            if proc.returncode != 0:
                STATE['last_error'] = f'collector exited with code {proc.returncode}'
            persist_state()
    except Exception as e:
        with LOCK:
            STATE['running'] = False
            STATE['last_finished_at'] = now_iso()
            STATE['last_status'] = 'failed'
            STATE['last_error'] = str(e)
            STATE['last_stderr_tail'] = str(e)
            persist_state()
    return True


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def _send(self, code, payload):
        body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def _auth_ok(self):
        expected = load_token()
        header = self.headers.get('Authorization', '')
        alt = self.headers.get('X-Collect-Token', '')
        return header == f'Bearer {expected}' or alt == expected

    def do_GET(self):
        if self.path == '/health':
            self._send(200, {'ok': True, 'service': 'collector-trigger', 'time': now_iso()})
            return
        if self.path == '/status':
            self._send(200, {'ok': True, 'state': STATE})
            return
        self._send(404, {'ok': False, 'error': 'not_found'})

    def do_POST(self):
        if self.path != '/collect-now':
            self._send(404, {'ok': False, 'error': 'not_found'})
            return
        if not self._auth_ok():
            self._send(401, {'ok': False, 'error': 'unauthorized'})
            return
        with LOCK:
            if STATE['running']:
                self._send(409, {'ok': False, 'error': 'already_running', 'state': STATE})
                return
        thread = threading.Thread(target=run_collect, daemon=True)
        thread.start()
        self._send(202, {'ok': True, 'accepted': True, 'state': STATE})


def main():
    persist_state()
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f'collector-trigger listening on http://{HOST}:{PORT}', flush=True)
    server.serve_forever()


if __name__ == '__main__':
    main()
