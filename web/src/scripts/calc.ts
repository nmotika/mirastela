// Free Ascendant and Moon sign calculator (an SEO tool page). Uses the same API as the funnel and,
// on the way to the funnel, hands over the birth data so the visitor does not type it again.
import { SIGN_GLYPHS } from './zodiac';
import { fill } from '../i18n/fill';

interface City { id: number; name: string; country: string; countryName: string; tz: string }
interface Chart { timeKnown: boolean; planets: { id: string; signIndex: number }[]; angles: { asc: { signIndex: number } } | null }

// Astro bundles page scripts per route, so this also loads on the other hubs: run only on the calculator.
const dataEl = document.getElementById('calc-data');
if (dataEl) init(JSON.parse(dataEl.textContent!));

function init(cfg: any) {
  const S = cfg.s;
  const $ = <T extends HTMLElement = HTMLElement>(id: string) => document.getElementById(id) as T;
  const place = $<HTMLInputElement>('cPlace');
  const list = $('cList');
  const err = $('cErr');
  let city: City | null = null;
  let timer = 0;
  const regionNames = (() => { try { return new Intl.DisplayNames([document.documentElement.lang], { type: 'region' }); } catch { return null; } })();
  const label = (c: City) => `${c.name}, ${regionNames?.of(c.country) ?? c.countryName}`;

  function showErr(msg: string) { err.textContent = msg; err.hidden = !msg; }

  place.addEventListener('input', () => {
    city = null;
    clearTimeout(timer);
    const q = place.value.trim();
    if (q.length < 2) { list.hidden = true; place.setAttribute('aria-expanded', 'false'); return; }
    timer = window.setTimeout(async () => {
      try {
        const res = await fetch(`/api/cities?q=${encodeURIComponent(q)}&lang=${cfg.lang}`);
        const items: City[] = res.ok ? await res.json() : [];
        list.replaceChildren(...items.slice(0, 8).map((c) => {
          const b = document.createElement('button');
          b.type = 'button'; b.setAttribute('role', 'option'); b.textContent = label(c);
          b.addEventListener('click', () => { city = c; place.value = label(c); list.hidden = true; place.setAttribute('aria-expanded', 'false'); showErr(''); });
          return b;
        }));
        list.hidden = items.length === 0;
        place.setAttribute('aria-expanded', String(items.length > 0));
      } catch { list.hidden = true; }
    }, 250);
  });

  $<HTMLInputElement>('cNoTime').addEventListener('change', (e) => {
    const t = $<HTMLInputElement>('cTime');
    t.disabled = (e.target as HTMLInputElement).checked;
    if (t.disabled) t.value = '';
  });

  function item(glyph: string, title: string, value: string, text: string) {
    const el = document.createElement('div');
    el.className = 'ci';
    el.innerHTML = `<span class="gl" aria-hidden="true"></span><div><b></b><strong></strong><p></p></div>`;
    el.querySelector('.gl')!.textContent = glyph;
    el.querySelector('b')!.textContent = title;
    el.querySelector('strong')!.textContent = value;
    el.querySelector('p')!.textContent = text;
    return el;
  }

  $('calcForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const date = $<HTMLInputElement>('cDate').value;
    const noTime = $<HTMLInputElement>('cNoTime').checked;
    const time = noTime ? null : ($<HTMLInputElement>('cTime').value || null);
    if (!date) { $('cDate').focus(); return; }
    if (!city) { showErr(S.placeErr); place.focus(); return; }
    showErr('');
    const btn = $<HTMLButtonElement>('cGo');
    btn.disabled = true;
    try {
      const res = await fetch('/api/chart', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ date, time, cityId: city.id }) });
      if (!res.ok) throw new Error(String(res.status));
      const c: Chart = await res.json();
      const A = cfg.astro;
      const sun = c.planets.find((p) => p.id === 'sun')!.signIndex;
      const moon = c.planets.find((p) => p.id === 'moon')!.signIndex;
      const out = $('cRes');
      const sunItem = item(SIGN_GLYPHS[sun], S.sun, A.signs[sun], fill(cfg.p1, { signIn: A.signIn[sun], trait: A.traits[sun] }));
      // On the Moon sign page the Moon comes first, with a short reading of the Moon in that sign.
      const nodes: HTMLElement[] = cfg.mode === 'moon'
        ? [item(SIGN_GLYPHS[moon], S.moon, A.signs[moon], `${S.explain.moon} ${fill(cfg.p3, { moonIn: A.signIn[moon], moonTrait: A.traits[moon] })}`), sunItem]
        : [sunItem, item(SIGN_GLYPHS[moon], S.moon, A.signs[moon], S.explain.moon)];
      if (c.timeKnown && c.angles) nodes.push(item(SIGN_GLYPHS[c.angles.asc.signIndex], S.asc, A.signs[c.angles.asc.signIndex], S.explain.asc));
      const notes = c.timeKnown ? [] : [S.ascNeedsTime, S.moonUnsure];
      for (const n of notes) { const p = document.createElement('p'); p.className = 'note'; p.textContent = n; nodes.push(p); }
      const go = document.createElement('a');
      go.className = 'btn'; go.href = cfg.start; go.textContent = document.querySelector('.pcta .btn')?.textContent ?? 'Start';
      go.addEventListener('click', () => {
        // Hand the birth data over to the funnel (same tab, same storage it uses itself).
        try { sessionStorage.setItem('mirastela-funnel', JSON.stringify({ focus: [], date, time, city })); } catch { /* ignore */ }
      });
      nodes.push(go);
      out.replaceChildren(...nodes);
      out.hidden = false;
      out.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } catch {
      showErr(S.error);
    } finally {
      btn.disabled = false;
    }
  });
}
