"""Social media content in every language, generated on the server and (optionally) published to the
Facebook page and Instagram account through the Meta Graph API.

  python social.py morning [DATE]   daily horoscope carousel (cover + 12 signs) and a short reel, all languages;
                                    publishes SOCIAL_LANG if Meta credentials are set
  python social.py evening [DATE]   the evergreen post of the day (14-day rotation), all languages; publishes too
  python social.py plan [LANGS] [--force]  write the 14 evergreen posts per language (skips languages already done)
  python social.py preview          render samples with placeholder text (no model, no publishing)

Files: SOCIAL_DIR (default /var/lib/mirastela/social)/<YYYY-MM-DD>/<lang>/..., caption.txt next to the images.
Env for publishing: META_PAGE_TOKEN (system-user or page token), SOCIAL_PUBLISH=1, SOCIAL_LANGS=pl,hr (pages to post to),
per language META_PAGE_ID_XX and optional IG_USER_ID_XX (META_PAGE_ID / IG_USER_ID without suffix = SOCIAL_LANG, default pl),
SOCIAL_START / SOCIAL_START_XX (YYYY-MM-DD, day 1 of
the evergreen rotation), SOCIAL_MEDIA_URL (public base URL of the files, default https://mirastela.com/api/social).
"""
from __future__ import annotations

import json
import os
import random
import shutil
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from datetime import date, timedelta
from pathlib import Path

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import emails
import report
import sky

HERE = Path(__file__).resolve().parent
FONTS = HERE / "fonts"
OUT = Path(os.environ.get("SOCIAL_DIR", "/var/lib/mirastela/social"))
W, H = 1080, 1350
GOLD, INK, MUTED, BG, PAPER = (217, 178, 106), (243, 238, 227), (169, 176, 198), (11, 16, 32), (246, 241, 231)
GLYPHS = "♈♉♊♋♌♍♎♏♐♑♒♓"
SITE_HOST = "mirastela.com"

# ---------------------------------------------------------------- text drawing with font fallback
_FAMILIES = {
    "serif": ["newsreader-latin-400-normal.ttf", "newsreader-latin-ext-400-normal.ttf"],
    "serif-bold": ["newsreader-latin-600-normal.ttf", "newsreader-latin-ext-600-normal.ttf"],
    "serif-italic": ["newsreader-latin-400-italic.ttf", "newsreader-latin-ext-400-italic.ttf"],
    "sans": ["manrope-latin-400-normal.ttf", "manrope-latin-ext-400-normal.ttf"],
    "sans-bold": ["manrope-latin-700-normal.ttf", "manrope-latin-ext-700-normal.ttf"],
    "glyph": ["noto-sans-symbols-symbols-400-normal.ttf"],
}
_CMAP: dict[str, set[int]] = {}
_CACHE: dict[tuple[str, int], ImageFont.FreeTypeFont] = {}


def _font(file: str, size: int) -> ImageFont.FreeTypeFont:
    key = (file, size)
    if key not in _CACHE:
        _CACHE[key] = ImageFont.truetype(str(FONTS / file), size)
    return _CACHE[key]


def _covers(file: str, ch: str) -> bool:
    if file not in _CMAP:
        _CMAP[file] = set(TTFont(str(FONTS / file)).getBestCmap())
    return ord(ch) in _CMAP[file]


def _runs(text: str, family: str) -> list[tuple[str, str]]:
    """Split text into runs by the font file that has the glyphs (the web fonts are split by script)."""
    files = _FAMILIES[family]
    out: list[tuple[str, str]] = []
    for ch in text:
        f = next((x for x in files if _covers(x, ch)), files[-1])
        if out and out[-1][0] == f:
            out[-1] = (f, out[-1][1] + ch)
        else:
            out.append((f, ch))
    return out


def width(text: str, family: str, size: int) -> float:
    return sum(_font(f, size).getlength(t) for f, t in _runs(text, family))


def draw_text(d: ImageDraw.ImageDraw, xy: tuple[float, float], text: str, family: str, size: int, fill, anchor: str = "l"):
    """y is the baseline; anchor: l (left), c (centre) or r (right)."""
    x, y = xy
    w = width(text, family, size)
    x = x - w / 2 if anchor == "c" else x - w if anchor == "r" else x
    for f, t in _runs(text, family):
        d.text((x, y), t, font=_font(f, size), fill=fill, anchor="ls")
        x += _font(f, size).getlength(t)


