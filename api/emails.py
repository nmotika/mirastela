"""Email texts and HTML for all languages. sl, ro, cs, hu are drafts for native review."""
from __future__ import annotations

import html as _h
import os
import re
from datetime import date

SITE = os.environ.get("SITE_URL", "https://mirastela.com")

MONTHS = {
    "pl": "stycznia lutego marca kwietnia maja czerwca lipca sierpnia września października listopada grudnia",
    "hr": "siječnja veljače ožujka travnja svibnja lipnja srpnja kolovoza rujna listopada studenoga prosinca",
    "sl": "januarja februarja marca aprila maja junija julija avgusta septembra oktobra novembra decembra",
    "ro": "ianuarie februarie martie aprilie mai iunie iulie august septembrie octombrie noiembrie decembrie",
    "cs": "ledna února března dubna května června července srpna září října listopadu prosince",
    "hu": "január február március április május június július augusztus szeptember október november december",
    "en": "January February March April May June July August September October November December",
}
DATE_FMT = {"pl": "{d} {m}", "hr": "{d}. {m}", "sl": "{d}. {m}", "ro": "{d} {m}", "cs": "{d}. {m}", "hu": "{m} {d}.", "en": "{d} {m}"}


def fmt_date(lang: str, d: date) -> str:
    return DATE_FMT[lang].format(d=d.day, m=MONTHS[lang].split()[d.month - 1])


