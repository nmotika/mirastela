"""Stripe Checkout (hosted) with Managed Payments: prices, line items, sessions and webhook parsing.

Env: STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET, STRIPE_MANAGED_PAYMENTS=1 (default on),
     STRIPE_TOS_CONSENT=1 (only without Managed Payments; needs the Terms URL in Stripe > Public details),
     STRIPE_API_VERSION (optional).
Prices must match web/src/i18n/config.ts (PRICE, UPSELL, SUB), which only displays them.
"""
from __future__ import annotations

import os

import emails

SITE = emails.SITE

# lang: (currency, natal, partner, forecast, bundle, child, sub_month, sub_year)
_P = {
    "pl": ("pln", 49.99, 59.99, 99.99, 129.99, 49.99, 29.99, 199),
    "hr": ("eur", 12.9, 9.9, 14.9, 29.9, 11.9, 6.99, 49.99),
    "sl": ("eur", 12.9, 9.9, 14.9, 29.9, 11.9, 6.99, 49.99),
    "en": ("eur", 12.9, 9.9, 14.9, 29.9, 11.9, 6.99, 49.99),
    "ro": ("ron", 59.99, 44.99, 69.99, 149.99, 59.99, 34.99, 229.99),
    "cs": ("czk", 299, 249, 349, 699, 299, 179, 1190),
    "hu": ("huf", 4990, 3990, 5990, 11990, 4990, 2790, 18990),
}
_KEYS = ("natal", "partner", "forecast", "bundle", "child", "sub_month", "sub_year")
TAX_CODE = "txcd_10000000"  # electronically supplied services

# Shown above the mandatory checkbox in Stripe Checkout: consent to immediate supply and loss of the
# right of withdrawal (Directive 2011/83/EU art. 16(m); PL: art. 38 ust. 1 pkt 13 u.p.k.).
WAIVER = {
    "pl": "Zgadzam się na natychmiastowe dostarczenie treści cyfrowych i przyjmuję do wiadomości, że z chwilą ich dostarczenia tracę prawo odstąpienia od umowy. Akceptuję [Regulamin]({url}).",
    "hr": "Pristajem da isporuka digitalnog sadržaja počne odmah i potvrđujem da time gubim pravo na jednostrani raskid ugovora. Prihvaćam [Uvjete korištenja]({url}).",
    "sl": "Soglašam, da se dobava digitalne vsebine začne takoj, in potrjujem, da s tem izgubim pravico do odstopa od pogodbe. Sprejemam [Pogoje uporabe]({url}).",
    "ro": "Sunt de acord ca furnizarea conținutului digital să înceapă imediat și confirm că astfel îmi pierd dreptul de retragere. Accept [Termenii și condițiile]({url}).",
    "cs": "Souhlasím s okamžitým dodáním digitálního obsahu a beru na vědomí, že tím ztrácím právo odstoupit od smlouvy. Souhlasím s [obchodními podmínkami]({url}).",
    "hu": "Hozzájárulok, hogy a digitális tartalom szolgáltatása azonnal megkezdődjön, és tudomásul veszem, hogy ezzel elveszítem az elállási jogomat. Elfogadom az [ÁSZF-et]({url}).",
    "en": "I agree that the digital content is supplied immediately and I acknowledge that I thereby lose my right of withdrawal. I accept the [Terms]({url}).",
}
BUNDLE_NAME = {"pl": "Pakiet", "hr": "Paket", "sl": "Paket", "ro": "Pachet", "cs": "Balíček", "hu": "Csomag", "en": "Bundle"}


def enabled() -> bool:
    return bool(os.environ.get("STRIPE_SECRET_KEY"))


def _stripe():
    import stripe
    stripe.api_key = os.environ["STRIPE_SECRET_KEY"]
    if os.environ.get("STRIPE_API_VERSION"):
        stripe.api_version = os.environ["STRIPE_API_VERSION"]
    return stripe


WHOLE = {"huf", "czk"}  # no cents shown; discounted prices are rounded to whole units


def price(lang: str, key: str, pct: int = 0) -> tuple[str, int]:
    """Currency and amount in minor units (HUF and CZK are sent with two decimals too, as Stripe expects),
    less pct percent. Must match the rounding in web/src/scripts/funnel.ts (discounted())."""
    row = _P.get(lang, _P["en"])
    amount = row[1 + _KEYS.index(key)] * (100 - pct) / 100
    if row[0] in WHOLE:
        amount = round(amount)
    return row[0], int(round(amount * 100))


def product_name(lang: str, key: str, year: int) -> str:
    names = emails.T[lang]["products"]
    if key == "bundle":
        return f"{BUNDLE_NAME[lang]}: {names['natal']} + {names['partner']} + {names['forecast'].format(year=year)}"
    if key.startswith("sub"):
        return emails.CAL[lang][0]
    return names[key].format(year=year)


