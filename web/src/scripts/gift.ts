// Gift page: start the payment, then show the printable card (after Stripe, or from the link in the email).
import { trackInfo, fbTrack } from './track';

const cfg = JSON.parse(document.getElementById('gift-data')!.textContent!);
const G = cfg.g;
const $ = <T extends HTMLElement = HTMLElement>(id: string) => document.getElementById(id) as T;
const plan = () => (document.querySelector<HTMLInputElement>('input[name="gp"]:checked')?.value ?? 'natal') as 'natal' | 'bundle';

document.querySelectorAll<HTMLInputElement>('input[name="gp"]').forEach((r) => r.addEventListener('change', () => {
  $('gBuy').textContent = G.buy.replace('{price}', cfg.prices[plan()]);
}));

$('gForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const email = $<HTMLInputElement>('gEmail');
  const ok = /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email.value.trim());
  email.setAttribute('aria-invalid', String(!ok));
  if (!ok) { email.focus(); return; }
  const btn = $<HTMLButtonElement>('gBuy');
  btn.disabled = true; $('gErr').hidden = true;
  try {
    const res = await fetch('/api/gift', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({
      lang: cfg.lang, email: email.value.trim(), product: plan(), toName: $<HTMLInputElement>('gTo').value,
      fromName: $<HTMLInputElement>('gFrom').value, message: $<HTMLTextAreaElement>('gMsg').value, track: trackInfo(),
    }) });
    if (!res.ok) throw new Error(String(res.status));
    const { checkout } = await res.json();
    fbTrack('InitiateCheckout', {});
    location.href = checkout;
  } catch {
    $('gErr').hidden = false; btn.disabled = false;
  }
});

interface GiftInfo { code: string; product: 'natal' | 'bundle'; toName: string; fromName: string; message: string; expires: string }

function showCard(g: GiftInfo) {
  $('buyView').hidden = true; $('doneView').hidden = false;
  $('cCode').textContent = g.code;
  $('cProduct').textContent = cfg.names[g.product] ?? '';
  const set = (id: string, text: string) => { $(id).textContent = text; $(id).hidden = !text; };
  set('cFor', g.toName ? G.cardFor.replace('{name}', g.toName) : '');
  set('cMsg', g.message);
  set('cFrom', g.fromName ? `${G.from}: ${g.fromName}` : '');
  const [y, m, d] = g.expires.split('-').map(Number);
  const date = new Intl.DateTimeFormat(cfg.intl, { day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC' }).format(new Date(Date.UTC(y, m - 1, d)));
  $('cValid').textContent = G.validUntil.replace('{date}', date);
  window.scrollTo({ top: 0 });
}

$('gPrint').addEventListener('click', () => window.print());
$('gDown').addEventListener('click', async () => {
  const blob = await cardImage();
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob); a.download = `mirastela-${$('cCode').textContent}.png`;
  document.body.append(a); a.click(); a.remove();
});

/** The card as an image (1600x1000) to send in a message. */
async function cardImage(): Promise<Blob> {
  try { await Promise.all(['500 60px Newsreader', 'italic 400 40px Newsreader', '700 30px Manrope'].map((f) => document.fonts.load(f, 'Aąćęłčšž'))); } catch { /* system fonts */ }
  const W = 1600, H = 1000, cv = document.createElement('canvas');
  cv.width = W; cv.height = H;
  const g = cv.getContext('2d')!;
  const bg = g.createRadialGradient(W / 2, 0, 50, W / 2, H / 2, W * 0.8);
  bg.addColorStop(0, '#FFF9EE'); bg.addColorStop(1, '#F6F1E7');
  g.fillStyle = bg; g.fillRect(0, 0, W, H);
  g.strokeStyle = '#DDD2BC'; g.lineWidth = 3; g.strokeRect(30, 30, W - 60, H - 60);
  g.textAlign = 'center';
  g.fillStyle = '#7E5E1C'; g.font = '48px serif'; g.fillText('✦', W / 2, 120);
  g.font = '700 26px Manrope, sans-serif'; g.fillText('M I R A S T E L A', W / 2, 170);
  g.fillStyle = '#1A1A24'; g.font = '500 64px Newsreader, Georgia, serif'; g.fillText($('cTitle').textContent ?? '', W / 2, 270);
  let y = 340;
  if (!$('cFor').hidden) { g.font = '400 44px Newsreader, Georgia, serif'; g.fillStyle = '#24222C'; g.fillText($('cFor').textContent ?? '', W / 2, y); y += 70; }
  if (!$('cMsg').hidden) {
    g.font = 'italic 400 38px Newsreader, Georgia, serif'; g.fillStyle = '#24222C';
    for (const line of wrap(g, $('cMsg').textContent ?? '', 1100).slice(0, 3)) { g.fillText(line, W / 2, y); y += 52; }
    y += 10;
  }
  if (!$('cFrom').hidden) { g.font = '600 28px Manrope, sans-serif'; g.fillStyle = '#5A5566'; g.fillText($('cFrom').textContent ?? '', W / 2, y); y += 50; }
  y = Math.max(y + 20, 600);
  g.setLineDash([14, 10]); g.strokeStyle = '#7E5E1C'; g.lineWidth = 3;
  g.strokeRect(W / 2 - 330, y, 660, 150); g.setLineDash([]);
  g.fillStyle = '#5A5566'; g.font = '700 22px Manrope, sans-serif'; g.fillText(G.code.toUpperCase(), W / 2, y + 42);
  g.fillStyle = '#1A1A24'; g.font = '700 54px Manrope, sans-serif'; g.fillText($('cCode').textContent ?? '', W / 2, y + 102);
  g.fillStyle = '#5A5566'; g.font = '600 22px Manrope, sans-serif'; g.fillText($('cProduct').textContent ?? '', W / 2, y + 135);
  g.font = '500 24px Manrope, sans-serif';
  let yy = y + 200;
  for (const line of wrap(g, G.howTo, 1200)) { g.fillText(line, W / 2, yy); yy += 34; }
  g.fillText($('cValid').textContent ?? '', W / 2, yy + 6);
  return new Promise((ok, fail) => cv.toBlob((b) => (b ? ok(b) : fail(new Error('canvas'))), 'image/png'));
}

function wrap(g: CanvasRenderingContext2D, text: string, max: number): string[] {
  const out: string[] = []; let cur = '';
  for (const w of text.split(/\s+/)) {
    const t = cur ? `${cur} ${w}` : w;
    if (g.measureText(t).width > max && cur) { out.push(cur); cur = w; } else cur = t;
  }
  if (cur) out.push(cur);
  return out;
}

// Back from Stripe (?paid=session), from the email (?code=...), or a cancelled payment.
(async () => {
  const q = new URLSearchParams(location.search);
  if (q.get('cancel')) $('gCancel').hidden = false;
  try {
    if (q.get('paid')) {
      const res = await fetch(`/api/checkout/confirm?session=${encodeURIComponent(q.get('paid')!)}`);
      if (res.ok) {
        const out = await res.json();
        if (out.gift) {
          showCard(out.gift);
          fbTrack('Purchase', { value: out.value, currency: out.currency }, out.eventId);
          window.gtag?.('event', 'purchase', { transaction_id: out.eventId, value: out.value, currency: out.currency, items: [{ item_id: `gift_${out.product}` }] });
          history.replaceState(null, '', `${location.pathname}?code=${out.gift.code}`);
        }
      }
    } else if (q.get('code')) {
      const res = await fetch(`/api/gift/${encodeURIComponent(q.get('code')!)}`);
      if (res.ok) showCard(await res.json());
    }
  } catch { /* stay on the buy view */ }
})();
