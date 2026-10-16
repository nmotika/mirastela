// Cloudflare Pages Function: forwards /api/* to the Python API behind the Cloudflare Tunnel.
// Env vars (Pages > Settings > Variables): API_ORIGIN, e.g. https://api-origin.mirastela.com
//                                          PROXY_SECRET, same value as MIRASTELA_PROXY_SECRET on the server
export async function onRequest({ request, env }) {
  const url = new URL(request.url);
  const target = env.API_ORIGIN.replace(/\/$/, '') + url.pathname + url.search;
  const headers = new Headers(request.headers);
  headers.delete('x-access-email');
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
