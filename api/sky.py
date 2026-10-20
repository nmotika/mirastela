"""The sky on a given day: positions for the free sign horoscopes and transits for personal ones."""
from __future__ import annotations

from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

import swisseph as swe

from chart import ASPECTS, FLAGS, PLANETS, SIGNS, _sign

TZ = ZoneInfo("Europe/Zagreb")
SKY_PLANETS = [p for p in PLANETS if p[0] != "node"]
# Transit orbs for personal horoscopes: fast movers get a wider orb, slow ones a tight one.
ORB = {"moon": 4.0, "sun": 2.0, "mercury": 2.0, "venus": 2.0, "mars": 1.5,
       "jupiter": 1.5, "saturn": 1.2, "uranus": 1.0, "neptune": 1.0, "pluto": 1.0}
NATAL_POINTS = ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn"]


def today() -> date:
    return datetime.now(TZ).date()


def _jd(dt: datetime) -> float:
    u = dt.astimezone(ZoneInfo("UTC"))
    return swe.julday(u.year, u.month, u.day, u.hour + u.minute / 60 + u.second / 3600)


def positions(dt: datetime) -> list[dict]:
    jd = _jd(dt)
    out = []
    for pid, num in SKY_PLANETS:
        xx, _ = swe.calc_ut(jd, num, FLAGS)
        out.append({"id": pid, "lon": round(xx[0], 3), "speed": xx[3],
                    "retro": xx[3] < 0 and pid not in ("sun", "moon"), **_sign(xx[0])})
    return out


def _angle(a: float, b: float) -> float:
    d = abs(a - b) % 360
    return min(d, 360 - d)


def moon_ingress(day: date) -> str | None:
    """Local time (HH:MM) when the Moon enters a new sign on this day, if it does."""
    start = datetime.combine(day, time(0, 0), TZ)
    prev = int(positions(start)[1]["lon"] // 30)
    for m in range(30, 24 * 60 + 1, 30):
        lon = positions(start + timedelta(minutes=m))[1]["lon"]
        if int(lon // 30) != prev:
            return (start + timedelta(minutes=m - 15)).strftime("%H:%M")
    return None


def moon_signs(day: date) -> tuple[str, str] | None:
    """(sign before, sign after) the Moon's ingress on this day, if it changes sign."""
    start = datetime.combine(day, time(0, 0), TZ)
    a = int(positions(start)[1]["lon"] // 30)
    b = int(positions(start + timedelta(hours=24))[1]["lon"] // 30)
    return (SIGNS[a], SIGNS[b]) if a != b else None


def day_sky(day: date) -> dict:
    """Facts for the twelve sign horoscopes of one day (noon, Zagreb time)."""
    noon = datetime.combine(day, time(12, 0), TZ)
    pos = positions(noon)
    aspects = []
    for i, a in enumerate(pos):
        for b in pos[i + 1:]:
            if "moon" in (a["id"], b["id"]):
                continue
            d = _angle(a["lon"], b["lon"])
            for name, ang, _ in ASPECTS:
                if abs(d - ang) <= 1.5:
                    aspects.append({"a": a["id"], "b": b["id"], "type": name, "orb": round(abs(d - ang), 2)})
    return {"day": day.isoformat(), "planets": pos, "aspects": aspects, "moonIngress": moon_ingress(day)}


AREAS = ["self, body and how you come across", "money, possessions and self-worth", "talks, short trips, siblings and neighbours",
         "home, family and roots", "love affairs, fun, creativity and children", "daily work, routines and health habits",
         "partnerships and close one-to-one relationships", "shared money, intimacy and deep change", "travel, study, beliefs and the big picture",
         "career, reputation and goals", "friends, groups and hopes", "rest, solitude and what happens behind the scenes"]


def sky_text(sky: dict) -> str:
    """Facts for the sign horoscopes, with the solar-house life area already worked out per sign, so the
    model never has to count houses itself (that is where contradictions came from)."""
    rows = [f"- {p['id']}: {p['sign']} {p['deg']}°{' (retrograde)' if p['retro'] else ''}" for p in sky["planets"]]
    if sky["moonIngress"]:
        ms = moon_signs(date.fromisoformat(sky["day"]))
        if ms:
            rows.append(f"- the Moon is in {ms[0]} until about {sky['moonIngress']} local time, then in {ms[1]} for the rest of the day"
                        " (the areas of life below use the Moon's noon sign)")
    asp = [f"- {a['a']} {a['type']} {a['b']} (orb {a['orb']}°)" for a in sky["aspects"]] or ["- no tight aspects between the planets"]
    per_sign = []
    for s, sign in enumerate(SIGNS):
        items = [f"{p['id']} in {p['sign']} → {AREAS[(p['signIndex'] - s) % 12]}" for p in sky["planets"]]
        per_sign.append(f"- {sign}: " + "; ".join(items))
    return ("Planet positions at noon:\n" + "\n".join(rows) + "\n\nAspects between planets today:\n" + "\n".join(asp)
            + "\n\nFor each sign, the area of life each planet touches today (solar houses, already worked out; use exactly these):\n"
            + "\n".join(per_sign))


def _natal_points(natal: dict) -> list[tuple[str, float]]:
    pts = [(p["id"], p["lon"]) for p in natal["planets"] if p["id"] in NATAL_POINTS]
    if not natal["timeKnown"]:
        pts = [p for p in pts if p[0] != "moon"]
    if natal.get("angles"):
        pts += [("asc", natal["angles"]["asc"]["lon"]), ("mc", natal["angles"]["mc"]["lon"])]
    return pts


def _house(lon: float, natal: dict) -> int | None:
    if not natal.get("houses"):
        return None
    from chart import _house_of
    return _house_of(lon, natal["houses"]["cusps"])


def personal_transits(natal: dict, day: date) -> list[dict]:
    """Transits to the natal chart active on this day (noon), tightest first."""
    pos = positions(datetime.combine(day, time(12, 0), TZ))
    hits = []
    for t in pos:
        for nid, nlon in _natal_points(natal):
            d = _angle(t["lon"], nlon)
            for name, ang, _ in ASPECTS:
                if abs(d - ang) <= ORB[t["id"]]:
                    hits.append({"transit": t["id"], "natal": nid, "type": name, "orb": round(abs(d - ang), 2)})
    hits.sort(key=lambda h: (h["orb"] / ORB[h["transit"]]))
    return hits


def personal_text(natal: dict, start: date, days: int) -> str:
    rows = []
    for i in range(days):
        d = start + timedelta(days=i)
        pos = positions(datetime.combine(d, time(12, 0), TZ))
        moon = pos[1]
        h = _house(moon["lon"], natal)
        head = f"{d.isoformat()} ({d.strftime('%A')}): Moon in {moon['sign']}" + (f", in natal house {h}" if h else "")
        tr = personal_transits(natal, d)[: (8 if days == 1 else 5)]
        lines = [f"  - transiting {x['transit']} {x['type']} natal {x['natal']} (orb {x['orb']}°)" for x in tr]
        rows.append(head + ("\n" + "\n".join(lines) if lines else "\n  - no close transits"))
    return "\n".join(rows)
