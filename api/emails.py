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
        repBtn="Otwórz raport", products=dict(natal="Kosmogram", partner="Dopasowanie", forecast="Prognoza {year}", child="Kosmogram dziecka"),
        subSubject="Subskrypcja jest aktywna", subDaily="Od jutra rano codziennie dostaniesz horoskop obliczony na podstawie Twojego kosmogramu.",
        subWeekly="W każdy poniedziałek rano dostaniesz horoskop na cały tydzień, obliczony na podstawie Twojego kosmogramu.",
        dailySubject="{name}, Twój horoskop na {date}", weeklySubject="{name}, Twój tydzień od {date}",
        unsub="Wypisz się z subskrypcji", unsubDone="Wypisano Cię z subskrypcji. Nie będziemy już wysyłać horoskopów.",
        loginSubject="Twój link do logowania w Mirastela", loginBody="Kliknij przycisk, aby zobaczyć swoje raporty i subskrypcję. Link działa 30 minut i tylko raz.", loginBtn="Otwórz moje raporty", loginAfter="Jeśli to nie Ty prosił(a)ś o link, zignoruj tę wiadomość.", account="Moje raporty i dane",
        stmt='Na wyciągu z karty płatność jest widoczna jako „LINK.COM* MIRASTELA”. Link to usługa płatnicza Stripe, przez którą rozliczamy zakupy.',
        why="Otrzymujesz tę wiadomość, ponieważ ten adres został podany na mirastela.com.",
        disclaimer="Treści służą rozrywce i autorefleksji."),
    "hr": dict(
        hi="Bok {name},", hiNoName="Bok,",
        sumSubject="{name}, sažetak tvoje natalne karte", sumIntro="Evo kratkog sažetka tvoje natalne karte.",
        sumCta="Pogledaj cijeli izvještaj", sumAfter="Cijeli izvještaj opisuje svih deset planeta, kuće i najvažnije aspekte.",
        big3=("Sunce", "Mjesec", "Podznak"),
        repSubject="Tvoj izvještaj je spreman: {product}", repBody="Tvoj izvještaj „{product}” je spreman. Otvori ga na poveznici ispod. Na stranici ga možeš preuzeti i kao PDF.",
        repBtn="Otvori izvještaj", products=dict(natal="Natalna karta", partner="Slaganje", forecast="Prognoza {year}", child="Natalna karta djeteta"),
        subSubject="Pretplata je uključena", subDaily="Od sutra ujutro svaki dan dobivaš horoskop izračunat prema svojoj natalnoj karti.",
        subWeekly="Svakog ponedjeljka ujutro dobivaš horoskop za cijeli tjedan, izračunat prema svojoj natalnoj karti.",
        dailySubject="{name}, tvoj horoskop za {date}", weeklySubject="{name}, tvoj tjedan od {date}",
        unsub="Odjava od pretplate", unsubDone="Odjava je uspjela. Više ti nećemo slati horoskope.",
        loginSubject="Tvoj link za prijavu u Mirastelu", loginBody="Klikni gumb da vidiš svoje izvještaje i pretplatu. Link vrijedi 30 minuta i samo jednom.", loginBtn="Otvori moje izvještaje", loginAfter="Ako nisi ti tražio/la link, zanemari ovu poruku.", account="Moji izvještaji i podaci",
        stmt='Na izvodu kartice plaćanje se prikazuje kao „LINK.COM* MIRASTELA”. Link je Stripeova usluga plaćanja preko koje naplaćujemo kupnje.',
        why="Ovaj e-mail dobivaš jer je ova adresa upisana na mirastela.com.",
        disclaimer="Sadržaj je namijenjen zabavi i samorefleksiji."),
    "sl": dict(
        hi="Živijo, {name},", hiNoName="Živijo,",
        sumSubject="{name}, povzetek tvoje natalne karte", sumIntro="Tukaj je kratek povzetek tvoje natalne karte.",
        sumCta="Poglej celotno poročilo", sumAfter="Celotno poročilo opiše vseh deset planetov, hiše in najpomembnejše aspekte.",
        big3=("Sonce", "Luna", "Ascendent"),
        repSubject="Tvoje poročilo je pripravljeno: {product}", repBody="Tvoje poročilo »{product}« je pripravljeno. Odpri ga spodaj. Na strani ga lahko preneseš tudi kot PDF.",
        repBtn="Odpri poročilo", products=dict(natal="Natalna karta", partner="Ujemanje", forecast="Napoved {year}", child="Natalna karta otroka"),
        subSubject="Naročnina je vklopljena", subDaily="Od jutri zjutraj vsak dan prejmeš horoskop, izračunan po tvoji natalni karti.",
        subWeekly="Vsak ponedeljek zjutraj prejmeš horoskop za ves teden, izračunan po tvoji natalni karti.",
        dailySubject="{name}, tvoj horoskop za {date}", weeklySubject="{name}, tvoj teden od {date}",
        unsub="Odjava od naročnine", unsubDone="Odjava je uspela. Horoskopov ti ne bomo več pošiljali.",
        loginSubject="Tvoja povezava za prijavo v Mirastelo", loginBody="Klikni gumb, da vidiš svoja poročila in naročnino. Povezava velja 30 minut in samo enkrat.", loginBtn="Odpri moja poročila", loginAfter="Če povezave nisi zahteval(a) ti, to sporočilo prezri.", account="Moja poročila in podatki",
        stmt='Na izpisku kartice je plačilo prikazano kot "LINK.COM* MIRASTELA". Link je Stripova plačilna storitev, prek katere obračunavamo nakupe.',
        why="To sporočilo prejemaš, ker je bil ta naslov vpisan na mirastela.com.",
        disclaimer="Vsebina je namenjena zabavi in samorefleksiji."),
    "ro": dict(
        hi="Bună, {name},", hiNoName="Bună,",
        sumSubject="{name}, rezumatul hărții tale natale", sumIntro="Iată un scurt rezumat al hărții tale natale.",
        sumCta="Vezi raportul complet", sumAfter="Raportul complet descrie toate cele zece planete, casele și cele mai importante aspecte.",
        big3=("Soarele", "Luna", "Ascendentul"),
        repSubject="Raportul tău este gata: {product}", repBody="Raportul tău „{product}” este gata. Deschide-l mai jos. Pe pagină îl poți descărca și ca PDF.",
        repBtn="Deschide raportul", products=dict(natal="Harta natală", partner="Compatibilitate", forecast="Prognoza {year}", child="Harta natală a copilului"),
        subSubject="Abonamentul este activ", subDaily="De mâine dimineață primești zilnic un horoscop calculat după harta ta natală.",
        subWeekly="În fiecare luni dimineață primești horoscopul pentru toată săptămâna, calculat după harta ta natală.",
        dailySubject="{name}, horoscopul tău pentru {date}", weeklySubject="{name}, săptămâna ta de la {date}",
        unsub="Dezabonare", unsubDone="Te-ai dezabonat. Nu îți mai trimitem horoscoape.",
        loginSubject="Linkul tău de autentificare în Mirastela", loginBody="Apasă butonul ca să vezi rapoartele și abonamentul tău. Linkul este valabil 30 de minute și o singură dată.", loginBtn="Deschide rapoartele mele", loginAfter="Dacă nu tu ai cerut linkul, ignoră acest mesaj.", account="Rapoartele și datele mele",
        stmt='Pe extrasul cardului, plata apare ca „LINK.COM* MIRASTELA”. Link este serviciul de plată Stripe prin care încasăm achizițiile.',
        why="Primești acest e-mail pentru că adresa a fost introdusă pe mirastela.com.",
        disclaimer="Conținutul are scop de divertisment și autoreflecție."),
    "cs": dict(
        hi="Ahoj {name},", hiNoName="Ahoj,",
        sumSubject="{name}, shrnutí tvého horoskopu", sumIntro="Tady je krátké shrnutí tvého natálního horoskopu.",
        sumCta="Zobrazit celou zprávu", sumAfter="Celá zpráva popisuje všech deset planet, domy a nejdůležitější aspekty.",
        big3=("Slunce", "Měsíc", "Ascendent"),
        repSubject="Tvoje zpráva je hotová: {product}", repBody="Tvoje zpráva „{product}“ je hotová. Otevři ji níže. Na stránce si ji můžeš stáhnout i jako PDF.",
        repBtn="Otevřít zprávu", products=dict(natal="Natální horoskop", partner="Partnerský soulad", forecast="Předpověď {year}", child="Natální horoskop dítěte"),
        subSubject="Předplatné je aktivní", subDaily="Od zítřejšího rána ti každý den přijde horoskop spočítaný podle tvého natálního horoskopu.",
        subWeekly="Každé pondělí ráno ti přijde horoskop na celý týden, spočítaný podle tvého natálního horoskopu.",
        dailySubject="{name}, tvůj horoskop na {date}", weeklySubject="{name}, tvůj týden od {date}",
        unsub="Odhlásit předplatné", unsubDone="Odhlášení proběhlo. Horoskopy ti už posílat nebudeme.",
        loginSubject="Tvůj odkaz pro přihlášení do Mirastely", loginBody="Klikni na tlačítko a uvidíš své zprávy a předplatné. Odkaz platí 30 minut a jen jednou.", loginBtn="Otevřít moje zprávy", loginAfter="Pokud jsi o odkaz nežádal(a) ty, tuto zprávu ignoruj.", account="Moje zprávy a údaje",
        stmt='Na výpisu z karty se platba zobrazí jako „LINK.COM* MIRASTELA“. Link je platební služba Stripe, přes kterou nákupy účtujeme.',
        why="Tento e-mail dostáváš, protože tato adresa byla zadána na mirastela.com.",
        disclaimer="Obsah slouží k zábavě a sebereflexi."),
    "hu": dict(
        hi="Szia, {name}!", hiNoName="Szia!",
        sumSubject="{name}, a születési képleted összefoglalója", sumIntro="Íme a születési képleted rövid összefoglalója.",
        sumCta="A teljes elemzés megtekintése", sumAfter="A teljes elemzés mind a tíz bolygót, a házakat és a legfontosabb fényszögeket leírja.",
        big3=("Nap", "Hold", "Aszcendens"),
        repSubject="Elkészült az elemzésed: {product}", repBody="Elkészült az elemzésed: „{product}”. Az alábbi gombbal megnyithatod. Az oldalon PDF-ként is letöltheted.",
        repBtn="Elemzés megnyitása", products=dict(natal="Születési képlet", partner="Párkapcsolati összhang", forecast="{year}. évi előrejelzés", child="A gyermek születési képlete"),
        subSubject="Az előfizetés aktív", subDaily="Holnap reggeltől minden nap kapsz egy horoszkópot, amely a születési képleted alapján készül.",
        subWeekly="Minden hétfő reggel megkapod az egész hetes horoszkópodat, a születési képleted alapján.",
        dailySubject="{name}, a horoszkópod: {date}", weeklySubject="{name}, a heti horoszkópod: {date}",
        unsub="Leiratkozás", unsubDone="Sikeresen leiratkoztál. Több horoszkópot nem küldünk.",
        loginSubject="Bejelentkezési linked a Mirastelához", loginBody="Kattints a gombra, és látod a jelentéseidet és az előfizetésedet. A link 30 percig és csak egyszer érvényes.", loginBtn="Jelentéseim megnyitása", loginAfter="Ha nem te kérted a linket, hagyd figyelmen kívül ezt az üzenetet.", account="Jelentéseim és adataim",
        stmt='A kártyakivonaton a fizetés „LINK.COM* MIRASTELA” néven jelenik meg. A Link a Stripe fizetési szolgáltatása, ezen keresztül számlázzuk a vásárlásokat.',
        why="Azért kapod ezt az e-mailt, mert ezt a címet megadták a mirastela.com oldalon.",
        disclaimer="A tartalom szórakoztatási és önismereti célt szolgál."),
    "en": dict(
        hi="Hi {name},", hiNoName="Hi,",
        sumSubject="{name}, your natal chart summary", sumIntro="Here is a short summary of your natal chart.",
        sumCta="See the full report", sumAfter="The full report covers all ten planets, the houses and the most important aspects.",
        big3=("Sun", "Moon", "Ascendant"),
        repSubject="Your report is ready: {product}", repBody="Your report “{product}” is ready. Open it below. You can also download it as a PDF from the page.",
        repBtn="Open the report", products=dict(natal="Natal chart", partner="Compatibility", forecast="Forecast {year}", child="Your child's natal chart"),
        subSubject="Your subscription is on", subDaily="From tomorrow morning you will get a daily horoscope calculated from your natal chart.",
        subWeekly="Every Monday morning you will get a horoscope for the whole week, calculated from your natal chart.",
        dailySubject="{name}, your horoscope for {date}", weeklySubject="{name}, your week from {date}",
        unsub="Unsubscribe", unsubDone="You have been unsubscribed. We will not send you any more horoscopes.",
        loginSubject="Your Mirastela sign-in link", loginBody="Click the button to see your reports and subscription. The link works for 30 minutes and only once.", loginBtn="Open my reports", loginAfter="If you did not ask for this link, ignore this email.", account="My reports and data",
        stmt='Your card statement will show the payment as "LINK.COM* MIRASTELA". Link is Stripe\'s payment service, through which we charge purchases.',
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
    unsub += f'<br><a href="{SITE}/{lang}/account/" style="color:#A9B0C6">{esc(t["account"])}</a>'
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


def report_ready(lang: str, name: str, product: str, year: int, url: str, paid: bool = False) -> tuple[str, str]:
    t = T[lang]
    pname = t["products"][product].format(year=year)
    body = _p(greeting(lang, name)) + _p(t["repBody"].format(product=pname)) + _button(t["repBtn"], url)
    if paid:  # how the charge appears on the card statement (Stripe Managed Payments via Link)
        body += _p(t["stmt"])
    return t["repSubject"].format(product=pname), layout(lang, body)


# Personal calendar block: title, intro, Google button, Apple button, other apps.
CAL = {'pl': ('Twój osobisty kalendarz astrologiczny', 'Codziennie w Twoim kalendarzu: zielony, niebieski lub pomarańczowy dzień i krótka wskazówka, liczona z Twojego kosmogramu. Dodaj go jednym kliknięciem:', 'Dodaj do Kalendarza Google', 'Dodaj do iPhone’a / Apple', 'Inny kalendarz (Outlook i inne): skopiuj ten adres i dodaj go jako subskrypcję z adresu URL:'),
       'hr': ('Tvoj osobni astrološki kalendar', 'Svaki dan u tvom kalendaru: zeleni, plavi ili narančasti dan i kratki savjet, izračunat prema tvojoj natalnoj karti. Dodaj ga jednim klikom:', 'Dodaj u Google kalendar', 'Dodaj na iPhone / Apple', 'Drugi kalendar (Outlook i ostali): kopiraj ovu adresu i dodaj je kao pretplatu putem URL-a:'),
       'sl': ('Tvoj osebni astrološki koledar', 'Vsak dan v tvojem koledarju: zelen, moder ali oranžen dan in kratek nasvet, izračunan po tvoji natalni karti. Dodaj ga z enim klikom:', 'Dodaj v Google Koledar', 'Dodaj na iPhone / Apple', 'Drug koledar (Outlook in drugi): kopiraj ta naslov in ga dodaj kot naročnino prek URL-ja:'),
       'ro': ('Calendarul tău astrologic personal', 'În fiecare zi, în calendarul tău: o zi verde, albastră sau portocalie și un sfat scurt, calculat după harta ta natală. Adaugă-l cu un clic:', 'Adaugă în Google Calendar', 'Adaugă pe iPhone / Apple', 'Alt calendar (Outlook și altele): copiază această adresă și adaug-o ca abonament prin URL:'),
       'cs': ('Tvůj osobní astrologický kalendář', 'Každý den v tvém kalendáři: zelený, modrý nebo oranžový den a krátká rada, spočítaná podle tvého natálního horoskopu. Přidej si ho jedním kliknutím:', 'Přidat do Kalendáře Google', 'Přidat do iPhonu / Apple', 'Jiný kalendář (Outlook a další): zkopíruj tuto adresu a přidej ji jako odběr z URL:'),
       'hu': ('A személyes asztrológiai naptárad', 'Minden nap a naptáradban: zöld, kék vagy narancs nap és egy rövid tanács, a születési képleted alapján. Add hozzá egy kattintással:', 'Hozzáadás a Google Naptárhoz', 'Hozzáadás iPhone-ra / Apple-re', 'Más naptár (Outlook és mások): másold ki ezt a címet, és add hozzá URL-es feliratkozásként:'),
       'en': ('Your personal astrological calendar', 'Every day in your calendar: a green, blue or orange day and a short tip, calculated from your natal chart. Add it in one click:', 'Add to Google Calendar', 'Add to iPhone / Apple', 'Another calendar (Outlook and others): copy this address and add it as a subscription from URL:')}


def cal_links(url: str) -> dict:
    from urllib.parse import quote
    webcal = "webcal://" + url.split("://", 1)[1]
    return {"google": "https://calendar.google.com/calendar/render?cid=" + quote(webcal, safe=""), "apple": webcal, "url": url}


def sub_welcome(lang: str, name: str, freq: str, unsub_url: str, cal_url: str | None = None) -> tuple[str, str]:
    t = T[lang]
    body = _p(greeting(lang, name)) + _p(t["subDaily"] if freq == "daily" else t["subWeekly"])
    if cal_url:
        title, intro, g, a, other = CAL[lang]
        links = cal_links(cal_url)
        body += (f'<h2 style="font:400 22px Georgia,serif;color:#F3EBDD;margin:28px 0 8px">{esc(title)}</h2>' + _p(intro)
                 + _button(g, links["google"]) + _button(a, links["apple"])
                 + f'<p style="font:13px/1.5 Arial,sans-serif;color:#A9B0C6">{esc(other)}<br><span style="color:#D9B26A;word-break:break-all">{esc(cal_url)}</span></p>')
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


def login(lang: str, url: str) -> tuple[str, str]:
    t = T[lang]
    return t["loginSubject"], layout(lang, _p(t["loginBody"]) + _button(t["loginBtn"], url) + _p(t["loginAfter"]))

# ---- de, fr, it (drafts for native review)
MONTHS['de'] = 'Januar Februar März April Mai Juni Juli August September Oktober November Dezember'
DATE_FMT['de'] = '{d}. {m}'
T['de'] = {'hi': 'Hallo {name},',
 'hiNoName': 'Hallo,',
 'sumSubject': '{name}, die Zusammenfassung deines Geburtshoroskops',
 'sumIntro': 'Hier ist eine kurze Zusammenfassung deines Geburtshoroskops.',
 'sumCta': 'Vollständige Auswertung ansehen',
 'sumAfter': 'Die vollständige Auswertung beschreibt alle zehn Planeten, die Häuser und die wichtigsten Aspekte.',
 'big3': ('Sonne', 'Mond', 'Aszendent'),
 'repSubject': 'Deine Auswertung ist fertig: {product}',
 'repBody': 'Deine Auswertung „{product}“ ist fertig. Öffne sie über den Button unten. Auf der Seite kannst du sie '
            'auch als PDF herunterladen.',
 'repBtn': 'Auswertung öffnen',
 'products': {'natal': 'Geburtshoroskop',
              'partner': 'Partnerhoroskop',
              'forecast': 'Prognose {year}',
              'child': 'Geburtshoroskop deines Kindes'},
 'subSubject': 'Dein Abo ist aktiv',
 'subDaily': 'Ab morgen früh bekommst du jeden Tag ein Horoskop, berechnet aus deinem Geburtshoroskop.',
 'subWeekly': 'Jeden Montagmorgen bekommst du ein Horoskop für die ganze Woche, berechnet aus deinem Geburtshoroskop.',
 'dailySubject': '{name}, dein Horoskop für den {date}',
 'weeklySubject': '{name}, deine Woche ab dem {date}',
 'unsub': 'Abo kündigen',
 'unsubDone': 'Du hast dich abgemeldet. Wir schicken dir keine Horoskope mehr.',
 'loginSubject': 'Dein Anmeldelink für Mirastela',
 'loginBody': 'Klicke auf den Button, um deine Auswertungen und dein Abo zu sehen. Der Link gilt 30 Minuten und nur '
              'einmal.',
 'loginBtn': 'Meine Auswertungen öffnen',
 'loginAfter': 'Wenn du diesen Link nicht angefordert hast, ignoriere diese E-Mail.',
 'account': 'Meine Auswertungen und Daten',
 'stmt': 'Auf deiner Kartenabrechnung erscheint die Zahlung als „LINK.COM* MIRASTELA“. Link ist der Zahlungsdienst von '
         'Stripe, über den wir Käufe abrechnen.',
 'why': 'Du erhältst diese E-Mail, weil diese Adresse auf mirastela.com eingegeben wurde.',
 'disclaimer': 'Die Inhalte dienen der Unterhaltung und Selbstreflexion.'}
CAL['de'] = ('Dein persönlicher astrologischer Kalender',
 'Jeden Tag in deinem Kalender: ein grüner, blauer oder orangefarbener Tag und ein kurzer Tipp, berechnet aus deinem '
 'Geburtshoroskop. Füge ihn mit einem Klick hinzu:',
 'Zu Google Kalender hinzufügen',
 'Zu iPhone / Apple hinzufügen',
 'Anderer Kalender (Outlook und andere): Kopiere diese Adresse und füge sie als Abo über eine URL hinzu:')
CUSP['de'] = 'an der Grenze zu:'
MONTHS['fr'] = 'janvier février mars avril mai juin juillet août septembre octobre novembre décembre'
DATE_FMT['fr'] = '{d} {m}'
T['fr'] = {'hi': 'Bonjour {name},',
 'hiNoName': 'Bonjour,',
 'sumSubject': '{name}, le résumé de ton thème astral',
 'sumIntro': 'Voici un court résumé de ton thème astral.',
 'sumCta': 'Voir le rapport complet',
 'sumAfter': 'Le rapport complet couvre les dix planètes, les maisons et les aspects les plus importants.',
 'big3': ('Soleil', 'Lune', 'Ascendant'),
 'repSubject': 'Ton rapport est prêt : {product}',
 'repBody': 'Ton rapport « {product} » est prêt. Ouvre-le ci-dessous. Tu peux aussi le télécharger en PDF depuis la '
            'page.',
 'repBtn': 'Ouvrir le rapport',
 'products': {'natal': 'Thème astral',
              'partner': 'Compatibilité',
              'forecast': 'Prévisions {year}',
              'child': 'Le thème astral de ton enfant'},
 'subSubject': 'Ton abonnement est activé',
 'subDaily': 'Dès demain matin, tu recevras chaque jour un horoscope calculé à partir de ton thème astral.',
 'subWeekly': 'Chaque lundi matin, tu recevras un horoscope pour toute la semaine, calculé à partir de ton thème '
              'astral.',
 'dailySubject': '{name}, ton horoscope du {date}',
 'weeklySubject': '{name}, ta semaine à partir du {date}',
 'unsub': 'Se désabonner',
 'unsubDone': 'Ton désabonnement est confirmé. Nous ne t’enverrons plus d’horoscopes.',
 'loginSubject': 'Ton lien de connexion à Mirastela',
 'loginBody': 'Clique sur le bouton pour voir tes rapports et ton abonnement. Le lien est valable 30 minutes et une '
              'seule fois.',
 'loginBtn': 'Ouvrir mes rapports',
 'loginAfter': 'Si tu n’as pas demandé ce lien, ignore cet e-mail.',
 'account': 'Mes rapports et mes données',
 'stmt': 'Sur ton relevé de carte, le paiement apparaîtra sous le nom « LINK.COM* MIRASTELA ». Link est le service de '
         'paiement de Stripe par lequel nous encaissons les achats.',
 'why': 'Tu reçois cet e-mail parce que cette adresse a été saisie sur mirastela.com.',
 'disclaimer': 'Le contenu est destiné au divertissement et à l’introspection.'}
CAL['fr'] = ('Ton calendrier astrologique personnel',
 'Chaque jour dans ton agenda : une journée verte, bleue ou orange et un court conseil, calculés à partir de ton thème '
 'astral. Ajoute-le en un clic :',
 'Ajouter à Google Agenda',
 'Ajouter sur iPhone / Apple',
 'Autre agenda (Outlook et autres) : copie cette adresse et ajoute-la comme abonnement par URL :')
CUSP['fr'] = 'à la limite avec :'
MONTHS['it'] = 'gennaio febbraio marzo aprile maggio giugno luglio agosto settembre ottobre novembre dicembre'
DATE_FMT['it'] = '{d} {m}'
T['it'] = {'hi': 'Ciao {name},',
 'hiNoName': 'Ciao,',
 'sumSubject': '{name}, il riassunto del tuo tema natale',
 'sumIntro': 'Ecco un breve riassunto del tuo tema natale.',
 'sumCta': 'Vedi il report completo',
 'sumAfter': 'Il report completo descrive tutti e dieci i pianeti, le case e gli aspetti più importanti.',
 'big3': ('Sole', 'Luna', 'Ascendente'),
 'repSubject': 'Il tuo report è pronto: {product}',
 'repBody': 'Il tuo report “{product}” è pronto. Aprilo qui sotto. Dalla pagina puoi anche scaricarlo in PDF.',
 'repBtn': 'Apri il report',
 'products': {'natal': 'Tema natale',
              'partner': 'Affinità di coppia',
              'forecast': 'Previsione {year}',
              'child': 'Il tema natale di tuo figlio'},
 'subSubject': 'Il tuo abbonamento è attivo',
 'subDaily': 'Da domani mattina riceverai ogni giorno un oroscopo calcolato sul tuo tema natale.',
 'subWeekly': 'Ogni lunedì mattina riceverai l’oroscopo per tutta la settimana, calcolato sul tuo tema natale.',
 'dailySubject': '{name}, il tuo oroscopo per il {date}',
 'weeklySubject': '{name}, la tua settimana dal {date}',
 'unsub': 'Annulla l’iscrizione',
 'unsubDone': 'Iscrizione annullata. Non ti invieremo più oroscopi.',
 'loginSubject': 'Il tuo link di accesso a Mirastela',
 'loginBody': 'Fai clic sul pulsante per vedere i tuoi report e il tuo abbonamento. Il link è valido per 30 minuti e '
              'una sola volta.',
 'loginBtn': 'Apri i miei report',
 'loginAfter': 'Se non hai richiesto tu questo link, ignora questa email.',
 'account': 'I miei report e i miei dati',
 'stmt': 'Sull’estratto conto della carta il pagamento comparirà come "LINK.COM* MIRASTELA". Link è il servizio di '
         'pagamento di Stripe con cui addebitiamo gli acquisti.',
 'why': 'Ricevi questa email perché questo indirizzo è stato inserito su mirastela.com.',
 'disclaimer': 'I contenuti hanno scopo di intrattenimento e riflessione personale.'}
CAL['it'] = ('Il tuo calendario astrologico personale',
 'Ogni giorno nel tuo calendario: una giornata verde, blu o arancione e un breve consiglio, calcolati sul tuo tema '
 'natale. Aggiungilo con un clic:',
 'Aggiungi a Google Calendar',
 'Aggiungi a iPhone / Apple',
 'Un altro calendario (Outlook e altri): copia questo indirizzo e aggiungilo come abbonamento da URL:')
CUSP['it'] = 'al confine con:'



# ---------------------------------------------------------------- free summary v2 and the 24 h reminder
# Summary: a picture of the person, one tension, then questions the full report answers (open loops)
# and a button with the price. Reminder: one of those questions, sent once, only with marketing consent.
FUNNEL = {
    "pl": dict(subj="{name}, oto co Twój kosmogram mówi o Tobie", subjNoName="Oto co Twój kosmogram mówi o Tobie",
               intro="Obliczyliśmy Twój kosmogram. Oto, co widać w nim na pierwszy rzut oka.",
               qTitle="Na te pytania odpowiada Twój pełny raport:", cta="Odblokuj cały kosmogram · {price}",
               after="Pełny raport jest napisany tylko dla Twojego kosmogramu, z osobnymi rozdziałami o obszarach wybranych w quizie.",
               remSubj="{name}, jedno pytanie z Twojego kosmogramu zostało otwarte", remSubjNoName="Jedno pytanie z Twojego kosmogramu zostało otwarte",
               remIntro="Wczoraj wysłaliśmy Ci podsumowanie Twojego kosmogramu. Jedno pytanie z niego zasługuje na odpowiedź:",
               remAfter="Odpowiedź jest w Twoim pełnym raporcie. Twoje dane są zapisane, więc nie musisz niczego wpisywać ponownie.",
               optout="Nie chcę więcej takich e-maili", optoutDone="Gotowe. Nie będziemy już wysyłać Ci e-maili z horoskopami i ofertami."),
    "hr": dict(subj="{name}, ovo tvoja karta kaže o tebi", subjNoName="Ovo tvoja natalna karta kaže o tebi",
               intro="Izračunali smo tvoju natalnu kartu. Ovo se iz nje vidi na prvi pogled.",
               qTitle="Na ova pitanja odgovara tvoj cijeli izvještaj:", cta="Otključaj cijelu kartu · {price}",
               after="Cijeli izvještaj napisan je samo za tvoju kartu, s posebnim poglavljima o područjima iz kviza.",
               remSubj="{name}, jedno pitanje iz tvoje karte ostalo je otvoreno", remSubjNoName="Jedno pitanje iz tvoje karte ostalo je otvoreno",
               remIntro="Jučer smo ti poslali sažetak tvoje natalne karte. Jedno pitanje iz njega zaslužuje odgovor:",
               remAfter="Odgovor je u tvom cijelom izvještaju. Tvoji podaci su spremljeni, pa ništa ne trebaš ponovno upisivati.",
               optout="Ne želim više ovakve e-mailove", optoutDone="Gotovo. Više ti nećemo slati e-mailove s horoskopima i ponudama."),
    "sl": dict(subj="{name}, to ti pove tvoja natalna karta", subjNoName="To ti pove tvoja natalna karta",
               intro="Izračunali smo tvojo natalno karto. To se v njej vidi na prvi pogled.",
               qTitle="Na ta vprašanja odgovori tvoje celotno poročilo:", cta="Odkleni celotno karto · {price}",
               after="Celotno poročilo je napisano samo za tvojo karto, s posebnimi poglavji o področjih iz kviza.",
               remSubj="{name}, eno vprašanje iz tvoje karte je ostalo odprto", remSubjNoName="Eno vprašanje iz tvoje karte je ostalo odprto",
               remIntro="Včeraj smo ti poslali povzetek tvoje natalne karte. Eno vprašanje iz njega si zasluži odgovor:",
               remAfter="Odgovor je v tvojem celotnem poročilu. Tvoji podatki so shranjeni, zato ti ni treba ničesar vnašati znova.",
               optout="Ne želim več takšnih e-poštnih sporočil", optoutDone="Končano. Ne bomo ti več pošiljali e-poštnih sporočil s horoskopi in ponudbami."),
    "ro": dict(subj="{name}, iată ce spune harta ta natală despre tine", subjNoName="Iată ce spune harta ta natală despre tine",
               intro="Ți-am calculat harta natală. Iată ce se vede în ea la prima vedere.",
               qTitle="Raportul tău complet răspunde la aceste întrebări:", cta="Deblochează harta completă · {price}",
               after="Raportul complet este scris doar pentru harta ta, cu capitole separate despre domeniile alese în chestionar.",
               remSubj="{name}, o întrebare din harta ta a rămas deschisă", remSubjNoName="O întrebare din harta ta a rămas deschisă",
               remIntro="Ieri ți-am trimis rezumatul hărții tale natale. O întrebare din el merită un răspuns:",
               remAfter="Răspunsul este în raportul tău complet. Datele tale sunt salvate, așa că nu trebuie să introduci nimic din nou.",
               optout="Nu mai vreau astfel de e-mailuri", optoutDone="Gata. Nu îți mai trimitem e-mailuri cu horoscoape și oferte."),
    "cs": dict(subj="{name}, tohle o tobě říká tvůj horoskop", subjNoName="Tohle o tobě říká tvůj natální horoskop",
               intro="Spočítali jsme tvůj natální horoskop. Tohle je v něm vidět na první pohled.",
               qTitle="Na tyto otázky odpovídá tvoje celá zpráva:", cta="Odemknout celý horoskop · {price}",
               after="Celá zpráva je napsaná jen pro tvůj horoskop, se samostatnými kapitolami o oblastech z kvízu.",
               remSubj="{name}, jedna otázka z tvého horoskopu zůstala otevřená", remSubjNoName="Jedna otázka z tvého horoskopu zůstala otevřená",
               remIntro="Včera jsme ti poslali shrnutí tvého natálního horoskopu. Jedna otázka z něj si zaslouží odpověď:",
               remAfter="Odpověď je v tvé celé zprávě. Tvoje údaje jsou uložené, takže nic nemusíš zadávat znovu.",
               optout="Už nechci takové e-maily", optoutDone="Hotovo. Už ti nebudeme posílat e-maily s horoskopy a nabídkami."),
    "hu": dict(subj="{name}, ezt mondja rólad a születési képleted", subjNoName="Ezt mondja rólad a születési képleted",
               intro="Kiszámoltuk a születési képletedet. Első ránézésre ez látszik belőle.",
               qTitle="Ezekre a kérdésekre válaszol a teljes elemzésed:", cta="A teljes képlet feloldása · {price}",
               after="A teljes elemzés csak a te képletedhez készül, külön fejezetekkel a kvízben választott területekről.",
               remSubj="{name}, egy kérdés a képletedből nyitva maradt", remSubjNoName="Egy kérdés a képletedből nyitva maradt",
               remIntro="Tegnap elküldtük a születési képleted összefoglalóját. Egy kérdés belőle választ érdemel:",
               remAfter="A válasz a teljes elemzésedben van. Az adataid el vannak mentve, így semmit sem kell újra beírnod.",
               optout="Nem kérek több ilyen e-mailt", optoutDone="Kész. Többé nem küldünk neked horoszkópokat és ajánlatokat e-mailben."),
    "de": dict(subj="{name}, das sagt dein Geburtshoroskop über dich", subjNoName="Das sagt dein Geburtshoroskop über dich",
               intro="Wir haben dein Geburtshoroskop berechnet. Das ist auf den ersten Blick darin zu sehen.",
               qTitle="Auf diese Fragen antwortet deine vollständige Auswertung:", cta="Ganzes Horoskop freischalten · {price}",
               after="Die vollständige Auswertung ist nur für dein Horoskop geschrieben, mit eigenen Kapiteln zu den Bereichen aus dem Quiz.",
               remSubj="{name}, eine Frage aus deinem Horoskop ist noch offen", remSubjNoName="Eine Frage aus deinem Horoskop ist noch offen",
               remIntro="Gestern haben wir dir die Zusammenfassung deines Geburtshoroskops geschickt. Eine Frage daraus verdient eine Antwort:",
               remAfter="Die Antwort steht in deiner vollständigen Auswertung. Deine Daten sind gespeichert, du musst nichts neu eingeben.",
               optout="Ich möchte solche E-Mails nicht mehr", optoutDone="Erledigt. Wir schicken dir keine E-Mails mit Horoskopen und Angeboten mehr."),
    "fr": dict(subj="{name}, voici ce que ton thème astral dit de toi", subjNoName="Voici ce que ton thème astral dit de toi",
               intro="Nous avons calculé ton thème astral. Voici ce qu’on y voit au premier coup d’œil.",
               qTitle="Ton rapport complet répond à ces questions :", cta="Débloquer tout le thème · {price}",
               after="Le rapport complet est écrit uniquement pour ton thème, avec des chapitres dédiés aux domaines choisis dans le quiz.",
               remSubj="{name}, une question de ton thème est restée ouverte", remSubjNoName="Une question de ton thème est restée ouverte",
               remIntro="Hier, nous t’avons envoyé le résumé de ton thème astral. Une question mérite une réponse :",
               remAfter="La réponse est dans ton rapport complet. Tes données sont enregistrées, tu n’as rien à ressaisir.",
               optout="Je ne veux plus recevoir ce type d’e-mails", optoutDone="C’est fait. Nous ne t’enverrons plus d’e-mails avec des horoscopes et des offres."),
    "it": dict(subj="{name}, ecco cosa dice di te il tuo tema natale", subjNoName="Ecco cosa dice di te il tuo tema natale",
               intro="Abbiamo calcolato il tuo tema natale. Ecco cosa si vede a prima vista.",
               qTitle="Il tuo report completo risponde a queste domande:", cta="Sblocca tutto il tema · {price}",
               after="Il report completo è scritto solo per il tuo tema, con capitoli dedicati alle aree scelte nel quiz.",
               remSubj="{name}, una domanda del tuo tema è rimasta aperta", remSubjNoName="Una domanda del tuo tema è rimasta aperta",
               remIntro="Ieri ti abbiamo inviato il riassunto del tuo tema natale. Una domanda merita una risposta:",
               remAfter="La risposta è nel tuo report completo. I tuoi dati sono salvati, non devi reinserire nulla.",
               optout="Non voglio più ricevere queste email", optoutDone="Fatto. Non ti invieremo più email con oroscopi e offerte."),
    "en": dict(subj="{name}, here is what your birth chart says about you", subjNoName="Here is what your birth chart says about you",
               intro="We have calculated your birth chart. Here is what it shows at first glance.",
               qTitle="Your full report answers these questions:", cta="Unlock your full chart · {price}",
               after="The full report is written for your chart only, with chapters on the areas you picked in the quiz.",
               remSubj="{name}, one question from your chart is still open", remSubjNoName="One question from your chart is still open",
               remIntro="Yesterday we sent you a summary of your birth chart. One question from it deserves an answer:",
               remAfter="The answer is in your full report. Your details are saved, so there is nothing to enter again.",
               optout="I don't want these emails any more", optoutDone="Done. We will not send you any more emails with horoscopes and offers."),
}

_CUR = {"eur": "€", "pln": "zł", "ron": "lei", "czk": "Kč", "huf": "Ft"}


def money(lang: str, cur: str, minor: int) -> str:
    """Price as the site shows it: 12,90 € / 49,99 zł / 299 Kč / 4990 Ft / €12.90 (English)."""
    v = minor / 100
    whole = abs(v - round(v)) < 0.005
    num = f"{v:.0f}" if whole else f"{v:.2f}"
    if lang == "en" and cur == "eur":
        return f"€{num}"
    return f"{num.replace('.', ',')} {_CUR.get(cur, cur.upper())}"


def _questions(lang: str, title: str, qs: list[str]) -> str:
    items = "".join(f'<tr><td style="padding:0 10px 10px 0;vertical-align:top;color:#D9B26A;font:17px Georgia,serif">&#10022;</td>'
                    f'<td style="padding:0 0 10px;font:17px/1.55 Georgia,serif;color:#F3EEE3">{esc(q)}</td></tr>' for q in qs)
    return (f'<table role="presentation" cellpadding="0" cellspacing="0" width="100%" style="margin:8px 0 6px;background:#1A2343;border-radius:14px">'
            f'<tr><td style="padding:18px 20px 8px"><p style="margin:0 0 12px;font:700 13px/1.4 Arial,sans-serif;letter-spacing:.06em;'
            f'text-transform:uppercase;color:#D9B26A">{esc(title)}</p><table role="presentation" cellpadding="0" cellspacing="0">{items}</table>'
            f'</td></tr></table>')


def summary2(lang: str, name: str, chart: dict, paras: list[str], questions: list[str], price: str, resume_url: str,
             catchup: bool = False, optout_url: str | None = None) -> tuple[str, str]:
    t, f = T[lang], FUNNEL[lang]
    sun, moon = chart["planets"][0], chart["planets"][1]
    asc = (chart.get("angles") or {}).get("asc")
    items = [(t["big3"][0], sun), (t["big3"][1], moon)] + ([(t["big3"][2], asc)] if asc else [])
    cells = "".join(
        f'<td style="padding:10px 12px;background:#1A2343;border-radius:12px;font:13px Arial,sans-serif;color:#A9B0C6;vertical-align:top">'
        f'{esc(k)}<br><strong style="font:400 19px Georgia,serif;color:#F3EEE3">{esc(sign_name(lang, p["signIndex"]))}</strong></td><td width="8"></td>'
        for k, p in items)
    body = (_p(greeting(lang, name)) + _p(f["cuIntro" if catchup else "intro"])
            + f'<table role="presentation" cellpadding="0" cellspacing="0" style="margin:6px 0 18px"><tr>{cells}</tr></table>'
            + "".join(_p(x) for x in paras)
            + (_questions(lang, f["qTitle"], questions) if questions else "")
            + _button(f["cta"].format(price=price), resume_url) + _p(f["after"]))
    if catchup:
        subject = f["cuSubj"].format(name=name) if name else f["cuSubjNoName"]
        html = layout(lang, body, optout_url)
        return subject, (html.replace(f'>{esc(T[lang]["unsub"])}</a>', f'>{esc(f["optout"])}</a>', 1) if optout_url else html)
    subject = f["subj"].format(name=name) if name else f["subjNoName"]
    return subject, layout(lang, body)


def reminder(lang: str, name: str, question: str, price: str, resume_url: str, optout_url: str) -> tuple[str, str]:
    f = FUNNEL[lang]
    body = (_p(greeting(lang, name)) + _p(f["remIntro"])
            + f'<p style="margin:6px 0 18px;padding:16px 20px;background:#1A2343;border-radius:14px;font:italic 19px/1.5 Georgia,serif;color:#F3EEE3">{esc(question)}</p>'
            + _p(f["remAfter"]) + _button(f["cta"].format(price=price), resume_url))
    subject = f["remSubj"].format(name=name) if name else f["remSubjNoName"]
    return subject, layout(lang, body, optout_url).replace(f'>{esc(T[lang]["unsub"])}</a>', f'>{esc(f["optout"])}</a>', 1)


def optout_page(lang: str, done: bool) -> str:
    f = FUNNEL.get(lang, FUNNEL["en"])
    if done:
        return layout(lang, _p(f["optoutDone"]))
    form = ('<form method="post"><button type="submit" style="padding:14px 26px;border:0;border-radius:999px;'
            f'background:#D9B26A;color:#0B1020;font:700 16px Arial,sans-serif;cursor:pointer">{esc(f["optout"])}</button></form>')
    return layout(lang, form)


# One-off e-mail for leads from before summary v2 (scripts: catchup.py): same body, own subject and intro.
FUNNEL['pl'].update(cuSubj='{name}, jeszcze raz przyjrzeliśmy się Twojemu kosmogramowi', cuSubjNoName='Jeszcze raz przyjrzeliśmy się Twojemu kosmogramowi', cuIntro='Niedawno obliczyliśmy Twój kosmogram. Od tego czasu ulepszyliśmy nasze podsumowania, więc spojrzeliśmy na niego jeszcze raz. Oto, co zobaczyliśmy:')
FUNNEL['hr'].update(cuSubj='{name}, pogledali smo tvoju kartu još jednom', cuSubjNoName='Pogledali smo tvoju natalnu kartu još jednom', cuIntro='Nedavno smo ti izračunali natalnu kartu. Od tada smo poboljšali sažetke, pa smo je pogledali još jednom. Ovo smo vidjeli:')
FUNNEL['sl'].update(cuSubj='{name}, še enkrat smo pogledali tvojo karto', cuSubjNoName='Še enkrat smo pogledali tvojo natalno karto', cuIntro='Pred kratkim smo ti izračunali natalno karto. Od takrat smo izboljšali povzetke, zato smo jo pogledali še enkrat. Tole smo videli:')
FUNNEL['ro'].update(cuSubj='{name}, ne-am mai uitat o dată la harta ta', cuSubjNoName='Ne-am mai uitat o dată la harta ta natală', cuIntro='De curând ți-am calculat harta natală. Între timp ne-am îmbunătățit rezumatele, așa că ne-am mai uitat o dată la ea. Iată ce am văzut:')
FUNNEL['cs'].update(cuSubj='{name}, ještě jednou jsme se podívali na tvůj horoskop', cuSubjNoName='Ještě jednou jsme se podívali na tvůj natální horoskop', cuIntro='Nedávno jsme ti spočítali natální horoskop. Mezitím jsme vylepšili shrnutí, tak jsme se na něj podívali ještě jednou. Tohle jsme viděli:')
FUNNEL['hu'].update(cuSubj='{name}, még egyszer megnéztük a képletedet', cuSubjNoName='Még egyszer megnéztük a születési képletedet', cuIntro='Nemrég kiszámoltuk a születési képletedet. Azóta továbbfejlesztettük az összefoglalóinkat, ezért még egyszer megnéztük. Ezt láttuk:')
FUNNEL['de'].update(cuSubj='{name}, wir haben uns dein Horoskop noch einmal angesehen', cuSubjNoName='Wir haben uns dein Geburtshoroskop noch einmal angesehen', cuIntro='Vor Kurzem haben wir dein Geburtshoroskop berechnet. Seitdem haben wir unsere Zusammenfassungen verbessert und es uns noch einmal angesehen. Das haben wir gesehen:')
FUNNEL['fr'].update(cuSubj='{name}, nous avons regardé ton thème une deuxième fois', cuSubjNoName='Nous avons regardé ton thème astral une deuxième fois', cuIntro='Nous avons calculé ton thème astral il y a peu. Depuis, nous avons amélioré nos résumés, alors nous l’avons regardé une deuxième fois. Voici ce que nous avons vu :')
FUNNEL['it'].update(cuSubj='{name}, abbiamo riguardato il tuo tema', cuSubjNoName='Abbiamo riguardato il tuo tema natale', cuIntro='Di recente abbiamo calcolato il tuo tema natale. Nel frattempo abbiamo migliorato i nostri riassunti, così l’abbiamo riguardato. Ecco cosa abbiamo visto:')
FUNNEL['en'].update(cuSubj='{name}, we took a second look at your chart', cuSubjNoName='We took a second look at your birth chart', cuIntro='We calculated your birth chart recently. Since then we have improved our summaries, so we took a second look at it. Here is what we saw:')

# ---- es (Spain Spanish, informal tú; draft for native review)
MONTHS['es'] = 'enero febrero marzo abril mayo junio julio agosto septiembre octubre noviembre diciembre'
DATE_FMT['es'] = '{d} de {m}'
T['es'] = {'hi': 'Hola, {name}:',
 'hiNoName': 'Hola:',
 'sumSubject': '{name}, el resumen de tu carta natal',
 'sumIntro': 'Aquí tienes un breve resumen de tu carta natal.',
 'sumCta': 'Ver el informe completo',
 'sumAfter': 'El informe completo describe los diez planetas, las casas y los aspectos más importantes.',
 'big3': ('Sol', 'Luna', 'Ascendente'),
 'repSubject': 'Tu informe está listo: {product}',
 'repBody': 'Tu informe «{product}» está listo. Ábrelo aquí abajo. Desde la página también puedes descargarlo en PDF.',
 'repBtn': 'Abrir el informe',
 'products': {'natal': 'Carta natal',
              'partner': 'Compatibilidad de pareja',
              'forecast': 'Previsión {year}',
              'child': 'La carta natal de tu hijo o hija'},
 'subSubject': 'Tu suscripción está activa',
 'subDaily': 'Desde mañana por la mañana recibirás cada día un horóscopo calculado a partir de tu carta natal.',
 'subWeekly': 'Cada lunes por la mañana recibirás el horóscopo de toda la semana, calculado a partir de tu carta natal.',
 'dailySubject': '{name}, tu horóscopo del {date}',
 'weeklySubject': '{name}, tu semana desde el {date}',
 'unsub': 'Darse de baja',
 'unsubDone': 'Te has dado de baja. No te enviaremos más horóscopos.',
 'loginSubject': 'Tu enlace de acceso a Mirastela',
 'loginBody': 'Haz clic en el botón para ver tus informes y tu suscripción. El enlace es válido durante 30 minutos y '
              'una sola vez.',
 'loginBtn': 'Abrir mis informes',
 'loginAfter': 'Si no has pedido este enlace, ignora este correo.',
 'account': 'Mis informes y mis datos',
 'stmt': 'En el extracto de tu tarjeta el pago aparecerá como «LINK.COM* MIRASTELA». Link es el servicio de pago de '
         'Stripe con el que cobramos las compras.',
 'why': 'Recibes este correo porque esta dirección se introdujo en mirastela.com.',
 'disclaimer': 'El contenido tiene fines de entretenimiento y autorreflexión.'}
CAL['es'] = ('Tu calendario astrológico personal',
 'Cada día en tu calendario: un día verde, azul o naranja y un breve consejo, calculados a partir de tu carta '
 'natal. Añádelo con un clic:',
 'Añadir a Google Calendar',
 'Añadir a iPhone / Apple',
 'Otro calendario (Outlook y otros): copia esta dirección y añádela como suscripción desde una URL:')
CUSP['es'] = 'en el límite con:'
FUNNEL['es'] = dict(subj="{name}, esto dice de ti tu carta natal", subjNoName="Esto dice de ti tu carta natal",
                    intro="Hemos calculado tu carta natal. Esto es lo que se ve en ella a primera vista.",
                    qTitle="Tu informe completo responde a estas preguntas:", cta="Desbloquea tu carta completa · {price}",
                    after="El informe completo está escrito solo para tu carta, con capítulos propios sobre las áreas que elegiste en el cuestionario.",
                    remSubj="{name}, una pregunta de tu carta sigue abierta", remSubjNoName="Una pregunta de tu carta sigue abierta",
                    remIntro="Ayer te enviamos el resumen de tu carta natal. Una pregunta merece respuesta:",
                    remAfter="La respuesta está en tu informe completo. Tus datos están guardados, así que no tienes que volver a introducir nada.",
                    optout="No quiero recibir más correos como este", optoutDone="Hecho. No te enviaremos más correos con horóscopos y ofertas.",
                    cuSubj="{name}, hemos vuelto a mirar tu carta", cuSubjNoName="Hemos vuelto a mirar tu carta natal",
                    cuIntro="Hace poco calculamos tu carta natal. Desde entonces hemos mejorado nuestros resúmenes, así que la hemos vuelto a mirar. Esto es lo que hemos visto:")
