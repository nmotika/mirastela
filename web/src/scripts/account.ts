// "My reports": sign in with a one-time email link, then list orders, add-ons, subscription and own data.
import { captcha } from './captcha';

type Product = 'natal' | 'partner' | 'forecast' | 'child';
interface Order {
  token: string; created: string; lang: string; name: string; bundle: boolean; free: boolean;
  owned: { product: Product; status: string }[]; missing: Product[];
  sub: { status: string; cal: string | null; billing: string | null; unsub: string | null } | null;
}

const cfg = JSON.parse(document.getElementById('account-data')!.textContent!);
const lang: string = cfg.lang;
const A = cfg.A;
const KEY = 'mirastela-account';
const htmlLang = document.documentElement.lang;
const $ = <T extends HTMLElement = HTMLElement>(id: string) => document.getElementById(id) as T;
const fill = (s: string, v: Record<string, string>) => s.replace(/\{(\w+)\}/g, (_, k) => v[k] ?? '');

let memKey: string | null = null; // used when storage is blocked: signed in for this page view only
const getKey = () => { try { return localStorage.getItem(KEY) ?? memKey; } catch { return memKey; } };
const setKey = (k: string | null) => {
  memKey = k;
  try { k ? localStorage.setItem(KEY, k) : localStorage.removeItem(KEY); } catch { /* private mode */ }
};

async function post<T>(path: string, body: unknown): Promise<T> {
  const r = await fetch(path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
  if (!r.ok) throw new Error(String(r.status));
  return r.json();
}
function el<K extends keyof HTMLElementTagNameMap>(tag: K, cls = '', text = ''): HTMLElementTagNameMap[K] {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text) e.textContent = text;
  return e;
}
function link(text: string, href: string, cls = 'btn2', blank = false) {
  const a = el('a', cls, text); a.href = href;
  if (blank) { a.target = '_blank'; a.rel = 'noopener'; }
  return a;
}
function msg(text: string) { $('aMsg').textContent = text; $('aMsg').hidden = !text; }
const fmtDate = (iso: string) => {
  const [y, m, d] = iso.split('-').map(Number);
  return new Intl.DateTimeFormat(htmlLang, { day: 'numeric', month: 'long', year: 'numeric' }).format(new Date(Date.UTC(y, m - 1, d)));
};

/* ---------- signed out ---------- */
let cap: ReturnType<typeof captcha> | undefined;
function showLogin() {
  $('aMain').hidden = true;
  $('aLogin').hidden = false;
  cap ??= captcha($('aCap'), lang);
}
$('aForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const input = $<HTMLInputElement>('aEmail');
  const email = input.value.trim();
  const ok = /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email);
  input.setAttribute('aria-invalid', String(!ok));
  if (!ok) { input.focus(); return; }
  const btn = (e.currentTarget as HTMLFormElement).querySelector('button')!;
  btn.disabled = true;
  try {
    await post('/api/account/login', { email, lang, captcha: await cap?.token() });
    msg(A.sent);
  } catch { msg(A.error); }
  cap?.reset();
  btn.disabled = false;
});