def draw_glyph(d: ImageDraw.ImageDraw, cx: float, cy: float, i: int, size: int, fill=None):
    """A zodiac glyph centred on (cx, cy) by its drawn outline."""
    f = _font(_FAMILIES["glyph"][0], size)
    l, t, r, b = f.getbbox(GLYPHS[i], anchor="ls")
    d.text((cx - (l + r) / 2, cy - (t + b) / 2), GLYPHS[i], font=f, fill=fill or GOLD, anchor="ls")


def wrap(text: str, family: str, size: int, max_w: int) -> list[str]:
    lines, cur = [], ""
    for word in text.split():
        t = f"{cur} {word}".strip()
        if width(t, family, size) > max_w and cur:
            lines.append(cur)
            cur = word
        else:
            cur = t
    if cur:
        lines.append(cur)
    return lines


def fit(text: str, family: str, size: int, max_w: int, max_lines: int, min_size: int = 28) -> tuple[list[str], int]:
    """Largest size (down to min_size) at which the text fits in max_lines."""
    while size > min_size:
        lines = wrap(text, family, size, max_w)
        if len(lines) <= max_lines:
            return lines, size
        size -= 2
    return wrap(text, family, size, max_w)[:max_lines], size


# ---------------------------------------------------------------- backgrounds
def night(seed: int, w: int = W, h: int = H) -> Image.Image:
    img = Image.new("RGB", (w, h), BG)
    glow = Image.new("RGB", (w, h), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((w * 0.25, h * 0.55, w * 1.25, h * 1.35), fill=(40, 52, 110))
    glow = glow.filter(ImageFilter.GaussianBlur(160))
    img = Image.blend(img, glow, 0.55)
    d = ImageDraw.Draw(img)
    rnd = random.Random(seed)
    for _ in range(140):
        x, y, r = rnd.random() * w, rnd.random() * h, rnd.random() * 1.8 + 0.4
        c = GOLD if rnd.random() > 0.85 else INK
        a = 0.25 + rnd.random() * 0.6
        col = tuple(int(BG[i] * (1 - a) + c[i] * a) for i in range(3))
        d.ellipse((x - r, y - r, x + r, y + r), fill=col)
    return img


def wheel(img: Image.Image, cx: float, cy: float, r: float, alpha: float = 0.13):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    col = GOLD + (int(255 * alpha),)
    for rr in (r, r * 0.85, r * 0.64):
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=col, width=2)
    import math
    for k in range(12):
        a = k / 12 * 2 * math.pi
        d.line((cx + math.cos(a) * r * 0.85, cy + math.sin(a) * r * 0.85, cx + math.cos(a) * r, cy + math.sin(a) * r), fill=col, width=2)
    img.paste(layer, (0, 0), layer)


def star(d: ImageDraw.ImageDraw, x: float, y: float, s: float, fill=GOLD):
    d.polygon([(x, y - s), (x + s * .2, y - s * .2), (x + s, y), (x + s * .2, y + s * .2), (x, y + s),
               (x - s * .2, y + s * .2), (x - s, y), (x - s * .2, y - s * .2)], fill=fill)


def footer(d: ImageDraw.ImageDraw, w: int = W, h: int = H):
    star(d, w / 2 - width(SITE_HOST, "sans-bold", 30) / 2 - 18, h - 70, 12)
    draw_text(d, (w / 2 + 8, h - 60), SITE_HOST, "sans-bold", 30, MUTED, "c")


