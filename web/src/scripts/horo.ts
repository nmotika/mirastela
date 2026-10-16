import { fill } from '../i18n/fill';

interface Daily {
  day: string; model: string;
  signs: { general: string; love: string; work: string }[];
  sky: { planets: { id: string; signIndex: number; deg: number; retro: boolean }[]; moonIngress: string | null };
}
const cfg = JSON.parse(document.getElementById('horo-data')!.textContent!);
const H = cfg.d.horo, A = cfg.d.astro;
const $ = (id: string) => document.getElementById(id);

function skyText(d: Daily): string {
  const parts = d.sky.planets.map((p) => `${A.planets[p.id]} ${A.signIn[p.signIndex]}`).join(' · ');
  const retro = d.sky.planets.filter((p) => p.retro).map((p) => A.planets[p.id]);
  return [parts + '.', d.sky.moonIngress ? fill(H.moonChange, { time: d.sky.moonIngress }) : '',
    retro.length ? fill(H.retro, { list: retro.join(', ') }) : ''].filter(Boolean).join(' ');
}

async function load() {
  try {
    const res = await fetch(`/api/daily?lang=${cfg.lang}`);
    if (!res.ok) throw new Error(String(res.status));
    const d: Daily = await res.json();
    const [y, m, dd] = d.day.split('-').map(Number);
    $('hDate')!.textContent = new Intl.DateTimeFormat(document.documentElement.lang, { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC' })
      .format(new Date(Date.UTC(y, m - 1, dd)));
    $('hSky')!.textContent = skyText(d);
    if (cfg.page === 'index') {
      document.querySelectorAll<HTMLElement>('[data-teaser]').forEach((el) => {
        const s = d.signs[+el.dataset.teaser!];
        el.textContent = s.general.split(/(?<=[.!?])\s/)[0];
      });
    } else {
      const s = d.signs[cfg.idx];
      $('hGeneral')!.textContent = s.general;
      $('hLove')!.textContent = s.love;
      $('hWork')!.textContent = s.work;
      $('hStatus')!.hidden = true;
      $('hBody')!.hidden = false;
    }
  } catch {
    $('hSky')!.textContent = H.error;
    const st = $('hStatus');
    if (st) st.textContent = H.error;
  }
}
load();
