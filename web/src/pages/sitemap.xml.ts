import { LOCALES, type Lang } from '../i18n/config';
import { t } from '../i18n';

const SITE = 'https://mirastela.com';

/** Indexable pages only: home, daily horoscope and the twelve sign pages, with hreflang alternates. */
export function GET() {
  const groups: Record<Lang, string>[] = [];
  const per = (f: (l: Lang) => string) => Object.fromEntries(LOCALES.map((l) => [l, f(l)])) as Record<Lang, string>;
  groups.push(per(() => ''));
  groups.push(per((l) => `${t(l).horo.slug}/`));
  for (let i = 0; i < 12; i++) groups.push(per((l) => `${t(l).horo.slug}/${t(l).horo.signSlugs[i]}/`));
  const urls = groups.flatMap((g) => LOCALES.map((l) => {
    const alts = LOCALES.map((a) => `<xhtml:link rel="alternate" hreflang="${a}" href="${SITE}/${a}/${g[a]}"/>`).join('');
    const daily = g[l] !== '';
    return `<url><loc>${SITE}/${l}/${g[l]}</loc>${daily ? '<changefreq>daily</changefreq>' : ''}${alts}<xhtml:link rel="alternate" hreflang="x-default" href="${SITE}/en/${g.en}"/></url>`;
  }));
  const xml = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n${urls.join('\n')}\n</urlset>\n`;
  return new Response(xml, { headers: { 'Content-Type': 'application/xml; charset=utf-8' } });
}
