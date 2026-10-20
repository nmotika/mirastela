// Meta pixel behind the cookie banner. Nothing loads and nothing is sent until the visitor accepts
// marketing cookies. Purchase and Lead are also sent server-side (Conversions API) with the same event id.
export const META_PIXEL_ID = '2027523501240767'; // dataset "Mirastela web" in Events Manager
export const GA_ID = 'G-4W6JYDV6GR'; // Google Analytics 4 measurement ID (G-...), loaded only after "accept all"
export const CONSENT_KEY = 'mirastela-consent'; // 'all' or 'necessary'

declare global { interface Window { fbq?: any; _fbq?: any; dataLayer?: unknown[]; gtag?: (...a: unknown[]) => void } }

export function consent(): string | null {
  try { return localStorage.getItem(CONSENT_KEY); } catch { return null; }
}
export function setConsent(v: 'all' | 'necessary') {
  try { localStorage.setItem(CONSENT_KEY, v); } catch { /* private mode: ask again next time */ }
  if (v === 'all') loadPixel();
}
const marketingOk = () => consent() === 'all';

// Where this visit came from (first page of the tab): referring site (host only), campaign tags and
// which ad network's click id was present (not the id itself). Kept for this tab only and stored with
// the lead, so every order can be attributed even without cookie consent.
try {
  if (!sessionStorage.getItem('mirastela-src')) {
    const q = new URLSearchParams(location.search);
    let ref = '';
    try { const h = document.referrer ? new URL(document.referrer).hostname : ''; ref = h === location.hostname ? '' : h; } catch { /* ignore */ }
    const src: Record<string, string> = { landing: location.pathname };
    if (ref) src.ref = ref;
    for (const k of ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term']) {
      const v = q.get(k); if (v) src[k.slice(4)] = v.slice(0, 100);
    }
    const click = ['fbclid', 'gclid', 'gbraid', 'wbraid', 'msclkid', 'ttclid', 'li_fat_id'].find((k) => q.has(k));
    if (click) src.click = click;
    sessionStorage.setItem('mirastela-src', JSON.stringify(src));
  }
} catch { /* ignore */ }
export function sourceInfo(): Record<string, string> | undefined {
  try { return JSON.parse(sessionStorage.getItem('mirastela-src') || 'null') ?? undefined; } catch { return undefined; }
}

// Keep the ad click id from the landing URL for this tab only; it is sent only after consent.
try {
  const id = new URLSearchParams(location.search).get('fbclid');
  if (id) sessionStorage.setItem('mirastela-fbclid', JSON.stringify({ id, t: Date.now() }));
} catch { /* ignore */ }

function loadGa() {
  if (!GA_ID || !marketingOk() || window.gtag) return;
  window.dataLayer = window.dataLayer || [];
  window.gtag = function () { window.dataLayer!.push(arguments); }; // gtag needs the arguments object
  // Consent Mode v2, basic: GA only runs after "accept all", which covers measurement but not ad personalisation.
  window.gtag('consent', 'default', { analytics_storage: 'granted', ad_storage: 'granted', ad_user_data: 'granted', ad_personalization: 'denied' });
  window.gtag('js', new Date());
  window.gtag('config', GA_ID);
  const s = document.createElement('script'); s.async = true; s.src = `https://www.googletagmanager.com/gtag/js?id=${GA_ID}`;
  document.head.appendChild(s);
}

/** Loads every tracker the visitor accepted (Meta pixel and Google Analytics). */
export function loadPixel() {
  loadGa();
  if (!META_PIXEL_ID || !marketingOk() || window.fbq) return;
  /* eslint-disable */
  const n: any = (window.fbq = function (...a: unknown[]) { n.callMethod ? n.callMethod(...a) : n.queue.push(a); });
  if (!window._fbq) window._fbq = n;
  n.push = n; n.loaded = true; n.version = '2.0'; n.queue = [];
  const s = document.createElement('script'); s.async = true; s.src = 'https://connect.facebook.net/en_US/fbevents.js';
  document.head.appendChild(s);
  /* eslint-enable */
  window.fbq('init', META_PIXEL_ID);
  window.fbq('track', 'PageView');
}

const GA_EVENT: Record<string, string> = { Lead: 'generate_lead', InitiateCheckout: 'begin_checkout', Purchase: 'purchase' };

/** One call per funnel event: Meta pixel (standard event) and its GA4 equivalent. */
export function fbTrack(event: string, params: Record<string, unknown> = {}, eventId?: string) {
  if (!marketingOk()) return;
  loadPixel();
  if (META_PIXEL_ID) window.fbq?.('track', event, params, eventId ? { eventID: eventId } : undefined);
  const ga = GA_EVENT[event];
  if (GA_ID && ga && window.gtag) {
    const p: Record<string, unknown> = {};
    if (params.value !== undefined) { p.value = params.value; p.currency = String(params.currency ?? 'EUR').toUpperCase(); }
    if (event === 'Purchase') {
      p.transaction_id = eventId;
      p.items = [{ item_name: params.content_name ?? 'report', price: params.value, quantity: 1 }];
    }
    window.gtag('event', ga, p);
  }
}

function cookie(name: string): string {
  const m = document.cookie.match(new RegExp(`(?:^|; )${name}=([^;]*)`));
  return m ? decodeURIComponent(m[1]) : '';
}

/** Identifiers the server needs for the Conversions API; empty unless marketing cookies were accepted. */
export function trackInfo() {
  if (!marketingOk()) return { consent: false };
  let fbc = cookie('_fbc');
  if (!fbc) {
    try {
      const c = JSON.parse(sessionStorage.getItem('mirastela-fbclid') ?? 'null');
      if (c) fbc = `fb.1.${c.t}.${c.id}`;
    } catch { /* ignore */ }
  }
  return { consent: true, fbp: cookie('_fbp'), fbc };
}
