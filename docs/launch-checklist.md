# Before public launch

Done together once the merchant of record and the selling entity are decided, so legal texts,
consent and tracking are written once.

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

## Content
- [ ] Native review of sl, ro, cs, hu texts
- [ ] Astrocartography and sky map (deferred)
