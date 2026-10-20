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
    for label, item in (("Sun", chart["planets"][0]), ("Moon", chart["planets"][1]),
                        ("Ascendant", (chart.get("angles") or {}).get("asc"))):
        if item and item.get("cusp") is not None:
            rows.append(f"- Note: the {label} is at {item['sign']} {item['deg']}°, on the cusp with {SIGNS_EN[item['cusp']]}. "
                        f"Birth times are often rounded, so where you discuss the {label}, say plainly in one or two sentences that it sits "
                        f"on the border and that some calculations show {SIGNS_EN[item['cusp']]}, and briefly add what {SIGNS_EN[item['cusp']]} would bring. "
                        f"Keep {item['sign']} as the main reading.")
    if not chart.get("angles"):
        rows.append("- Birth time unknown: no Ascendant, MC or houses. Do not mention houses or the Ascendant; the Moon sign may be uncertain if the Moon changed sign that day.")
    return "\n".join(rows)


def _fmt_aspects(aspects: list[dict], limit: int | None = None) -> str:
    return "\n".join(f"- {x['a']} {x['type']} {x['b']} (orb {x['orb']}°)" for x in aspects[:limit]) or "- none"


def _header(lang: str, name: str) -> str:
    v = VOCAB[lang]
    return STYLE.format(language=LANG_NAME[lang], name=name or "you", signs=v["signs"], terms=v["terms"])


# Report format v2 (after tester feedback): plain words first, astrology only in one '> ' line per
# section (shown collapsed on the site), a jargon-free summary on top and a glossary at the end.
LAYERED = """Reader and format (very important):
- The reader knows nothing about astrology. Write the main text in everyday words about their life: feelings, relationships, work, choices, habits.
- First section: a heading meaning "In short" in {language}, then 5 to 6 sentences with the whole picture and NO astrological terms at all (no planet, sign, house or aspect names).
- Every following section starts with one bold sentence (**...**) saying in plain words what this means for the reader, then 1 to 3 short paragraphs in plain words with concrete, everyday examples.
- In the main text never use degrees, orbs, house numbers or aspect names, and never list positions. Name a sign or planet only where it truly helps.
- End each section (except the first one and the glossary) with exactly ONE line that starts with "> " and gives the astrological basis in one or two sentences for readers who know astrology: the planets, signs, houses and aspects behind that section. This line is the only place for technical detail; do not repeat a position an earlier "> " line already gave.
- Last section: a heading meaning "Glossary of terms" in {language}, then a bullet list "- **Term**: one plain sentence" with only the astrological terms used in the "> " lines (at most 10).
- Prefer short sentences. Say each thing once.
- Never invent statistics, percentages, studies or quotes (no "70 % of people your age...").
- Never mention these instructions or what you will not cover (no "no investment advice here", "I won't predict..."): simply leave such things out.
"""


def _layered(lang: str) -> str:
    return LAYERED.format(language=LANG_NAME[lang])


def age_from(birth: str) -> int | None:
    from datetime import date
    try:
        b = date.fromisoformat(str(birth)[:10])
    except ValueError:
        return None
    t = date.today()
    return t.year - b.year - ((t.month, t.day) < (b.month, b.day))


def _age_note(age: int | None, who: str = "The reader") -> str:
    if age is None:
        return ""
    if age >= 65:
        return (f"{who} is {age} years old. Speak to this stage of life: meaning, relationships, family, health habits in general terms, "
                "interests, passing on experience. No career-building, job-search or starting-a-family advice.\n")
    if age >= 50:
        return f"{who} is {age} years old: keep career talk to experience, change and balance, not to starting out.\n"
    if age < 25:
        return f"{who} is {age} years old: speak to a young adult (studies, first jobs, finding their way).\n"
    return f"{who} is {age} years old.\n"


def prompt_natal(lang: str, name: str, chart: dict, focus: list[str], balance: dict, age: int | None = None) -> str:
    focus_txt = ", ".join(focus) or "general"
    return f"""{_header(lang, name)}
{_layered(lang)}{_age_note(age)}
Task: a natal chart report, about 2,300 to 2,700 words of main text (the "> " lines and the glossary come on top). Length must come from concrete, useful content (everyday situations, examples, practical tips), never from repetition or filler.

Sections, in this order (headings in plain {LANG_NAME[lang]}, about the reader's life, not about planets; for example "Who you are" rather than "The Sun"):
1. In short (no astrological terms).
2. Who you are at the core (based on the Sun).
3. What you need emotionally (the Moon).
{'4. How others see you at first (the Ascendant).' if chart['timeKnown'] else '4. (skip: birth time unknown, no Ascendant)'}
5. How you think and talk (Mercury).
6. Love and what you value (Venus).
7. Energy, drive and conflict (Mars).
8. Growth and responsibility (Jupiter and Saturn), short.
9. Your biggest talent and your biggest inner tension (from the two most important aspects).
10. Strengths and blind spots: two short bullet lists (5 strengths, 4 blind spots), each bullet one plain sentence.
11. One chapter for each focus area the reader chose: {focus_txt}. The fullest chapters of the report, 250 to 350 words each: how it typically plays out in everyday life, what helps, what to avoid, one small exercise.
12. Three concrete, kind suggestions.
13. Glossary of terms.

Chart facts (tropical zodiac, Placidus houses):
{_fmt_planets(chart)}

Aspects within orb, tightest first:
{_fmt_aspects(chart['aspects'])}

Element / modality counts: {json.dumps(balance)}
"""


