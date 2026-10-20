// "My Sun, Moon and Ascendant" card for Instagram/Facebook stories (1080x1920), drawn in the browser.
// Shared through the system share sheet where files can be shared (phones), otherwise downloaded.
import { SIGN_GLYPHS } from './zodiac';

export interface BigThree {
  title: string; footer: string;
  rows: { label: string; sign: string; glyph: number }[];
}

const W = 1080, H = 1920;
const GOLD = '#D9B26A', INK = '#F3EEE3', MUTED = '#A9B0C6', BG = '#0B1020';

function rnd(seed: number) {
  return () => { seed = (seed * 16807) % 2147483647; return seed / 2147483647; };
}

export async function drawBigThree(card: BigThree): Promise<Blob> {
  try {
    await Promise.all(['500 80px Newsreader', '400 80px Newsreader', '700 40px Manrope', '600 40px Manrope', '80px "Noto Sans Symbols"']
      .map((f) => document.fonts.load(f, 'Aa♈♉♊♋♌♍♎♏♐♑♒♓ąęćłńóśźżčšž')));
  } catch { /* fall back to system fonts */ }
  const cv = document.createElement('canvas');
  cv.width = W; cv.height = H;
  const g = cv.getContext('2d')!;

  // Night sky: gradient, stars, faint wheel.
  const bg = g.createRadialGradient(W * 0.7, H * 0.95, 50, W * 0.5, H * 0.6, H);
  bg.addColorStop(0, '#1C2550'); bg.addColorStop(0.55, BG); bg.addColorStop(1, '#070A16');
  g.fillStyle = bg; g.fillRect(0, 0, W, H);
  const r = rnd(card.rows.map((x) => x.glyph).reduce((a, b) => a * 13 + b + 1, 7));
  for (let i = 0; i < 160; i++) {
    g.globalAlpha = 0.25 + r() * 0.6;
    g.fillStyle = r() > 0.85 ? GOLD : INK;
    g.beginPath(); g.arc(r() * W, r() * H, r() * 2.2 + 0.4, 0, Math.PI * 2); g.fill();
  }
  g.globalAlpha = 0.12; g.strokeStyle = GOLD; g.lineWidth = 2;
  for (const rad of [470, 400, 300]) { g.beginPath(); g.arc(W / 2, 280, rad, 0, Math.PI * 2); g.stroke(); }
  for (let k = 0; k < 12; k++) {
    const a = (k / 12) * Math.PI * 2;
    g.beginPath(); g.moveTo(W / 2 + Math.cos(a) * 400, 280 + Math.sin(a) * 400); g.lineTo(W / 2 + Math.cos(a) * 470, 280 + Math.sin(a) * 470); g.stroke();
  }
  g.globalAlpha = 1;

  // Logo star + brand.
  const star = (x: number, y: number, s: number) => {
    g.fillStyle = GOLD; g.beginPath();
    g.moveTo(x, y - s); g.lineTo(x + s * 0.2, y - s * 0.2); g.lineTo(x + s, y); g.lineTo(x + s * 0.2, y + s * 0.2);
    g.lineTo(x, y + s); g.lineTo(x - s * 0.2, y + s * 0.2); g.lineTo(x - s, y); g.lineTo(x - s * 0.2, y - s * 0.2); g.closePath(); g.fill();
  };
  star(W / 2, 200, 46);

  // Title, wrapped.
  g.fillStyle = INK; g.textAlign = 'center'; g.font = '400 82px Newsreader, Georgia, serif';
  const words = card.title.split(' ');
  const lines: string[] = [];
  let cur = '';
  for (const w of words) {
    const t = cur ? `${cur} ${w}` : w;
    if (g.measureText(t).width > W - 160 && cur) { lines.push(cur); cur = w; } else cur = t;
  }
  lines.push(cur);
  lines.forEach((l, i) => g.fillText(l, W / 2, 360 + i * 96));

  // Three rows.
  let y = 360 + lines.length * 96 + 90; // stays clear of the story UI at the top and bottom
  for (const row of card.rows) {
    const h = 270;
    g.fillStyle = 'rgba(246,241,231,0.06)'; g.strokeStyle = 'rgba(217,178,106,0.45)'; g.lineWidth = 2;
    roundRect(g, 90, y, W - 180, h, 36); g.fill(); g.stroke();
    g.strokeStyle = GOLD; g.beginPath(); g.arc(240, y + h / 2, 92, 0, Math.PI * 2); g.stroke();
    g.fillStyle = GOLD; g.font = '96px "Noto Sans Symbols", "Segoe UI Symbol", serif'; g.textAlign = 'center'; g.textBaseline = 'middle';
    g.fillText(SIGN_GLYPHS[row.glyph].replace('︎', ''), 240, y + h / 2 + 6);
    g.textAlign = 'left'; g.textBaseline = 'alphabetic';
    g.fillStyle = GOLD; g.font = '700 34px Manrope, sans-serif';
    g.fillText(spaced(row.label.toUpperCase()), 380, y + 108);
    g.fillStyle = INK; g.font = '500 84px Newsreader, Georgia, serif';
    g.fillText(row.sign, 380, y + 195);
    y += h + 30;
  }

  // Footer.
  g.textAlign = 'center'; g.fillStyle = MUTED; g.font = '600 38px Manrope, sans-serif';
  g.fillText(card.footer, W / 2, y + 60);
  return new Promise((ok, fail) => cv.toBlob((b) => (b ? ok(b) : fail(new Error('canvas'))), 'image/png'));
}

function spaced(s: string) { return s.split('').join(String.fromCharCode(8202)); }

function roundRect(g: CanvasRenderingContext2D, x: number, y: number, w: number, h: number, r: number) {
  g.beginPath(); g.moveTo(x + r, y); g.arcTo(x + w, y, x + w, y + h, r); g.arcTo(x + w, y + h, x, y + h, r);
  g.arcTo(x, y + h, x, y, r); g.arcTo(x, y, x + w, y, r); g.closePath();
}

/** Share the card (phones) or download it (desktop). Returns how it went. */
export async function shareBigThree(card: BigThree, text: string, url: string): Promise<'shared' | 'downloaded' | 'cancelled'> {
  const blob = await drawBigThree(card);
  const file = new File([blob], 'mirastela.png', { type: 'image/png' });
  const nav = navigator as Navigator & { canShare?: (d: ShareData) => boolean };
  if (nav.share && nav.canShare?.({ files: [file] })) {
    try { await nav.share({ files: [file], text, url }); return 'shared'; } catch { return 'cancelled'; }
  }
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob); a.download = 'mirastela.png';
  document.body.append(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(a.href), 5000);
  return 'downloaded';
}
