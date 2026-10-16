"""Report generation: facts from the chart → prompt → Claude → Markdown.

Without ANTHROPIC_API_KEY the generator returns a test report that lists the computed
facts, so the whole funnel and the data can be checked before the model is wired in.
"""
from __future__ import annotations

import json
import os

LANG_NAME = {"pl": "Polish", "hr": "Croatian", "sl": "Slovenian", "ro": "Romanian",
             "cs": "Czech", "hu": "Hungarian", "en": "English"}

# Localised astrological vocabulary, so the model uses the same terms as the website.
VOCAB = {
    "pl": {"signs": "Baran, Byk, Bliźnięta, Rak, Lew, Panna, Waga, Skorpion, Strzelec, Koziorożec, Wodnik, Ryby",
           "terms": "kosmogram, Ascendent, dom (1.–12.), aspekt, koniunkcja, opozycja, trygon, kwadratura, sekstyl, tranzyt"},
    "hr": {"signs": "Ovan, Bik, Blizanci, Rak, Lav, Djevica, Vaga, Škorpion, Strijelac, Jarac, Vodenjak, Ribe",
           "terms": "natalna karta, podznak (ascendent), kuća (1.–12.), aspekt, konjunkcija, opozicija, trigon, kvadrat, sekstil, tranzit"},
    "sl": {"signs": "Oven, Bik, Dvojčka, Rak, Lev, Devica, Tehtnica, Škorpijon, Strelec, Kozorog, Vodnar, Ribi",
           "terms": "natalna karta, ascendent, hiša (1.–12.), aspekt, konjunkcija, opozicija, trigon, kvadrat, sekstil, tranzit"},
    "ro": {"signs": "Berbec, Taur, Gemeni, Rac, Leu, Fecioară, Balanță, Scorpion, Săgetător, Capricorn, Vărsător, Pești",
           "terms": "hartă natală, ascendent, casă (1–12), aspect, conjuncție, opoziție, trigon, careu, sextil, tranzit"},
    "cs": {"signs": "Beran, Býk, Blíženci, Rak, Lev, Panna, Váhy, Štír, Střelec, Kozoroh, Vodnář, Ryby",
           "terms": "natální horoskop, ascendent, dům (1.–12.), aspekt, konjunkce, opozice, trigon, kvadratura, sextil, tranzit"},
    "hu": {"signs": "Kos, Bika, Ikrek, Rák, Oroszlán, Szűz, Mérleg, Skorpió, Nyilas, Bak, Vízöntő, Halak",
           "terms": "születési képlet, aszcendens, ház (1–12.), fényszög, együttállás, szembenállás, trigon, kvadrát, szextil, tranzit"},
    "en": {"signs": "Aries, Taurus, Gemini, Cancer, Leo, Virgo, Libra, Scorpio, Sagittarius, Capricorn, Aquarius, Pisces",
           "terms": "natal chart, Ascendant, house (1st–12th), aspect, conjunction, opposition, trine, square, sextile, transit"},
}

STYLE = """Writing rules:
- Write entirely in {language}, addressing the reader informally by first name ({name}) in the second person singular.
- Use exactly this vocabulary for signs: {signs}. Other terms: {terms}.
- Use ONLY the facts given below. Never invent positions, houses, aspects or dates.
- Warm, specific, psychologically literate, never generic horoscope filler. Each section must connect at least two facts from the chart.
- Describe tendencies and possibilities, never certainties. No predictions of illness, death, accidents, pregnancy, lottery wins or breakups.
- No medical, legal or financial advice. No fatalism.
- Do not use em dashes or en dashes as punctuation; use commas, colons or separate sentences.
- Output Markdown only: '## ' for section headings, plain paragraphs, occasional short bullet lists. No title line, no preamble, no closing remarks about being an AI.
"""


def _fmt_planets(chart: dict) -> str:
    rows = []
    for p in chart["planets"]:
        house = f", house {p['house']}" if p.get("house") else ""
        rows.append(f"- {p['id']}: {p['sign']} {p['deg']}°{p['min']:02d}'{house}{' (retrograde)' if p['retro'] else ''}")
    if chart.get("angles"):
        a = chart["angles"]
        rows.append(f"- Ascendant: {a['asc']['sign']} {a['asc']['deg']}°")
        rows.append(f"- Midheaven (MC): {a['mc']['sign']} {a['mc']['deg']}°")
    else:
        rows.append("- Birth time unknown: no Ascendant, MC or houses. Do not mention houses or the Ascendant; the Moon sign may be uncertain if the Moon changed sign that day.")
    return "\n".join(rows)


