# Before public launch

Done together once the merchant of record and the selling entity are decided, so legal texts,
consent and tracking are written once.

## Plan, in order

1. Waiting: director sets up Stripe (Managed Payments) and gives nmotika@gmail.com the Developer role.
2. [done 2026-10-19: Stripe; account page /{lang}/account/ with magic link, add-ons, subscription, export and delete] Stripe integration: products and tax codes, Checkout with `managed_payments`, webhook, bundle and child as line items, subscription (calendar, monthly and yearly), withdrawal-consent checkbox. Plus a minimal account page "Moji izvještaji": magic-link login by email (link valid 30 min, no passwords), list of purchased reports, missing products with price and buy button (reuses the add-to-order flow), subscription status with calendar link and a button to the Stripe customer portal (cancel, card, invoices). Not now: editing birth data, horoscope archive, family profiles, loyalty.
3. [done 2026-10-19: Meta pixel + CAPI dataset 2027523501240767, GA4 G-4W6JYDV6GR, consent banner; mark generate_lead as key event in GA once it shows up] Tracking: Meta pixel + Conversions API (lead, checkout, purchase, upsells), analytics, all behind the consent banner.
4. [done 2026-10-19: terms, privacy, cookies in 7 languages, site public] Legal pages: terms, privacy, cookies, withdrawal and refund policy, imprint for Something Digital d.o.o., in all languages.
5. [done 2026-10-19: harden.sh (key-only SSH, fail2ban, ufw), R2 backups with restore test, UptimeRobot, Turnstile, 2 workers] Production hardening: daily offsite backup of the SQLite database (e.g. Hetzner Storage Box or Cloudflare R2, keep 30 days, test a restore), uptime monitoring of /api/health with alerts (UptimeRobot or Cloudflare health check), 2 uvicorn workers. CX23 is enough for the planned volume; if ever needed, rescale in Hetzner to CPX/CCX.
6. Sandbox testing: full flow with Stripe test cards for every path (natal, bundle, upsells, child, subscription, cancel, failed payment, refund), checking emails, reports and pixel events.
7. Flight 1 in Poland (natal entry). Payments stay on Stripe Managed Payments with a separate hosted checkout per add-on (MP has no one-click upsell). Measure: share of upsell viewers who complete the second checkout, and checkout drop-off without BLIK. If the second checkout passes under ~15% or BLIK is missed, consider regular Stripe (one-click upsells, BLIK, own VAT/OSS).
8. Affiliate and influencer programme (after flight 1, once real conversion is known): own tracking (`?ref=` stored on lead and order, 30-day cookie, last click or used code wins), a personal discount code per creator (10 to 15%), a simple creator page with their sales, and a short contract template. Terms: 40% of net revenue (excl. VAT and fees) on first purchases, 20 to 25% on subscriptions for the first 12 months, monthly payout with a 30-day hold. Start with 5 to 10 micro creators in Poland (10k to 50k followers; lifestyle, mums, relationships, tarot), not astrologers. Paid posts must be labelled per UOKiK ("reklama"). If a ready tool (Rewardful, Tolt) is considered, first check it works with Stripe Managed Payments.
9. Flight 2: compatibility as a second entry, multi-entry funnel.
10. After flight 2: astrocartography.
11. After astrocartography: a Human Design style product under our own name. The calculation (planet positions at birth and at the Sun's 88° arc before birth, mapped to 64 gates, 36 channels, 9 centres, type and authority) is doable with swisseph. Do not use the trademarked names ("Human Design", "BodyGraph", "Rave") in product names, ads or headings, draw our own chart graphic and write our own texts; check the trademark registrations in the EU before launch.

## Business and payments
- [x] Merchant of record decision: Stripe Managed Payments (inquiries: Lemon Squeezy, Digistore24, Payhip, PayPro, 2Checkout; fallback Stripe direct)
- [x] Selling entity: Something Digital d.o.o., details in the footer
- [ ] Checkout screen from the design, payments (BLIK for pl), receipts/invoices
- [ ] Remove tester coupon MIRATEST

## Legal and privacy (GDPR)
- [x] Privacy policy in 7 languages: what is stored, why, how long, processors, rights, AZOP
- [x] Terms of sale, entertainment disclaimer, right of withdrawal for digital content
- [x] Checkbox before payment: consent to immediate delivery of digital content and loss of the 14-day withdrawal right (PL: art. 38 ust. 1 pkt 13 ustawy o prawach konsumenta; EU equivalent elsewhere)
- [ ] Accept DPAs: Hetzner, Cloudflare, Resend, Anthropic (later Stripe/MoR, Meta)
- [x] Self-service "delete my data" link in every email and on the report page (deletes by email across leads, orders, items, subs, emails)
- [x] Server commands: delete by email, export by email as JSON (access requests)
- [x] Retention (sender.py prune, daily): leads without purchase 12 months, email log 12 months, sign-in links 1 day, sessions 90 days; backups 30 days offsite
- [x] Emails table: store recipient, kind, status, time only; no HTML body
- [ ] Legal review of the texts

## Tracking and consent
- [x] Consent banner (decline by default for non-essential)
- [x] Meta pixel + Conversions API, analytics (GA4), all behind consent
- [x] Marketing consent wording at the email step (separate optional checkbox)

## Security
- [x] Rate limiting on all public POST endpoints; Turnstile on email step and account sign-in
- [x] SSH key-only login, fail2ban, ufw (only SSH; API stays local behind the tunnel)
- [x] Encrypted off-server backups (R2 bucket mirastela-backup, EU, nightly 03:30, restore tested)
- [x] Open landing and horoscope pages to the public (Access bypass); keep /api/ private paths as now

## Product
- [x] Bundle (natal + partner + 2027 forecast) and child chart in the funnel, before flight 1
- [x] Personal astrological calendar (ICS feed `/api/cal/{token}.ics`, daily Great / Act / Slow down + short text, 14 days ahead, filled by the 06:00 job)
- [x] Cloudflare Access: Bypass policy for `mirastela.com/api/cal/*` (separate Access app, policy "Kalendar feed (javno)") while the site is behind Access (calendar apps cannot log in)
- [ ] Test the calendar subscription on Google Calendar, iPhone and Outlook with a real feed
- [ ] Multiple entry points on one funnel engine: each product (natal, compatibility, child, calendar, astrocartography) gets its own landing page and ad angle; the entry product is the main offer, the rest become upsells and the bundle. Built as an entry parameter (`/start/?p=partner`) that swaps landing copy, offer card and upsell order, so quiz, checkout and report stay shared. Test order: natal (flight 1), compatibility as a second angle (flight 2), then calendar and astrocartography.
- [ ] Astrocartography (after flight 2): planet lines (ASC/DSC/MC/IC) on a world map, top cities by theme (love, career, home, avoid) from ~300 relocation cities, match score from distance to lines, generated text. Birth time required. Product ~49 zł or part of a bigger bundle; also test as an ad hook (PL diaspora: UK, DE, NL). No fake testimonial ads, show a labelled example chart instead.

## Content
- [x] German, French, Italian added 2026-10-19 (EUR 14.90 / 11.90 / 17.90 / 34.90 / 13.90, sub 7.99 / 59.99); drafts for native review
- [ ] DE legal review before any German campaign: Widerrufsbelehrung, Impressum (MBS and director filled in)
- [ ] Native review of sl, ro, cs, hu texts
- [ ] Astrocartography and sky map (deferred)
