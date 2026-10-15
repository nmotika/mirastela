/**
 * One dictionary per language. Placeholders in {braces} are filled at runtime.
 * Teaser templates: {signIn} sign with preposition, {trait}, {house}, {topic}, {houseArt} (Hungarian article).
 */
export interface Extra {
  coupon: { link: string; label: string; ph: string; apply: string; invalid: string; applied: string; claim: string };
  upsell: {
    eyebrow: string; partnerTitle: string; partnerSub: string; partnerBullets: string[];
    pName: string; pDate: string; pTime: string; pTimeUnknown: string; pPlace: string;
    forecastTitle: string; forecastSub: string; forecastBullets: string[];
    add: string; addFree: string; no: string;
  };
  report: {
    title: string; forName: string; tabs: { natal: string; partner: string; forecast: string };
    generating: string; error: string; notFound: string; print: string; dataTitle: string;
    cols: { point: string; sign: string; position: string; house: string };
    aspectsTitle: string; aspects: Record<string, string>; synastryTitle: string; transitsTitle: string;
    transitCols: { period: string; exact: string; transit: string };
  };
}

export type BaseDict = Omit<Dict, keyof Extra>;

export interface Dict extends Extra {
  meta: { title: string; description: string };
  ui: { changeLang: string; home: string; back: string; next: string; stepOf: string; error: string };
  landing: {
    eyebrow: string; h1: string; sub: string; cta: string; ctaNote: string;
    trust: [string, string, string];
    howTitle: string; how: [string, string][];
    incEyebrow: string; incTitle: string; inc: string[];
    finalTitle: string; finalSub: string;
  };
  footer: { terms: string; privacy: string; cookies: string; contact: string; disclaimer: string; languages: string; seller: string };
  quiz: {
    dateQ: string; dateHint: string; day: string; month: string; year: string; months: string[]; sunReward: string;
    timeQ: string; timeHint: string; timeLabel: string; timeUnknown: string; timeWhy: string;
    placeQ: string; placeHint: string; placePh: string; placeNone: string;
    nameQ: string; nameHint: string; namePh: string;
    focusQ: string; focusHint: string; focus: { love: string; career: string; money: string; growth: string };
    statusQ: string; status: { relationship: string; single: string; complicated: string };
    calcTitle: string;
    emailQ: string; emailSub: string; emailPh: string; emailConsent: string; emailCta: string; emailErr: string; emailPrivacy: string;
  };
  offer: {
    eyebrow: string; title: string; fragment: string; lock: string;
    incTitle: string; inc: [string, string][]; chapters: string; chaptersDesc: string;
    cardTitle: string; priceNote: string; payMethods: string; cta: string; ctaNote: string; soon: string;
    ascUnknown: string; noTimeNote: string;
  };
  teaser: { title: string; titleHouse: string; p1: string; p2House: string; p2NoTime: string; p3: string };
  astro: {
    signs: string[]; signIn: string[]; traits: string[]; houseTopics: string[];
    planets: Record<string, string>; asc: string;
  };
}
