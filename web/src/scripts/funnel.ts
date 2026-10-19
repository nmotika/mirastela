import { wheelSvg } from './wheel';
import { CUSP } from './cusp';
import { fill, huArticle } from '../i18n/fill';
import { SIGN_GLYPHS } from './zodiac';
import { fbTrack, trackInfo } from './track';
import { captcha, type Captcha } from './captcha';

type Step = 'date' | 'time' | 'place' | 'name' | 'focus' | 'status' | 'calc' | 'email' | 'offer' | 'upsell' | 'pdata' | 'kid' | 'sub' | 'done';
const STEPS: Step[] = ['date', 'time', 'place', 'name', 'focus', 'status', 'calc', 'email', 'offer', 'upsell', 'pdata', 'kid', 'sub', 'done'];
const QUIZ_STEPS = 6;
const BARE: Step[] = ['upsell', 'pdata', 'kid', 'sub'];
const NEEDS_TOKEN: Step[] = ['upsell', 'pdata', 'kid', 'sub', 'done'];

interface City { id: number; name: string; country: string; countryName: string; tz: string }
interface Planet { id: string; lon: number; sign: string; signIndex: number; deg: number; min: number; house?: number; retro: boolean; cusp?: number | null }
interface Chart {
  timeKnown: boolean;
  planets: Planet[];
  houses: { cusps: number[] } | null;
  angles: { asc: { lon: number; signIndex: number; deg: number; min: number; cusp?: number | null } } | null;
  aspects: { a: string; b: string; type: string }[];
}
interface State {
  date?: string; time?: string | null; city?: City; name?: string;
  focus: string[]; status?: string; email?: string; chart?: Chart; coupon?: string; token?: string;
  sub?: string; cal?: string; plan?: 'natal' | 'bundle'; pMode?: 'partner' | 'child';
  up?: 'partner' | 'forecast'; // add-on chosen on the account page
  disc?: { code: string; pct: number }; // discount code (not free): lower prices on one-time purchases
}

const data = JSON.parse(document.getElementById('funnel-data')!.textContent!);
const lang: string = data.lang;
const D = data.d;
const KEY = 'mirastela-funnel';
const htmlLang = document.documentElement.lang;
const regionNames = (() => { try { return new Intl.DisplayNames([htmlLang], { type: 'region' }); } catch { return null; } })();
const countryOf = (c: City) => regionNames?.of(c.country) ?? c.countryName;
const pos = (deg: number, min: number) => `${deg}°${String(min).padStart(2, '0')}′`;

const $ = <T extends HTMLElement = HTMLElement>(id: string) => document.getElementById(id) as T;
const sections = Object.fromEntries(
  STEPS.map((s) => [s, document.querySelector<HTMLElement>(`[data-step="${s}"]`)!]),
) as Record<Step, HTMLElement>;

function load(): State {
  try {
    const raw = sessionStorage.getItem(KEY);
    if (raw) return JSON.parse(raw);
  } catch { /* storage blocked */ }
  return { focus: [] };
}
function save() {
  try { sessionStorage.setItem(KEY, JSON.stringify(state)); } catch { /* ignore */ }
}
const state: State = load();
let current: Step = 'date';

async function api<T>(path: string, body?: unknown): Promise<T> {
  const res = await fetch(path, body === undefined ? undefined : {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`${res.status}`);
  return res.json();
}
function el<K extends keyof HTMLElementTagNameMap>(tag: K, cls = '', text = ''): HTMLElementTagNameMap[K] {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text) e.textContent = text;
  return e;
}

/* ---------- navigation ---------- */
function show(step: Step, push = true) {
  current = step;
  syncWaivers();
  STEPS.forEach((s) => (sections[s].hidden = s !== step));
  const i = STEPS.indexOf(step);
  const inQuiz = i < QUIZ_STEPS;
  const head = $('fhead');
  head.classList.toggle('center', step === 'calc');
  head.classList.toggle('bare', BARE.includes(step));
  $('back').hidden = !inQuiz;
  $('prog').hidden = !inQuiz;
  $('brand').hidden = inQuiz;
  $('funnel').classList.toggle('wide', step === 'offer');
  if (inQuiz) {
    $('progLabel').textContent = fill(D.ui.stepOf, { n: i + 1, t: QUIZ_STEPS });
    $('progBar').style.width = `${((i + 1) / QUIZ_STEPS) * 100}%`;
  }
  if (push) history.pushState({ step }, '', `#${step}`);
  window.scrollTo(0, 0);
  const h = sections[step].querySelector<HTMLElement>('h1');
  h?.setAttribute('tabindex', '-1');
  if (push) h?.focus({ preventScroll: true });
  const hooks: Partial<Record<Step, () => void>> = {
    date: () => syncDate(), time: () => syncTime(), name: renderName, focus: renderFocus,
    // Coming back with a status already picked: offer Continue, not only a re-tap of the option.
    status: () => { $('statusDock').hidden = !state.status; },
    calc: runCalc, email: renderEmail, offer: renderOffer, upsell: renderUpsell, pdata: renderPdata, kid: renderKid,
    sub: renderSub, done: renderDone,
  };
  hooks[step]?.();
}
function go(offset: number) {
  show(STEPS[STEPS.indexOf(current) + offset]);
}
window.addEventListener('popstate', (e) => {
  const step = (e.state?.step as Step) ?? 'date';
  // Never re-enter the calculation by going back; skip to the step before it.
  show(step === 'calc' ? 'status' : step, false);
});
$('back').addEventListener('click', () => history.back());
document.querySelectorAll<HTMLButtonElement>('[data-next]').forEach((b) => b.addEventListener('click', () => {
  commitWheels();
  if (current === 'name' && !validName()) return;
  go(1);
}));

