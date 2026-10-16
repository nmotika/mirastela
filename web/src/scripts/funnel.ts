import { wheelSvg } from './wheel';
import { fill, huArticle } from '../i18n/fill';

type Step = 'date' | 'time' | 'place' | 'name' | 'focus' | 'status' | 'calc' | 'email' | 'offer' | 'upsell' | 'sub' | 'done';
const STEPS: Step[] = ['date', 'time', 'place', 'name', 'focus', 'status', 'calc', 'email', 'offer', 'upsell', 'sub', 'done'];
const QUIZ_STEPS = 6;

interface City { id: number; name: string; country: string; countryName: string; tz: string }
interface Planet { id: string; lon: number; sign: string; signIndex: number; deg: number; min: number; house?: number; retro: boolean }
interface Chart {
  timeKnown: boolean;
  planets: Planet[];
  houses: { cusps: number[] } | null;
  angles: { asc: { lon: number; signIndex: number; deg: number } } | null;
  aspects: { a: string; b: string; type: string }[];
}
interface State {
  date?: string; time?: string | null; city?: City; name?: string;
  focus: string[]; status?: string; email?: string; chart?: Chart; coupon?: string; token?: string;
  sub?: 'daily' | 'weekly';
}

const data = JSON.parse(document.getElementById('funnel-data')!.textContent!);
const lang: string = data.lang;
const D = data.d;
const KEY = 'mirastela-funnel';
const regionNames = (() => { try { return new Intl.DisplayNames([document.documentElement.lang], { type: 'region' }); } catch { return null; } })();
const countryOf = (c: City) => regionNames?.of(c.country) ?? c.countryName;

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

function nextBtn(step: Step) {
  return sections[step].querySelector<HTMLButtonElement>('[data-next]');
}

