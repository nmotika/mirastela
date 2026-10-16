import { wheelSvg } from './wheel';
import { mdToHtml } from './md';
import { fill } from '../i18n/fill';

interface Planet { id: string; lon: number; signIndex: number; deg: number; min: number; house?: number; retro: boolean }
interface Angle { lon: number; signIndex: number; deg: number; min: number }
interface Chart {
  timeKnown: boolean; planets: Planet[];
  houses: { cusps: number[] } | null;
  angles: { asc: Angle; mc: Angle } | null;
  aspects: { a: string; b: string; type: string; orb: number }[];
  city?: { name: string; country: string };
}
interface Item { product: 'natal' | 'partner' | 'forecast'; status: string; markdown: string; data: any; model: string }
interface Order { lang: string; name: string; chart: Chart; input: { date: string; time: string | null }; forecastYear: number; items: Item[] }

const cfg = JSON.parse(document.getElementById('report-data')!.textContent!);
const R = cfg.d.report, R2 = cfg.d.rep2, A = cfg.d.astro;
const htmlLang = document.documentElement.lang;
const $ = (id: string) => document.getElementById(id)!;
const params = new URLSearchParams(location.search);
const token = params.get('o') ?? '';
const GLYPH: Record<string, string> = {
  sun: '☉', moon: '☽', mercury: '☿', venus: '♀', mars: '♂', jupiter: '♃', saturn: '♄',
  uranus: '♅', neptune: '♆', pluto: '♇', node: '☊',
};
const ASPECT_GLYPH: Record<string, string> = { conjunction: '☌', opposition: '☍', trine: '△', square: '□', sextile: '⚹' };
const dl = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M12 4v11M7 10l5 5 5-5M5 20h14"/></svg>';
let active: string | null = params.get('t');
let rendered = '';
let heroDone = false;

function el<K extends keyof HTMLElementTagNameMap>(tag: K, cls = '', text = ''): HTMLElementTagNameMap[K] {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text) e.textContent = text;
  return e;
}
const pName = (id: string) => (id === 'asc' ? A.asc : id === 'mc' ? 'MC' : A.planets[id] ?? id);
const pos = (deg: number, min: number) => `${deg}°${String(min).padStart(2, '0')}′`;
const fmtDate = (iso: string, withYear = false) => {
  const [y, m, d] = iso.split('-').map(Number);
  return new Intl.DateTimeFormat(htmlLang, { day: 'numeric', month: 'long', ...(withYear ? { year: 'numeric' } : {}) })
    .format(new Date(Date.UTC(y, m - 1, d)));
};
const slug = (s: string, i: number) => `s${i}-${s.toLowerCase().normalize('NFD').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 40)}`;

function hero(o: Order) {
  if (heroDone) return;
  heroDone = true;
  const c = o.chart;
  $('rName').textContent = o.name || R.title;
  const regionNames = (() => { try { return new Intl.DisplayNames([htmlLang], { type: 'region' }); } catch { return null; } })();
  const place = c.city ? [c.city.name, regionNames?.of(c.city.country) ?? c.city.country].join(', ') : '';
  $('rBirth').textContent = [o.input?.date ? fmtDate(o.input.date, true) : '', o.input?.time ?? '', place].filter(Boolean).join(' · ');
  const wd = { planets: c.planets, asc: c.angles?.asc.lon ?? null, cusps: c.houses?.cusps ?? null, aspects: c.aspects.slice(0, 8) };
  $('rWheelM').innerHTML = wheelSvg(wd, { size: 300, label: R.tabs.natal, still: true });
  $('rWheelD').innerHTML = wheelSvg(wd, { size: 460, label: R.tabs.natal, still: true });
  const sun = c.planets[0], moon = c.planets[1];
  const big = [[A.planets.sun, A.signs[sun.signIndex]], [A.planets.moon, A.signs[moon.signIndex]]];
  if (c.angles) big.push([A.asc, A.signs[c.angles.asc.signIndex]]);
  $('rBig3').replaceChildren(...big.map(([l, v]) => { const d = el('div'); d.append(el('span', 'l', l), el('strong', '', v)); return d; }));
  $('rBig3').style.gridTemplateColumns = `repeat(${big.length}, minmax(0, 1fr))`;
}

