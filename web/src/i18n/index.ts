import type { Lang } from './config';
import type { Dict } from './types';
import pl from './lang/pl';
import hr from './lang/hr';
import sl from './lang/sl';
import ro from './lang/ro';
import cs from './lang/cs';
import hu from './lang/hu';
import en from './lang/en';

import { EXTRA } from './lang/extra';
import { MORE } from './lang/more';
import { SHOP } from './lang/shop';
import { ACCOUNT } from './lang/account';

const BASE = { pl, hr, sl, ro, cs, hu, en };
export const DICTS = Object.fromEntries(
  Object.entries(BASE).map(([l, d]) => [l, { ...d, ...EXTRA[l as Lang], ...MORE[l as Lang], shop: SHOP[l as Lang], account: ACCOUNT[l as Lang] }]),
) as Record<Lang, Dict>;

export function t(lang: Lang): Dict {
  return DICTS[lang];
}

export { fill, huArticle } from './fill';