T = {
    "pl": dict(
        hi="Cześć {name},", hiNoName="Cześć,",
        sumSubject="{name}, podsumowanie Twojego kosmogramu", sumIntro="Oto krótkie podsumowanie Twojego kosmogramu.",
        sumCta="Zobacz pełny raport", sumAfter="Pełny raport opisuje wszystkie dziesięć planet, domy i najważniejsze aspekty.",
        big3=("Słońce", "Księżyc", "Ascendent"),
        repSubject="Twój raport jest gotowy: {product}", repBody="Twój raport „{product}” jest gotowy. Otwórz go poniżej. Na stronie możesz go też pobrać jako PDF.",
        repBtn="Otwórz raport", products=dict(natal="Kosmogram", partner="Dopasowanie", forecast="Prognoza {year}"),
        subSubject="Subskrypcja jest aktywna", subDaily="Od jutra rano codziennie dostaniesz horoskop obliczony na podstawie Twojego kosmogramu.",
        subWeekly="W każdy poniedziałek rano dostaniesz horoskop na cały tydzień, obliczony na podstawie Twojego kosmogramu.",
        dailySubject="{name}, Twój horoskop na {date}", weeklySubject="{name}, Twój tydzień od {date}",
        unsub="Wypisz się z subskrypcji", unsubDone="Wypisano Cię z subskrypcji. Nie będziemy już wysyłać horoskopów.",
        why="Otrzymujesz tę wiadomość, ponieważ ten adres został podany na mirastela.com.",
        disclaimer="Treści służą rozrywce i autorefleksji."),
    "hr": dict(
        hi="Bok {name},", hiNoName="Bok,",
        sumSubject="{name}, sažetak tvoje natalne karte", sumIntro="Evo kratkog sažetka tvoje natalne karte.",
        sumCta="Pogledaj cijeli izvještaj", sumAfter="Cijeli izvještaj opisuje svih deset planeta, kuće i najvažnije aspekte.",
        big3=("Sunce", "Mjesec", "Podznak"),
        repSubject="Tvoj izvještaj je spreman: {product}", repBody="Tvoj izvještaj „{product}” je spreman. Otvori ga na poveznici ispod. Na stranici ga možeš preuzeti i kao PDF.",
        repBtn="Otvori izvještaj", products=dict(natal="Natalna karta", partner="Slaganje", forecast="Prognoza {year}"),
        subSubject="Pretplata je uključena", subDaily="Od sutra ujutro svaki dan dobivaš horoskop izračunat prema svojoj natalnoj karti.",
        subWeekly="Svakog ponedjeljka ujutro dobivaš horoskop za cijeli tjedan, izračunat prema svojoj natalnoj karti.",
        dailySubject="{name}, tvoj horoskop za {date}", weeklySubject="{name}, tvoj tjedan od {date}",
        unsub="Odjava od pretplate", unsubDone="Odjava je uspjela. Više ti nećemo slati horoskope.",
        why="Ovaj e-mail dobivaš jer je ova adresa upisana na mirastela.com.",
        disclaimer="Sadržaj je namijenjen zabavi i samorefleksiji."),
    "sl": dict(
        hi="Živijo, {name},", hiNoName="Živijo,",
        sumSubject="{name}, povzetek tvoje natalne karte", sumIntro="Tukaj je kratek povzetek tvoje natalne karte.",
        sumCta="Poglej celotno poročilo", sumAfter="Celotno poročilo opiše vseh deset planetov, hiše in najpomembnejše aspekte.",
        big3=("Sonce", "Luna", "Ascendent"),
        repSubject="Tvoje poročilo je pripravljeno: {product}", repBody="Tvoje poročilo »{product}« je pripravljeno. Odpri ga spodaj. Na strani ga lahko preneseš tudi kot PDF.",
        repBtn="Odpri poročilo", products=dict(natal="Natalna karta", partner="Ujemanje", forecast="Napoved {year}"),
        subSubject="Naročnina je vklopljena", subDaily="Od jutri zjutraj vsak dan prejmeš horoskop, izračunan po tvoji natalni karti.",
        subWeekly="Vsak ponedeljek zjutraj prejmeš horoskop za ves teden, izračunan po tvoji natalni karti.",
        dailySubject="{name}, tvoj horoskop za {date}", weeklySubject="{name}, tvoj teden od {date}",
        unsub="Odjava od naročnine", unsubDone="Odjava je uspela. Horoskopov ti ne bomo več pošiljali.",
        why="To sporočilo prejemaš, ker je bil ta naslov vpisan na mirastela.com.",
        disclaimer="Vsebina je namenjena zabavi in samorefleksiji."),
    "ro": dict(
        hi="Bună, {name},", hiNoName="Bună,",
        sumSubject="{name}, rezumatul hărții tale natale", sumIntro="Iată un scurt rezumat al hărții tale natale.",
        sumCta="Vezi raportul complet", sumAfter="Raportul complet descrie toate cele zece planete, casele și cele mai importante aspecte.",
        big3=("Soarele", "Luna", "Ascendentul"),
        repSubject="Raportul tău este gata: {product}", repBody="Raportul tău „{product}” este gata. Deschide-l mai jos. Pe pagină îl poți descărca și ca PDF.",
        repBtn="Deschide raportul", products=dict(natal="Harta natală", partner="Compatibilitate", forecast="Prognoza {year}"),
        subSubject="Abonamentul este activ", subDaily="De mâine dimineață primești zilnic un horoscop calculat după harta ta natală.",
        subWeekly="În fiecare luni dimineață primești horoscopul pentru toată săptămâna, calculat după harta ta natală.",
        dailySubject="{name}, horoscopul tău pentru {date}", weeklySubject="{name}, săptămâna ta de la {date}",
        unsub="Dezabonare", unsubDone="Te-ai dezabonat. Nu îți mai trimitem horoscoape.",
        why="Primești acest e-mail pentru că adresa a fost introdusă pe mirastela.com.",
        disclaimer="Conținutul are scop de divertisment și autoreflecție."),
    "cs": dict(
        hi="Ahoj {name},", hiNoName="Ahoj,",
        sumSubject="{name}, shrnutí tvého horoskopu", sumIntro="Tady je krátké shrnutí tvého natálního horoskopu.",
        sumCta="Zobrazit celou zprávu", sumAfter="Celá zpráva popisuje všech deset planet, domy a nejdůležitější aspekty.",
        big3=("Slunce", "Měsíc", "Ascendent"),
        repSubject="Tvoje zpráva je hotová: {product}", repBody="Tvoje zpráva „{product}“ je hotová. Otevři ji níže. Na stránce si ji můžeš stáhnout i jako PDF.",
        repBtn="Otevřít zprávu", products=dict(natal="Natální horoskop", partner="Partnerský soulad", forecast="Předpověď {year}"),
        subSubject="Předplatné je aktivní", subDaily="Od zítřejšího rána ti každý den přijde horoskop spočítaný podle tvého natálního horoskopu.",
        subWeekly="Každé pondělí ráno ti přijde horoskop na celý týden, spočítaný podle tvého natálního horoskopu.",
        dailySubject="{name}, tvůj horoskop na {date}", weeklySubject="{name}, tvůj týden od {date}",
        unsub="Odhlásit předplatné", unsubDone="Odhlášení proběhlo. Horoskopy ti už posílat nebudeme.",
        why="Tento e-mail dostáváš, protože tato adresa byla zadána na mirastela.com.",
        disclaimer="Obsah slouží k zábavě a sebereflexi."),
    "hu": dict(
        hi="Szia, {name}!", hiNoName="Szia!",
        sumSubject="{name}, a születési képleted összefoglalója", sumIntro="Íme a születési képleted rövid összefoglalója.",
        sumCta="A teljes elemzés megtekintése", sumAfter="A teljes elemzés mind a tíz bolygót, a házakat és a legfontosabb fényszögeket leírja.",
        big3=("Nap", "Hold", "Aszcendens"),
        repSubject="Elkészült az elemzésed: {product}", repBody="Elkészült az elemzésed: „{product}”. Az alábbi gombbal megnyithatod. Az oldalon PDF-ként is letöltheted.",
        repBtn="Elemzés megnyitása", products=dict(natal="Születési képlet", partner="Párkapcsolati összhang", forecast="{year}. évi előrejelzés"),
        subSubject="Az előfizetés aktív", subDaily="Holnap reggeltől minden nap kapsz egy horoszkópot, amely a születési képleted alapján készül.",
        subWeekly="Minden hétfő reggel megkapod az egész hetes horoszkópodat, a születési képleted alapján.",
        dailySubject="{name}, a horoszkópod: {date}", weeklySubject="{name}, a heti horoszkópod: {date}",
        unsub="Leiratkozás", unsubDone="Sikeresen leiratkoztál. Több horoszkópot nem küldünk.",
        why="Azért kapod ezt az e-mailt, mert ezt a címet megadták a mirastela.com oldalon.",
        disclaimer="A tartalom szórakoztatási és önismereti célt szolgál."),
    "en": dict(
        hi="Hi {name},", hiNoName="Hi,",
        sumSubject="{name}, your natal chart summary", sumIntro="Here is a short summary of your natal chart.",
        sumCta="See the full report", sumAfter="The full report covers all ten planets, the houses and the most important aspects.",
        big3=("Sun", "Moon", "Ascendant"),
        repSubject="Your report is ready: {product}", repBody="Your report “{product}” is ready. Open it below. You can also download it as a PDF from the page.",
        repBtn="Open the report", products=dict(natal="Natal chart", partner="Compatibility", forecast="Forecast {year}"),
        subSubject="Your subscription is on", subDaily="From tomorrow morning you will get a daily horoscope calculated from your natal chart.",
        subWeekly="Every Monday morning you will get a horoscope for the whole week, calculated from your natal chart.",
        dailySubject="{name}, your horoscope for {date}", weeklySubject="{name}, your week from {date}",
        unsub="Unsubscribe", unsubDone="You have been unsubscribed. We will not send you any more horoscopes.",
        why="You are receiving this email because this address was entered on mirastela.com.",
        disclaimer="The content is meant for entertainment and self-reflection."),
}

