// Cloudflare Pages Function: forwards /api/* to the Python API behind the Cloudflare Tunnel.
// Env vars (Pages > Settings > Variables): API_ORIGIN, e.g. https://api-origin.mirastela.com
//                                          PROXY_SECRET, same value as MIRASTELA_PROXY_SECRET on the server
export async function onRequest({ request, env }) {
  const url = new URL(request.url);
  const target = env.API_ORIGIN.replace(/\/$/, '') + url.pathname + url.search;
  const headers = new Headers(request.headers);
  // Who is signed in through Cloudflare Access: the CF_Authorization cookie was already checked by
  // Access before this function runs, so its e-mail claim can be passed on. Never trust a client header.
  headers.delete('x-access-email');
  const jwt = (request.headers.get('cookie') || '').match(/(?:^|;\s*)CF_Authorization=([^;]+)/);
  if (jwt) {
    try {
      const b64 = jwt[1].split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
      const claims = JSON.parse(atob(b64 + '='.repeat((4 - (b64.length % 4)) % 4)));
      if (claims.email) headers.set('x-access-email', String(claims.email));
    } catch { /* no e-mail then */ }
  }
  headers.delete('cookie');
  headers.set('X-Proxy-Secret', env.PROXY_SECRET);
  headers.set('X-Forwarded-For', request.headers.get('CF-Connecting-IP') ?? '');
  const init = { method: request.method, headers, redirect: 'manual' };
  if (!['GET', 'HEAD'].includes(request.method)) init.body = await request.arrayBuffer();
  const res = await fetch(target, init);
  const out = new Response(res.body, res);
  out.headers.set('Cache-Control', 'no-store');
  return out;
}
