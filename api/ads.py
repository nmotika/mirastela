"""Static ad creatives for paid campaigns, drawn with the social.py helpers.

  python ads.py [OUTDIR]     renders every creative in 4:5 (1080x1350, feed) and 9:16 (1080x1920, stories/reels)

Texts live in ADS below, per language; only the languages present are rendered.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw

import social as s
from social import GOLD, INK, MUTED, BG, draw_text, draw_glyph, star, wheel, width

SIGN = {"aries": 0, "taurus": 1, "gemini": 2, "cancer": 3, "leo": 4, "virgo": 5, "libra": 6, "scorpio": 7,
        "sagittarius": 8, "capricorn": 9, "aquarius": 10, "pisces": 11}

# kind: big3 | pair | wheel ; head is the large serif line, sub the smaller text, cta the button
ADS = {
    "pl": [
        {"id": "A1", "kind": "big3", "head": "Znasz swój znak. A swój Księżyc i Ascendent?",
         "rows": [("sun", "Słońce", "to, kim jesteś"), ("moon", "Księżyc", "to, co czujesz"), ("asc", "Ascendent", "to, jak widzą Cię inni")],
         "cta": "Sprawdź za darmo"},
        {"id": "A2", "kind": "big3", "head": "Twój znak to tylko jedna trzecia historii.",
         "rows": [("sun", "Słońce", "?"), ("moon", "Księżyc", "?"), ("asc", "Ascendent", "?")],
         "sub": "Podaj datę, godzinę i miejsce urodzenia. Resztę obliczymy.", "cta": "Oblicz w 2 minuty"},
        {"id": "A3", "kind": "big3", "head": "Lew na zewnątrz, Ryby w środku?",
         "rows": [("sun", "Słońce", "w Lwie"), ("moon", "Księżyc", "w Rybach"), ("asc", "Ascendent", "w Pannie")],
         "sub": "Tak wygląda pełniejszy obraz. Sprawdź swój.", "cta": "Zobacz swój kosmogram"},
        {"id": "B1", "kind": "pair", "head": "Czy wasze znaki naprawdę do siebie pasują?", "pair": ("taurus", "scorpio"),
         "sub": "Porównanie dwóch kosmogramów mówi więcej niż sam znak Słońca.", "cta": "Sprawdź zgodność"},
        {"id": "B2", "kind": "pair", "head": "W miłości liczy się nie tylko znak. Liczą się Wenus i Mars.", "pair": ("venus", "mars"),
         "sub": "Zobacz, jak kochasz i czego szukasz w związku.", "cta": "Zacznij za darmo"},
        {"id": "B3", "kind": "pair", "head": "Ogień i woda. Przyciąganie czy ciągłe iskry?", "pair": ("leo", "cancer"),
         "sub": "Twój kosmogram pokaże, co Was łączy, a co dzieli.", "cta": "Sprawdź za darmo"},
        {"id": "C1", "kind": "wheel", "head": "Co Twój kosmogram mówi o Tobie?",
         "sub": "Słońce, Księżyc, Ascendent, planety i domy. Opisane zrozumiałym językiem.", "cta": "Zacznij za darmo"},
        {"id": "C2", "kind": "wheel", "head": "Niebo w chwili Twoich narodzin wyglądało tak tylko raz.",
         "sub": "Oblicz swój osobisty kosmogram na podstawie efemeryd astronomicznych.", "cta": "Oblicz kosmogram"},
        {"id": "C3", "kind": "wheel", "head": "6 pytań. 2 minuty. Twój kosmogram.",
         "sub": "Bezpłatne podsumowanie od razu. Pełny raport w PDF, jeśli zechcesz.", "cta": "Zacznij za darmo"},
    ],
}

SIZES = {"4x5": (1080, 1350), "9x16": (1080, 1920)}


def sun(d: ImageDraw.ImageDraw, cx: float, cy: float, r: float, col=GOLD):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=col, width=max(3, int(r / 7)))
    d.ellipse((cx - r / 5, cy - r / 5, cx + r / 5, cy + r / 5), fill=col)


def moon(d: ImageDraw.ImageDraw, cx: float, cy: float, r: float, bg, col=GOLD):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col)
    d.ellipse((cx - r * 0.45, cy - r * 1.05, cx + r * 1.4, cy + r * 0.9), fill=bg)


def asc(d: ImageDraw.ImageDraw, cx: float, cy: float, r: float, col=GOLD):
    w = max(3, int(r / 7))
    d.line((cx - r, cy + r * 0.55, cx + r, cy + r * 0.55), fill=col, width=w)
    d.line((cx, cy + r * 0.55, cx, cy - r), fill=col, width=w)
    d.polygon([(cx, cy - r * 1.15), (cx - r * 0.45, cy - r * 0.45), (cx + r * 0.45, cy - r * 0.45)], fill=col)


def planet(d: ImageDraw.ImageDraw, cx: float, cy: float, r: float, which: str, col=GOLD):
    w = max(4, int(r / 6))
    if which == "venus":
        d.ellipse((cx - r * .55, cy - r, cx + r * .55, cy + r * .1), outline=col, width=w)
        d.line((cx, cy + r * .1, cx, cy + r), fill=col, width=w)
        d.line((cx - r * .4, cy + r * .58, cx + r * .4, cy + r * .58), fill=col, width=w)
    else:  # mars
        d.ellipse((cx - r * .75, cy - r * .35, cx + r * .35, cy + r * .75), outline=col, width=w)
        d.line((cx + r * .15, cy - r * .15, cx + r * .8, cy - r * .8), fill=col, width=w)
        d.line((cx + r * .25, cy - r * .8, cx + r * .8, cy - r * .8), fill=col, width=w)
        d.line((cx + r * .8, cy - r * .8, cx + r * .8, cy - r * .25), fill=col, width=w)


def button(d: ImageDraw.ImageDraw, cx: float, y: float, text: str, size: int = 40):
    tw = width(text, "sans-bold", size)
    pw, ph = tw + 110, size * 2.4
    d.rounded_rectangle((cx - pw / 2, y, cx + pw / 2, y + ph), radius=ph / 2, fill=GOLD)
    draw_text(d, (cx, y + ph / 2 + size * 0.36), text, "sans-bold", size, BG, "c")
    return y + ph


def _wrap(text: str, family: str, size: int, max_w: int) -> list[str]:
    """Like social.wrap, but keeps one-letter words (w, z, i, a...) with the next word, as Polish typography wants."""
    words, out, cur = [], [], ""
    for wd in text.split(" "):
        if words and len(words[-1]) == 1:
            words[-1] += "\u00a0" + wd
        else:
            words.append(wd)
    for wd in words:
        t = f"{cur} {wd}".strip()
        if width(t, family, size) > max_w and cur:
            out.append(cur)
            cur = wd
        else:
            cur = t
    return out + [cur] if cur else out


def fit(text: str, family: str, size: int, max_w: int, max_lines: int, min_size: int = 28):
    while size > min_size and len(_wrap(text, family, size, max_w)) > max_lines:
        size -= 2
    return _wrap(text, family, size, max_w)[:max_lines], size


def headline(d, text: str, top: float, w: int, size: int = 84, lines: int = 3) -> float:
    ls, sz = fit(text, "serif", size, w - 160, lines, 52)
    y = top
    for ln in ls:
        y += sz * 1.12
        draw_text(d, (w / 2, y), ln, "serif", sz, INK, "c")
    return y + sz * 0.3


def subline(d, text: str, top: float, w: int, size: int = 36) -> float:
    ls, sz = fit(text, "sans", size, w - 220, 3, 28)
    y = top
    for ln in ls:
        y += sz * 1.4
        draw_text(d, (w / 2, y), ln, "sans", sz, MUTED, "c")
    return y


def brand(d, w: int, top: float):
    tw = width("MIRASTELA", "sans-bold", 30)
    star(d, w / 2 - tw / 2 - 26, top - 10, 15)
    draw_text(d, (w / 2 + 12, top), "MIRASTELA", "sans-bold", 30, GOLD, "c")


def render(ad: dict, w: int, h: int, seed: int) -> Image.Image:
    img = s.night(seed, w, h)
    tall = h > 1500
    d = ImageDraw.Draw(img)
    top = 330 if tall else 120
    brand(d, w, top)
    y = headline(d, ad["head"], top + 40, w)

    if ad["kind"] == "big3":
        y += 90 if tall else 40
        rh = 190 if tall else 150
        for k, (icon, label, val) in enumerate(ad["rows"]):
            y0 = y + k * (rh + 22)
            d.rounded_rectangle((90, y0, w - 90, y0 + rh), radius=26, fill=(20, 27, 52), outline=(70, 66, 70), width=2)
            cx, cy = 185, y0 + rh / 2
            {"sun": lambda: sun(d, cx, cy, 38), "moon": lambda: moon(d, cx, cy, 38, (20, 27, 52)), "asc": lambda: asc(d, cx, cy, 38)}[icon]()
            draw_text(d, (270, cy + 16), label, "sans-bold", 46, INK)
            vs = 70 if val == "?" else 44
            draw_text(d, (w - 135, cy + vs * 0.33), val, "serif-italic" if val != "?" else "serif", vs, GOLD, "r")
        y = y + 3 * (rh + 22) + 20
    elif ad["kind"] == "pair":
        cy = y + (330 if tall else 230)
        r = 150 if tall else 120
        a, b = ad["pair"]
        for cx in (w / 2 - r * 1.25, w / 2 + r * 1.25):
            d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=GOLD, width=3)
        for cx, key in ((w / 2 - r * 1.25, a), (w / 2 + r * 1.25, b)):
            if key in SIGN:
                draw_glyph(d, cx, cy, SIGN[key], int(r * 1.0))
            else:
                planet(d, cx, cy, r * 0.55, key)
        star(d, w / 2, cy, 22)
        y = cy + r + (90 if tall else 60)
    else:  # wheel
        r = 330 if tall else (210 if ad.get("sub") and len(fit(ad["head"], "serif", 84, w - 160, 3, 52)[0]) > 2 else 235)
        cy = y + r + (70 if tall else 40)
        wheel(img, w / 2, cy, r, 0.5)
        d = ImageDraw.Draw(img)
        for k in range(12):
            a = (k + 0.5) / 12 * 2 * math.pi - math.pi / 2
            draw_glyph(d, w / 2 + math.cos(a) * r * 0.745, cy + math.sin(a) * r * 0.745, k, int(r * 0.13), GOLD)
        sun(d, w / 2, cy, r * 0.16)
        y = cy + r + (80 if tall else 50)

    if ad.get("sub"):
        y = subline(d, ad["sub"], y, w)
    by = max(y + 40, h - (500 if tall else 250))
    end = button(d, w / 2, by, ad["cta"])
    draw_text(d, (w / 2, end + 58), "mirastela.com", "sans-bold", 30, MUTED, "c")
    return img


def main():
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "ads_out")
    for lang, ads in ADS.items():
        for n, ad in enumerate(ads):
            for tag, (w, h) in SIZES.items():
                p = out / lang / f"{ad['id']}_{tag}.jpg"
                p.parent.mkdir(parents=True, exist_ok=True)
                render(ad, w, h, 500 + n * 11).save(p, quality=92)
                print(p)


if __name__ == "__main__":
    main()
