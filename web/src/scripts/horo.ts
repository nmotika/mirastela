// Daily horoscope pages. Today's text is normally already in the HTML (filled at the edge);
// this script only fills it when it is missing and handles the yesterday/today/tomorrow tabs.
interface Daily { day: string; signs: { general: string; love: string; work: string }[] }
const cfg = JSON.parse(document.getElementById('horo-data')!.textContent!);
const H = cfg.d.horo;
const read = document.querySelector<HTMLElement>('.hread');
const cache: Record<string, Daily> = {};

function fmtDay(iso: string): string {
  const [y, m, d] = iso.split('-').map(Number);
  const s = new Intl.DateTimeFormat(document.documentElement.lang, { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC' })
    .format(new Date(Date.UTC(y, m - 1, d)));
  return s.charAt(0).toUpperCase() + s.slice(1);
}
function zagrebDay(offset: number): string {
  const now = new Date(Date.now() + offset * 86400000);
  return new Intl.DateTimeFormat('en-CA', { timeZone: 'Europe/Zagreb', year: 'numeric', month: '2-digit', day: '2-digit' }).format(now);
}
async function fetchDay(day: string, tries = 0): Promise<Daily> {
  if (cache[day]) return cache[day];
  const res = await fetch(`/api/daily?lang=${cfg.lang}&day=${day}`);
  if (res.status === 202 && tries < 20) {
    await new Promise((r) => setTimeout(r, 5000));
    return fetchDay(day, tries + 1);
  }
  if (!res.ok) throw new Error(String(res.status));
  return (cache[day] = await res.json());
}
function setDate(day: string) {
  document.querySelectorAll<HTMLElement>('[data-hdate]').forEach((el) => (el.textContent = fmtDay(day)));
}
let shown = 0; // the latest tab click wins, even if an earlier day finishes loading later
async function showDay(offset: number) {
  const run = ++shown;
  const day = zagrebDay(offset);
  setDate(day);
  if (!read) return;
  read.classList.remove('ready');
  const st = document.getElementById('hStatus')!;
  st.textContent = H.loading;
  read.querySelectorAll<HTMLElement>('[data-h]').forEach((p) => (p.textContent = ''));
  try {
    const d = await fetchDay(day);
    if (run !== shown) return;
    const s = d.signs[cfg.idx];
    read.querySelectorAll<HTMLElement>('[data-h]').forEach((p) => (p.textContent = s[p.dataset.h as 'general' | 'love' | 'work']));
    read.classList.add('ready');
  } catch {
    if (run === shown) st.textContent = H.error;
  }
}

const h1 = document.querySelector<HTMLElement>('main h1, h1');
const h1Today = h1?.textContent ?? '';
if (read) {
  document.querySelectorAll<HTMLButtonElement>('[data-day]').forEach((b) => b.addEventListener('click', () => {
    document.querySelectorAll('[data-day]').forEach((x) => x.setAttribute('aria-selected', String(x === b)));
    // "Sign: horoscope for today" would be wrong on the yesterday/tomorrow tabs.
    if (h1) h1.textContent = +b.dataset.day! === 0 ? h1Today : `${h1Today.split(':')[0]}: ${b.textContent?.trim()}`;
    showDay(+b.dataset.day!);
  }));
  if (read.dataset.ssr === '1') read.classList.add('ready');
  else showDay(0);
}
const dateEl = document.querySelector<HTMLElement>('[data-hdate]');
if (dateEl && !dateEl.textContent!.trim()) setDate(zagrebDay(0));