def _fmt_aspects(aspects: list[dict], limit: int | None = None) -> str:
    return "\n".join(f"- {x['a']} {x['type']} {x['b']} (orb {x['orb']}°)" for x in aspects[:limit]) or "- none"


def _header(lang: str, name: str) -> str:
    v = VOCAB[lang]
    return STYLE.format(language=LANG_NAME[lang], name=name or "you", signs=v["signs"], terms=v["terms"])


def prompt_natal(lang: str, name: str, chart: dict, focus: list[str], balance: dict) -> str:
    focus_txt = ", ".join(focus) or "general"
    return f"""{_header(lang, name)}
Task: a full natal chart report, about 2,500 to 3,200 words.

Sections, in this order (translate the headings naturally into {LANG_NAME[lang]}):
1. Introduction: the overall picture of the chart in 2 to 3 paragraphs.
2. Sun: identity and core drive (sign{', house' if chart['timeKnown'] else ''}, key aspects).
3. Moon: emotional needs.
{'4. Ascendant: how others see you, first impressions.' if chart['timeKnown'] else '4. (skip the Ascendant section, birth time unknown)'}
5. Mercury: mind and communication.
6. Venus: love, taste, values.
7. Mars: drive, conflict, desire.
8. Jupiter and Saturn: growth and responsibility.
9. Uranus, Neptune and Pluto: one short section, generational context made personal through house{' ' if chart['timeKnown'] else ''}and aspects only.
10. The three most important aspects, one sub-paragraph each.
11. One chapter for each focus area the reader chose: {focus_txt}.
12. Element and modality balance and what it means in practice.
13. Closing: three concrete, kind suggestions for reflection.

Chart facts (tropical zodiac, Placidus houses):
{_fmt_planets(chart)}

Aspects within orb, tightest first:
{_fmt_aspects(chart['aspects'])}

Element / modality counts: {json.dumps(balance)}
"""


def prompt_partner(lang: str, name: str, partner_name: str, a: dict, b: dict, syn: list[dict]) -> str:
    return f"""{_header(lang, name)}
Task: a relationship compatibility (synastry) report between {name or 'the reader'} (person A) and {partner_name or 'the partner'} (person B), about 1,800 to 2,400 words.
Refer to person B by first name. Be balanced: name strengths and friction points, always constructive.

Sections, in this order (translate headings into {LANG_NAME[lang]}):
1. The overall dynamic of this pair.
2. Emotional connection (Moons, Moon contacts).
3. Attraction and romance (Venus and Mars contacts).
4. Communication (Mercury contacts).
5. Stability and long-term potential (Saturn and Jupiter contacts).
6. Possible friction and how to handle it.
7. Three practical suggestions for the two of them.

Person A chart:
{_fmt_planets(a)}

Person B chart:
{_fmt_planets(b)}

Inter-chart aspects (A planet → B planet), most important first:
{_fmt_aspects(syn, 16)}
"""


def prompt_forecast(lang: str, name: str, natal: dict, tr: dict) -> str:
    ev = "\n".join(
        f"- transiting {e['transit']} {e['type']} natal {e['natal']}: {e['from']} to {e['to']}, exact around {e['exact']}"
        for e in tr["events"]) or "- no major slow-planet transits within 1°"
    signs = "; ".join(f"{p}: " + ", ".join(f"{s['sign']} from {s['from']}" for s in seq) for p, seq in tr["signs"].items())
    return f"""{_header(lang, name)}
Task: a personal forecast for the year {tr['year']}, about 2,000 to 2,600 words.
Dates must be written in the reader's language and local style (day and month names), and only dates from the list below may be used.

Sections, in this order (translate headings into {LANG_NAME[lang]}):
1. The theme of the year in short.
2. One section per quarter (January to March, April to June, July to September, October to December), weaving in the transits active in that quarter with their dates.
3. Love and relationships in {tr['year']}.
4. Work and money in {tr['year']}.
5. The three most important periods of the year, with dates.
6. Closing advice.

Natal chart:
{_fmt_planets(natal)}

Slow-planet transits to the natal chart in {tr['year']} (orb 1°):
{ev}

Sign of the slow planets during the year: {signs}
"""


def _model(fast: bool) -> str:
    if fast:
        return os.environ.get("MIRASTELA_FAST_MODEL", "claude-haiku-5-5")
    return os.environ.get("MIRASTELA_MODEL", "claude-sonnet-5-5")


def has_key() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


SYSTEM = "You are an experienced, careful astrologer and an excellent writer. You write personalised texts for entertainment and self-reflection."