/** Splits the model's Markdown into one section per '## ' heading. */
function sectionsFrom(md: string): { title: string; html: string }[] {
  const out: { title: string; html: string }[] = [];
  let cur: { title: string; lines: string[] } | null = null;
  for (const line of md.split(/\r?\n/)) {
    const h = /^#{1,2}\s+(.*)$/.exec(line.trim());
    if (h) { if (cur) out.push({ title: cur.title, html: mdToHtml(cur.lines.join('\n')) }); cur = { title: h[1].replace(/\*\*/g, ''), lines: [] }; continue; }
    (cur ??= { title: '', lines: [] }).lines.push(line);
  }
  if (cur) out.push({ title: cur.title, html: mdToHtml(cur.lines.join('\n')) });
  return out.filter((s) => s.title || s.html.trim());
}

function planetList(c: Chart): HTMLElement {
  const box = el('div');
  const rows: [string, string, string, string][] = c.planets.map((p) => [
    GLYPH[p.id] ?? '', `${pName(p.id)} ${A.signIn[p.signIndex]}`,
    p.house ? fill(R2.house, { n: p.house }) : '', `${pos(p.deg, p.min)}${p.retro ? ' R' : ''}`,
  ]);
  if (c.angles) {
    rows.push(['ASC', `${A.asc} ${A.signIn[c.angles.asc.signIndex]}`, '', pos(c.angles.asc.deg, c.angles.asc.min)]);
    rows.push(['MC', `MC ${A.signIn[c.angles.mc.signIndex]}`, '', pos(c.angles.mc.deg, c.angles.mc.min)]);
  }
  for (const [g, label, house, p] of rows) {
    const row = el('div', 'pl');
    const tag = g === 'ASC' || g === 'MC';
    const gs = el('span', tag ? 'tg' : 'g', tag ? g : `${g}\uFE0E`); gs.setAttribute('aria-hidden', 'true');
    const d = el('div');
    d.append(el('strong', '', [label, house].filter(Boolean).join(' · ')), el('span', 'ps', p));
    row.append(gs, d);
    box.append(row);
  }
  return box;
}

function aspectCards(list: { a: string; b: string; type: string; orb: number }[], who?: [string, string]): HTMLElement {
  const tag = (id: string, n?: string) => (n ? `${pName(id)} (${n})` : pName(id));
  const box = el('div', 'asps');
  for (const x of list) {
    const c = el('div', 'asp');
    c.append(el('strong', '', `${tag(x.a, who?.[0])} ${ASPECT_GLYPH[x.type] ?? ''} ${tag(x.b, who?.[1])}`),
      el('span', 'ao', `${R.aspects[x.type] ?? x.type} · ${x.orb.toFixed(1)}°`));
    box.append(c);
  }
  return box;
}

function dataSection(id: string, kicker: string, title: string, body: HTMLElement): HTMLElement {
  const s = el('section', 'rd');
  s.id = id;
  s.append(el('p', 'kick', kicker), el('h2', '', title), body);
  return s;
}

