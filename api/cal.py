"""Personal astrological calendar: a daily label (great / act / slow down) from transits to the
natal chart, a short generated text per day, and an ICS feed that calendar apps subscribe to."""
from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone

import report
import sky

LABELS = {
    "pl": {"super": "Super dzień", "act": "Działaj", "slow": "Zwolnij"},
    "hr": {"super": "Super dan", "act": "Djeluj", "slow": "Uspori"},
    "sl": {"super": "Super dan", "act": "Ukrepaj", "slow": "Upočasni"},
    "ro": {"super": "Zi super", "act": "Acționează", "slow": "Încetinește"},
    "cs": {"super": "Skvělý den", "act": "Jednej", "slow": "Zpomal"},
    "hu": {"super": "Szuper nap", "act": "Cselekedj", "slow": "Lassíts"},
    "en": {"super": "Great day", "act": "Act", "slow": "Slow down"},
}
DOT = {"super": "🟢", "act": "🔵", "slow": "🟠"}
CAL_NAME = {"pl": "Mirastela · mój kalendarz", "hr": "Mirastela · moj kalendar", "sl": "Mirastela · moj koledar",
            "ro": "Mirastela · calendarul meu", "cs": "Mirastela · můj kalendář", "hu": "Mirastela · a naptáram",
            "en": "Mirastela · my calendar"}

# How strongly each transiting planet colours a day, and which ones count as easy or hard on a conjunction.
WEIGHT = {"moon": 0.6, "sun": 0.8, "mercury": 0.6, "venus": 1.0, "mars": 1.0, "jupiter": 1.2,
          "saturn": 1.3, "uranus": 1.0, "neptune": 0.8, "pluto": 1.1}
EASY = {"venus", "jupiter", "sun", "moon"}
HARD = {"mars", "saturn", "uranus", "pluto", "neptune"}
POINT = {"sun": 1.3, "moon": 1.2, "asc": 1.2, "mc": 1.0, "venus": 1.0, "mars": 1.0}


def score(transits: list[dict]) -> float:
    s = 0.0
    for t in transits:
        if t["type"] in ("trine", "sextile"):
            sign = 1
        elif t["type"] in ("square", "opposition"):
            sign = -1
        else:  # conjunction: depends on who is passing over the natal point
            sign = 1 if t["transit"] in EASY else -1 if t["transit"] in HARD else 0.3
        close = 1 - t["orb"] / sky.ORB[t["transit"]]
        s += sign * WEIGHT[t["transit"]] * POINT.get(t["natal"], 0.8) * (0.4 + 0.6 * close)
    return s


def _score_day(natal: dict, d: date) -> tuple[float, list[dict]]:
    tr = sky.personal_transits(natal, d)
    return score(tr), tr


def labels_for(natal: dict, days: list[date]) -> list[tuple[str, list[dict]]]:
    """Labels relative to the person's own rhythm: a day is compared with the 90 days around it, so
    a long Jupiter trine does not turn a whole season green. Roughly 30% great, 25% slow down."""
    lo, hi = days[0] - timedelta(days=45), days[-1] + timedelta(days=45)
    window = {lo + timedelta(days=i): _score_day(natal, lo + timedelta(days=i)) for i in range((hi - lo).days + 1)}
    out = []
    for d in days:
        around = sorted(window[d + timedelta(days=k)][0] for k in range(-45, 46))
        s, tr = window[d]
        top, bottom = around[int(len(around) * 0.70)], around[int(len(around) * 0.25)]
        out.append(("super" if s >= top and s > 0 else "slow" if s <= bottom and s < 0 else "act", tr))
    return out


def days_text(natal: dict, days: list[date]) -> tuple[list[str], list[str]]:
    """Labels for each day, plus the facts for the prompt, one block per day."""
    labels, rows = [], []
    for d, (lab, tr) in zip(days, labels_for(natal, days)):
        labels.append(lab)
        pos = sky.positions(datetime.combine(d, time(12, 0), sky.TZ))
        moon = pos[1]
        h = sky._house(moon["lon"], natal)
        head = f"{d.isoformat()} ({d.strftime('%A')}), label {lab.upper()}: Moon in {moon['sign']}" + (f", natal house {h}" if h else "")
        lines = [f"  - transiting {x['transit']} {x['type']} natal {x['natal']} (orb {x['orb']}°)" for x in tr[:4]]
        rows.append(head + ("\n" + "\n".join(lines) if lines else "\n  - no close transits"))
    return labels, rows


