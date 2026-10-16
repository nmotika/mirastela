export const LOCALES = ['pl', 'hr', 'sl', 'ro', 'cs', 'hu', 'en'] as const;
export type Lang = (typeof LOCALES)[number];

/** Native names, shown in the language switcher. */
export const LANG_NAMES: Record<Lang, string> = {
  pl: 'Polski', hr: 'Hrvatski', sl: 'Slovenščina', ro: 'Română',
  cs: 'Čeština', hu: 'Magyar', en: 'English',
};

/** BCP-47 tags for Intl formatting and <html lang>. */
export const INTL: Record<Lang, string> = {
  pl: 'pl-PL', hr: 'hr-HR', sl: 'sl-SI', ro: 'ro-RO', cs: 'cs-CZ', hu: 'hu-HU', en: 'en-GB',
};

/** Price of the full natal report per market (placeholders until tested). */
export const PRICE: Record<Lang, { amount: number; currency: string }> = {
  pl: { amount: 49.99, currency: 'PLN' },
  hr: { amount: 12.9, currency: 'EUR' },
  sl: { amount: 12.9, currency: 'EUR' },
  ro: { amount: 59.99, currency: 'RON' },
  cs: { amount: 299, currency: 'CZK' },
  hu: { amount: 4990, currency: 'HUF' },
  en: { amount: 12.9, currency: 'EUR' },
};

/** Upsell prices: partner compatibility and yearly forecast. */
export const UPSELL: Record<Lang, { partner: number; forecast: number }> = {
  pl: { partner: 39.99, forecast: 59.99 },
  hr: { partner: 9.9, forecast: 14.9 },
  sl: { partner: 9.9, forecast: 14.9 },
  ro: { partner: 44.99, forecast: 69.99 },
  cs: { partner: 249, forecast: 349 },
  hu: { partner: 3990, forecast: 5990 },
  en: { partner: 9.9, forecast: 14.9 },
};

/** Weekly personal horoscope subscription: monthly price and yearly price (8 months). Placeholders until tested. */
export const SUB: Record<Lang, { month: number; year: number }> = {
  pl: { month: 19.99, year: 159.99 }, hr: { month: 4.99, year: 39.99 }, sl: { month: 4.99, year: 39.99 },
  ro: { month: 24.99, year: 199.99 }, cs: { month: 119, year: 949 }, hu: { month: 1990, year: 15990 }, en: { month: 4.99, year: 39.99 },
};

export function formatPrice(lang: Lang, p = PRICE[lang]): string {
  const whole = Number.isInteger(p.amount);
  return new Intl.NumberFormat(INTL[lang], {
    style: 'currency', currency: p.currency,
    minimumFractionDigits: whole ? 0 : 2, maximumFractionDigits: whole ? 0 : 2,
  }).format(p.amount);
}

export function isLang(x: string | undefined): x is Lang {
  return !!x && (LOCALES as readonly string[]).includes(x);
}
