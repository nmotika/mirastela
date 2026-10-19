// Cloudflare Turnstile, shown only when Cloudflare is unsure (interaction-only). Strictly necessary
// security, so it does not wait for the cookie banner. Without a site key everything is a no-op.
import { TURNSTILE_SITEKEY } from '../i18n/config';

declare global { interface Window { turnstile?: any } }

let loading: Promise<void> | null = null;
function load(): Promise<void> {
  if (!loading) {
    loading = new Promise((ok, fail) => {
      const s = document.createElement('script');
      s.src = 'https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit';
      s.async = true; s.onload = () => ok(); s.onerror = () => fail(new Error('turnstile'));
      document.head.appendChild(s);
    });
  }
  return loading;
}

export interface Captcha { token(): Promise<string | undefined>; reset(): void }

/** Render a widget into box; token() waits (up to 15 s) for a fresh token. */
export function captcha(box: HTMLElement, lang: string): Captcha {
  if (!TURNSTILE_SITEKEY) return { token: async () => undefined, reset() {} };
  let current: string | undefined;
  let id: string | undefined;
  const ready = load().then(() => {
    id = window.turnstile.render(box, {
      sitekey: TURNSTILE_SITEKEY, appearance: 'interaction-only', language: lang, theme: 'dark',
      callback: (t: string) => { current = t; }, 'expired-callback': () => { current = undefined; },
    });
  }).catch(() => { /* blocked: the server still has rate limits; it answers 403 if it insists */ });
  return {
    async token() {
      await ready;
      for (let i = 0; i < 60 && !current && id !== undefined; i++) await new Promise((r) => setTimeout(r, 250));
      return current;
    },
    reset() { current = undefined; if (id !== undefined) window.turnstile?.reset(id); },
  };
}
