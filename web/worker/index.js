// Cloudflare Worker for mirastela.com: static Astro build (assets binding) plus the edge logic that
// used to live in Pages Functions:
//   1. www / workers.dev -> https://mirastela.com (301)
//   2. /  -> visitor's browser language (302); crawlers get the language list
//   3. /api/*  -> Python API behind the Cloudflare Tunnel (secret header)
//   4. daily horoscope pages: today's text written into the HTML at the edge
// Secrets (wrangler secret put / dashboard): API_ORIGIN, PROXY_SECRET
const HORO = /^\/(pl|hr|sl|ro|cs|hu|de|fr|it|es|en)\/(horoskop|horoscop|horoszkop|horoscope|oroscopo|horoscopo)\/(?:[a-z-]+\/)?$/;
const INTL = { pl: 'pl-PL', hr: 'hr-HR', sl: 'sl-SI', ro: 'ro-RO', cs: 'cs-CZ', hu: 'hu-HU', de: 'de-DE', fr: 'fr-FR', it: 'it-IT', es: 'es-ES', en: 'en-GB' };

function zagrebDay() {
  return new Intl.DateTimeFormat('en-CA', { timeZone: 'Europe/Zagreb', year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date());
}

async function daily(env, lang, ctx) {
  const day = zagrebDay();
  const key = new Request(`https://cache.mirastela.internal/daily/${lang}/${day}`);
  const cache = caches.default;
  const hit = await cache.match(key);
  if (hit) return hit.json();
  if (!env.API_ORIGIN) return null;
  // Never hold the page: if the API is slow (text still being generated), serve the page as is
  // and let the browser fill it in.
  const res = await fetch(`${env.API_ORIGIN}/api/daily?lang=${lang}&day=${day}`, {
    headers: { 'X-Proxy-Secret': env.PROXY_SECRET || '' },
    signal: AbortSignal.timeout(2500),
  });
  if (res.status !== 200) return null;
  const data = await res.json();
  ctx.waitUntil(cache.put(key, new Response(JSON.stringify(data), {
    headers: { 'Content-Type': 'application/json', 'Cache-Control': 'max-age=600' },
  })));
  return data;
}

const SUPPORTED = ['pl', 'hr', 'sl', 'ro', 'cs', 'hu', 'de', 'fr', 'it', 'es', 'en'];
const ALIAS = { sk: 'cs', bs: 'hr', sr: 'hr' };
function pickLang(header) {
  for (const part of header.split(',')) {
    const code = part.trim().split(';')[0].slice(0, 2).toLowerCase();
    const l = ALIAS[code] || code;
    if (SUPPORTED.includes(l)) return l;
  }
  return null;
}


const REDIRECTS = { '/hr/upitnik/': '/hr/', '/hr/upitnik': '/hr/' };
const SECURITY = {
  'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
  'X-Frame-Options': 'SAMEORIGIN',
  'X-Content-Type-Options': 'nosniff',
  'Referrer-Policy': 'strict-origin-when-cross-origin',
  'Permissions-Policy': 'camera=(), microphone=(), geolocation=(), payment=(self "https://checkout.stripe.com")',
  'Content-Security-Policy': "frame-ancestors 'self'; base-uri 'self'; object-src 'none'; upgrade-insecure-requests",
};

async function proxyApi(request, env) {
  const url = new URL(request.url);
  const target = env.API_ORIGIN.replace(/\/$/, '') + url.pathname + url.search;
  const headers = new Headers(request.headers);
  headers.delete('x-access-email');
  headers.delete('cookie');
  headers.set('X-Proxy-Secret', env.PROXY_SECRET);
  headers.set('X-Forwarded-For', request.headers.get('CF-Connecting-IP') ?? '');
  headers.set('X-Client-IP', request.headers.get('CF-Connecting-IP') ?? '');
  const init = { method: request.method, headers, redirect: 'manual' };
  if (!['GET', 'HEAD'].includes(request.method)) init.body = await request.arrayBuffer();
  const res = await fetch(target, init);
  const out = new Response(res.body, res);
  out.headers.set('Cache-Control', 'no-store');
  return out;
}

async function horoscope(page, env, lang, ctx) {
  if (!(page.headers.get('content-type') || '').includes('text/html')) return page;
  let data = null;
  try { data = await daily(env, lang, ctx); } catch { data = null; }
  if (!data) return page;

  const [y, mo, d] = data.day.split('-').map(Number);
  let label = new Intl.DateTimeFormat(INTL[m[1]], { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC' })
    .format(new Date(Date.UTC(y, mo - 1, d)));
  label = label.charAt(0).toUpperCase() + label.slice(1);
  let sign = null;

  return new HTMLRewriter()
    .on('[data-hdate]', { element(el) { el.setInnerContent(label); } })
    .on('article.hread', {
      element(el) {
        const i = Number(el.getAttribute('data-sign'));
        sign = data.signs?.[i] || null;
        if (sign) el.setAttribute('data-ssr', '1');
      },
    })
    .on('[data-h]', {
      element(el) {
        const k = el.getAttribute('data-h');
        if (sign && sign[k]) el.setInnerContent(sign[k]);
      },
    })
    .transform(page);
}

function secure(res) {
  const out = new Response(res.body, res);
  for (const [k, v] of Object.entries(SECURITY)) if (!out.headers.has(k)) out.headers.set(k, v);
  return out;
}

async function handle(request, env, ctx) {
  const url = new URL(request.url);
  if (url.hostname !== 'mirastela.com' && !url.hostname.endsWith('localhost') && url.hostname !== '127.0.0.1') {
    url.hostname = 'mirastela.com';
    url.port = '';
    url.protocol = 'https:';
    return Response.redirect(url.toString(), 301);
  }
  if (url.pathname.startsWith('/api/')) return proxyApi(request, env);
  if (REDIRECTS[url.pathname]) return Response.redirect(new URL(REDIRECTS[url.pathname] + url.search, url).toString(), 301);
  // Root: send visitors to their browser language; others (and crawlers) get the language list.
  if (url.pathname === '/' && request.method === 'GET') {
    const lang = pickLang(request.headers.get('accept-language') || '');
    if (lang) return new Response(null, { status: 302, headers: { Location: `/${lang}/${url.search}`, Vary: 'Accept-Language', 'Cache-Control': 'private, no-store' } });
  }
  const page = await env.ASSETS.fetch(request);
  const m = request.method === 'GET' && page.status === 200 && HORO.exec(url.pathname);
  return m ? horoscope(page, env, m[1], ctx) : page;
}

export default {
  async fetch(request, env, ctx) {
    return secure(await handle(request, env, ctx));
  },
};