def generate(prompt: str, fast: bool = False, max_tokens: int = 32000, fallback: str | None = None) -> tuple[str, str]:
    """Return (text, model). Without an API key returns a test text so the flow can be checked."""
    model = _model(fast)
    if not has_key():
        if fallback is not None:
            return fallback, "test"
        facts = prompt.split("Chart facts", 1)[-1] if "Chart facts" in prompt else prompt.split("chart:", 1)[-1]
        md = ("## TEST MODE\n\nANTHROPIC_API_KEY is not set, so this is a placeholder instead of the written report. "
              "Below are the facts the model would receive. Check them against another chart calculator.\n\n"
              "## Facts\n\n" + facts.strip())
        return md, "test"
    import anthropic
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    messages = [{"role": "user", "content": prompt}]
    text = ""
    # Long reports in some languages can hit the output limit: continue from where the model stopped.
    for _ in range(3):
        with client.messages.stream(model=model, max_tokens=max_tokens, system=SYSTEM, messages=messages) as stream:
            msg = stream.get_final_message()
        part = "".join(b.text for b in msg.content if b.type == "text")
        text += part if not text or part[:1].isspace() or text[-1:] in "\n " else " " + part
        if msg.stop_reason != "max_tokens":
            break
        text = text.rstrip()
        messages = [{"role": "user", "content": prompt}, {"role": "assistant", "content": text},
                    {"role": "user", "content": "Continue exactly where you stopped, mid-sentence if needed. Do not repeat anything and do not add any preface."}]
    return text.strip(), model


def parse_json(text: str):
    """Model JSON output, tolerant of code fences and stray prose around it."""
    t = text.strip()
    if t.startswith("```"):
        t = t.split("\n", 1)[1].rsplit("```", 1)[0]
    i, j = min([x for x in (t.find("["), t.find("{")) if x >= 0] or [0]), max(t.rfind("]"), t.rfind("}"))
    return json.loads(t[i:j + 1])


# ---------------------------------------------------------------- short texts
def prompt_summary(lang: str, name: str, chart: dict, focus: list[str]) -> str:
    return f"""{_header(lang, name)}
Task: a short free summary of the natal chart for an email, 110 to 150 words, two short paragraphs.
Paragraph 1: the Sun, the Moon{' and the Ascendant' if chart['timeKnown'] else ''} together, as one picture of the person.
Paragraph 2: the single tightest aspect and what it adds, then one sentence saying the full report goes deeper into: {', '.join(focus) or 'love, work and personal growth'}.
Plain text paragraphs only: no headings, no Markdown, no lists, no greeting, no sign-off.

Chart facts (tropical zodiac, Placidus houses):
{_fmt_planets(chart)}

Aspects within orb, tightest first:
{_fmt_aspects(chart['aspects'], 5)}
"""


def prompt_daily_signs(lang: str, day: str, sky_txt: str) -> str:
    v = VOCAB[lang]
    return f"""Task: today's horoscope for all twelve signs, for a website. Date: {day}.
Write entirely in {LANG_NAME[lang]}, addressing the reader informally in the second person singular.
Use exactly this vocabulary for signs: {v['signs']}.
Base every sign's text on the real sky facts below, especially the planets in that sign's solar houses and the Moon's solar house today. Mention at least one concrete fact (a planet and a sign or house) per sign, in plain words.
Tendencies, not certainties. No predictions of illness, death, accidents, pregnancy, lottery wins or breakups. No medical, legal or financial advice.
Do not use em dashes or en dashes as punctuation. Vary sentence openings between signs; no filler.

Output ONLY a JSON array of 12 objects in zodiac order Aries to Pisces, each:
{{"general": "70 to 100 words", "love": "25 to 40 words", "work": "25 to 40 words"}}

Sky facts:
{sky_txt}
"""


def prompt_personal(lang: str, name: str, natal: dict, period_txt: str, weekly: bool) -> str:
    length = "320 to 420 words" if weekly else "150 to 220 words"
    span = "the coming week (Monday to Sunday)" if weekly else "today"
    sections = ("a one-line title, then short sections: the week overall, love, work, the best days, one piece of advice"
                if weekly else "a one-line title, then: the day overall (one paragraph), love (one or two sentences), work (one or two sentences), advice of the day (one sentence)")
    return f"""{_header(lang, name)}
Task: a personal horoscope for {span}, based on transits to the reader's own natal chart, {length}.
Structure: {sections}. Use '## ' only for the title line and '**Label:**' style bold labels for the parts.
Mention the concrete transits in plain words (for example "the Moon passes over your natal Venus"). Never invent transits that are not listed.

Natal chart:
{_fmt_planets(natal)}

Transits for {span}:
{period_txt}
"""