# ---------------------------------------------------------------- localisation
WEEKDAYS = {
    "pl": "poniedziałek wtorek środa czwartek piątek sobota niedziela",
    "hr": "ponedjeljak utorak srijeda četvrtak petak subota nedjelja",
    "sl": "ponedeljek torek sreda četrtek petek sobota nedelja",
    "ro": "luni marți miercuri joi vineri sâmbătă duminică",
    "cs": "pondělí úterý středa čtvrtek pátek sobota neděle",
    "hu": "hétfő kedd szerda csütörtök péntek szombat vasárnap",
    "en": "Monday Tuesday Wednesday Thursday Friday Saturday Sunday",
    "de": "Montag Dienstag Mittwoch Donnerstag Freitag Samstag Sonntag",
    "fr": "lundi mardi mercredi jeudi vendredi samedi dimanche",
    "it": "lunedì martedì mercoledì giovedì venerdì sabato domenica",
}
# cover title, swipe hint, caption intro, caption call to action, hashtags
DAILY = {
    "pl": ("Horoskop dzienny", "Przesuń i znajdź swój znak ›", "Horoskop na {date}: co dziś mówi niebo dla Twojego znaku?", "Pełny horoskop i Twój osobisty kosmogram: link w bio.", "#horoskop #horoskopdzienny #astrologia #znakizodiaku #kosmogram"),
    "hr": ("Dnevni horoskop", "Povuci i pronađi svoj znak ›", "Horoskop za {date}: što danas nebo kaže tvom znaku?", "Cijeli horoskop i tvoja osobna natalna karta: link u biografiji.", "#horoskop #dnevnihoroskop #astrologija #horoskopskiznakovi #natalnakarta"),
    "sl": ("Dnevni horoskop", "Podrsaj in poišči svoje znamenje ›", "Horoskop za {date}: kaj danes nebo pravi tvojemu znamenju?", "Celoten horoskop in tvoja osebna natalna karta: povezava v opisu profila.", "#horoskop #dnevnihoroskop #astrologija #znamenja #natalnakarta"),
    "ro": ("Horoscopul zilei", "Glisează și găsește-ți zodia ›", "Horoscopul pentru {date}: ce spune cerul azi pentru zodia ta?", "Horoscopul complet și harta ta natală: link în bio.", "#horoscop #horoscopulzilei #astrologie #zodii #hartanatala"),
    "cs": ("Denní horoskop", "Posuň a najdi své znamení ›", "Horoskop na {date}: co dnes říká nebe tvému znamení?", "Celý horoskop a tvůj osobní natální horoskop: odkaz v biu.", "#horoskop #dennihoroskop #astrologie #znameni #natalnihoroskop"),
    "hu": ("Napi horoszkóp", "Lapozz, és keresd meg a jegyed ›", "Horoszkóp – {date}: mit üzen ma az ég a csillagjegyednek?", "A teljes horoszkóp és a személyes születési képleted: link a bióban.", "#horoszkóp #napihoroszkóp #asztrológia #csillagjegyek #születésiképlet"),
    "en": ("Daily horoscope", "Swipe to find your sign ›", "Your horoscope for {date}: what the sky says for your sign today.", "Full horoscope and your personal birth chart: link in bio.", "#horoscope #dailyhoroscope #astrology #zodiac #birthchart"),
    "de": ("Tageshoroskop", "Wischen und dein Zeichen finden ›", "Dein Horoskop für {date}: was der Himmel heute für dein Sternzeichen bereithält.", "Das ganze Horoskop und dein persönliches Geburtshoroskop: Link in der Bio.", "#horoskop #tageshoroskop #astrologie #sternzeichen #geburtshoroskop"),
    "fr": ("Horoscope du jour", "Fais défiler pour trouver ton signe ›", "Ton horoscope du {date} : ce que le ciel dit à ton signe aujourd’hui.", "L’horoscope complet et ton thème astral personnel : lien en bio.", "#horoscope #horoscopedujour #astrologie #signeastrologique #themeastral"),
    "it": ("Oroscopo del giorno", "Scorri e trova il tuo segno ›", "Il tuo oroscopo per {date}: cosa dice oggi il cielo al tuo segno.", "L’oroscopo completo e il tuo tema natale: link in bio.", "#oroscopo #oroscopodioggi #astrologia #segnizodiacali #temanatale"),
}
ALL_LANGS = list(report.LANG_NAME)


def day_label(lang: str, day: date) -> str:
    wd = WEEKDAYS[lang].split()[day.weekday()]
    return f"{wd}, {emails.fmt_date(lang, day)}"


def sign_names(lang: str) -> list[str]:
    return [s.strip() for s in report.VOCAB[lang]["signs"].split(",")]


# ---------------------------------------------------------------- daily carousel
def cover(lang: str, day: date) -> Image.Image:
    img = night(day.toordinal())
    wheel(img, W / 2, 520, 470)
    d = ImageDraw.Draw(img)
    star(d, W / 2, 180, 34)
    title, hint = DAILY[lang][0], DAILY[lang][1]
    lines, size = fit(title, "serif", 92, W - 160, 1, 60)
    draw_text(d, (W / 2, 330), lines[0], "serif", size, INK, "c")
    label = day_label(lang, day)
    draw_text(d, (W / 2, 410), label[:1].upper() + label[1:], "sans-bold", 36, GOLD, "c")
    names = sign_names(lang)
    for i in range(12):
        col, row = i % 3, i // 3
        x, y = 210 + col * 330, 530 + row * 165
        draw_glyph(d, x, y, i, 64)
        draw_text(d, (x, y + 82), names[i], "sans-bold", 28, INK, "c")
    draw_text(d, (W / 2, H - 140), hint, "sans", 30, MUTED, "c")
    footer(d)
    return img