function panel(o: Order, it: Item): HTMLElement {
  const p = el('section', 'panel');
  p.id = `p-${it.product}`;
  p.setAttribute('role', 'tabpanel');
  const wrap = el('div', 'wrap');
  p.append(wrap);
  if (it.status === 'pending') {
    const box = el('div', 'pending');
    const row = el('p', 'pr'); const sp = el('span', 'spin'); sp.setAttribute('aria-hidden', 'true');
    row.append(sp, R.generating);
    box.append(row, el('p', '', R2.emailNote));
    wrap.append(el('div'), box);
    return p;
  }
  if (it.status === 'error') { wrap.append(el('div'), el('p', 'rerr', R.error)); return p; }

  const toc = el('nav', 'toc'); toc.setAttribute('aria-label', R2.toc);
  const main = el('div');
  sectionsFrom(it.markdown).forEach((s, i) => {
    const sec = el('section', 'rd');
    sec.id = slug(s.title || 'intro', i);
    if (s.title) sec.append(el('h2', '', s.title));
    const body = el('div'); body.innerHTML = s.html;
    sec.append(...Array.from(body.childNodes));
    main.append(sec);
    if (s.title) { const a = el('a', '', s.title); a.href = `#${sec.id}`; toc.append(a); }
  });

  const extra: [string, string, string, HTMLElement][] = [];
  if (it.product === 'natal') {
    extra.push([`d-planets-${it.product}`, R.dataTitle, R2.planetsTitle, planetList(o.chart)]);
    extra.push([`d-aspects-${it.product}`, R.aspectsTitle, R.aspectsTitle, aspectCards(o.chart.aspects.slice(0, 12))]);
  } else if (it.product === 'partner' && it.data?.partnerChart) {
    const pc: Chart = it.data.partnerChart;
    extra.push([`d-partner`, R.dataTitle, it.data.partner?.name || R.dataTitle, planetList(pc)]);
    extra.push([`d-syn`, R.synastryTitle, R.synastryTitle, aspectCards((it.data.synastry ?? []).slice(0, 15), [o.name || 'A', it.data.partner?.name || 'B'])]);
  } else if (it.product === 'forecast' && it.data?.transits) {
    const tr = it.data.transits;
    const tw = el('div', 'twrap');
    const t = el('table', 'ttable');
    const head = el('tr');
    [R.transitCols.transit, R.transitCols.period, R.transitCols.exact].forEach((h) => { const th = el('th', '', h); th.scope = 'col'; head.append(th); });
    const tb = el('tbody');
    for (const e of tr.events) {
      const r = el('tr');
      r.append(el('td', '', `${pName(e.transit)} ${ASPECT_GLYPH[e.type] ?? ''} ${pName(e.natal)}`),
        el('td', 'num', `${fmtDate(e.from)} – ${fmtDate(e.to)}`), el('td', 'num', fmtDate(e.exact)));
      tb.append(r);
    }
    t.append(el('thead'), tb); t.tHead!.append(head); tw.append(t);
    extra.push([`d-transits`, R.dataTitle, fill(R.transitsTitle, { year: tr.year }), tw]);
  }
  for (const [id, k, title, body] of extra) {
    main.append(dataSection(id, k, title, body));
    const a = el('a', '', title); a.href = `#${id}`; toc.append(a);
  }
  const pb = el('button', 'btn pdfb noprint'); pb.type = 'button'; pb.innerHTML = `${dl}${R.print}`;
  pb.addEventListener('click', () => window.print());
  toc.append(pb);

  const end = el('section', 'rend');
  const pb2 = el('button', 'btn noprint'); pb2.type = 'button'; pb2.innerHTML = `${dl}${R.print}`;
  pb2.addEventListener('click', () => window.print());
  end.append(pb2, el('p', '', R2.disclaimer));
  main.append(end);
  wrap.append(toc, main);
  return p;
}

function render(o: Order) {
  hero(o);
  const sig = JSON.stringify(o.items.map((i) => [i.product, i.status]));
  if (sig === rendered) return;
  rendered = sig;
  const tabs = $('rTabs'), panels = $('rPanels');
  tabs.replaceChildren(); panels.replaceChildren();
  if (!active || !o.items.some((i) => i.product === active)) active = o.items[0]?.product ?? null;
  for (const it of o.items) {
    const label = fill(R.tabs[it.product], { year: it.data?.transits?.year ?? o.forecastYear });
    const b = el('button', '', label);
    b.type = 'button';
    b.setAttribute('role', 'tab');
    b.setAttribute('aria-controls', `p-${it.product}`);
    b.setAttribute('aria-selected', String(it.product === active));
    b.addEventListener('click', () => {
      active = it.product;
      tabs.querySelectorAll('button').forEach((x) => x.setAttribute('aria-selected', String(x === b)));
      panels.querySelectorAll<HTMLElement>('.panel').forEach((x) => (x.hidden = x.id !== `p-${active}`));
    });
    tabs.append(b);
    const pnl = panel(o, it);
    pnl.hidden = it.product !== active;
    panels.append(pnl);
  }
  tabs.hidden = o.items.length < 2;
  $('rPrint').hidden = o.items.every((i) => i.status !== 'ready');
}

async function poll() {
  if (!token) { $('rMsg').textContent = R.notFound; return; }
  try {
    const res = await fetch(`/api/order/${encodeURIComponent(token)}`);
    if (res.status === 404) { $('rMsg').textContent = R.notFound; return; }
    if (!res.ok) throw new Error(String(res.status));
    const o: Order = await res.json();
    $('rMsg').textContent = '';
    render(o);
    if (o.items.some((i) => i.status === 'pending')) setTimeout(poll, 4000);
  } catch {
    $('rMsg').textContent = cfg.d.ui.error;
    setTimeout(poll, 8000);
  }
}
$('rPrint').addEventListener('click', () => window.print());
poll();
