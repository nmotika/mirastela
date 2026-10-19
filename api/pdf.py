"""Report as a real PDF file (WeasyPrint), instead of the browser's print dialog.

The narrative comes from the database; the chart wheel is drawn here from the stored chart. Labels
that only the website has in every language (birth line, the Sun/Moon/Ascendant chips, data tables)
are sent by the report page as plain strings and escaped here; the only resources are the local font files.
Fonts (SIL OFL): Newsreader, Manrope, Noto Sans Symbols, in api/fonts.
"""
from __future__ import annotations

import html
import math
import os
import re

FONTS = os.path.join(os.path.dirname(__file__), "fonts")
SIGN_GLYPHS = "♈♉♊♋♌♍♎♏♐♑♒♓"
PLANET_GLYPHS = {"sun": "☉", "moon": "☽", "mercury": "☿", "venus": "♀", "mars": "♂", "jupiter": "♃",
                 "saturn": "♄", "uranus": "♅", "neptune": "♆", "pluto": "♇", "node": "☊"}
SIGNS = ["aries", "taurus", "gemini", "cancer", "leo", "virgo", "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"]


def esc(s) -> str:
    return html.escape(str(s if s is not None else ""), quote=True)


# ---------------------------------------------------------------- wheel (port of web/src/scripts/wheel.ts)
def _lon(p: dict) -> float:
    if "lon" in p:
        return float(p["lon"])
    return SIGNS.index(p["sign"].lower()) * 30 + p["deg"] + p.get("min", 0) / 60


_GLYPHS = None


def _glyph(ch: str, x: float, y: float, size: float, fill: str) -> str:
    """A symbol as an SVG path from Noto Sans Symbols, so the PDF never falls back to colour emoji."""
    global _GLYPHS
    if ch == "☉":  # not in the font: circle with a dot
        r = size * 0.36
        return (f'<circle cx="{x}" cy="{y}" r="{r:.2f}" fill="none" stroke="{fill}" stroke-width="{size * 0.07:.2f}"/>'
                f'<circle cx="{x}" cy="{y}" r="{size * 0.07:.2f}" fill="{fill}"/>')
    if _GLYPHS is None:
        from fontTools.ttLib import TTFont
        f = TTFont(os.path.join(FONTS, "noto-sans-symbols-symbols-400-normal.ttf"))
        _GLYPHS = (f.getGlyphSet(), f.getBestCmap(), f["head"].unitsPerEm)
    gs, cmap, upm = _GLYPHS
    name = cmap.get(ord(ch))
    if not name:
        return ""
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.boundsPen import BoundsPen
    g = gs[name]
    pen, bp = SVGPathPen(gs), BoundsPen(gs)
    g.draw(pen)
    g.draw(bp)
    x0, y0, x1, y1 = bp.bounds or (0, 0, upm, upm)
    k = size / upm
    tx, ty = x - (x0 + x1) / 2 * k, y + (y0 + y1) / 2 * k
    return f'<path transform="translate({tx:.2f} {ty:.2f}) scale({k:.5f} {-k:.5f})" d="{pen.getCommands()}" fill="{fill}"/>'


def wheel_svg(chart: dict, size: int = 300) -> str:
    R_OUT, R_SIGN, R_PLANET, R_IN = 152, 130, 106, 74
    ang = chart.get("angles") or {}
    asc = _lon(ang["asc"]) if ang.get("asc") else 0.0

    def theta(lon):
        return 180 - (lon - asc)

    def xy(t, r):
        a = math.radians(t)
        return round(r * math.cos(a), 2), round(r * math.sin(a), 2)

    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-160 -160 320 320" width="{size}" height="{size}">',
         '<g fill="none" stroke="#B08A3E" stroke-width="1">']
    for r, op in ((R_OUT, 1), (R_SIGN, 1), (R_IN, .6)):
        o.append(f'<circle r="{r}" stroke-opacity="{op}"/>')
    for i in range(12):
        (x1, y1), (x2, y2) = xy(theta(i * 30), R_SIGN), xy(theta(i * 30), R_OUT)
        o.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>')
    o.append("</g>")
    cusps = (chart.get("houses") or {}).get("cusps")
    if cusps and len(cusps) == 12:
        o.append('<g stroke="#B08A3E" stroke-opacity=".4" stroke-width=".6">')
        for c in cusps:
            (x1, y1), (x2, y2) = xy(theta(c), R_IN), xy(theta(c), R_SIGN)
            o.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>')
        o.append("</g>")
    if ang.get("asc"):
        (xi, yi), (x, y) = xy(theta(asc), R_IN), xy(theta(asc), 160)
        o.append(f'<line x1="{xi}" y1="{yi}" x2="{x}" y2="{y}" stroke="#B08A3E" stroke-width="1.4"/>')
    for i, g in enumerate(SIGN_GLYPHS):
        x, y = xy(theta(i * 30 + 15), 141)
        o.append(_glyph(g, x, y, 11, "#9A7631"))
    lon_of = {p["id"]: _lon(p) for p in chart["planets"]}
    asp = [a for a in (chart.get("aspects") or [])[:8] if a["type"] != "conjunction" and a["a"] in lon_of and a["b"] in lon_of]
    if asp:
        o.append('<g stroke="#B08A3E" stroke-opacity=".45" stroke-width=".6">')
        for a in asp:
            (x1, y1), (x2, y2) = xy(theta(lon_of[a["a"]]), R_IN), xy(theta(lon_of[a["b"]]), R_IN)
            dash = "" if a["type"] in ("square", "opposition") else ' stroke-dasharray="2 2"'
            o.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"{dash}/>')
        o.append("</g>")
    placed = sorted(({"id": i, "lon": l, "pos": l} for i, l in lon_of.items() if i in PLANET_GLYPHS), key=lambda p: p["lon"])
    for _ in range(3):
        for i in range(1, len(placed)):
            if placed[i]["pos"] - placed[i - 1]["pos"] < 8:
                placed[i]["pos"] = placed[i - 1]["pos"] + 8
    o.append('<g stroke="#B08A3E" stroke-width="1">')
    for p in placed:
        (x1, y1), (x2, y2) = xy(theta(p["lon"]), R_SIGN), xy(theta(p["lon"]), R_SIGN - 7)
        o.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>')
    o.append("</g>")
    for p in placed:
        x, y = xy(theta(p["pos"]), R_PLANET)
        o.append(_glyph(PLANET_GLYPHS[p["id"]], x, y, 13, "#1D1A14"))
    o.append('<circle r="2.5" fill="#B08A3E"/></svg>')
    return "".join(o)


