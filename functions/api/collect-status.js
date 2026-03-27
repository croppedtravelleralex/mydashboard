export async function onRequestGet(context) {
  const { env, request } = context;
  const origin = request.headers.get('origin') || '';
  const allowedOrigin = env.DASHBOARD_ALLOWED_ORIGIN || 'https://www.alexstudio.top';
  if (origin && origin !== allowedOrigin) {
    return json({ ok: false, error: 'forbidden_origin' }, 403);
  }
  if (!env.COLLECT_TRIGGER_URL || !env.COLLECT_TRIGGER_TOKEN) {
    return json({ ok: false, error: 'trigger_not_configured' }, 500);
  }
  try {
    const resp = await fetch(joinUrl(env.COLLECT_TRIGGER_URL, '/status'), {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${env.COLLECT_TRIGGER_TOKEN}`,
      },
    });
    const data = await safeJson(resp);
    return json(data, resp.status);
  } catch (err) {
    return json({ ok: false, error: 'upstream_request_failed', detail: String(err) }, 502);
  }
}

function joinUrl(base, path) {
  return String(base).replace(/\/$/, '') + path;
}
function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      'content-type': 'application/json; charset=utf-8',
      'cache-control': 'no-store',
      'access-control-allow-origin': 'https://www.alexstudio.top',
    },
  });
}
async function safeJson(resp) {
  const text = await resp.text();
  try { return JSON.parse(text); } catch { return { ok: resp.ok, raw: text }; }
}
