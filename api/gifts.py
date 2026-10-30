"""Gifts: someone buys a natal chart (or the bundle) for another person and gets a one-time code.
The recipient enters the code on the offer step of the funnel with their own birth data. Legally it
is the same digital product, paid in advance and supplied when the code is redeemed (no stored value)."""
from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone

import emails

PRODUCTS = ("natal", "bundle")
VALID_DAYS = 365
_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # no 0/O, 1/I


def new_code() -> str:
    raw = "".join(secrets.choice(_ALPHABET) for _ in range(8))
    return f"GIFT-{raw[:4]}-{raw[4:]}"


def norm(code: str) -> str:
    return (code or "").strip().upper().replace(" ", "")


def schema(con):
    con.execute("""create table if not exists gifts(code text primary key, created text, lang text, email text, product text,
        to_name text, from_name text, message text, session text, status text, used_token text, used_at text, expires text)""")


def create(con, lang: str, email: str, product: str, to_name: str, from_name: str, message: str) -> str:
    now = datetime.now(timezone.utc)
    for _ in range(5):
        code = new_code()
        try:
            con.execute("insert into gifts(code, created, lang, email, product, to_name, from_name, message, status, expires)"
                        " values(?,?,?,?,?,?,?,?,?,?)",
                        (code, now.isoformat(), lang, email.lower(), product, to_name[:40], from_name[:40], message[:300], "unpaid",
                         (now + timedelta(days=VALID_DAYS)).date().isoformat()))
            return code
        except Exception:
            continue
    raise RuntimeError("could not create a gift code")


def active(con, code: str) -> dict | None:
    row = con.execute("select code, product, lang, expires from gifts where code=? and status='active'", (norm(code),)).fetchone()
    if not row or row[3] < datetime.now(timezone.utc).date().isoformat():
        return None
    return {"code": row[0], "product": row[1], "lang": row[2], "expires": row[3]}


def redeem(con, code: str, order_token: str) -> bool:
    """Mark the code used for this order. False if someone else was faster or it is not active."""
    return con.execute("update gifts set status='used', used_token=?, used_at=? where code=? and status='active'",
                       (order_token, datetime.now(timezone.utc).isoformat(), norm(code))).rowcount == 1


def info(con, code: str) -> dict | None:
    row = con.execute("select code, product, lang, to_name, from_name, message, status, expires from gifts where code=?", (norm(code),)).fetchone()
    if not row:
        return None
    return dict(zip(("code", "product", "lang", "toName", "fromName", "message", "status", "expires"), row))


# Email to the buyer with the code (the printable card is on the website).
T = {
    "pl": ("Twój prezent od Mirastela: kod {code}", "Dziękujemy! Oto kod prezentowy na {product}:", "Osoba obdarowana wchodzi na mirastela.com, podaje swoje dane urodzenia i na ostatnim kroku wpisuje kod w polu „Masz kod?”. Kod jest jednorazowy i ważny do {expires}.", "Otwórz kartę prezentową do wydruku"),
    "hr": ("Tvoj poklon s Mirastele: kod {code}", "Hvala! Ovo je poklon kod za {product}:", "Osoba kojoj poklanjaš otvori mirastela.com, upiše svoje podatke o rođenju i u zadnjem koraku unese kod u polje „Imaš kod?”. Kod je jednokratan i vrijedi do {expires}.", "Otvori poklon karticu za ispis"),
    "sl": ("Tvoje darilo z Mirastele: koda {code}", "Hvala! To je koda za darilo {product}:", "Obdarovanec odpre mirastela.com, vnese svoje podatke o rojstvu in v zadnjem koraku vpiše kodo v polje »Imaš kodo?«. Koda je enkratna in velja do {expires}.", "Odpri darilno kartico za tisk"),
    "ro": ("Cadoul tău de la Mirastela: codul {code}", "Mulțumim! Acesta este codul cadou pentru {product}:", "Persoana care primește cadoul intră pe mirastela.com, introduce datele de naștere și, la ultimul pas, scrie codul în câmpul „Ai un cod?”. Codul este de unică folosință și valabil până la {expires}.", "Deschide cardul cadou pentru tipărire"),
    "cs": ("Tvůj dárek od Mirastely: kód {code}", "Děkujeme! Tady je dárkový kód na {product}:", "Obdarovaný otevře mirastela.com, zadá své údaje o narození a v posledním kroku vloží kód do pole „Máš kód?“. Kód je jednorázový a platí do {expires}.", "Otevřít dárkovou kartu k tisku"),
    "hu": ("Ajándékod a Mirastelától: {code}", "Köszönjük! Íme az ajándékkód ehhez: {product}", "A megajándékozott megnyitja a mirastela.com oldalt, megadja a születési adatait, és az utolsó lépésben beírja a kódot a „Van kódod?” mezőbe. A kód egyszer használható, és {expires}-ig érvényes.", "Nyomtatható ajándékkártya megnyitása"),
    "en": ("Your Mirastela gift: code {code}", "Thank you! Here is your gift code for {product}:", "The recipient opens mirastela.com, enters their birth details and, on the last step, types the code into the “Have a code?” field. The code can be used once and is valid until {expires}.", "Open the printable gift card"),
    "de": ("Dein Geschenk von Mirastela: Code {code}", "Danke! Hier ist dein Geschenkcode für {product}:", "Die beschenkte Person öffnet mirastela.com, gibt ihre Geburtsdaten ein und trägt im letzten Schritt den Code im Feld „Hast du einen Code?“ ein. Der Code ist einmal einlösbar und gültig bis {expires}.", "Geschenkkarte zum Ausdrucken öffnen"),
    "fr": ("Ton cadeau Mirastela : code {code}", "Merci ! Voici ton code cadeau pour {product} :", "La personne qui reçoit le cadeau ouvre mirastela.com, saisit ses données de naissance et, à la dernière étape, entre le code dans le champ « Tu as un code ? ». Le code est utilisable une fois et valable jusqu’au {expires}.", "Ouvrir la carte cadeau à imprimer"),
    "it": ("Il tuo regalo Mirastela: codice {code}", "Grazie! Ecco il codice regalo per {product}:", "Chi riceve il regalo apre mirastela.com, inserisce i propri dati di nascita e, all’ultimo passaggio, scrive il codice nel campo «Hai un codice?». Il codice vale una sola volta ed è valido fino al {expires}.", "Apri la carta regalo da stampare"),
    "es": ("Tu regalo de Mirastela: código {code}", "¡Gracias! Aquí tienes el código regalo para {product}:", "La persona que recibe el regalo abre mirastela.com, introduce sus datos de nacimiento y, en el último paso, escribe el código en el campo «¿Tienes un código?». El código es de un solo uso y es válido hasta el {expires}.", "Abrir la tarjeta regalo para imprimir"),
}


def email(lang: str, code: str, product_name: str, expires: str, card_url: str) -> tuple[str, str]:
    subj, intro, how, btn = T.get(lang, T["en"])
    exp = emails.fmt_date(lang, datetime.fromisoformat(expires).date())
    code_box = (f'<p style="margin:6px 0 18px;padding:16px;border:1px dashed #D9B26A;border-radius:12px;text-align:center;'
                f'font:700 26px/1.2 Arial,sans-serif;letter-spacing:.08em;color:#D9B26A">{emails.esc(code)}</p>')
    body = emails._p(intro.format(product=product_name)) + code_box + emails._p(how.format(expires=exp)) + emails._button(btn, card_url)
    body += emails._p(emails.T[lang]["stmt"])
    return subj.format(code=code), emails.layout(lang, body)