def line_item(lang: str, key: str, year: int, pct: int = 0) -> dict:
    cur, amount = price(lang, key, pct)
    name = f"Mirastela · {product_name(lang, key, year)}" + (f" (−{pct} %)" if pct else "")
    pd = {"currency": cur, "unit_amount": amount, "tax_behavior": "inclusive",
          "product_data": {"name": name, "tax_code": TAX_CODE}}
    if key.startswith("sub"):
        pd["recurring"] = {"interval": "month" if key == "sub_month" else "year"}
    return {"price_data": pd, "quantity": 1}


def create_session(lang: str, email: str, key: str, year: int, metadata: dict, cancel_step: str, pct: int = 0) -> dict:
    """Hosted Checkout for one product, pct percent off (one-time purchases only). Returns {"id", "url"}."""
    stripe = _stripe()
    sub = key.startswith("sub")
    pct = 0 if sub or pct >= 100 else pct
    params: dict = {
        "mode": "subscription" if sub else "payment",
        "line_items": [line_item(lang, key, year, pct)],
        "customer_email": email,
        "locale": lang,
        "success_url": f"{SITE}/{lang}/start/?paid={{CHECKOUT_SESSION_ID}}",
        "cancel_url": f"{SITE}/{lang}/start/?cancel=1#{cancel_step}",
        "metadata": metadata,
        "allow_promotion_codes": False,
    }
    if sub:
        params["subscription_data"] = {"metadata": metadata}
    else:
        params["payment_intent_data"] = {"metadata": metadata}
    if os.environ.get("STRIPE_MANAGED_PAYMENTS", "1") == "1":
        params["managed_payments"] = {"enabled": True}
    elif os.environ.get("STRIPE_TOS_CONSENT", "0") == "1":
        # Managed Payments rejects custom_text, so the withdrawal waiver is collected on our offer screens
        # (stored with the payment); this only applies when Managed Payments is switched off.
        params["consent_collection"] = {"terms_of_service": "required"}
        params["custom_text"] = {"terms_of_service_acceptance": {
            "message": WAIVER.get(lang, WAIVER["en"]).format(url=f"{SITE}/{lang}/terms/")}}
    s = stripe.checkout.Session.create(**params)
    return {"id": s.id, "url": s.url}


def _plain(obj) -> dict:
    """Stripe objects are not dicts in stripe-python 12+; work with plain data everywhere."""
    return obj.to_dict() if hasattr(obj, "to_dict") else dict(obj)


def retrieve_session(session_id: str) -> dict:
    s = _plain(_stripe().checkout.Session.retrieve(session_id))
    return {"id": s["id"], "paid": s.get("payment_status") in ("paid", "no_payment_required") or s.get("status") == "complete",
            "metadata": dict(s.get("metadata") or {}), "customer": s.get("customer"), "subscription": s.get("subscription"),
            "mode": s.get("mode")}


def parse_webhook(payload: bytes, sig: str) -> dict:
    """Verify the signature and return the event as plain data."""
    stripe = _stripe()
    return _plain(stripe.Webhook.construct_event(payload, sig, os.environ["STRIPE_WEBHOOK_SECRET"]))


def cancel_subscription(sub_id: str, now: bool = False):
    """Stop renewal; access runs to the end of the paid period (the webhook then ends it).
    now=True cancels immediately (account deletion)."""
    if now:
        _stripe().Subscription.cancel(sub_id)
    else:
        _stripe().Subscription.modify(sub_id, cancel_at_period_end=True)


def portal_url(customer: str, return_url: str) -> str:
    return _stripe().billing_portal.Session.create(customer=customer, return_url=return_url).url

# ---- de, fr, it (drafts for native review)
_P['de'] = ('eur', 14.9, 11.9, 17.9, 34.9, 13.9, 7.99, 59.99)
WAIVER['de'] = 'Ich stimme zu, dass die Bereitstellung der digitalen Inhalte sofort beginnt, und nehme zur Kenntnis, dass ich damit mein Widerrufsrecht verliere. Ich akzeptiere die [AGB]({url}).'
BUNDLE_NAME['de'] = 'Paket'
_P['fr'] = ('eur', 14.9, 11.9, 17.9, 34.9, 13.9, 7.99, 59.99)
WAIVER['fr'] = 'J’accepte que le contenu numérique me soit fourni immédiatement et je reconnais perdre ainsi mon droit de rétractation. J’accepte les [conditions générales]({url}).'
BUNDLE_NAME['fr'] = 'Pack'
_P['it'] = ('eur', 14.9, 11.9, 17.9, 34.9, 13.9, 7.99, 59.99)
WAIVER['it'] = 'Acconsento alla fornitura immediata del contenuto digitale e prendo atto che in questo modo perdo il diritto di recesso. Accetto i [Termini e condizioni]({url}).'
BUNDLE_NAME['it'] = 'Pacchetto'

