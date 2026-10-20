import { LOCALES, type Lang } from '../i18n/config';
import { t } from '../i18n';
import { SEO } from '../i18n/lang/seo';

// Generated page texts (api/seo_gen.py). A language or page that is not generated yet is simply not built.
export const SIGN_KEYS = ['aries', 'taurus', 'gemini', 'cancer', 'leo', 'virgo', 'libra', 'scorpio', 'sagittarius', 'capricorn', 'aquarius', 'pisces'];
export type Kind = 'year' | 'signs' | 'compat';
export interface Faq { q: string; a: string }
export type Page = Record<string, string> & { faq?: Faq[] };

const files = import.meta.glob<Record<string, Page>>('../data/seo/*/*.json', { eager: true, import: 'default' });
const DATA: Record<Kind, Partial<Record<Lang, Record<string, Page>>>> = { year: {}, signs: {}, compat: {} };
for (const [path, data] of Object.entries(files)) {
  const m = /seo\/(year|signs|compat)\/([a-z]{2})\.json$/.exec(path);
  if (m) DATA[m[1] as Kind][m[2] as Lang] = data;
}

export function page(kind: Kind, lang: Lang, key: string): Page | undefined {
  return DATA[kind][lang]?.[key];
}
export function langsWith(kind: Kind, key: string): Lang[] {
  return LOCALES.filter((l) => !!DATA[kind][l]?.[key]);
}
export function hasAny(kind: Kind, lang: Lang): boolean {
  return Object.keys(DATA[kind][lang] ?? {}).length > 0;
}
export const pairKey = (a: number, b: number) => `${SIGN_KEYS[Math.min(a, b)]}-${SIGN_KEYS[Math.max(a, b)]}`;
export const signSlug = (lang: Lang, i: number) => t(lang).horo.signSlugs[i];
export const pairSlug = (lang: Lang, a: number, b: number) => `${signSlug(lang, Math.min(a, b))}-${signSlug(lang, Math.max(a, b))}`;

/** Path (without /lang/) of a page in every language; languages without the page get their hub. */
export function pathsFor(kind: Kind | 'calc', sub: (l: Lang) => string, key?: string): Record<Lang, string> {
  return Object.fromEntries(LOCALES.map((l) => {
    const hub = `${SEO[l].slugs[kind]}/`;
    if (!key || kind === 'calc') return [l, sub(l) ? `${hub}${sub(l)}/` : hub];
    return [l, page(kind, l, key) ? `${hub}${sub(l)}/` : hub];
  })) as Record<Lang, string>;
}

export const paragraphs = (text = '') => text.split(/\n\s*\n/).map((p) => p.trim()).filter(Boolean);

export function ldJson(items: object[]): string {
  return JSON.stringify(items.length === 1 ? items[0] : items).replace(/</g, '\\u003c');
}
export function faqLd(faq: Faq[] = []) {
  return { '@context': 'https://schema.org', '@type': 'FAQPage', mainEntity: faq.map((f) => ({ '@type': 'Question', name: f.q, acceptedAnswer: { '@type': 'Answer', text: f.a } })) };
}
export function crumbsLd(items: [string, string][]) {
  return { '@context': 'https://schema.org', '@type': 'BreadcrumbList', itemListElement: items.map(([name, url], i) => ({ '@type': 'ListItem', position: i + 1, name, item: `https://mirastela.com${url}` })) };
}
export function articleLd(headline: string, description: string, url: string, lang: Lang) {
  return { '@context': 'https://schema.org', '@type': 'Article', headline, description, inLanguage: lang, url: `https://mirastela.com${url}`,
    author: { '@type': 'Organization', name: 'Mirastela' }, publisher: { '@type': 'Organization', name: 'Mirastela', url: 'https://mirastela.com' } };
}