def sign_slide(lang: str, day: date, i: int, entry: dict) -> Image.Image:
    img = night(day.toordinal() * 13 + i)
    wheel(img, W / 2, 330, 300, 0.10)
    d = ImageDraw.Draw(img)
    d.ellipse((W / 2 - 120, 210, W / 2 + 120, 450), outline=GOLD, width=3)
    draw_glyph(d, W / 2, 330, i, 120)
    draw_text(d, (W / 2, 590), sign_names(lang)[i], "serif", 96, INK, "c")
    label = day_label(lang, day)
    draw_text(d, (W / 2, 660), label[:1].upper() + label[1:], "sans-bold", 30, GOLD, "c")
    text = entry.get("short") or first_sentence(entry.get("general", ""))
    lines, size = fit(text, "serif-italic", 58, W - 200, 5)
    y = 790
    for ln in lines:
        draw_text(d, (W / 2, y), ln, "serif-italic", size, INK, "c")
        y += int(size * 1.32)
    footer(d)
    return img


def first_sentence(text: str) -> str:
    for sep in (". ", "! ", "? "):
        if sep in text:
            return text.split(sep)[0] + sep.strip()
    return text[:140]


def make_reel(slides: list[Path], out: Path, seconds: float = 2.6):
    """Vertical 1080x1920 video from the carousel slides, with a silent audio track."""
    if not shutil.which("ffmpeg"):
        return False
    lst = out.with_name("slides.ffconcat")
    lst.write_text("".join(f"file '{p.name}'\nduration {seconds}\n" for p in slides) + f"file '{slides[-1].name}'\n")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
           "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
           "-vf", "scale=1080:1350,pad=1080:1920:0:285:color=0x0B1020,fps=30,format=yuv420p",
           "-c:v", "libx264", "-preset", "medium", "-crf", "22", "-c:a", "aac", "-shortest", "-movflags", "+faststart", str(out)]
    subprocess.run(cmd, check=True, cwd=out.parent)
    lst.unlink()
    return True


def morning(day: date, langs=None, publish_now: bool = True):
    import app  # the daily texts (generated two days ahead by the batch job)
    for lang in langs or ALL_LANGS:
        try:
            data = app.daily_for(lang, day)
        except Exception as e:
            print("social morning", lang, day, "no daily text:", e, flush=True)
            continue
        folder = OUT / day.isoformat() / lang
        folder.mkdir(parents=True, exist_ok=True)
        slides = [folder / "h00.jpg"]
        cover(lang, day).save(slides[0], quality=92)
        for i, entry in enumerate(data["signs"]):
            p = folder / f"h{i + 1:02d}.jpg"
            sign_slide(lang, day, i, entry).save(p, quality=92)
            slides.append(p)
        intro, cta, tags = DAILY[lang][2], DAILY[lang][3], DAILY[lang][4]
        (folder / "horoscope.txt").write_text(f"{intro.format(date=emails.fmt_date(lang, day))} ✨\n\n{cta}\n\n{tags}\n")
        try:
            make_reel(slides, folder / "horoscope.mp4")
        except Exception as e:
            print("social reel", lang, "failed:", e, flush=True)
        print("social morning", lang, day, "ready", flush=True)
    if publish_now:
        publish_morning(day)