SIGN_NAMES = {}  # filled lazily from report.VOCAB


def sign_name(lang: str, idx: int) -> str:
    if lang not in SIGN_NAMES:
        from report import VOCAB
        SIGN_NAMES[lang] = [s.strip() for s in VOCAB[lang]["signs"].split(",")]
    return SIGN_NAMES[lang][idx]


def esc(s: str) -> str:
    return _h.escape(s, quote=True)


def md_to_html(md: str) -> str:
    """Minimal Markdown for model output: ## headings, **bold**, *italic*, lists, paragraphs."""
    def inline(s: str) -> str:
        s = esc(s)
        s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
        return re.sub(r"(?<!\*)\*([^*\s][^*]*?)\*", r"<em>\1</em>", s)
    out, para, items = [], [], []
    P = 'style="margin:0 0 14px;font:17px/1.6 Georgia,serif;color:#F3EEE3"'

    def flush():
        nonlocal para, items
        if para:
            out.append(f"<p {P}>{inline(' '.join(para))}</p>")
            para = []
        if items:
            out.append('<ul style="margin:0 0 14px;padding-left:20px">' + "".join(
                f'<li style="font:17px/1.6 Georgia,serif;color:#F3EEE3">{inline(i)}</li>' for i in items) + "</ul>")
            items = []
    for raw in md.splitlines():
        line = raw.strip()
        if not line:
            flush()
            continue
        m = re.match(r"^#{1,4}\s+(.*)$", line)
        if m:
            flush()
            out.append(f'<h2 style="margin:6px 0 12px;font:400 24px/1.25 Georgia,serif;color:#F3EEE3">{inline(m.group(1))}</h2>')
            continue
        m = re.match(r"^[-*]\s+(.*)$", line)
        if m:
            if para:
                flush()
            items.append(m.group(1))
            continue
        if items:
            flush()
        para.append(line)
    flush()
    return "\n".join(out)


def _p(text: str) -> str:
    return f'<p style="margin:0 0 14px;font:17px/1.6 Georgia,serif;color:#F3EEE3">{esc(text)}</p>'


def _button(label: str, url: str) -> str:
    return (f'<p style="margin:22px 0"><a href="{esc(url)}" style="display:inline-block;padding:14px 26px;border-radius:999px;'
            f'background:#D9B26A;color:#0B1020;font:700 16px Arial,sans-serif;text-decoration:none">{esc(label)}</a></p>')


