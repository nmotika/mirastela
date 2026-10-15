/** Replace {key} placeholders. {Key} with a capital first letter capitalises the value. */
export function fill(tpl: string, vars: Record<string, string | number>): string {
  return tpl.replace(/\{(\w+)\}/g, (m, k: string) => {
    const lower = k[0].toLowerCase() + k.slice(1);
    if (k in vars) return String(vars[k]);
    if (lower in vars) {
      const v = String(vars[lower]);
      return v.charAt(0).toUpperCase() + v.slice(1);
    }
    return m;
  });
}

/** Hungarian definite article before a number: az 1. and az 5. (egy, öt), else a. */
export function huArticle(n: number): string {
  return n === 1 || n === 5 || (n >= 50 && n < 60) ? 'az' : 'a';
}
