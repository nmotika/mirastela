import { LOCALES, type Lang } from '../i18n/config';
import { t } from '../i18n';
import { SEO } from '../i18n/lang/seo';
import { GIFT } from '../i18n/lang/gift';
import { PARTNER } from '../i18n/lang/partner';
import { SIGN_KEYS, page, hasAny, pairKey, pairSlug, type Kind } from '../lib/seo';

const SITE = 'https://mirastela.com';

/** Indexable pages only: home, daily horoscope and sign pages, evergreen pages and the calculator, with hreflang alternates. */
export function GET() {
  const groups: Record<Lang, string>[] = [];
  const per = (f: (l: Lang) => string) => Object.fromEntries(LOCALES.map((l) => [l, f(l)])) as Record<Lang, string>;
  groups.push(per(() => ''));
  groups.push(per((l) => `${t(l).horo.slug}/`));
  for (let i = 0; i < 12; i++) groups.push(per((l) => `${t(l).horo.slug}/${t(l).horo.signSlugs[i]}/`));
  const urls = groups.flatMap((g) => LOCALES.map((l) => {
    const alts = LOCALES.map((a) => `<xhtml:link rel="alternate" hreflang="${a}" href="${SITE}/${a}/${g[a]}"/>`).join('');
    const daily = g[l] !== '';
    const xdef = g.en === '' ? `${SITE}/` : `${SITE}/en/${g.en}`;
    return `<url><loc>${SITE}/${l}/${g[l]}</loc>${daily ? '<changefreq>daily</changefreq>' : ''}${alts}<xhtml:link rel="alternate" hreflang="x-default" href="${xdef}"/></url>`;
  }));
  urls.unshift(`<url><loc>${SITE}/</loc>${LOCALES.map((a) => `<xhtml:link rel="alternate" hreflang="${a}" href="${SITE}/${a}/"/>`).join('')}<xhtml:link rel="alternate" hreflang="x-default" href="${SITE}/"/></url>`);
  // Evergreen pages: only languages where the page exists are listed as alternates.
  const evergreen: Partial<Record<Lang, string>>[] = [];
  const hub = (k: Kind | 'calc') => evergreen.push(Object.fromEntries(LOCALES.filter((l) => k === 'calc' || hasAny(k, l)).map((l) => [l, `${SEO[l].slugs[k]}/`])));
  (['year', 'signs', 'compat', 'calc'] as const).forEach(hub);
  evergreen.push(Object.fromEntries(LOCALES.map((l) => [l, `${GIFT[l].slug}/`])));
  evergreen.push(Object.fromEntries(LOCALES.map((l) => [l, `${PARTNER[l].slug}/`])));
  for (let i = 0; i < 12; i++) {
    for (const k of ['year', 'signs'] as const) {
      evergreen.push(Object.fromEntries(LOCALES.filter((l) => page(k, l, SIGN_KEYS[i])).map((l) => [l, `${SEO[l].slugs[k]}/${t(l).horo.signSlugs[i]}/`])));
    }
    for (let j = i; j < 12; j++) {
      evergreen.push(Object.fromEntries(LOCALES.filter((l) => page('compat', l, pairKey(i, j))).map((l) => [l, `${SEO[l].slugs.compat}/${pairSlug(l, i, j)}/`])));
    }
  }
  for (const g of evergreen) {
    const ls = Object.keys(g) as Lang[];
    const alts = ls.map((a) => `<xhtml:link rel="alternate" hreflang="${a}" href="${SITE}/${a}/${g[a]}"/>`).join('')
      + (g.en ? `<xhtml:link rel="alternate" hreflang="x-default" href="${SITE}/en/${g.en}"/>` : '');
    for (const l of ls) urls.push(`<url><loc>${SITE}/${l}/${g[l]}</loc>${alts}</url>`);
  }
  const xml = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n${urls.join('\n')}\n</urlset>\n`;
  return new Response(xml, { headers: { 'Content-Type': 'application/xml; charset=utf-8' } });
}