# ---------------------------------------------------------------- evergreen posts (14-day rotation)
TOPICS = [
    "What a birth chart is: a map of the sky at the moment of birth; the Sun, Moon and Ascendant as its three pillars.",
    "The four elements (fire, earth, air, water): which signs belong to each and what each element brings.",
    "Sun sign versus Moon sign: who you are becoming versus what you need to feel safe.",
    "The Ascendant (rising sign): the first impression you make and why it needs the birth time.",
    "Fire signs (Aries, Leo, Sagittarius) in love: what they need and what they give.",
    "Mercury retrograde explained calmly: what it really is, and three practical tips (no fear-mongering).",
    "Earth signs (Taurus, Virgo, Capricorn) at work: their strengths and the kind of work where they thrive.",
    "Air signs (Gemini, Libra, Aquarius) and communication: how they talk, listen and connect.",
    "Water signs (Cancer, Scorpio, Pisces) and emotions: depth, intuition and how to support them.",
    "Why two people with the same Sun sign can be so different: Moon, Ascendant and planets in the chart.",
    "Cardinal, fixed and mutable signs: starters, keepers and adapters.",
    "Your Venus sign: how you love and what makes you feel loved.",
    "Why the birth time matters: houses and Ascendant change every few minutes; how to find your birth time.",
    "A question for the audience: which sign are you, and which trait of your sign do you recognise most? Invite them to answer in the comments.",
]
PLAN_SCHEMA = {"type": "object", "required": ["posts"], "properties": {"posts": {"type": "array", "items": {
    "type": "object", "required": ["title", "text", "caption", "hashtags"],
    "properties": {"title": {"type": "string"}, "text": {"type": "string"}, "caption": {"type": "string"},
                   "hashtags": {"type": "array", "items": {"type": "string"}}}}}}}


def plan_prompt(lang: str) -> str:
    topics = "\n".join(f"{n + 1}. {t}" for n, t in enumerate(TOPICS))
    return f"""Task: 14 social media posts (Facebook and Instagram) for an astrology brand that offers personal birth chart reports.
Write entirely in {report.LANG_NAME[lang]} with its correct alphabet and all diacritics, addressing the reader informally ({report.ADDRESS[lang]}).
Use exactly this vocabulary for signs: {report.VOCAB[lang]['signs']}.
Warm, clear, a little playful, never mystical exaggeration. Tendencies, not predictions. No health, money or legal claims. No em dashes or en dashes as punctuation. No emoji in "title" and "text"; at most two emoji in "caption".
One post per topic, in this order:
{topics}
Fields for each post:
- title: the headline on the image, at most 48 characters.
- text: the body on the image, at most 210 characters, one or two short sentences.
- caption: the post text, 300 to 550 characters, adds something the image does not say; the last sentence invites people to find out their own birth chart (the link is in the profile, do not write a URL). Post 14 asks for comments instead.
- hashtags: 4 to 6 relevant hashtags in {report.LANG_NAME[lang]}, without spaces, each starting with #.
Save the result with the save tool: "posts" is a list of exactly 14 posts.
"""


def plan_path(lang: str) -> Path:
    return OUT / "plan" / f"{lang}.json"


def plan(langs=None, force: bool = False):
    """Languages that already have a plan are skipped (a run that stopped halfway continues where it was)."""
    for lang in langs or ALL_LANGS:
        if plan_path(lang).exists() and not force:
            print("social plan", lang, "already done", flush=True)
            continue
        for attempt in range(3):
            out, _ = report.generate_json(plan_prompt(lang), PLAN_SCHEMA, fast=False, max_tokens=20000)  # above ~21k the SDK requires streaming
            posts = (out or {}).get("posts")
            if isinstance(posts, list) and len(posts) == 14 and all(isinstance(p, dict) and p.get("title") for p in posts):
                text = " ".join(p["title"] + " " + p["text"] for p in posts)
                if not report.daily_problem(lang, {"general": text}):
                    plan_path(lang).parent.mkdir(parents=True, exist_ok=True)
                    plan_path(lang).write_text(json.dumps(posts, ensure_ascii=False, indent=1))
                    print("social plan", lang, "ok", flush=True)
                    break
            print("social plan", lang, "retry", attempt, flush=True)


def rotation_day(day: date, lang: str = "") -> int:
    """Day of the 14-post rotation; each page can start on its own day (SOCIAL_START_HR...)."""
    raw = (os.environ.get(f"SOCIAL_START_{lang.upper()}") if lang else None) or os.environ.get("SOCIAL_START") or day.isoformat()
    return (day - date.fromisoformat(raw)).days % len(TOPICS)