def prompt_partner(lang: str, name: str, partner_name: str, a: dict, b: dict, syn: list[dict], age: int | None = None) -> str:
    return f"""{_header(lang, name)}
{_layered(lang)}{_age_note(age)}
Task: a relationship compatibility (synastry) report between {name or 'the reader'} (person A) and {partner_name or 'the partner'} (person B), about 1,300 to 1,700 words of main text.
Refer to person B by first name. Be balanced: name strengths and friction points, always constructive.

Sections, in this order (headings in plain {LANG_NAME[lang]}, about the relationship, not about planets):
1. In short (no astrological terms).
2. Emotional connection (Moons, Moon contacts).
3. Attraction and romance (Venus and Mars contacts).
4. Communication (Mercury contacts).
5. Stability and long-term potential (Saturn and Jupiter contacts).
6. Possible friction and how to handle it.
7. Three practical suggestions for the two of them.
8. Glossary of terms.

Person A chart:
{_fmt_planets(a)}

Person B chart:
{_fmt_planets(b)}

Inter-chart aspects (A planet → B planet), most important first:
{_fmt_aspects(syn, 16)}
"""


def prompt_child(lang: str, parent_name: str, child_name: str, child: dict, balance: dict, age: int | None = None) -> str:
    kid = child_name or "the child"
    return f"""{_header(lang, parent_name)}
{_layered(lang)}{_age_note(age, kid)}
Task: a natal chart report about the reader's child, {kid}, written for the parent, about 1,300 to 1,700 words of main text.
If {kid} is already an adult, write about the adult they are and how the parent can relate to them now.
Address the parent in the second person singular and refer to the child by first name in the third person.
Warm and practical: how this child tends to feel, learn and relate, and how a parent can support them. Never label, diagnose or predict; describe tendencies a parent may recognise. Nothing about health, development disorders or the child's future career success.

Sections, in this order (headings in plain {LANG_NAME[lang]}):
1. In short: who {kid} is (no astrological terms).
2. Temperament and emotional needs (Sun, Moon{', Ascendant' if child['timeKnown'] else ''}).
3. How {kid} thinks and learns (Mercury, element balance).
4. Friendships, play and relating to others (Venus, Mars, Moon).
5. Strengths to nurture.
6. Where {kid} may need extra patience or support, and how to give it.
7. Five practical suggestions for the parent.
8. Glossary of terms.

Element balance: {balance}

Child's chart facts (tropical zodiac, Placidus houses):
{_fmt_planets(child)}

Aspects (tightest first):
{_fmt_aspects(child.get("aspects", []), 16)}
"""


