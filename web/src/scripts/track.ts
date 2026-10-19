// Meta pixel behind the cookie banner. Nothing loads and nothing is sent until the visitor accepts
// marketing cookies. Purchase and Lead are also sent server-side (Conversions API) with the same event id.
export const META_PIXEL_ID = '';          // set when the dataset exists in Events Manager
export const CONSENT_KEY = 'mirastela-consent'; // 'all' or 'necessary'

declare global { interface Window { fbq?: any; _fbq?: any } }

export function consent(): string | null {
  try { return localStorage.getItem(CONSENT_KEY); } catch { return null; }
}
export function setConsent(v: 'all' | 'necessary') {
  try { localStorage.setItem(CONSENT_KEY, v); } catch { /* private mode: ask again next time */ }
  if (v === 'all') loadPixel();
}
const marketingOk = () => consent() === 'all';

// Keep the ad click id from the landing URL for this tab only; it is sent only after consent.
try {
  const id = new URLSearchParams(location.search).get('fbclid');
  if (id) sessionStorage.setItem('mirastela-fbclid', JSON.stringify({ id, t: Date.now() }));
} catch { /* ignore */ }

export function loadPixel() {
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

export function fbTrack(event: string, params: Record<string, unknown> = {}, eventId?: string) {
  if (!META_PIXEL_ID || !marketingOk()) return;
  loadPixel();
  window.fbq?.('track', event, params, eventId ? { eventID: eventId } : undefined);
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