def post_image(lang: str, post: dict, n: int) -> Image.Image:
    img = night(1000 + n * 7)
    wheel(img, W - 120, 220, 330, 0.12)
    d = ImageDraw.Draw(img)
    star(d, 120, 150, 30)
    draw_text(d, (165, 160), "MIRASTELA", "sans-bold", 28, GOLD)
    lines, size = fit(post["title"], "serif", 104, W - 220, 4, 60)
    y = 330 + size
    for ln in lines:
        draw_text(d, (110, y), ln, "serif", size, INK)
        y += int(size * 1.12)
    y += 10 - int(size * 1.12) + int(size * 0.35)
    d.line((110, y, 250, y), fill=GOLD, width=4)
    blines, bsize = fit(post["text"], "sans", 44, W - 220, 6, 30)
    y += 50 + bsize
    for ln in blines:
        draw_text(d, (110, y), ln, "sans", bsize, (214, 218, 230))
        y += int(bsize * 1.45)
    footer(d)
    return img


def evening(day: date, langs=None, publish_now: bool = True):
    for lang in langs or ALL_LANGS:
        n = rotation_day(day, lang)
        p = plan_path(lang)
        if not p.exists():
            print("social evening", lang, "no plan yet (python social.py plan)", flush=True)
            continue
        post = json.loads(p.read_text())[n]
        folder = OUT / day.isoformat() / lang
        folder.mkdir(parents=True, exist_ok=True)
        post_image(lang, post, n).save(folder / "post.jpg", quality=92)
        (folder / "post.txt").write_text(f"{post['caption']}\n\n{' '.join(post['hashtags'])}\n")
        print("social evening", lang, day, "post", n + 1, "ready", flush=True)
    if publish_now:
        publish_evening(day)


# ---------------------------------------------------------------- publishing (Meta Graph API)
GRAPH = "https://graph.facebook.com/v21.0"


_TOKENS: dict[str, str] = {}


def _env(name: str, lang: str) -> str:
    """Per-language setting (META_PAGE_ID_HR...), with the unsuffixed one as the default for SOCIAL_LANG/pl."""
    v = os.environ.get(f"{name}_{lang.upper()}", "")
    if not v and lang == os.environ.get("SOCIAL_LANG", "pl"):
        v = os.environ.get(name, "")
    return v


def publish_langs() -> list[str]:
    raw = os.environ.get("SOCIAL_LANGS") or os.environ.get("SOCIAL_LANG", "pl")
    return [x.strip() for x in raw.split(",") if x.strip() in ALL_LANGS]


def _token(page: str) -> str:
    """META_PAGE_TOKEN may hold the system-user token or a page token; posting needs that page's own token."""
    if page not in _TOKENS:
        tok = os.environ["META_PAGE_TOKEN"]
        if page:
            try:
                q = urllib.parse.urlencode({"fields": "access_token", "access_token": tok})
                with urllib.request.urlopen(f"{GRAPH}/{page}?{q}", timeout=60) as r:
                    tok = json.loads(r.read()).get("access_token") or tok
            except urllib.error.HTTPError:
                pass
        _TOKENS[page] = tok
    return _TOKENS[page]


def _graph(path: str, params: dict, method: str = "POST", page: str = "") -> dict:
    params = {**params, "access_token": _token(page)}
    data = urllib.parse.urlencode(params).encode()
    url = f"{GRAPH}/{path}" if method == "POST" else f"{GRAPH}/{path}?{data.decode()}"
    req = urllib.request.Request(url, data=data if method == "POST" else None, method=method)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"graph {path}: {e.code} {e.read()[:400]!r}") from None


def _media_url(day: date, lang: str, name: str) -> str:
    base = os.environ.get("SOCIAL_MEDIA_URL", f"https://{SITE_HOST}/api/social").rstrip("/")
    return f"{base}/{day.isoformat()}/{lang}/{name}"


def _enabled() -> bool:
    return os.environ.get("SOCIAL_PUBLISH") == "1" and bool(os.environ.get("META_PAGE_TOKEN"))


def _done(day: date, lang: str, what: str) -> Path:
    return OUT / day.isoformat() / lang / f".published-{what}"


def _ig_wait(container: str, page: str):
    for _ in range(60):
        st = _graph(container, {"fields": "status_code"}, "GET", page).get("status_code")
        if st == "FINISHED":
            return
        if st == "ERROR":
            raise RuntimeError(f"instagram container {container} failed")
        time.sleep(5)
    raise RuntimeError("instagram container timeout")