def layout(lang: str, body: str, unsubscribe_url: str | None = None) -> str:
    t = T[lang]
    unsub = (f'<br><a href="{esc(unsubscribe_url)}" style="color:#A9B0C6">{esc(t["unsub"])}</a>' if unsubscribe_url else "")
    return f"""<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="dark"><meta name="supported-color-schemes" content="dark"></head>
<body style="margin:0;padding:0;background:#0B1020">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#0B1020"><tr><td align="center" style="padding:24px 12px">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:600px;background:#121A33;border:1px solid #1E2744;border-radius:18px">
<tr><td style="padding:26px 28px 6px;font:400 24px Georgia,serif;color:#F3EEE3"><span style="color:#D9B26A">&#10022;</span> Mirastela</td></tr>
<tr><td style="padding:12px 28px 18px">{body}</td></tr>
<tr><td style="padding:16px 28px 26px;border-top:1px solid #1E2744;font:13px/1.5 Arial,sans-serif;color:#A9B0C6">
Mirastela · {esc(t['disclaimer'])}<br>{esc(t['why'])}{unsub}</td></tr>
</table></td></tr></table></body></html>"""


def greeting(lang: str, name: str) -> str:
    t = T[lang]
    return t["hi"].format(name=name) if name else t["hiNoName"]


# ---------------------------------------------------------------- the emails
CUSP = {"pl": "na granicy z:", "hr": "na granici sa:", "sl": "na meji z:", "ro": "la limita cu:",
        "cs": "na hranici s:", "hu": "határeset:", "en": "on the cusp with:"}


def summary(lang: str, name: str, chart: dict, text: str, resume_url: str) -> tuple[str, str]:
    t = T[lang]
    sun, moon = chart["planets"][0], chart["planets"][1]
    asc = (chart.get("angles") or {}).get("asc")
    items = [(t["big3"][0], sun), (t["big3"][1], moon)] + ([(t["big3"][2], asc)] if asc else [])

    def cell(k: str, p: dict) -> str:
        cu = (f'<br><span style="font:11px Arial,sans-serif;color:#D9B26A">{esc(CUSP[lang])} {esc(sign_name(lang, p["cusp"]))}</span>'
              if p.get("cusp") is not None else "")
        return (f'<td style="padding:10px 12px;background:#1A2343;border-radius:12px;font:13px Arial,sans-serif;color:#A9B0C6;vertical-align:top">'
                f'{esc(k)}<br><strong style="font:400 19px Georgia,serif;color:#F3EEE3">{esc(sign_name(lang, p["signIndex"]))}</strong>{cu}</td><td width="8"></td>')
    big3 = "".join(cell(k, p) for k, p in items)
    body = (_p(greeting(lang, name)) + _p(t["sumIntro"])
            + f'<table role="presentation" cellpadding="0" cellspacing="0" style="margin:6px 0 18px"><tr>{big3}</tr></table>'
            + "".join(_p(x.strip()) for x in text.split("\n") if x.strip())
            + _p(t["sumAfter"]) + _button(t["sumCta"], resume_url))
    subject = t["sumSubject"].format(name=name).lstrip(", ") if name else t["sumSubject"].split(", ", 1)[-1].capitalize()
    return subject, layout(lang, body)


def report_ready(lang: str, name: str, product: str, year: int, url: str) -> tuple[str, str]:
    t = T[lang]
    pname = t["products"][product].format(year=year)
    body = _p(greeting(lang, name)) + _p(t["repBody"].format(product=pname)) + _button(t["repBtn"], url)
    return t["repSubject"].format(product=pname), layout(lang, body)


def sub_welcome(lang: str, name: str, freq: str, unsub_url: str) -> tuple[str, str]:
    t = T[lang]
    body = _p(greeting(lang, name)) + _p(t["subDaily"] if freq == "daily" else t["subWeekly"])
    return t["subSubject"], layout(lang, body, unsub_url)


def horoscope(lang: str, name: str, freq: str, day: date, md: str, unsub_url: str) -> tuple[str, str]:
    t = T[lang]
    key = "dailySubject" if freq == "daily" else "weeklySubject"
    subject = t[key].format(name=name or "Mirastela", date=fmt_date(lang, day))
    return subject, layout(lang, md_to_html(md), unsub_url)


def unsub_page(lang: str, done: bool) -> str:
    t = T.get(lang, T["en"])
    if done:
        return layout(lang, _p(t["unsubDone"]))
    # GET only shows a button: mail scanners that open links must not unsubscribe anyone.
    form = ('<form method="post"><button type="submit" style="padding:14px 26px;border:0;border-radius:999px;'
            f'background:#D9B26A;color:#0B1020;font:700 16px Arial,sans-serif;cursor:pointer">{esc(t["unsub"])}</button></form>')
    return layout(lang, form)