/* ---------- wheel picker ---------- */
interface Wheel { set(v: number, smooth?: boolean): void; value(): number; layout(): void; commit(): void }
const allWheels: Wheel[] = [];
/** Takes each visible wheel's position as its value, so a tap on Next while a wheel is still
 *  gliding (or before the scroll debounce fired) never keeps the old value. */
function commitWheels() { allWheels.forEach((w) => w.commit()); }
function wheel(box: HTMLElement, onChange: (v: number) => void): Wheel {
  const items = [...box.querySelectorAll<HTMLButtonElement>('button')];
  let idx = 0, timer = 0;
  const step = () => items[0].offsetHeight || 48;
  // Mouse and keyboard (desktop): a plain dropdown is quicker than dragging a wheel. Same values,
  // same API; the wheel is hidden by CSS under the same media query.
  let sel: HTMLSelectElement | null = null;
  if (matchMedia('(hover: hover) and (pointer: fine)').matches) {
    sel = document.createElement('select');
    sel.className = 'inp wsel';
    sel.setAttribute('aria-label', box.getAttribute('aria-label') || '');
    items.forEach((b) => sel!.add(new Option(b.textContent!, b.dataset.v)));
    box.after(sel);
    box.removeAttribute('tabindex');
    sel.addEventListener('change', () => pick(sel!.selectedIndex));
  }
  const mark = (i: number) => {
    items.forEach((b, j) => b.setAttribute('aria-selected', String(j === i)));
    if (sel) sel.selectedIndex = i;
  };
  const clamp = (i: number) => Math.max(0, Math.min(items.length - 1, i));
  function pick(i: number, smooth = false, notify = true) {
    idx = clamp(i);
    mark(idx);
    box.scrollTo({ top: idx * step(), behavior: smooth ? 'smooth' : 'auto' });
    if (notify) onChange(+items[idx].dataset.v!);
  }
  box.addEventListener('scroll', () => {
    const i = clamp(Math.round(box.scrollTop / step()));
    mark(i);
    box.dispatchEvent(new CustomEvent('wheelpreview', { detail: +items[i].dataset.v!, bubbles: true }));
    clearTimeout(timer);
    timer = window.setTimeout(() => { if (i !== idx) { idx = i; onChange(+items[i].dataset.v!); } }, 90);
  }, { passive: true });
  items.forEach((b, i) => b.addEventListener('click', () => pick(i, true)));
  box.addEventListener('keydown', (e) => {
    const k = ({ ArrowDown: 1, ArrowUp: -1, PageDown: 5, PageUp: -5 } as Record<string, number>)[e.key];
    if (!k) return;
    e.preventDefault();
    pick(idx + k, true);
  });
  function commit() {
    if (sel || !box.offsetParent) return; // dropdown mode, or the step is hidden
    const i = clamp(Math.round(box.scrollTop / step()));
    clearTimeout(timer);
    if (i !== idx) { idx = i; mark(i); onChange(+items[i].dataset.v!); }
  }
  box.addEventListener('scrollend', commit);
  const w: Wheel = {
    set(v, smooth = false) { const i = items.findIndex((b) => +b.dataset.v! === v); if (i >= 0) pick(i, smooth, false); },
    value: () => +items[idx].dataset.v!,
    layout() { box.scrollTop = idx * step(); mark(idx); },
    commit,
  };
  allWheels.push(w);
  return w;
}