/* ---------- signed in ---------- */
function orderCard(o: Order): HTMLElement {
  const P = A.products, card = el('section', 'acard');
  card.append(el('h2', 'sf', fill(A.chartOf, { name: o.name || '·' })), el('p', 'mu', fill(A.ordered, { date: fmtDate(o.created) })));
  const ul = el('ul');
  for (const it of o.owned) {
    const li = el('li');
    li.append(el('span', '', P[it.product] ?? it.product));
    if (it.status !== 'ready') li.append(el('span', 'mu', A.preparing));
    ul.append(li);
  }
  card.append(ul);
  const row = el('div', 'arow');
  row.append(link(A.open, `/${lang}/report/?o=${encodeURIComponent(o.token)}`, 'btn'));
  card.append(row);

  const start = (add?: string) => `/${lang}/start/?o=${encodeURIComponent(o.token)}${add ? `&add=${add}` : ''}`;
  if (o.missing.length) {
    card.append(el('h3', '', A.addTitle));
    const adds = el('div', 'arow');
    for (const p of o.missing) {
      if (p === 'partner' && o.bundle) adds.append(link(A.addPartnerFree, start()));
      else adds.append(link(o.free ? P[p] : `${P[p]} · ${cfg.prices[p]}`, start(p)));
    }
    card.append(adds);
  }

  card.append(el('h3', '', A.subTitle));
  const s = o.sub, subRow = el('div', 'arow');
  if (s && s.status === 'active') {
    card.append(el('p', '', A.subActive));
    if (s.cal) {
      const webcal = 'webcal://' + s.cal.split('://')[1];
      subRow.append(link(cfg.shop.calGoogle, 'https://calendar.google.com/calendar/render?cid=' + encodeURIComponent(webcal), 'btn2', true),
        link(cfg.shop.calApple, webcal));
    }
    if (s.billing) subRow.append(link(A.manage, s.billing));
    else if (s.unsub) subRow.append(link(A.cancel, s.unsub));
  } else {
    card.append(el('p', 'mu', A.subOff));
    subRow.append(link(o.free ? A.subStart : `${A.subStart} · ${cfg.prices.sub}`, start('sub')));
  }
  card.append(subRow);
  return card;
}

async function load(key: string) {
  try {
    const me = await post<{ email: string; orders: Order[] }>('/api/account/me', { key });
    $('aLogin').hidden = true;
    $('aMain').hidden = false;
    $('aWho').textContent = fill(A.signedAs, { email: me.email });
    const box = $('aOrders');
    box.replaceChildren(...me.orders.map(orderCard));
    if (!me.orders.length) {
      const empty = el('section', 'acard');
      empty.append(el('p', '', A.empty), link(A.startCta, `/${lang}/start/`, 'btn'));
      box.append(empty);
    }
  } catch (e) {
    if ((e as Error).message === '401') setKey(null);
    else msg(A.error);
    showLogin();
  }
}

$('aOut').addEventListener('click', async () => {
  const key = getKey();
  setKey(null);
  if (key) post('/api/account/logout', { key }).catch(() => {});
  msg('');
  showLogin();
});
$('aExport').addEventListener('click', async () => {
  const key = getKey();
  if (!key) return;
  try {
    const r = await fetch('/api/account/export', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ key }) });
    if (!r.ok) throw new Error(String(r.status));
    const url = URL.createObjectURL(await r.blob());
    const a = el('a'); a.href = url; a.download = 'mirastela-data.json'; document.body.append(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 5000);
  } catch { msg(A.error); }
});
$('aDel').addEventListener('click', () => { $('aDelBox').hidden = false; $('aDelOk').focus(); });
$('aDelOk').addEventListener('change', () => { $<HTMLButtonElement>('aDelGo').disabled = !$<HTMLInputElement>('aDelOk').checked; });
$('aDelGo').addEventListener('click', async () => {
  const key = getKey();
  if (!key) return;
  $<HTMLButtonElement>('aDelGo').disabled = true;
  try {
    await post('/api/account/delete', { key, confirm: true });
    setKey(null);
    $('aMain').hidden = true;
    msg(A.delDone);
  } catch { msg(A.error); $<HTMLButtonElement>('aDelGo').disabled = false; }
});

/* ---------- start ---------- */
(async () => {
  const t = new URLSearchParams(location.search).get('t');
  if (t) {
    history.replaceState(null, '', location.pathname);  // the link works once; keep it out of history
    try {
      const { key } = await post<{ key: string }>('/api/account/session', { t });
      setKey(key);
    } catch {
      if (!getKey()) msg(A.expired);  // an old link while already signed in: just show the account
    }
  }
  const key = getKey();
  if (key) await load(key); else showLogin();
})();