# ---------------------------------------------------------------- markdown (model output)
def _inline(s: str) -> str:
    s = esc(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    return re.sub(r"(?<![*\w])\*([^*\s][^*]*?)\*", r"<em>\1</em>", s)


def md_sections(md: str, basis_label: str) -> list[tuple[str, str]]:
    """[(title, html)] split on '## ' headings; '> ' lines become a small 'astrological basis' note."""
    secs, title, lines = [], "", []

    def body(ls):
        out, para, items, quote = [], [], [], []

        def flush():
            nonlocal para, items, quote
            if para:
                out.append(f"<p>{_inline(' '.join(para))}</p>")
                para = []
            if items:
                out.append("<ul>" + "".join(f"<li>{_inline(i)}</li>" for i in items) + "</ul>")
                items = []
            if quote:
                out.append(f'<div class="basis"><b>{esc(basis_label)}</b> {_inline(" ".join(quote))}</div>')
                quote = []
        for raw in ls:
            line = raw.strip()
            if not line:
                flush()
                continue
            m = re.match(r"^#{3,4}\s+(.*)$", line)
            if m:
                flush()
                out.append(f"<h3>{_inline(m.group(1))}</h3>")
                continue
            m = re.match(r"^>\s?(.*)$", line)
            if m:
                if para or items:
                    flush()
                quote.append(m.group(1))
                continue
            m = re.match(r"^[-*]\s+(.*)$", line)
            if m:
                if para or quote:
                    flush()
                items.append(m.group(1))
                continue
            if items or quote:
                flush()
            para.append(line)
        flush()
        return "\n".join(out)

    for raw in md.splitlines():
        m = re.match(r"^#{1,2}\s+(.*)$", raw.strip())
        if m:
            if title or any(x.strip() for x in lines):
                secs.append((title, body(lines)))
            title, lines = m.group(1).replace("**", ""), []
            continue
        lines.append(raw)
    if title or any(x.strip() for x in lines):
        secs.append((title, body(lines)))
    return secs


# ---------------------------------------------------------------- document
CSS = """
@font-face { font-family: MiraSerif; src: url(newsreader-latin-400-normal.ttf); }
@font-face { font-family: MiraSerifX; src: url(newsreader-latin-ext-400-normal.ttf); }
@font-face { font-family: MiraSerif; font-style: italic; src: url(newsreader-latin-400-italic.ttf); }
@font-face { font-family: MiraSerifX; font-style: italic; src: url(newsreader-latin-ext-400-italic.ttf); }
@font-face { font-family: MiraSerif; font-weight: 700; src: url(newsreader-latin-600-normal.ttf); }
@font-face { font-family: MiraSerifX; font-weight: 700; src: url(newsreader-latin-ext-600-normal.ttf); }
@font-face { font-family: MiraSans; src: url(manrope-latin-400-normal.ttf); }
@font-face { font-family: MiraSansX; src: url(manrope-latin-ext-400-normal.ttf); }
@font-face { font-family: MiraSans; font-weight: 700; src: url(manrope-latin-700-normal.ttf); }
@font-face { font-family: MiraSansX; font-weight: 700; src: url(manrope-latin-ext-700-normal.ttf); }
@font-face { font-family: MiraSym; src: url(noto-sans-symbols-symbols-400-normal.ttf); }
@page { size: A4; margin: 20mm 18mm 22mm;
  @bottom-center { content: counter(page); font: 9pt MiraSans, MiraSansX; color: #8A8273; } }
@page :first { @bottom-center { content: none; } }
html { font: 11.5pt/1.55 MiraSerif, MiraSerifX, MiraSym, serif; color: #2B2722; }
h1, h2, h3, .sans, .kick, table, .basis b { font-family: MiraSans, MiraSansX, MiraSym, sans-serif; }
.cover { text-align: center; padding-top: 18mm; page-break-after: always; }
.brand { font: 15pt MiraSerif, MiraSerifX; color: #1D1A14; letter-spacing: .02em; }
.brand span { color: #B08A3E; font-family: MiraSym; }
.kick { font-size: 8.5pt; letter-spacing: .16em; text-transform: uppercase; color: #9A7631; font-weight: 700; margin-top: 16mm; }
.cover h1 { font: 34pt/1.1 MiraSerif, MiraSerifX; color: #1D1A14; margin: 4mm 0 2mm; }
.cover .birth { color: #6E675C; font-size: 11pt; }
.cover .wheel { margin: 10mm auto 8mm; }
.big3 { display: flex; justify-content: center; gap: 4mm; }
.big3 div { border: 0.6pt solid #D9CBAE; border-radius: 3mm; padding: 2.5mm 4mm; min-width: 34mm; text-align: left; }
.big3 .l { display: block; font: 8.5pt MiraSans, MiraSansX; color: #8A8273; }
.big3 strong { font: 700 11pt MiraSans, MiraSansX; color: #1D1A14; }
.big3 .cu { display: block; font: 8pt MiraSans, MiraSansX; color: #9A7631; }
h2 { font: 400 19pt/1.2 MiraSerif, MiraSerifX; color: #1D1A14; margin: 9mm 0 3mm; page-break-after: avoid; }
h3 { font-size: 11.5pt; margin: 5mm 0 2mm; color: #1D1A14; }
p { margin: 0 0 3mm; orphans: 3; widows: 3; }
ul { margin: 0 0 3mm; padding-left: 6mm; }
li { margin-bottom: 1.5mm; }
strong { color: #1D1A14; }
.sum { background: #F4EEE2; border-radius: 4mm; padding: 5mm 6mm 3mm; margin-top: 2mm; }
.sum h2 { margin-top: 0; font-size: 16pt; }
.basis { font: 9pt/1.5 MiraSans, MiraSansX, MiraSym; color: #6E675C; border-left: 1.4pt solid #B08A3E; padding: 1mm 0 1mm 3mm; margin: 1mm 0 4mm; }
.basis b { color: #9A7631; }
.gloss { font-size: 10pt; }
.gloss h2 { font-size: 15pt; }
.data { page-break-before: always; }
table { width: 100%; border-collapse: collapse; font-size: 9.5pt; margin-bottom: 6mm; }
td { padding: 2mm 1.5mm; border-bottom: 0.5pt solid #E3D9C6; vertical-align: top; }
td:last-child { text-align: right; color: #6E675C; white-space: nowrap; }
.disc { margin-top: 10mm; font: 8.5pt MiraSans, MiraSansX; color: #8A8273; text-align: center; }
"""


def render(md: str, chart: dict | None, head: dict, tables: list[dict], basis_label: str, layered: bool) -> bytes:
    """head: {kicker, title, birth, big3: [[label, value, cusp]], disclaimer}; tables: [{title, rows: [[...]]}]."""
    from weasyprint import HTML

    big3 = "".join(f'<div><span class="l">{esc(r[0])}</span><strong>{esc(r[1])}</strong>'
                   + (f'<span class="cu">{esc(r[2])}</span>' if len(r) > 2 and r[2] else "") + "</div>"
                   for r in (head.get("big3") or [])[:3])
    cover = (f'<section class="cover"><div class="brand"><span>✦</span> Mirastela</div>'
             f'<p class="kick">{esc(head.get("kicker"))}</p><h1>{esc(head.get("title"))}</h1>'
             f'<p class="birth">{esc(head.get("birth"))}</p>'
             + (f'<div class="wheel">{wheel_svg(chart, 330)}</div>' if chart else "")
             + f'<div class="big3">{big3}</div></section>')
    secs = md_sections(md, basis_label)
    parts = []
    for i, (title, body) in enumerate(secs):
        cls = "sum" if layered and i == 0 else "gloss" if layered and i == len(secs) - 1 and len(secs) > 2 else ""
        parts.append(f'<section class="{cls}">' + (f"<h2>{_inline(title)}</h2>" if title else "") + body + "</section>")
    data = ""
    for t in tables[:4]:
        rows = "".join("<tr>" + "".join(f"<td>{esc(c)}</td>" for c in r[:4]) + "</tr>" for r in (t.get("rows") or [])[:40])
        data += f'<h2>{esc(t.get("title"))}</h2><table>{rows}</table>'
    doc = (f'<!doctype html><html lang="{esc(head.get("lang", "en"))}"><head><meta charset="utf-8"><style>{CSS}</style></head><body>'
           + cover + "".join(parts) + (f'<section class="data">{data}</section>' if data else "")
           + f'<p class="disc">{esc(head.get("disclaimer"))}</p></body></html>')

    # All strings from the browser are escaped and the SVG is drawn here, so the only URLs are our font files.
    return HTML(string=doc, base_url="file://" + FONTS + "/").write_pdf()