def _each(day: date, what: str, fn):
    """Publish for every language in SOCIAL_LANGS; one failing page does not stop the others."""
    if not _enabled():
        return
    failed = []
    for lang in publish_langs():
        page, ig = _env("META_PAGE_ID", lang), _env("IG_USER_ID", lang)
        if not (page or ig) or _done(day, lang, what).exists():
            continue
        try:
            if fn(day, lang, page, ig):
                _done(day, lang, what).touch()
                print("social published", what, lang, day, flush=True)
        except Exception as e:  # noqa: BLE001
            print("social", what, lang, "error", e, flush=True)
            failed.append(lang)
    if failed:
        raise SystemExit(f"social {what}: failed for {', '.join(failed)}")


def _morning_one(day: date, lang: str, page: str, ig: str) -> bool:
    folder = OUT / day.isoformat() / lang
    if not folder.exists():
        return False
    caption = (folder / "horoscope.txt").read_text()
    names = sorted(p.name for p in folder.glob("h*.jpg"))
    if page:  # Facebook: unpublished photos attached to one post
        ids = [_graph(f"{page}/photos", {"url": _media_url(day, lang, n), "published": "false"}, page=page)["id"] for n in names[:10]]
        _graph(f"{page}/feed", {"message": caption, **{f"attached_media[{k}]": json.dumps({"media_fbid": i}) for k, i in enumerate(ids)}}, page=page)
    if ig:  # Instagram: carousel of up to 10 images (cover + 9 signs; the reel shows all 12)
        children = [_graph(f"{ig}/media", {"image_url": _media_url(day, lang, n), "is_carousel_item": "true"}, page=page)["id"] for n in names[:10]]
        for c in children:
            _ig_wait(c, page)
        car = _graph(f"{ig}/media", {"media_type": "CAROUSEL", "children": ",".join(children), "caption": caption}, page=page)["id"]
        _ig_wait(car, page)
        _graph(f"{ig}/media_publish", {"creation_id": car}, page=page)
        if (folder / "horoscope.mp4").exists():
            reel = _graph(f"{ig}/media", {"media_type": "REELS", "video_url": _media_url(day, lang, "horoscope.mp4"), "caption": caption,
                                          "share_to_feed": "false"}, page=page)["id"]
            _ig_wait(reel, page)
            _graph(f"{ig}/media_publish", {"creation_id": reel}, page=page)
    return True


def _evening_one(day: date, lang: str, page: str, ig: str) -> bool:
    folder = OUT / day.isoformat() / lang
    if not (folder / "post.jpg").exists():
        return False
    caption = (folder / "post.txt").read_text()
    if page:
        _graph(f"{page}/photos", {"url": _media_url(day, lang, "post.jpg"), "caption": caption}, page=page)
    if ig:
        c = _graph(f"{ig}/media", {"image_url": _media_url(day, lang, "post.jpg"), "caption": caption}, page=page)["id"]
        _ig_wait(c, page)
        _graph(f"{ig}/media_publish", {"creation_id": c}, page=page)
    return True


def publish_morning(day: date):
    _each(day, "morning", _morning_one)


def publish_evening(day: date):
    _each(day, "evening", _evening_one)


def prune(keep_days: int = 21):
    cutoff = (sky.today() - timedelta(days=keep_days)).isoformat()
    for p in OUT.glob("20??-??-??"):
        if p.name < cutoff:
            shutil.rmtree(p, ignore_errors=True)


# ---------------------------------------------------------------- preview without the model
def preview(lang: str = "pl", out: Path | None = None):
    out = out or OUT / "preview" / lang
    out.mkdir(parents=True, exist_ok=True)
    day = sky.today()
    cover(lang, day).save(out / "h00.jpg", quality=92)
    entry = {"short": "Dziś łatwiej Ci powiedzieć na głos, czego naprawdę potrzebujesz. Zrób to spokojnie i bez pośpiechu."}
    sign_slide(lang, day, 9, entry).save(out / "h10.jpg", quality=92)
    post = {"title": "Czym jest kosmogram?", "text": "To mapa nieba w chwili Twoich narodzin. Słońce, Księżyc i ascendent to jej trzy filary, a reszta planet dopowiada szczegóły."}
    post_image(lang, post, 0).save(out / "post.jpg", quality=92)
    print("preview in", out)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "morning"
    day = date.fromisoformat(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2][:2] == "20" else sky.today()
    if cmd == "morning":
        morning(day)
        prune()
    elif cmd == "evening":
        evening(day)
    elif cmd == "plan":
        args = [a for a in sys.argv[2:] if a != "--force"]
        plan(args or None, force="--force" in sys.argv)
    elif cmd == "preview":
        preview(sys.argv[2] if len(sys.argv) > 2 else "pl")