/* ---------- 1 date ---------- */
const nextOf = (s: Step) => sections[s].querySelector<HTMLButtonElement>('[data-next]');
const wDay = wheel($('wDay'), () => onDate());
const wMonth = wheel($('wMonth'), () => onDate());
const wYear = wheel($('wYear'), () => onDate());
let sunSeq = 0;
async function onDate() {
  const y = wYear.value(), m = wMonth.value(), d = wDay.value();
  const valid = new Date(Date.UTC(y, m - 1, d)).getUTCDate() === d;
  nextOf('date')!.disabled = !valid;
  if (!valid) { $('sunReward').hidden = true; return; }
  state.date = `${y}-${String(m).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
  save();
  const seq = ++sunSeq;
  try {
    const s = await api<{ signIndex: number }>(`/api/sun?d=${state.date}`);
    if (seq !== sunSeq) return;
    const A = D.astro;
    $('rGlyph').textContent = SIGN_GLYPHS[s.signIndex];
    $('rLabel').textContent = fill(D.quiz2.sunLabel, { sign: A.signs[s.signIndex] });
    $('rText').textContent = fill(D.teaser.p1, { signIn: A.signIn[s.signIndex], trait: A.traits[s.signIndex] });
    $('sunReward').hidden = false;
  } catch { /* reward is optional */ }
}
function syncDate() {
  const [y, m, d] = (state.date ?? '1990-01-01').split('-').map(Number);
  wYear.set(y); wMonth.set(m); wDay.set(d);
  [wYear, wMonth, wDay].forEach((w) => w.layout());
  onDate();
}

/* ---------- 2 time ---------- */
const tUnknown = $<HTMLInputElement>('tUnknown');
const wHour = wheel($('wHour'), () => onTime());
const wMin = wheel($('wMin'), () => onTime());
const PICKED: Record<string, string> = { pl: 'Wybrana godzina:', hr: 'Odabrano vrijeme:', sl: 'Izbrani čas:', ro: 'Ora aleasă:', cs: 'Vybraný čas:', hu: 'Kiválasztott idő:', de: 'Gewählte Uhrzeit:', fr: 'Heure choisie :', it: 'Ora scelta:', en: 'Selected time:' };
const two = (n: number) => String(n).padStart(2, '0');
function showPicked(h: number, m: number) {
  $('timePick').textContent = tUnknown.checked ? '' : `${PICKED[lang] ?? PICKED.en} ${two(h)}:${two(m)}`;
}
function onTime() {
  $('timeWheels').classList.toggle('off', tUnknown.checked);
  state.time = tUnknown.checked ? null : `${two(wHour.value())}:${two(wMin.value())}`;
  showPicked(wHour.value(), wMin.value());
  save();
}
// While a wheel glides, show the value under the band right away.
$('wHour').addEventListener('wheelpreview', (e) => showPicked((e as CustomEvent).detail, wMin.value()));
$('wMin').addEventListener('wheelpreview', (e) => showPicked(wHour.value(), (e as CustomEvent).detail));
function syncTime() {
  tUnknown.checked = state.time === null;
  const [h, m] = (state.time ?? '12:00').split(':').map(Number);
  wHour.set(h); wMin.set(m);
  wHour.layout(); wMin.layout();
  onTime();
}
tUnknown.addEventListener('change', onTime);

/* ---------- 3 place ---------- */
const pin = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><path d="M12 21s-7-6.2-7-11a7 7 0 0 1 14 0c0 4.8-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/></svg>';
function cityOption(c: City, q: string, selected: boolean, onPick: (c: City) => void): HTMLButtonElement {
  const b = el('button', 'opt');
  b.type = 'button';
  b.setAttribute('role', 'option');
  b.setAttribute('aria-selected', String(selected));
  b.innerHTML = pin;
  (b.firstElementChild as SVGElement).style.color = selected ? '#D9B26A' : '#A9B0C6';
  const t = el('span', 't');
  const name = el('span');
  const n = q.length && c.name.toLowerCase().startsWith(q.toLowerCase()) ? q.length : 0;
  if (n) { name.append(el('strong', '', c.name.slice(0, n)), c.name.slice(n)); } else name.textContent = c.name;
  t.append(name, el('small', '', countryOf(c)));
  b.append(t);
  b.addEventListener('click', () => onPick(c));
  return b;
}
function citySearch(input: HTMLInputElement, list: HTMLElement, onPick: (c: City) => void, ui?: { loading: HTMLElement; none: HTMLElement; err: HTMLElement; noneTitle: HTMLElement }) {
  let timer = 0, seq = 0;
  const reset = () => { if (ui) { ui.loading.hidden = true; ui.none.hidden = true; ui.err.hidden = true; } };
  async function run() {
    const q = input.value.trim();
    reset();
    if (q.length < 2) { list.hidden = true; list.replaceChildren(); return; }
    const s = ++seq;
    if (ui) ui.loading.hidden = false;
    try {
      const res = await api<City[]>(`/api/cities?q=${encodeURIComponent(q)}&lang=${lang}`);
      if (s !== seq) return;
      reset();
      list.replaceChildren(...res.slice(0, 6).map((c) => cityOption(c, q, false, (city) => {
        input.value = `${city.name}, ${countryOf(city)}`;
        list.replaceChildren(cityOption(city, '', true, () => {}));
        onPick(city);
      })));
      list.hidden = res.length === 0;
      input.setAttribute('aria-expanded', String(res.length > 0));
      if (ui && !res.length) { ui.noneTitle.textContent = fill(D.quiz2.placeNoneTitle, { q }); ui.none.hidden = false; }
    } catch {
      if (s !== seq) return;
      reset();
      list.hidden = true;
      if (ui) ui.err.hidden = false;
    }
  }
  input.addEventListener('input', () => { clearTimeout(timer); timer = window.setTimeout(run, 220); });
  return run;
}
const pInput = $<HTMLInputElement>('pInput'), pList = $('pList');
const placeRun = citySearch(pInput, pList, (c) => { state.city = c; save(); nextOf('place')!.disabled = false; },
  { loading: $('pLoading'), none: $('pNone'), err: $('pErr'), noneTitle: $('pNoneTitle') });
pInput.addEventListener('input', () => { state.city = undefined; nextOf('place')!.disabled = true; });
$('pRetry').addEventListener('click', () => placeRun());

/* ---------- 4 name ---------- */
const nInput = $<HTMLInputElement>('nInput');
function fmtBirth(withTime = true): string {
  const [y, m, d] = (state.date ?? '').split('-').map(Number);
  const dt = new Intl.DateTimeFormat(htmlLang, { day: 'numeric', month: 'long', year: 'numeric' }).format(new Date(Date.UTC(y, m - 1, d)));
  return [dt, withTime ? state.time : null, state.city?.name].filter(Boolean).join(' · ');
}
function renderName() { $('nSummary').textContent = fmtBirth(); }
function validName(): boolean {
  const ok = nInput.value.trim().length > 0;
  nInput.setAttribute('aria-invalid', String(!ok));
  $('nErr').hidden = ok;
  if (!ok) nInput.focus();
  return ok;
}
nInput.addEventListener('input', () => {
  state.name = nInput.value.trim(); save();
  if (state.name) { nInput.setAttribute('aria-invalid', 'false'); $('nErr').hidden = true; }
});

/* ---------- 5 focus ---------- */
const focusCards = [...document.querySelectorAll<HTMLButtonElement>('[data-focus]')];
function renderFocus() {
  focusCards.forEach((b) => b.setAttribute('aria-pressed', String(state.focus.includes(b.dataset.focus!))));
  $('fNext').textContent = fill(D.quiz2.focusCount, { n: state.focus.length });
  $<HTMLButtonElement>('fNext').disabled = state.focus.length === 0;
}
focusCards.forEach((b) => b.addEventListener('click', () => {
  const k = b.dataset.focus!;
  state.focus = state.focus.includes(k) ? state.focus.filter((x) => x !== k) : [...state.focus, k];
  save(); renderFocus();
}));

/* ---------- 6 status (auto-advance) ---------- */
const statusRows = [...document.querySelectorAll<HTMLButtonElement>('[data-status]')];
statusRows.forEach((b) => b.addEventListener('click', () => {
  state.status = b.dataset.status; save();
  statusRows.forEach((x) => x.setAttribute('aria-pressed', String(x === b)));
  setTimeout(() => go(1), 250);
}));

/* ---------- 7 calculating ---------- */
function who(): string {
  const [y, m, d] = (state.date ?? '').split('-').map(Number);
  const dt = new Intl.DateTimeFormat(htmlLang, { day: 'numeric', month: 'long', year: 'numeric' }).format(new Date(Date.UTC(y, m - 1, d)));
  return [state.name, `${dt}${state.time ? `, ${state.time}` : ''}`, state.city?.name].filter(Boolean).join(' · ');
}
function wheelData(c: Chart) {
  return { planets: c.planets, asc: c.angles?.asc.lon ?? null, cusps: c.houses?.cusps ?? null, aspects: c.aspects.slice(0, 8) };
}
function big3(c: Chart): { g: string; tag: boolean; label: string; sign: string; pos: string; cusp: string }[] {
  const A = D.astro, sun = c.planets[0], moon = c.planets[1];
  const cusp = (i?: number | null) => (i == null ? '' : `${CUSP[lang] ?? CUSP.en} ${A.signs[i]}`);
  const rows = [
    { g: '☉︎', tag: false, label: A.planets.sun, sign: A.signs[sun.signIndex], pos: pos(sun.deg, sun.min), cusp: cusp(sun.cusp) },
    { g: '☽︎', tag: false, label: A.planets.moon, sign: A.signs[moon.signIndex], pos: pos(moon.deg, moon.min), cusp: cusp(moon.cusp) },
  ];
  rows.push(c.angles
    ? { g: 'ASC', tag: true, label: A.asc, sign: A.signs[c.angles.asc.signIndex], pos: pos(c.angles.asc.deg, c.angles.asc.min ?? 0), cusp: cusp(c.angles.asc.cusp) }
    : { g: 'ASC', tag: true, label: A.asc, sign: D.offer.ascUnknown, pos: '', cusp: '' });
  return rows;
}
function chipsInto(box: HTMLElement, c: Chart) {
  box.replaceChildren(...big3(c).map((r) => {
    const div = el('div', 'chip');
    const g = el('span', r.tag ? 't' : 'g', r.g); g.setAttribute('aria-hidden', 'true');
    div.append(g, el('span', 'l', r.label), el('strong', '', r.sign));
    if (r.cusp) div.append(el('span', 'cu', r.cusp));
    return div;
  }));
}
let calcTimers: number[] = [];
async function runCalc() {
  calcTimers.forEach(clearTimeout); calcTimers = [];
  $('calcErr').hidden = true;
  $('calcGo').hidden = true;
  $('calcStatus').hidden = false;
  $('calcWho').textContent = who();
  $('calcVals').replaceChildren();
  const bar = $('calcBar');
  bar.style.transition = 'none'; bar.style.width = '3%';
  requestAnimationFrame(() => requestAnimationFrame(() => { bar.style.transition = 'width 6s linear'; bar.style.width = '100%'; }));
  const started = Date.now();
  try {
    const chart = await api<Chart>('/api/chart', { date: state.date, time: state.time ?? null, cityId: state.city!.id });
    state.chart = chart; save();
    $('calcWheel').innerHTML = wheelSvg(wheelData(chart), { size: 290, label: D.quiz.calcTitle, animate: true });
    big3(chart).forEach((r, i) => calcTimers.push(window.setTimeout(() => {
      const row = el('div', 'vr');
      const g = el('span', r.tag ? 't' : 'g', r.g); g.setAttribute('aria-hidden', 'true');
      const v = el('span', '', r.sign);
      if (r.pos) v.append(' ', el('span', 'mu', r.pos));
      row.append(g, el('span', 'l', r.label), v);
      $('calcVals').append(row);
    }, 1800 + i * 1200)));
    const wait = Math.max(0, 6400 - (Date.now() - started));
    calcTimers.push(window.setTimeout(() => {
      if (current !== 'calc') return;
      $('calcStatus').hidden = true;
      $('calcGo').hidden = false;
      $('calcGo').focus({ preventScroll: true });
    }, wait));
  } catch {
    $('calcErr').hidden = false;
  }
}
$('calcGo').addEventListener('click', () => {
  history.replaceState({ step: 'status' }, '', '#status');
  show('email');
});

/* ---------- 8 email ---------- */
let eCap: Captcha | undefined;
function renderEmail() {
  if (!state.chart) { show('date'); return; }
  eCap ??= captcha($('eCaptcha'), lang);
  chipsInto($('eChips'), state.chart);
  if (state.email) $<HTMLInputElement>('eInput').value = state.email;
}
$('eForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const input = $<HTMLInputElement>('eInput');
  const email = input.value.trim();
  const ok = /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email);
  input.setAttribute('aria-invalid', String(!ok));
  $('eErr').hidden = ok;
  if (!ok) {
    $('eErrText').textContent = email.includes('@') ? D.quiz.emailErr : D.quiz2.emailErrAt;
    input.focus();
    return;
  }
  state.email = email; save();
  const btn = (e.currentTarget as HTMLFormElement).querySelector<HTMLButtonElement>('button[type=submit]')!;
  btn.disabled = true;
  try {
    const cap = await eCap?.token();
    const r = await api<{ token: string }>('/api/lead', {
      email, lang, name: state.name ?? '', date: state.date ?? '', time: state.time ?? null,
      cityId: state.city?.id ?? null, focus: state.focus, status: state.status ?? '',
      marketingConsent: $<HTMLInputElement>('eConsent').checked, track: trackInfo(), captcha: cap,
    });
    fbTrack('Lead', {}, `lead_${r.token}`);
  } catch (err) {
    eCap?.reset();
    if (String((err as Error).message) === '403') {  // the security check failed: let them try again
      btn.disabled = false; $('eErrText').textContent = D.ui.error; $('eErr').hidden = false; return;
    }
    /* otherwise keep the funnel moving even if the lead call fails */
  }
  btn.disabled = false;
  show('offer');
});
$('eInput').addEventListener('input', () => { $('eErr').hidden = true; $('eInput').setAttribute('aria-invalid', 'false'); });

/* ---------- 9 offer ---------- */
function renderOffer() {
  const c = state.chart;
  if (!c) { show('date'); return; }
  const A = D.astro, T = D.teaser;
  const sun = c.planets[0], moon = c.planets[1];
  $('oWho').textContent = who();
  chipsInto($('oChips'), c);
  $('oNoTime').hidden = c.timeKnown;
  const vars = {
    signIn: A.signIn[sun.signIndex], trait: A.traits[sun.signIndex],
    house: sun.house ?? '', topic: sun.house ? A.houseTopics[sun.house - 1] : '',
    houseArt: sun.house ? huArticle(sun.house) : '',
    moonIn: A.signIn[moon.signIndex], moonTrait: A.traits[moon.signIndex],
  };
  $('oTitle').textContent = fill(sun.house ? T.titleHouse : T.title, vars);
  $('oP1').textContent = fill(T.p1, vars);
  $('oP2').textContent = fill(sun.house ? T.p2House : T.p2NoTime, vars);
  $('oP3').textContent = fill(T.p3, vars);
  document.querySelectorAll<HTMLElement>('[data-incs]').forEach((box) => {
    box.querySelector('[data-chapters]')?.remove();
    if (!state.focus.length) return;
    const row = box.lastElementChild!.cloneNode(true) as HTMLElement;
    row.dataset.chapters = '';
    const label = fill(D.offer.chapters, { list: state.focus.map((f) => D.quiz.focus[f]).join(', ') });
    const strong = row.querySelector('strong');
    if (strong) { strong.textContent = label; row.querySelector('p')!.textContent = D.offer.chaptersDesc; } else row.querySelector('span')!.textContent = label;
    box.insertBefore(row, box.lastElementChild);
  });
  applyCouponUi();
}
const planRadios = [...document.querySelectorAll<HTMLInputElement>('input[name="oplan"]')];
type PriceKey = 'natal' | 'bundle' | 'partner' | 'forecast' | 'child';
/** Price shown for a one-time product, less the discount code. Rounding matches api/pay.py price(). */
function P(key: PriceKey): string {
  let a: number = data.amounts[key];
  const whole = ['HUF', 'CZK'].includes(data.cur);
  if (state.disc) { a = (a * (100 - state.disc.pct)) / 100; a = whole ? Math.round(a) : Math.round(a * 100) / 100; }
  const int = Number.isInteger(a);
  return new Intl.NumberFormat(data.intl, { style: 'currency', currency: data.cur,
    minimumFractionDigits: int ? 0 : 2, maximumFractionDigits: int ? 0 : 2 }).format(a);
}
const offerPrice = () => P(state.plan === 'bundle' ? 'bundle' : 'natal');
function syncPlan() {
  planRadios.forEach((r) => (r.checked = r.value === (state.plan ?? 'natal')));
  if (!state.coupon) $('oBuy').textContent = D.offer.cta.replace('{price}', offerPrice());
}
planRadios.forEach((r) => r.addEventListener('change', () => { state.plan = r.value as 'natal' | 'bundle'; save(); syncPlan(); }));
function applyCouponUi() {
  syncPlan();
  syncWaivers();
  $('pNatal').textContent = P('natal');
  $('pBundle').textContent = P('bundle');
  if (state.disc) {
    $('cOk').textContent = fill(D.coupon.appliedPct, { code: state.disc.code, pct: state.disc.pct });
    $('cOk').hidden = false;
    $('cBox').hidden = true;
    return;
  }
  if (!state.coupon) return;
  $('cOk').textContent = fill(D.coupon.applied, { code: state.coupon });
  $('cOk').hidden = false;
  $('cBox').hidden = true;
  $('oBuy').textContent = D.coupon.claim;
}
$('cForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const code = $<HTMLInputElement>('cInput').value.trim().toUpperCase();
  if (!code) return;
  let pct = 0;
  try { pct = (await api<{ valid: boolean; percent?: number }>('/api/coupon', { code })).percent ?? 0; } catch { /* treat as invalid */ }
  $('cErr').hidden = pct > 0;
  if (pct >= 100) { state.coupon = code; state.disc = undefined; }
  else if (pct > 0) state.disc = { code, pct };
  if (pct > 0) { save(); applyCouponUi(); }
});
/** The withdrawal waiver must be ticked before any paid checkout (Managed Payments has no checkbox of its own). */
function consented(id: string): boolean {
  if (state.coupon) return true;
  const c = $<HTMLInputElement>(id);
  const box = $(`${id}Box`);
  box.classList.toggle('err', !c.checked);
  if (!c.checked) { box.scrollIntoView({ behavior: 'smooth', block: 'center' }); return false; }
  return true;
}
const waiverBoxes = ['wOffer', 'wUp', 'wKid', 'wSub'];
function syncWaivers() { waiverBoxes.forEach((id) => { $(`${id}Box`).hidden = !!state.coupon; }); }
waiverBoxes.forEach((id) => $<HTMLInputElement>(id).addEventListener('change', () => $(`${id}Box`).classList.remove('err')));
/** Leave for Stripe Checkout; the state stays in sessionStorage for the way back (?paid=...). */
function toCheckout(url: string, value?: string) {
  save();
  const [amount, currency] = priceParts(value);
  fbTrack('InitiateCheckout', amount ? { value: amount, currency } : {});
  location.href = url;
}
/** "49,99 zł" -> [49.99, 'PLN'] for the pixel, using the market currency. */
function priceParts(v?: string): [number, string] {
  const cur = ({ pl: 'PLN', ro: 'RON', cs: 'CZK', hu: 'HUF' } as Record<string, string>)[lang] ?? 'EUR';
  const n = v ? Number(v.replace(/[^\d,.]/g, '').replace(/\.(?=\d{3}\b)/g, '').replace(',', '.')) : 0;
  return [Number.isFinite(n) ? n : 0, cur];
}
$('oBuy').addEventListener('click', async () => {
  if (!consented('wOffer')) return;
  const btn = $<HTMLButtonElement>('oBuy');
  btn.disabled = true;
  btn.setAttribute('aria-busy', 'true');
  $('oErr').hidden = true;
  try {
    if (!state.token) {
      const res = await api<{ token: string; checkout?: string }>('/api/order', {
        lang, email: state.email, name: state.name ?? '', date: state.date, time: state.time ?? null,
        cityId: state.city!.id, focus: state.focus, status: state.status ?? '', coupon: state.coupon ?? state.disc?.code ?? '',
        bundle: state.plan === 'bundle', consent: true, track: trackInfo(),
      });
      state.up = undefined;
      if (res.checkout) { state.token = undefined; save(); toCheckout(res.checkout, offerPrice()); return; }
      state.token = res.token; save();
    }
    if (state.plan === 'bundle') { state.pMode = 'partner'; save(); show('pdata'); } else show('upsell');
  } catch {
    $('oErr').hidden = false;
  }
  btn.disabled = false;
  btn.removeAttribute('aria-busy');
});

/* ---------- 10 upsell ---------- */
const forecastYear = (() => { const n = new Date(); return n.getMonth() >= 9 ? n.getFullYear() + 1 : n.getFullYear(); })();
const upsellProduct = () => state.up ?? (state.status === 'single' ? 'forecast' : 'partner');
const reportUrl = () => `/${lang}/report/?o=${encodeURIComponent(state.token ?? '')}`;
function renderUpsell() {
  if (!state.token) { show('offer'); return; }
  const prod = upsellProduct();
  $('uBanner').textContent = state.coupon ? D.upsell2.paidCoupon : D.upsell2.paid;
  $('uBanner').parentElement!.hidden = !!state.up;
  $('uPartner').hidden = prod !== 'partner';
  $('uForecast').hidden = prod !== 'forecast';
  $('ufTitle').textContent = fill(D.upsell2.forecastTitle, { year: forecastYear });
  if (prod === 'forecast' && !$('uMonths').childElementCount) {
    const fmt = new Intl.DateTimeFormat(htmlLang, { month: 'short' });
    const heights = [30, 46, 92, 40, 58, 34, 50, 104, 44, 62, 36, 54];
    $('uMonths').replaceChildren(...heights.map((h, i) => {
      const m = el('div', i === 2 || i === 7 ? 'm on' : 'm');
      const bar = el('i'); bar.style.height = `${h}px`;
      m.append(bar, el('span', '', fmt.format(new Date(Date.UTC(2001, i, 15))).replace('.', '')));
      return m;
    }));
  }
  const price = P(prod);
  $('uPrice').textContent = price;
  $('uPriceRow').hidden = !!state.coupon;
  $('uOneClick').hidden = !!state.coupon;
  $('uAdd').textContent = state.coupon ? fill(D.upsell.addFree, { code: state.coupon }) : fill(D.upsell2.addFor, { price });
}
$('uAdd').addEventListener('click', async () => {
  if (!consented('wUp')) return;
  if (upsellProduct() === 'partner') { state.pMode = 'partner'; save(); show('pdata'); return; }
  const btn = $<HTMLButtonElement>('uAdd');
  btn.disabled = true; $('uErr').hidden = true;
  try {
    const r = await api<{ checkout?: string }>(`/api/order/${encodeURIComponent(state.token!)}/add`, { product: 'forecast', consent: true, track: trackInfo() });
    if (r.checkout) { toCheckout(r.checkout, P('forecast')); return; }
    show('kid');
  } catch { $('uErr').hidden = false; }
  btn.disabled = false;
});
$('uNo').addEventListener('click', () => show('kid'));

/* ---------- 10b partner details ---------- */
const upName = $<HTMLInputElement>('upName'), upTimeUnknown = $<HTMLInputElement>('upTimeUnknown');
const upPlace = $<HTMLInputElement>('upPlace');
let partnerCity: City | undefined;
const pwDay = wheel($('pwDay'), () => checkPartner());
const pwMonth = wheel($('pwMonth'), () => checkPartner());
const pwYear = wheel($('pwYear'), () => checkPartner());
const pwHour = wheel($('pwHour'), () => checkPartner());
const pwMin = wheel($('pwMin'), () => checkPartner());
let pdataReady = false;
function partnerDate(): string | null {
  const y = pwYear.value(), m = pwMonth.value(), d = pwDay.value();
  if (new Date(Date.UTC(y, m - 1, d)).getUTCDate() !== d) return null;
  const iso = `${y}-${String(m).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
  return iso <= new Date().toISOString().slice(0, 10) ? iso : null;
}
let pdataMode: 'partner' | 'child' | null = null;
function renderPdata() {
  if (!state.token) { show('offer'); return; }
  const mode = state.pMode ?? 'partner', U = D.upsell, U2 = D.upsell2, SH = D.shop;
  if (mode !== pdataMode) {
    // A different person: start the form from scratch.
    pdataMode = mode; pdataReady = false;
    upName.value = ''; upPlace.value = ''; partnerCity = undefined; upTimeUnknown.checked = false;
    $('upList').replaceChildren(); $('upList').hidden = true;
  }
  const kid = mode === 'child';
  $('pdEy').textContent = kid ? SH.kidEyebrow : U2.partnerEyebrow;
  $('pdTitle').textContent = kid ? SH.kidFormTitle : U2.pformTitle;
  $('pdSub').textContent = kid ? SH.kidFormSub : U2.pformSub;
  $('pdNameLbl').textContent = kid ? SH.kidName : U.pName;
  $('pdGo').textContent = kid ? SH.kidCta : U2.pformCta;
  const bundled = !kid && state.plan === 'bundle';
  $('pdBundle').hidden = !bundled;
  $('pdLater').hidden = !bundled;
  checkPartner();
}
$('pdLater').addEventListener('click', () => show('kid'));
function checkPartner() {
  if (!pdataReady) {
    // Wheels can only be positioned once the step is visible.
    pdataReady = true;
    pwYear.set(pdataMode === 'child' ? 2015 : 1990); pwMonth.set(1); pwDay.set(1); pwHour.set(12); pwMin.set(0);
    [pwYear, pwMonth, pwDay, pwHour, pwMin].forEach((w) => w.layout());
  }
  $('ptWheels').classList.toggle('off', upTimeUnknown.checked);
  $<HTMLButtonElement>('pdGo').disabled = !(partnerDate() && partnerCity);
}
upTimeUnknown.addEventListener('change', checkPartner);
citySearch(upPlace, $('upList'), (c) => { partnerCity = c; checkPartner(); });
upPlace.addEventListener('input', () => { partnerCity = undefined; checkPartner(); });
$('pdGo').addEventListener('click', async () => {
  commitWheels();
  const btn = $<HTMLButtonElement>('pdGo');
  btn.disabled = true; $('pdErr').hidden = true;
  const time = upTimeUnknown.checked ? null : `${String(pwHour.value()).padStart(2, '0')}:${String(pwMin.value()).padStart(2, '0')}`;
  try {
    const product = pdataMode === 'child' ? 'child' : 'partner';
    const r = await api<{ checkout?: string }>(`/api/order/${encodeURIComponent(state.token!)}/add`, {
      product,
      partner: { name: upName.value.trim(), date: partnerDate(), time, cityId: partnerCity!.id }, consent: true, track: trackInfo(),
    });
    if (r.checkout) { toCheckout(r.checkout, P(product)); return; }
    btn.disabled = false;
    show(fromReport ? 'done' : product === 'child' ? 'sub' : 'kid');
  } catch { $('pdErr').hidden = false; btn.disabled = false; }
});

/* ---------- 10c child chart offer ---------- */
function renderKid() {
  if (!state.token) { show('offer'); return; }
  $('kPriceRow').hidden = !!state.coupon;
  $('kPrice').textContent = P('child');
  $('kAdd').textContent = state.coupon ? fill(D.upsell.addFree, { code: state.coupon }) : fill(D.upsell2.addFor, { price: P('child') });
}
$('kAdd').addEventListener('click', () => {
  if (!consented('wKid')) return; state.pMode = 'child'; save(); show('pdata'); });
$('kNo').addEventListener('click', () => show('sub'));

/* ---------- 11 subscription ---------- */
const planInputs = [...document.querySelectorAll<HTMLInputElement>('input[name="plan"]')];
const plan = () => planInputs.find((x) => x.checked)?.value ?? 'year';
function renderSub() {
  if (!state.token) { show('offer'); return; }
  const now = new Date();
  const mon = new Date(now); mon.setDate(now.getDate() + ((8 - now.getDay()) % 7 || 7));
  const sun = new Date(mon); sun.setDate(mon.getDate() + 6);
  let range: string;
  try { range = new Intl.DateTimeFormat(htmlLang, { day: 'numeric', month: 'long' }).formatRange(mon, sun); }
  catch { range = `${mon.toLocaleDateString(htmlLang)} – ${sun.toLocaleDateString(htmlLang)}`; }
  $('sExLabel').textContent = fill(D.sub.exLabel, { range });
  updateSubCta();
}
function updateSubCta() {
  const S = D.sub, P = data.subPrices;
  if (state.coupon) {
    $('sAdd').textContent = fill(S.ctaFree, { code: state.coupon });
    $('sNote').textContent = '';
  } else {
    $('sAdd').textContent = plan() === 'year' ? fill(S.ctaYear, { price: P.year }) : fill(S.ctaMonth, { price: P.month });
    $('sNote').textContent = plan() === 'year' ? S.noteYear : S.noteMonth;
  }
}
planInputs.forEach((x) => x.addEventListener('change', updateSubCta));
$('sAdd').addEventListener('click', async () => {
  if (!consented('wSub')) return;
  const btn = $<HTMLButtonElement>('sAdd');
  btn.disabled = true; $('sErr').hidden = true;
  try {
    const r = await api<{ cal?: string; checkout?: string }>('/api/subscribe', { order: state.token, freq: 'weekly', plan: plan(), consent: true, track: trackInfo() });
    if (r.checkout) { toCheckout(r.checkout, plan() === 'year' ? data.subPrices.year : data.subPrices.month); return; }
    state.sub = 'weekly'; state.cal = r.cal; save();
    show('done');
  } catch {
    $('sErr').textContent = D.ui.error; $('sErr').hidden = false;
  }
  btn.disabled = false;
});
$('sNo').addEventListener('click', () => show('done'));

/* ---------- 12 done ---------- */
function renderDone() {
  if (!state.token) { show('offer'); return; }
  $('dDesc').textContent = fill(D.done.desc, { email: state.email ?? '' });
  $('dStmt').hidden = !!state.coupon; // paid through Stripe: say how the charge looks on the statement
  $('dSub').hidden = !state.sub;
  $<HTMLAnchorElement>('dOpen').href = reportUrl();
  $('dCal').hidden = !state.cal;
  if (state.cal) {
    const webcal = 'webcal://' + state.cal.split('://')[1];
    $<HTMLAnchorElement>('dCalG').href = 'https://calendar.google.com/calendar/render?cid=' + encodeURIComponent(webcal);
    $<HTMLAnchorElement>('dCalA').href = webcal;
  }
}
$('dCalC').addEventListener('click', async () => {
  const b = $<HTMLButtonElement>('dCalC');
  try { await navigator.clipboard.writeText(state.cal ?? ''); b.textContent = b.dataset.done ?? ''; } catch { /* clipboard blocked */ }
});

/* ---------- resume from the summary email ---------- */
async function resume(token: string): Promise<boolean> {
  try {
    const L = await api<{ email: string; name: string; date: string; time: string | null; city: City | null; focus: string[]; status: string }>(
      `/api/lead/${encodeURIComponent(token)}`);
    if (!L.city || !L.date) return false;
    Object.assign(state, { email: L.email, name: L.name, date: L.date, time: L.time, city: L.city, focus: L.focus, status: L.status,
      token: undefined, sub: undefined, cal: undefined });
    state.chart = await api<Chart>('/api/chart', { date: L.date, time: L.time, cityId: L.city.id });
    save();
    history.replaceState(null, '', `${location.pathname}#offer`);
    return true;
  } catch { return false; }
}

/* ---------- restore ---------- */
function restore() {
  if (state.city) {
    pInput.value = `${state.city.name}, ${countryOf(state.city)}`;
    pList.replaceChildren(cityOption(state.city, '', true, () => {}));
    pList.hidden = false;
    nextOf('place')!.disabled = false;
  }
  if (state.name) nInput.value = state.name;
  statusRows.forEach((r) => r.setAttribute('aria-pressed', String(r.dataset.status === state.status)));
  const hash = location.hash.slice(1) as Step;
  const ok = STEPS.includes(hash) && hash !== 'calc'
    && (!['email', 'offer'].includes(hash) || !!state.chart)
    && (!NEEDS_TOKEN.includes(hash) || !!state.token);
  const start: Step = ok ? hash : 'date';
  history.replaceState({ step: start }, '', `#${start}`);
  show(start, false);
}
/** Back from Stripe Checkout: confirm the payment and continue where the purchase led. */
async function returnFromCheckout(session: string) {
  history.replaceState(null, '', location.pathname);
  type Paid = { token: string; kind: 'order' | 'add' | 'sub'; product: string; email: string; cal?: string;
    value?: number; currency?: string; eventId?: string };
  let r: Paid | undefined;
  for (let i = 0; i < 12 && !r; i++) {  // the payment can take a few seconds to settle
    try { r = await api<Paid>(`/api/checkout/confirm?session=${encodeURIComponent(session)}`); }
    catch { await new Promise((ok) => setTimeout(ok, 2500)); }
  }
  if (!r) {
    // Not confirmed yet: stay on the offer and say so, instead of starting the quiz over.
    restore();
    if (state.chart) {
      history.replaceState({ step: 'offer' }, '', `${location.pathname}#offer`);
      show('offer', false);
      $('oErr').textContent = D.shop.payPending; $('oErr').hidden = false;
    }
    return;
  }
  Object.assign(state, { token: r.token, email: state.email || r.email });
  fbTrack('Purchase', { value: r.value, currency: r.currency, content_name: r.product, content_type: 'product' }, r.eventId);
  let next: Step;
  if (r.kind === 'order') {
    state.plan = r.product === 'bundle' ? 'bundle' : 'natal';
    if (state.plan === 'bundle') { state.pMode = 'partner'; next = 'pdata'; } else next = 'upsell';
  } else if (r.kind === 'add') next = r.product === 'child' ? 'sub' : 'kid';
  else { state.sub = 'weekly'; state.cal = r.cal ?? undefined; next = 'done'; }
  save();
  history.replaceState({ step: next }, '', `${location.pathname}#${next}`);
  show(next, false);
}

const params = new URLSearchParams(location.search);
const paidSession = params.get('paid');
const resumeToken = params.get('r');
const orderToken = params.get('o');
let fromReport = false;
if (orderToken) {
  fromReport = true;
  // From the report or account page. Without "add": the partner that came with a bundle.
  // With add=partner|forecast|child|sub: buy that add-on for an existing order.
  const add = params.get('add');
  let step: Step = 'pdata';
  Object.assign(state, { token: orderToken, plan: 'bundle', pMode: 'partner', up: undefined, coupon: undefined, disc: undefined });
  if (add === 'partner' || add === 'forecast') { Object.assign(state, { plan: 'natal', up: add }); step = 'upsell'; }
  else if (add === 'child') { state.plan = 'natal'; step = 'kid'; }
  else if (add === 'sub') step = 'sub';
  save();
  history.replaceState({ step }, '', `${location.pathname}#${step}`);
  show(step, false);
} else if (paidSession) returnFromCheckout(paidSession);
else if (resumeToken) resume(resumeToken).then(restore); else restore();
