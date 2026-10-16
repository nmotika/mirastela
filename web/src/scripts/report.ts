import { wheelSvg } from './wheel';
import { mdToHtml } from './md';
import { fill } from '../i18n/fill';

interface Planet { id: string; lon: number; signIndex: number; deg: number; min: number; house?: number; retro: boolean }
interface Chart {
  timeKnown: boolean; planets: Planet[];
  houses: { cusps: number[] } | null;
  angles: { asc: { lon: number; signIndex: number; deg: number; min: number }; mc: { lon: number; signIndex: number; deg: number; min: number } } | null;
  aspects: { a: string; b: string; type: string; orb: number }[];
}
interface Item { product: 'natal' | 'partner' | 'forecast'; status: string; markdown: string; data: any; model: string }
interface Order { lang: string; name: string; chart: Chart; forecastYear: number; items: Item[] }

const cfg = JSON.parse(document.getElementById('report-data')!.textContent!);
const R = cfg.d.report, A = cfg.d.astro;
const htmlLang = document.documentElement.lang;
const $ = (id: string) => document.getElementById(id)!;
const token = new URLSearchParams(location.search).get('o') ?? '';
const GLYPH: Record<string, string> = {
  sun: '☉', moon: '☽', mercury: '☿', venus: '♀', mars: '♂', jupiter: '♃', saturn: '♄',
  uranus: '♅', neptune: '♆', pluto: '♇', node: '☊', asc: 'AC', mc: 'MC',
};
let active: string | null = new URLSearchParams(location.search).get('t');
let rendered = '';

function el<K extends keyof HTMLElementTagNameMap>(tag: K, props: Record<string, string> = {}, ...kids: (Node | string)[]) {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(props)) k === 'class' ? (e.className = v) : e.setAttribute(k, v);
  e.append(...kids);
  return e;
}
const pName = (id: string) => (id === 'asc' ? A.asc : id === 'mc' ? 'MC' : A.planets[id] ?? id);
const glyph = (id: string) => el('span', { class: 'gl', 'aria-hidden': 'true' }, `${GLYPH[id] ?? ''}︎`);
const pos = (deg: number, min: number) => `${deg}°${String(min).padStart(2, '0')}′`;
const fmtDate = (iso: string, withYear = false) => {
  const [y, m, d] = iso.split('-').map(Number);
  return new Intl.DateTimeFormat(htmlLang, { day: 'numeric', month: 'long', ...(withYear ? { year: 'numeric' } : {}) })
    .format(new Date(Date.UTC(y, m - 1, d)));
};

function table(head: string[], rows: (Node | string)[][]) {
  return el('div', { class: 'tablewrap' }, el('table', {},
    el('thead', {}, el('tr', {}, ...head.map((h) => el('th', { scope: 'col' }, h)))),
    el('tbody', {}, ...rows.map((r) => el('tr', {}, ...r.map((c, i) => el('td', i === 2 ? { class: 'num' } : {}, c))))),
  ));
}

function planetTable(c: Chart) {
  const rows: (Node | string)[][] = c.planets.map((p) => [
    el('span', {}, glyph(p.id), pName(p.id)), A.signs[p.signIndex], `${pos(p.deg, p.min)}${p.retro ? ' R' : ''}`, p.house ? String(p.house) : '–',
  ]);
  if (c.angles) {
    for (const k of ['asc', 'mc'] as const) {
      const a = c.angles[k];
      rows.push([el('span', {}, glyph(k), pName(k)), A.signs[a.signIndex], pos(a.deg, a.min), '–']);
    }
  }
  return table([R.cols.point, R.cols.sign, R.cols.position, R.cols.house], rows);
}

function aspectList(list: { a: string; b: string; type: string; orb: number }[], who?: [string, string]) {
  const tag = (id: string, n?: string) => (n ? `${pName(id)} (${n})` : pName(id));
  return el('ul', {}, ...list.map((x) => el('li', {},
    `${tag(x.a, who?.[0])} · ${R.aspects[x.type] ?? x.type} · ${tag(x.b, who?.[1])} (${x.orb.toFixed(1)}°)`)));
}

function dataBlock(title: string, ...kids: Node[]) {
  return el('section', { class: 'dt' }, el('h2', {}, title), ...kids);
}

function wheelFor(c: Chart, label: string) {
  const box = el('div', { class: 'wheelbox' });
  box.innerHTML = wheelSvg({ planets: c.planets, asc: c.angles?.asc.lon ?? null, cusps: c.houses?.cusps ?? null, aspects: c.aspects.slice(0, 8) },
    { size: 320, label, still: true });
  return box;
}

function panel(o: Order, it: Item): HTMLElement {
  const p = el('section', { class: 'panel', role: 'tabpanel', id: `p-${it.product}` });
  if (it.status === 'pending') {
    p.append(el('div', { class: 'pending' }, el('span', { class: 'spin', 'aria-hidden': 'true' }), R.generating));
    return p;
  }
  if (it.status === 'error') {
    p.append(el('p', { class: 'err' }, R.error));
    return p;
  }
  if (it.product === 'natal') p.append(wheelFor(o.chart, R.tabs.natal));
  const doc = el('article', { class: 'doc' });
  doc.innerHTML = mdToHtml(it.markdown);
  p.append(doc);

  if (it.product === 'natal') {
    p.append(dataBlock(R.dataTitle, planetTable(o.chart)));
    p.append(dataBlock(R.aspectsTitle, aspectList(o.chart.aspects)));
  } else if (it.product === 'partner' && it.data?.partnerChart) {
    const pc: Chart = it.data.partnerChart;
    p.append(dataBlock(`${R.dataTitle}: ${it.data.partner?.name || ''}`.replace(/: $/, ''), planetTable(pc)));
    p.append(dataBlock(R.synastryTitle, aspectList(it.data.synastry ?? [], [o.name || 'A', it.data.partner?.name || 'B'])));
  } else if (it.product === 'forecast' && it.data?.transits) {
    const tr = it.data.transits;
    p.append(dataBlock(fill(R.transitsTitle, { year: tr.year }), table(
      [R.transitCols.transit, R.transitCols.period, R.transitCols.exact],
      tr.events.map((e: any) => [
        el('span', {}, glyph(e.transit), `${pName(e.transit)} · ${R.aspects[e.type] ?? e.type} · ${pName(e.natal)}`),
        `${fmtDate(e.from)} – ${fmtDate(e.to)}`, fmtDate(e.exact),
      ]),
    )));
  }
  return p;
}

function render(o: Order) {
  const sig = JSON.stringify(o.items.map((i) => [i.product, i.status]));
  if (sig === rendered) return;
  rendered = sig;
  $('rFor').textContent = o.name ? fill(R.forName, { name: o.name }) : '';
  const tabs = $('rTabs'), panels = $('rPanels');
  tabs.replaceChildren(); panels.replaceChildren();
  if (!active || !o.items.some((i) => i.product === active)) active = o.items[0]?.product ?? null;
  for (const it of o.items) {
    const label = fill(R.tabs[it.product], { year: it.data?.transits?.year ?? o.forecastYear });
    const b = el('button', { type: 'button', role: 'tab', 'aria-controls': `p-${it.product}`, 'aria-selected': String(it.product === active) }, label);
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
