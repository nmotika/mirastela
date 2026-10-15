/**
 * Natal chart wheel as an SVG string. Works on the server (Astro) and in the browser.
 * Orientation: Ascendant on the left, zodiac running counter-clockwise, as in a classic chart.
 */
export interface WheelPlanet { id: string; lon: number }
export interface WheelAspect { a: string; b: string; type: string }
export interface WheelData {
  planets: WheelPlanet[];
  asc?: number | null;
  cusps?: number[] | null;
  aspects?: WheelAspect[];
}

const SIGN_GLYPHS = ['♈', '♉', '♊', '♋', '♌', '♍', '♎', '♏', '♐', '♑', '♒', '♓'];
const PLANET_GLYPHS: Record<string, string> = {
  sun: '☉', moon: '☽', mercury: '☿', venus: '♀', mars: '♂', jupiter: '♃',
  saturn: '♄', uranus: '♅', neptune: '♆', pluto: '♇', node: '☊',
};
const VS = '︎'; // text presentation, never emoji

const R_OUT = 152, R_SIGN = 130, R_PLANET = 106, R_IN = 74;

function xy(theta: number, r: number): [number, number] {
  const a = (theta * Math.PI) / 180;
  return [+(r * Math.cos(a)).toFixed(2), +(r * Math.sin(a)).toFixed(2)];
}

export function wheelSvg(data: WheelData, opts: { size?: number; label?: string; animate?: boolean; still?: boolean } = {}): string {
  const size = opts.size ?? 320;
  const asc = data.asc ?? 0;
  const theta = (lon: number) => 180 - (lon - asc); // SVG angle, y axis down
  const anim = opts.animate ? ' class="dr" pathLength="1"' : '';
  const out: string[] = [];

  out.push(`<svg viewBox="-160 -160 320 320" width="${size}" height="${size}" role="img" aria-label="${opts.label ?? ''}" class="wheel${opts.still ? ' static' : ''}">`);
  out.push(`<g class="wl">`);
  for (const [r, op] of [[R_OUT, 1], [R_SIGN, 1], [R_IN, 0.6]] as const) {
    out.push(`<circle${anim} r="${r}" stroke-opacity="${op}" transform="rotate(-90)"/>`);
  }
  out.push('</g><g class="wl fi">');
  for (let i = 0; i < 12; i++) {
    const [x1, y1] = xy(theta(i * 30), R_SIGN);
    const [x2, y2] = xy(theta(i * 30), R_OUT);
    out.push(`<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}"/>`);
  }
  out.push('</g>');

  if (data.cusps?.length === 12) {
    out.push('<g class="wl fi" stroke-opacity=".4" stroke-width=".6">');
    data.cusps.forEach((c) => {
      const [x1, y1] = xy(theta(c), R_IN);
      const [x2, y2] = xy(theta(c), R_SIGN);
      out.push(`<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}"/>`);
    });
    out.push('</g>');
  }
  if (data.asc != null) {
    const [x, y] = xy(theta(asc), 160);
    const [xi, yi] = xy(theta(asc), R_IN);
    out.push(`<line class="fi" x1="${xi}" y1="${yi}" x2="${x}" y2="${y}" stroke="#D9B26A" stroke-width="1.4"/>`);
  }

  out.push('<g class="gl fi" fill="#D9B26A" font-size="12" text-anchor="middle" dominant-baseline="central">');
  SIGN_GLYPHS.forEach((g, i) => {
    const [x, y] = xy(theta(i * 30 + 15), 141);
    out.push(`<text x="${x}" y="${y}">${g}${VS}</text>`);
  });
  out.push('</g>');

  // Aspect lines between planets (inner circle)
  if (data.aspects?.length) {
    const lonOf = Object.fromEntries(data.planets.map((p) => [p.id, p.lon]));
    out.push('<g class="fi" stroke="#D9B26A" stroke-opacity=".45" stroke-width=".6">');
    for (const a of data.aspects) {
      if (a.type === 'conjunction' || !(a.a in lonOf) || !(a.b in lonOf)) continue;
      const [x1, y1] = xy(theta(lonOf[a.a]), R_IN);
      const [x2, y2] = xy(theta(lonOf[a.b]), R_IN);
      const dash = a.type === 'square' || a.type === 'opposition' ? '' : ' stroke-dasharray="2 2"';
      out.push(`<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}"${dash}/>`);
    }
    out.push('</g>');
  }

  // Planets: spread glyphs that would overlap (min 8° apart on the ring)
  const placed = [...data.planets].filter((p) => p.id in PLANET_GLYPHS).sort((a, b) => a.lon - b.lon)
    .map((p) => ({ ...p, pos: p.lon }));
  for (let pass = 0; pass < 3; pass++) {
    for (let i = 1; i < placed.length; i++) {
      if (placed[i].pos - placed[i - 1].pos < 8) placed[i].pos = placed[i - 1].pos + 8;
    }
  }
  out.push('<g class="wl fi">');
  for (const p of placed) {
    const [x1, y1] = xy(theta(p.lon), R_SIGN);
    const [x2, y2] = xy(theta(p.lon), R_SIGN - 7);
    out.push(`<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}"/>`);
  }
  out.push('</g><g class="gl fi" fill="#F3EEE3" font-size="15" text-anchor="middle" dominant-baseline="central">');
  for (const p of placed) {
    const [x, y] = xy(theta(p.pos), R_PLANET);
    out.push(`<text x="${x}" y="${y}">${PLANET_GLYPHS[p.id]}${VS}</text>`);
  }
  out.push('</g><circle r="2.5" fill="#D9B26A"/></svg>');
  return out.join('');
}

/** Fixed example chart for decorative use on the landing page. */
export const SAMPLE_WHEEL: WheelData = {
  asc: 61,
  planets: [
    { id: 'sun', lon: 353.6 }, { id: 'moon', lon: 138.4 }, { id: 'mercury', lon: 329.4 },
    { id: 'venus', lon: 313.1 }, { id: 'mars', lon: 133.5 }, { id: 'jupiter', lon: 254.5 },
    { id: 'saturn', lon: 346.9 }, { id: 'uranus', lon: 299.3 }, { id: 'neptune', lon: 295.8 },
    { id: 'pluto', lon: 240.9 },
  ],
  cusps: [61, 82, 101, 121, 144, 175, 241, 262, 281, 301, 324, 355],
  aspects: [
    { a: 'venus', b: 'mars', type: 'opposition' }, { a: 'mars', b: 'jupiter', type: 'trine' },
    { a: 'jupiter', b: 'saturn', type: 'square' }, { a: 'uranus', b: 'pluto', type: 'sextile' },
  ],
};