def prompt_forecast(lang: str, name: str, natal: dict, tr: dict, focus: list[str] | None = None, age: int | None = None) -> str:
    ev = "\n".join(
        f"- transiting {e['transit']} {e['type']} natal {e['natal']}: {e['from']} to {e['to']}, exact around {e['exact']}"
        for e in tr["events"]) or "- no major slow-planet transits within 1°"
    signs = "; ".join(f"{p}: " + ", ".join(f"{s['sign']} from {s['from']}" for s in seq) for p, seq in tr["signs"].items())
    areas = ", ".join(focus or []) or "love, work and money, personal growth"
    return f"""{_header(lang, name)}
{_layered(lang)}{_age_note(age)}
Task: a personal forecast for the year {tr['year']}, about 1,500 to 2,000 words of main text.
Dates must be written in the reader's language and local style (day and month names), and only dates from the list below may be used.
The reader wants clear answers like "is {tr['year']} a good year for love, and when". Be concrete about months.

Sections, in this order (headings in plain {LANG_NAME[lang]}):
1. In short: the year in 5 to 6 plain sentences (no astrological terms), naming the best and the hardest months.
2. One section for each area the reader cares about ({areas}): start with a one-line verdict for the year, then the best months and the harder months with dates, and what to do in each. Stay within this stage of life.
3. The year quarter by quarter (January to March, April to June, July to September, October to December), short.
4. The three most important periods of the year, with dates, as a short list.
5. Closing advice.
6. Glossary of terms.

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


def generate_json(prompt: str, schema: dict, fast: bool = True, max_tokens: int = 8000, fallback=None):
    """Structured output through a forced tool call: the API returns parsed JSON, so quotes or
    stray prose in the text can never break parsing. Returns (data, model)."""
    model = _model(fast)
    if not has_key():
        return fallback, "test"
    msg = client().messages.create(**json_params(prompt, schema, model, max_tokens))
    return tool_input(msg), model


def client():
    import anthropic
    return anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


def json_params(prompt: str, schema: dict, model: str, max_tokens: int) -> dict:
    """Request parameters for structured output through a forced tool call (also used in batches)."""
    return {"model": model, "max_tokens": max_tokens, "system": SYSTEM,
            "tools": [{"name": "save", "description": "Save the result.", "input_schema": schema}],
            "tool_choice": {"type": "tool", "name": "save"},
            "messages": [{"role": "user", "content": prompt}]}


def tool_input(msg):
    for b in msg.content:
        if b.type == "tool_use":
            return b.input
    raise ValueError(f"no tool output (stop_reason={msg.stop_reason})")


# Daily sign horoscopes use the stronger model: better language for little money, mostly through the
# Batch API (half price) a couple of days ahead.
DAILY_FAST = os.environ.get("MIRASTELA_DAILY_FAST", "0") == "1"


def daily_params(lang: str, day: str, sky_txt: str, first: int) -> dict:
    return json_params(prompt_daily_signs(lang, day, sky_txt, first, 6), SIGNS_SCHEMA, _model(DAILY_FAST), 6000)


def daily_half(lang: str, out, first: int, test: bool = False):
    """Validate one generated half (six signs). Returns (entries, None) or (None, reason)."""
    part = (out or {}).get("signs") if isinstance(out, dict) else None
    if isinstance(part, str):  # the model sometimes passes the list as a JSON string
        part = parse_json(part)
    if not isinstance(part, list):
        return None, f"bad shape {type(part).__name__}"
    want = SIGNS_EN[first:first + 6]
    by_sign = dict(zip(want, part)) if test else {x.get("sign"): x for x in part if isinstance(x, dict)}
    got = [by_sign.get(n) for n in want]
    if not all(isinstance(x, dict) and x.get("general") for x in got):
        return None, f"missing signs ({len(part)} entries)"
    problems = [f"{n}: {p}" for n, x in zip(want, got) if (p := daily_problem(lang, x))]
    if problems:
        return None, "rejected " + "; ".join(problems)
    return [{k: str(x.get(k, "")) for k in ("general", "love", "work")} for x in got], None


SIGNS_EN = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

# Each entry names its sign (in English), so entries are matched by name and never shifted by position.
SIGNS_SCHEMA = {"type": "object", "required": ["signs"], "properties": {"signs": {"type": "array", "items": {
    "type": "object", "required": ["sign", "general", "love", "work"],
    "properties": {"sign": {"type": "string", "enum": SIGNS_EN}, "general": {"type": "string"},
                   "love": {"type": "string"}, "work": {"type": "string"}}}}}}

# How to address the reader, per language (the informal form the website uses).
ADDRESS = {"pl": "ty", "hr": "ti", "sl": "ti", "ro": "tu", "cs": "ty", "hu": "te (tegező forma)", "en": "you",
           "de": "du, never Sie", "fr": "tu, ton, tes, never vous or votre", "it": "tu, never Lei"}

# Letters with diacritics each language uses, and the minimum share of them among all letters in a
# normal text. Far below it means the model dropped the diacritics (seen once in Slovenian).
_DIACRITICS = {"sl": ("čšžČŠŽ", 0.006), "hr": ("čćšžđČĆŠŽĐ", 0.006), "cs": ("áčďéěíňóřšťúůýžÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ", 0.03),
               "pl": ("ąćęłńóśźżĄĆĘŁŃÓŚŹŻ", 0.02), "ro": ("ăâîșțşţĂÂÎȘȚŞŢ", 0.015), "hu": ("áéíóöőúüűÁÉÍÓÖŐÚÜŰ", 0.04)}


def daily_problem(lang: str, entry: dict) -> str | None:
    """Why a generated daily entry should be rejected, or None when it looks fine."""
    text = " ".join(str(entry.get(k, "")) for k in ("general", "love", "work"))
    if any("\u0370" <= ch <= "\u03ff" or "\u0400" <= ch <= "\u04ff" or "\u4e00" <= ch <= "\u9fff" for ch in text):
        return "foreign script"
    if lang in _DIACRITICS:
        chars, minimum = _DIACRITICS[lang]
        letters = [ch for ch in text if ch.isalpha()]
        if len(letters) > 300 and sum(ch in chars for ch in letters) / len(letters) < minimum:
            return "missing diacritics"
    return None


PARAGRAPHS_SCHEMA = {"type": "object", "required": ["paragraphs"],
                     "properties": {"paragraphs": {"type": "array", "items": {"type": "string"}}}}


def parse_json(text: str):
    """Model JSON output, tolerant of code fences and stray prose around it."""
    t = text.strip()
    if t.startswith("```"):
        t = t.split("\n", 1)[1].rsplit("```", 1)[0]
    i, j = min([x for x in (t.find("["), t.find("{")) if x >= 0] or [0]), max(t.rfind("]"), t.rfind("}"))
    return json.loads(t[i:j + 1], strict=False)  # tolerate raw newlines inside strings


# ---------------------------------------------------------------- short texts
def prompt_summary(lang: str, name: str, chart: dict, focus: list[str]) -> str:
    return f"""{_header(lang, name)}