CAL_SCHEMA = {"type": "object", "required": ["days"], "properties": {"days": {"type": "array", "items": {
    "type": "object", "required": ["title", "text"],
    "properties": {"title": {"type": "string"}, "text": {"type": "string"}}}}}}


def prompt(lang: str, name: str, natal: dict, facts: str, n: int) -> str:
    lab = LABELS[lang]
    return f"""{report._header(lang, name)}
Task: entries for a personal astrological calendar, one per day for {n} days, shown as all-day events in the reader's phone calendar.
Every day already has a label computed from the transits: SUPER = "{lab['super']}" (easy, supportive day), ACT = "{lab['act']}" (good for getting things done, mixed energy), SLOW = "{lab['slow']}" (tense day, better to slow down and avoid big decisions). The text must fit the label.
For each day: "title" is 2 to 6 words, a concrete theme for the day (no date, no label word). "text" is 30 to 50 words: what the day favours, one concrete transit in plain words, and one practical tip.
Never invent transits that are not listed. Tendencies, not certainties. Do not use em dashes or en dashes.
Save with the save tool: "days" is a list of exactly {n} entries, in date order.

Natal chart:
{report._fmt_planets(natal)}

Days:
{facts}
"""


def generate(lang: str, name: str, natal: dict, start: date, n: int) -> list[dict]:
    days = [start + timedelta(days=i) for i in range(n)]
    labels, rows = days_text(natal, days)
    fallback = {"days": [{"title": "TEST", "text": r} for r in rows]}
    data, model = report.generate_json(prompt(lang, name, natal, "\n".join(rows), n), CAL_SCHEMA, fast=True, max_tokens=4000, fallback=fallback)
    entries = (data or {}).get("days") or []
    if len(entries) != n and model != "test":
        raise ValueError(f"calendar: expected {n} days, got {len(entries)}")
    out = []
    for i, d in enumerate(days):
        e = entries[i] if i < len(entries) else {"title": "", "text": ""}
        out.append({"day": d.isoformat(), "label": labels[i], "title": e.get("title", "").strip(),
                    "text": e.get("text", "").strip(), "model": model})
    return out


# ---------------------------------------------------------------- ICS
def _esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\r", "").replace("\n", "\\n")


def _fold(line: str) -> str:
    """RFC 5545: lines longer than 75 octets continue on the next line after a space."""
    raw = line.encode("utf-8")
    if len(raw) <= 75:
        return line
    parts, cur = [], b""
    for ch in line:
        b = ch.encode("utf-8")
        if len(cur) + len(b) > (75 if not parts else 74):
            parts.append(cur.decode("utf-8"))
            cur = b""
        cur += b
    parts.append(cur.decode("utf-8"))
    return "\r\n ".join(parts)


def ics(lang: str, name: str, token: str, rows: list[tuple[str, str, str, str]], site: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    cal_name = CAL_NAME[lang] + (f" · {name}" if name else "")
    out = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Mirastela//Calendar//EN", "CALSCALE:GREGORIAN", "METHOD:PUBLISH",
           f"X-WR-CALNAME:{_esc(cal_name)}", "X-WR-TIMEZONE:Europe/Zagreb",
           "REFRESH-INTERVAL;VALUE=DURATION:PT6H", "X-PUBLISHED-TTL:PT6H"]
    for day, lab, title, text in rows:
        d = date.fromisoformat(day)
        summary = f"{DOT[lab]} {LABELS[lang][lab]}" + (f" · {title}" if title else "")
        out += ["BEGIN:VEVENT", f"UID:{day}-{token[:10]}@mirastela.com", f"DTSTAMP:{stamp}",
                f"DTSTART;VALUE=DATE:{d.strftime('%Y%m%d')}", f"DTEND;VALUE=DATE:{(d + timedelta(days=1)).strftime('%Y%m%d')}",
                f"SUMMARY:{_esc(summary)}", f"DESCRIPTION:{_esc(text + chr(10) + chr(10) + site)}",
                "TRANSP:TRANSPARENT", "END:VEVENT"]
    out.append("END:VCALENDAR")
    return "\r\n".join(_fold(x) for x in out) + "\r\n"
