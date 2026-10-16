/** Zodiac glyphs and date ranges (tropical, the usual boundaries; exact days vary by a day year to year). */
export const SIGN_GLYPHS = ['♈', '♉', '♊', '♋', '♌', '♍', '♎', '♏', '♐', '♑', '♒', '♓'].map((g) => `${g}︎`);
const STARTS: [number, number][] = [[3, 21], [4, 20], [5, 21], [6, 21], [7, 23], [8, 23], [9, 23], [10, 23], [11, 22], [12, 22], [1, 20], [2, 19]];

export function signRange(intl: string, i: number): string {
  const fmt = new Intl.DateTimeFormat(intl, { day: 'numeric', month: 'short', timeZone: 'UTC' });
  const [m1, d1] = STARTS[i];
  const [m2, d2] = STARTS[(i + 1) % 12];
  const end = new Date(Date.UTC(2001, m2 - 1, d2 - 1));
  return `${fmt.format(new Date(Date.UTC(2001, m1 - 1, d1)))} – ${fmt.format(end)}`;
}