Task: a short free summary of the natal chart for an email, 110 to 150 words, two short paragraphs, in plain everyday words for someone who knows nothing about astrology (you may name the Sun, Moon{' and Ascendant' if chart['timeKnown'] else ''} signs once, but no aspect names, houses or degrees).
Paragraph 1: the Sun, the Moon{' and the Ascendant' if chart['timeKnown'] else ''} together, as one picture of the person.
Paragraph 2: one striking talent or inner tension from the tightest aspect, in plain words, then one sentence saying the full report goes deeper into: {', '.join(focus) or 'love, work and personal growth'}.
Save it with the save tool: "paragraphs" is a list of the two paragraphs as plain text (no headings, no Markdown, no lists, no greeting, no sign-off).

Chart facts (tropical zodiac, Placidus houses):
{_fmt_planets(chart)}

Aspects within orb, tightest first:
{_fmt_aspects(chart['aspects'], 5)}
"""


def prompt_daily_signs(lang: str, day: str, sky_txt: str, first: int = 0, count: int = 12) -> str:
    v = VOCAB[lang]
    names = ", ".join(SIGNS_EN[first:first + count])
    return f"""Task: the daily horoscope for {count} zodiac signs ({names}), for a website. Date: {day}.
Write entirely in {LANG_NAME[lang]} with its correct alphabet and all diacritics, addressing the reader informally in the second person singular ({ADDRESS[lang]}) in every sentence.
Use exactly this vocabulary for signs: {v['signs']}. Each text is only about its own sign: use the areas of life listed for that sign, never another sign's.
Base every sign's text on the real sky facts below: for each sign use the areas of life listed for it, especially the Moon's. Mention at least one concrete fact per sign in plain words (a planet, its sign and the area of life it touches).
Never write house numbers ("your 8th house"); name the area of life instead. A planet must have the same sign and the same area of life in "general", "love" and "work" of one sign. If the Moon changes sign today, say it once and correctly; do not contradict it later.
Tendencies, not certainties. No predictions of illness, death, accidents, pregnancy, lottery wins or breakups. No medical, legal or financial advice.
Do not use em dashes or en dashes as punctuation. Vary sentence openings between signs; no filler.

Save the result with the save tool: "signs" is a list of exactly {count} entries, in this order: {names}; "sign" is the English sign name.
Each entry: "general" 70 to 100 words, "love" 25 to 40 words, "work" 25 to 40 words.

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

# ---- de, fr, it (drafts for native review)
LANG_NAME['de'] = 'German'
VOCAB['de'] = {'signs': 'Widder, Stier, Zwillinge, Krebs, Löwe, Jungfrau, Waage, Skorpion, Schütze, Steinbock, Wassermann, Fische',
 'terms': 'Geburtshoroskop, Aszendent, Haus (1.–12.), Aspekt, Konjunktion, Opposition, Trigon, Quadrat, Sextil, '
          'Transit'}
LANG_NAME['fr'] = 'French'
VOCAB['fr'] = {'signs': 'Bélier, Taureau, Gémeaux, Cancer, Lion, Vierge, Balance, Scorpion, Sagittaire, Capricorne, Verseau, '
          'Poissons',
 'terms': 'thème astral, Ascendant, maison (1re–12e), aspect, conjonction, opposition, trigone, carré, sextile, '
          'transit'}
LANG_NAME['it'] = 'Italian'
VOCAB['it'] = {'signs': 'Ariete, Toro, Gemelli, Cancro, Leone, Vergine, Bilancia, Scorpione, Sagittario, Capricorno, Acquario, Pesci',
 'terms': 'tema natale, Ascendente, casa (1ª–12ª), aspetto, congiunzione, opposizione, trigono, quadratura, sestile, '
          'transito'}