/* ---------- navigation ---------- */
function show(step: Step, push = true) {
  current = step;
  STEPS.forEach((s) => (sections[s].hidden = s !== step));
  const i = STEPS.indexOf(step);
  const inQuiz = i < QUIZ_STEPS;
  $('back').hidden = i === 0 || !inQuiz;
  $('prog').hidden = !inQuiz;
  $('brand').hidden = inQuiz;
  if (inQuiz) {
    $('progLabel').textContent = fill(D.ui.stepOf, { n: i + 1, t: QUIZ_STEPS });
    $('progBar').style.width = `${((i + 1) / QUIZ_STEPS) * 100}%`;
  }
  if (push) history.pushState({ step }, '', `#${step}`);
  window.scrollTo(0, 0);
  const h = sections[step].querySelector<HTMLElement>('h1');
  h?.setAttribute('tabindex', '-1');
  h?.focus({ preventScroll: true });
  if (step === 'calc') runCalc();
  if (step === 'offer') renderOffer();
  if (step === 'upsell') renderUpsell();
  if (step === 'sub') renderSub();
  if (step === 'done') renderDone();
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
document.querySelectorAll<HTMLButtonElement>('[data-next]').forEach((b) => b.addEventListener('click', () => go(1)));

/* ---------- 1 date ---------- */
const dDay = $<HTMLSelectElement>('dDay'), dMonth = $<HTMLSelectElement>('dMonth'), dYear = $<HTMLSelectElement>('dYear');
async function onDate() {
  const y = +dYear.value, m = +dMonth.value, d = +dDay.value;
  const valid = y && m && d && new Date(Date.UTC(y, m - 1, d)).getUTCDate() === d;
  nextBtn('date')!.disabled = !valid;
  if (!valid) { $('sunReward').hidden = true; return; }
  state.date = `${y}-${String(m).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
  save();
  try {
    const s = await api<{ signIndex: number }>(`/api/sun?d=${state.date}`);
    $('sunReward').textContent = fill(D.quiz.sunReward, { sign: D.astro.signs[s.signIndex] });
    $('sunReward').hidden = false;
  } catch { /* reward is optional */ }
}
[dDay, dMonth, dYear].forEach((el) => el.addEventListener('change', onDate));

/* ---------- 2 time ---------- */
const tTime = $<HTMLInputElement>('tTime'), tUnknown = $<HTMLInputElement>('tUnknown');
function onTime() {
  tTime.disabled = tUnknown.checked;
  $('tWhy').hidden = !tUnknown.checked;
  state.time = tUnknown.checked ? null : tTime.value || undefined;
  nextBtn('time')!.disabled = !(tUnknown.checked || /^\d{2}:\d{2}$/.test(tTime.value));
  save();
}
tTime.addEventListener('input', onTime);
tUnknown.addEventListener('change', onTime);

/* ---------- 3 place ---------- */
const pInput = $<HTMLInputElement>('pInput'), pList = $('pList');
let pTimer = 0, pSeq = 0;
function renderCities(list: City[]) {
  pList.replaceChildren(...list.map((c) => {
    const li = document.createElement('li');
    const b = document.createElement('button');
    b.type = 'button';
    b.setAttribute('role', 'option');
    b.setAttribute('aria-selected', String(state.city?.id === c.id));
    const name = document.createElement('span'); name.textContent = c.name;
    const country = document.createElement('small'); country.textContent = countryOf(c);
    b.append(name, country);
    b.addEventListener('click', () => {
      state.city = c; save();
      pInput.value = `${c.name}, ${countryOf(c)}`;
      renderCities([c]);
      nextBtn('place')!.disabled = false;
    });
    li.append(b);
    return li;
  }));
  pInput.setAttribute('aria-expanded', String(list.length > 0));
}
pInput.addEventListener('input', () => {
  state.city = undefined;
  nextBtn('place')!.disabled = true;
  clearTimeout(pTimer);
  const q = pInput.value.trim();
  if (q.length < 2) { renderCities([]); $('pNone').hidden = true; return; }
  pTimer = window.setTimeout(async () => {
    const seq = ++pSeq;
    try {
      const list = await api<City[]>(`/api/cities?q=${encodeURIComponent(q)}&lang=${lang}`);
      if (seq !== pSeq) return;
      renderCities(list);
      $('pNone').hidden = list.length > 0;
    } catch { $('pNone').hidden = false; }
  }, 220);
});

/* ---------- 4 name ---------- */
const nInput = $<HTMLInputElement>('nInput');
nInput.addEventListener('input', () => {
  state.name = nInput.value.trim();
  nextBtn('name')!.disabled = state.name.length < 1;
  save();
});

/* ---------- 5 focus ---------- */
const focusBoxes = [...document.querySelectorAll<HTMLInputElement>('input[name="focus"]')];
focusBoxes.forEach((b) => b.addEventListener('change', () => {
  state.focus = focusBoxes.filter((x) => x.checked).map((x) => x.value);
  nextBtn('focus')!.disabled = state.focus.length === 0;
  save();
}));

/* ---------- 6 status (auto-advance) ---------- */
document.querySelectorAll<HTMLInputElement>('input[name="status"]').forEach((r) => r.addEventListener('change', () => {
  state.status = r.value; save();
  setTimeout(() => go(1), 250);
}));

/* ---------- 7 calculating ---------- */
function who(): string {
  const [y, m, d] = (state.date ?? '').split('-').map(Number);
  const dt = new Intl.DateTimeFormat(document.documentElement.lang, { day: 'numeric', month: 'long', year: 'numeric' })
    .format(new Date(Date.UTC(y, m - 1, d)));
  return [state.name, `${dt}${state.time ? `, ${state.time}` : ''}`, state.city?.name].filter(Boolean).join(' · ');
}
function wheelData(c: Chart) {
  return { planets: c.planets, asc: c.angles?.asc.lon ?? null, cusps: c.houses?.cusps ?? null, aspects: c.aspects.slice(0, 8) };
}
async function runCalc() {
  $('calcErr').hidden = true;
  $('calcWho').textContent = who();
  $('calcVals').replaceChildren();
  const started = Date.now();
  try {
    const chart = await api<Chart>('/api/chart', { date: state.date, time: state.time ?? null, cityId: state.city!.id });
    state.chart = chart; save();
    $('calcWheel').innerHTML = wheelSvg(wheelData(chart), { size: 290, label: D.quiz.calcTitle, animate: true });
    const sun = chart.planets[0], moon = chart.planets[1];
    const rows: [string, string, string][] = [
      ['☉', D.astro.planets.sun, D.astro.signs[sun.signIndex]],
      ['☽', D.astro.planets.moon, D.astro.signs[moon.signIndex]],
      ['↑', D.astro.asc, chart.angles ? D.astro.signs[chart.angles.asc.signIndex] : D.offer.ascUnknown],
    ];
    rows.forEach(([g, label, val], i) => setTimeout(() => {
      const li = document.createElement('li');
      const gs = document.createElement('span'); gs.className = 'gl'; gs.textContent = `${g}︎`;
      const ls = document.createElement('span'); ls.textContent = label;
      const vs = document.createElement('strong'); vs.textContent = val;
      li.append(gs, ls, vs);
      $('calcVals').append(li);
    }, 1600 + i * 1100));
    const wait = Math.max(0, 6200 - (Date.now() - started));
    setTimeout(() => { if (current === 'calc') { history.replaceState({ step: 'status' }, '', '#status'); show('email'); } }, wait);
  } catch {
    $('calcErr').hidden = false;
  }
}

/* ---------- 8 email ---------- */
$('eForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const email = $<HTMLInputElement>('eInput').value.trim();
  const ok = /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email);
  $('eErr').hidden = ok;
  if (!ok) return;
  state.email = email; save();
  const btn = (e.currentTarget as HTMLFormElement).querySelector('button')!;
  btn.disabled = true;
  try {
    await api('/api/lead', {
      email, lang, name: state.name ?? '', date: state.date ?? '', time: state.time ?? null,
      cityId: state.city?.id ?? null, focus: state.focus, status: state.status ?? '',
      marketingConsent: $<HTMLInputElement>('eConsent').checked,
    });
  } catch { /* keep the funnel moving even if the lead call fails */ }
  btn.disabled = false;
  show('offer');
});

/* ---------- 9 offer ---------- */
function renderOffer() {
  const c = state.chart;
  if (!c) { show('date'); return; }
  const A = D.astro, T = D.teaser;
  const sun = c.planets[0], moon = c.planets[1];
  $('oWho').textContent = who();
  const chips: [string, string, string][] = [
    ['☉︎', A.planets.sun, A.signs[sun.signIndex]],
    ['☽︎', A.planets.moon, A.signs[moon.signIndex]],
    ['ASC', A.asc, c.angles ? A.signs[c.angles.asc.signIndex] : D.offer.ascUnknown],
  ];
  $('oChips').replaceChildren(...chips.map(([g, l, v]) => {
    const div = document.createElement('div'); div.className = 'chip';
    const gs = document.createElement('span'); gs.className = g === 'ASC' ? 'tag' : 'gl'; gs.textContent = g; gs.setAttribute('aria-hidden', 'true');
    const ls = document.createElement('span'); ls.className = 'l'; ls.textContent = l;
    const vs = document.createElement('strong'); vs.textContent = v;
    div.append(gs, ls, vs);
    return div;
  }));
  $('oNoTime').hidden = c.timeKnown;
  $('oWheel').innerHTML = wheelSvg(wheelData(c), { size: 300, label: D.offer.title, still: true });

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

  if (state.focus.length) {
    const li = document.createElement('li');
    const s = document.createElement('strong');
    s.textContent = fill(D.offer.chapters, { list: state.focus.map((f) => D.quiz.focus[f]).join(', ') });
    const sp = document.createElement('span'); sp.className = 'mu'; sp.textContent = D.offer.chaptersDesc;
    li.append(s, sp);
    const list = $('oIncl');
    list.querySelector('[data-chapters]')?.remove();
    li.dataset.chapters = '';
    list.insertBefore(li, list.lastElementChild);
  }
}
function applyCouponUi() {
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
  let valid = false;
  try { valid = (await api<{ valid: boolean }>('/api/coupon', { code })).valid; } catch { /* treat as invalid */ }
  $('cErr').hidden = valid;
  if (valid) { state.coupon = code; save(); applyCouponUi(); }
});

$('oBuy').addEventListener('click', async () => {
  if (!state.coupon) {
    // Payments come in the next iteration (Stripe Checkout).
    $('oSoon').hidden = false;
    $('oSoon').scrollIntoView({ behavior: 'smooth', block: 'center' });
    return;
  }
  const btn = $<HTMLButtonElement>('oBuy');
  btn.disabled = true;
  $('oErr').hidden = true;
  try {
    if (!state.token) {
      const res = await api<{ token: string }>('/api/order', {
        lang, email: state.email, name: state.name ?? '', date: state.date, time: state.time ?? null,
        cityId: state.city!.id, focus: state.focus, status: state.status ?? '', coupon: state.coupon,
      });
      state.token = res.token; save();
    }
    show('upsell');
  } catch {
    $('oErr').hidden = false;
  }
  btn.disabled = false;
});

/* ---------- 10 upsell ---------- */
const forecastYear = (() => { const n = new Date(); return n.getMonth() >= 9 ? n.getFullYear() + 1 : n.getFullYear(); })();
const upsellProduct = () => (state.status === 'single' ? 'forecast' : 'partner');
let partnerCity: City | undefined;
const reportUrl = () => `/${lang}/report/?o=${encodeURIComponent(state.token ?? '')}`;
function goReport() {
  // The report arrives by email; next comes the subscription offer, then the final screen.
  show(state.sub ? 'done' : 'sub');
}
function renderUpsell() {
  if (!state.token) { show('offer'); return; }
  const prod = upsellProduct();
  $('uPartner').hidden = prod !== 'partner';
  $('uForecast').hidden = prod !== 'forecast';
  $('ufTitle').textContent = fill(D.upsell.forecastTitle, { year: forecastYear });
  $('uAdd').textContent = state.coupon
    ? fill(D.upsell.addFree, { code: state.coupon })
    : fill(D.upsell.add, { price: data.upPrices[prod] });
  checkPartner();
}
const upName = $<HTMLInputElement>('upName'), upDate = $<HTMLInputElement>('upDate');
const upTime = $<HTMLInputElement>('upTime'), upTimeUnknown = $<HTMLInputElement>('upTimeUnknown');
const upPlace = $<HTMLInputElement>('upPlace'), upList = $('upList');
upDate.max = new Date().toISOString().slice(0, 10);
function checkPartner() {
  if (upsellProduct() !== 'partner') { $<HTMLButtonElement>('uAdd').disabled = false; return; }
  upTime.disabled = upTimeUnknown.checked;
  const ok = !!upDate.value && !!partnerCity && (upTimeUnknown.checked || /^\d{2}:\d{2}$/.test(upTime.value));
  $<HTMLButtonElement>('uAdd').disabled = !ok;
}
[upName, upDate, upTime].forEach((el) => el.addEventListener('input', checkPartner));
upTimeUnknown.addEventListener('change', checkPartner);
let upTimer = 0;
upPlace.addEventListener('input', () => {
  partnerCity = undefined; checkPartner();
  clearTimeout(upTimer);
  const q = upPlace.value.trim();
  if (q.length < 2) { upList.replaceChildren(); return; }
  upTimer = window.setTimeout(async () => {
    let list: City[] = [];
    try { list = await api<City[]>(`/api/cities?q=${encodeURIComponent(q)}&lang=${lang}`); } catch { /* ignore */ }
    upList.replaceChildren(...list.map((c) => {
      const li = document.createElement('li');
      const b = document.createElement('button'); b.type = 'button'; b.setAttribute('role', 'option');
      const n = document.createElement('span'); n.textContent = c.name;
      const k = document.createElement('small'); k.textContent = countryOf(c);
      b.append(n, k);
      b.addEventListener('click', () => {
        partnerCity = c; upPlace.value = `${c.name}, ${countryOf(c)}`;
        upList.replaceChildren(); checkPartner();
      });
      li.append(b); return li;
    }));
  }, 220);
});
$('uAdd').addEventListener('click', async () => {
  const prod = upsellProduct();
  const btn = $<HTMLButtonElement>('uAdd');
  btn.disabled = true;
  $('uErr').hidden = true;
  try {
    await api(`/api/order/${encodeURIComponent(state.token!)}/add`, prod === 'partner'
      ? { product: 'partner', partner: { name: upName.value.trim(), date: upDate.value, time: upTimeUnknown.checked ? null : upTime.value, cityId: partnerCity!.id } }
      : { product: 'forecast' });
    goReport();
  } catch {
    $('uErr').hidden = false;
    btn.disabled = false;
  }
});
$('uNo').addEventListener('click', (e) => { e.preventDefault(); goReport(); });

/* ---------- 11 subscription ---------- */
function renderSub() {
  if (!state.token) { show('offer'); return; }
  $('sAdd').textContent = state.coupon ? fill(D.sub.ctaFree, { code: state.coupon }) : D.sub.cta;
  $('sPrice').hidden = !!state.coupon;
}
$('sAdd').addEventListener('click', async () => {
  const freq = (document.querySelector<HTMLInputElement>('input[name="freq"]:checked')?.value ?? 'daily') as 'daily' | 'weekly';
  if (!state.coupon) {
    // Paid subscriptions arrive with payments; until then the offer only shows the price.
    $('sErr').textContent = D.offer.soon; $('sErr').hidden = false; return;
  }
  const btn = $<HTMLButtonElement>('sAdd');
  btn.disabled = true; $('sErr').hidden = true;
  try {
    await api('/api/subscribe', { order: state.token, freq });
    state.sub = freq; save();
    show('done');
  } catch {
    $('sErr').textContent = D.ui.error; $('sErr').hidden = false;
  }
  btn.disabled = false;
});
$('sNo').addEventListener('click', (e) => { e.preventDefault(); show('done'); });

/* ---------- 12 done ---------- */
function renderDone() {
  if (!state.token) { show('offer'); return; }
  $('dDesc').textContent = fill(D.done.desc, { email: state.email ?? '' });
  $('dSub').hidden = !state.sub;
  if (state.sub) $('dSub').textContent = state.sub === 'daily' ? D.done.subDaily : D.done.subWeekly;
  $<HTMLAnchorElement>('dOpen').href = reportUrl();
}

/* ---------- resume from the summary email ---------- */
async function resume(token: string): Promise<boolean> {
  try {
    const L = await api<{ email: string; name: string; date: string; time: string | null; city: City | null; focus: string[]; status: string }>(
      `/api/lead/${encodeURIComponent(token)}`);
    if (!L.city || !L.date) return false;
    Object.assign(state, { email: L.email, name: L.name, date: L.date, time: L.time, city: L.city, focus: L.focus, status: L.status,
      token: undefined, sub: undefined });
    state.chart = await api<Chart>('/api/chart', { date: L.date, time: L.time, cityId: L.city.id });
    save();
    history.replaceState(null, '', `${location.pathname}#offer`);
    return true;
  } catch { return false; }
}

