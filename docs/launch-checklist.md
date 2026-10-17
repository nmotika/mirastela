# Before public launch

Done together once the merchant of record and the selling entity are decided, so legal texts,
consent and tracking are written once.

## Plan, in order

1. Waiting: director sets up Stripe (Managed Payments) and gives nmotika@gmail.com the Developer role.
2. Stripe integration: products and tax codes, Checkout with `managed_payments`, webhook, bundle and child as line items, subscription (calendar, monthly and yearly), withdrawal-consent checkbox.
3. Tracking: Meta pixel + Conversions API (lead, checkout, purchase, upsells), analytics, all behind the consent banner.
4. Legal pages that are missing: terms, privacy, cookies, withdrawal and refund policy, imprint for Something Digital d.o.o., in all languages.
5. Sandbox testing: full flow with Stripe test cards for every path (natal, bundle, upsells, child, subscription, cancel, failed payment, refund), checking emails, reports and pixel events.
6. Flight 1 in Poland (natal entry).
7. Flight 2: compatibility as a second entry, multi-entry funnel.
8. After flight 2: astrocartography.
9. After astrocartography: a Human Design style product under our own name. The calculation (planet positions at birth and at the Sun's 88° arc before birth, mapped to 64 gates, 36 channels, 9 centres, type and authority) is doable with swisseph. Do not use the trademarked names ("Human Design", "BodyGraph", "Rave") in product names, ads or headings, draw our own chart graphic and write our own texts; check the trademark registrations in the EU before launch.

## Business and payments
- [ ] Merchant of record decision (inquiries: Lemon Squeezy, Digistore24, Payhip, PayPro, 2Checkout; fallback Stripe direct)
- [ ] Selling entity (obrt or company); real seller details in the footer (now `[NAZIV OBRTA] · [ADRESA]`)
- [ ] Checkout screen from the design, payments (BLIK for pl), receipts/invoices
- [ ] Remove tester coupon MIRATEST

## Legal and privacy (GDPR)
- [ ] Privacy policy in 7 languages: what is stored, why, how long, processors, rights, AZOP
- [ ] Terms of sale, entertainment disclaimer, right of withdrawal for digital content
- [ ] Checkbox before payment: consent to immediate delivery of digital content and loss of the 14-day withdrawal right (PL: art. 38 ust. 1 pkt 13 ustawy o prawach konsumenta; EU equivalent elsewhere)
- [ ] Accept DPAs: Hetzner, Cloudflare, Resend, Anthropic (later Stripe/MoR, Meta)
- [ ] Self-service "delete my data" link in every email and on the report page (deletes by email across leads, orders, items, subs, emails)
- [ ] Server commands: delete by email, export by email as JSON (access requests)
- [ ] Retention: leads without purchase 12 months; email bodies 30 days; backups 14 days (stated in policy)
- [ ] Emails table: store recipient, kind, status, time only; no HTML body
- [ ] Legal review of the texts

## Tracking and consent
- [ ] Consent banner (decline by default for non-essential)
- [ ] Meta pixel + Conversions API, analytics, other pixels, all behind consent
- [ ] Marketing consent wording at the email step

## Security
- [ ] Turnstile + rate limiting on /api/lead and other public POST endpoints
- [ ] SSH key-only login, fail2ban, ufw (only SSH; API stays local behind the tunnel)
- [ ] Encrypted off-server backups (R2 or Hetzner Storage Box)
- [ ] Open landing and horoscope pages to the public (Access bypass); keep /api/ private paths as now

## Product
- [ ] Bundle (natal + partner + 2027 forecast) and child chart in the funnel, before flight 1
- [x] Personal astrological calendar (ICS feed `/api/cal/{token}.ics`, daily Great / Act / Slow down + short text, 14 days ahead, filled by the 06:00 job)
- [x] Cloudflare Access: Bypass policy for `mirastela.com/api/cal/*` (separate Access app, policy "Kalendar feed (javno)") while the site is behind Access (calendar apps cannot log in)
- [ ] Test the calendar subscription on Google Calendar, iPhone and Outlook with a real feed
- [ ] Multiple entry points on one funnel engine: each product (natal, compatibility, child, calendar, astrocartography) gets its own landing page and ad angle; the entry product is the main offer, the rest become upsells and the bundle. Built as an entry parameter (`/start/?p=partner`) that swaps landing copy, offer card and upsell order, so quiz, checkout and report stay shared. Test order: natal (flight 1), compatibility as a second angle (flight 2), then calendar and astrocartography.
- [ ] Astrocartography (after flight 2): planet lines (ASC/DSC/MC/IC) on a world map, top cities by theme (love, career, home, avoid) from ~300 relocation cities, match score from distance to lines, generated text. Birth time required. Product ~49 zł or part of a bigger bundle; also test as an ad hook (PL diaspora: UK, DE, NL). No fake testimonial ads, show a labelled example chart instead.

## Content
- [ ] Native review of sl, ro, cs, hu texts
- [ ] Astrocartography and sky map (deferred)