/* ---------- restore ---------- */
function restore() {
  if (state.date) {
    const [y, m, d] = state.date.split('-').map(Number);
    dYear.value = String(y); dMonth.value = String(m); dDay.value = String(d); onDate();
  }
  if (state.time === null) tUnknown.checked = true; else if (state.time) tTime.value = state.time;
  onTime();
  if (state.city) { pInput.value = `${state.city.name}, ${countryOf(state.city)}`; renderCities([state.city]); nextBtn('place')!.disabled = false; }
  if (state.name) { nInput.value = state.name; nextBtn('name')!.disabled = false; }
  focusBoxes.forEach((b) => (b.checked = state.focus.includes(b.value)));
  nextBtn('focus')!.disabled = state.focus.length === 0;
  document.querySelectorAll<HTMLInputElement>('input[name="status"]').forEach((r) => (r.checked = r.value === state.status));
  const hash = location.hash.slice(1) as Step;
  applyCouponUi();
  const start: Step = STEPS.includes(hash) && hash !== 'calc' && (hash !== 'offer' || state.chart) && (hash !== 'email' || state.chart) && (!['upsell', 'sub', 'done'].includes(hash) || state.token) ? hash : 'date';
  history.replaceState({ step: start }, '', `#${start}`);
  show(start, false);
}
const resumeToken = new URLSearchParams(location.search).get('r');
if (resumeToken) resume(resumeToken).then(restore); else restore();
