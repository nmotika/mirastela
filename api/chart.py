"""Natal chart calculation on top of the Swiss Ephemeris (pyswisseph).

Licensing: Swiss Ephemeris is used here under the GNU AGPL. Running it as a public
web service requires offering this service's complete source code to its users,
until a Swiss Ephemeris Professional License is purchased.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time
from zoneinfo import ZoneInfo

import swisseph as swe

# Moshier ephemeris is built in (no data files needed) and is accurate to well
# under an arcsecond for the planets, which is more than enough for astrology.
FLAGS = swe.FLG_MOSEPH | swe.FLG_SPEED

PLANETS = [
    ("sun", swe.SUN), ("moon", swe.MOON), ("mercury", swe.MERCURY),
    ("venus", swe.VENUS), ("mars", swe.MARS), ("jupiter", swe.JUPITER),
    ("saturn", swe.SATURN), ("uranus", swe.URANUS), ("neptune", swe.NEPTUNE),
    ("pluto", swe.PLUTO), ("node", swe.TRUE_NODE),
]
SIGNS = ["aries", "taurus", "gemini", "cancer", "leo", "virgo", "libra",
         "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"]

# (name, exact angle, base orb)
ASPECTS = [("conjunction", 0, 8), ("opposition", 180, 8), ("trine", 120, 7),
           ("square", 90, 7), ("sextile", 60, 5)]
LUMINARIES = {"sun", "moon"}


@dataclass
class BirthData:
    day: date
    clock: time | None          # None = birth time unknown
    lat: float
    lon: float
    tz: str


def _sign(lon: float) -> dict:
    lon %= 360
    idx = int(lon // 30)
    deg = lon - idx * 30
    return {"sign": SIGNS[idx], "signIndex": idx, "deg": int(deg),
            "min": int(round((deg - int(deg)) * 60)) % 60}


def _house_of(lon: float, cusps: list[float]) -> int:
    for i in range(12):
        a, b = cusps[i], cusps[(i + 1) % 12]
        span = (b - a) % 360
        if (lon - a) % 360 < span:
            return i + 1
    return 12


def calculate(b: BirthData) -> dict:
    time_known = b.clock is not None
    local = datetime.combine(b.day, b.clock or time(12, 0), tzinfo=ZoneInfo(b.tz))
    utc = local.astimezone(ZoneInfo("UTC"))
    jd = swe.julday(utc.year, utc.month, utc.day,
                    utc.hour + utc.minute / 60 + utc.second / 3600)

    planets = []
    for name, pid in PLANETS:
        xx, _ = swe.calc_ut(jd, pid, FLAGS)
        planets.append({"id": name, "lon": round(xx[0], 4),
                        "retro": xx[3] < 0 and name not in LUMINARIES and name != "node",
                        **_sign(xx[0])})

    houses = None
    angles = None
    if time_known:
        hsys = b"P"  # Placidus; fails above the polar circles
        try:
            cusps, ascmc = swe.houses_ex(jd, b.lat, b.lon, hsys)
        except swe.Error:
            hsys = b"W"
            cusps, ascmc = swe.houses_ex(jd, b.lat, b.lon, hsys)
        cusps = list(cusps)[:12]
        houses = {"system": hsys.decode(), "cusps": [round(c, 4) for c in cusps]}
        angles = {"asc": {"lon": round(ascmc[0], 4), **_sign(ascmc[0])},
                  "mc": {"lon": round(ascmc[1], 4), **_sign(ascmc[1])}}
        for p in planets:
            p["house"] = _house_of(p["lon"], cusps)

    aspects = []
    pts = [p for p in planets if p["id"] != "node"]
    for i, a in enumerate(pts):
        for c in pts[i + 1:]:
            if not time_known and "moon" in (a["id"], c["id"]):
                continue  # Moon moves ~13°/day: aspects unreliable without a time
            d = abs(a["lon"] - c["lon"]) % 360
            d = min(d, 360 - d)
            for name, ang, orb in ASPECTS:
                if a["id"] in LUMINARIES or c["id"] in LUMINARIES:
                    orb += 2
                if abs(d - ang) <= orb:
                    aspects.append({"a": a["id"], "b": c["id"], "type": name,
                                    "orb": round(abs(d - ang), 2)})
                    break
    aspects.sort(key=lambda x: x["orb"])

    return {"timeKnown": time_known, "utc": utc.isoformat(), "jd": round(jd, 6),
            "planets": planets, "houses": houses, "angles": angles,
            "aspects": aspects}


# ---------------------------------------------------------------- synastry
SYN_POINTS = ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn"]
ELEMENTS = ["fire", "earth", "air", "water"]
MODES = ["cardinal", "fixed", "mutable"]


def balance(chart: dict) -> dict:
    """Element and modality count over the ten planets (plus Ascendant when known)."""
    el = dict.fromkeys(ELEMENTS, 0)
    md = dict.fromkeys(MODES, 0)
    idxs = [p["signIndex"] for p in chart["planets"] if p["id"] != "node"]
    if chart.get("angles"):
        idxs.append(chart["angles"]["asc"]["signIndex"])
    for i in idxs:
        el[ELEMENTS[i % 4]] += 1
        md[MODES[i % 3]] += 1
    return {"elements": el, "modes": md}


def synastry(a: dict, b: dict) -> list[dict]:
    """Aspects between person A's and person B's planets (and Ascendants when known)."""
    def pts(c):
        out = [(p["id"], p["lon"]) for p in c["planets"] if p["id"] in SYN_POINTS + ["uranus", "neptune", "pluto"]]
        if c.get("angles"):
            out.append(("asc", c["angles"]["asc"]["lon"]))
        if not c["timeKnown"]:
            out = [x for x in out if x[0] != "moon"]
        return out

    res = []
    for ida, la in pts(a):
        for idb, lb in pts(b):
            if ida in ("uranus", "neptune", "pluto") and idb in ("uranus", "neptune", "pluto"):
                continue  # generational, shared by people of the same age
            d = abs(la - lb) % 360
            d = min(d, 360 - d)
            for name, ang, orb in ASPECTS:
                orb = 6 if {ida, idb} & LUMINARIES else 4
                if abs(d - ang) <= orb:
                    res.append({"a": ida, "b": idb, "type": name, "orb": round(abs(d - ang), 2)})
                    break
    res.sort(key=lambda x: (x["a"] not in ("sun", "moon", "venus", "mars"), x["orb"]))
    return res


# ---------------------------------------------------------------- transits
TRANSIT_PLANETS = [("jupiter", swe.JUPITER), ("saturn", swe.SATURN), ("uranus", swe.URANUS),
                   ("neptune", swe.NEPTUNE), ("pluto", swe.PLUTO)]
NATAL_TARGETS = ["sun", "moon", "mercury", "venus", "mars"]


def transits(natal: dict, year: int, orb: float = 1.0) -> dict:
    """Slow-planet transits to the natal chart through a calendar year, grouped into periods."""
    targets = [(p["id"], p["lon"]) for p in natal["planets"] if p["id"] in NATAL_TARGETS]
    if not natal["timeKnown"]:
        targets = [t for t in targets if t[0] != "moon"]
    if natal.get("angles"):
        targets += [("asc", natal["angles"]["asc"]["lon"]), ("mc", natal["angles"]["mc"]["lon"])]

    start = swe.julday(year, 1, 1, 12.0)
    days = int(swe.julday(year + 1, 1, 1, 12.0) - start)
    track: dict[tuple, list] = {}
    ingress: dict[str, list] = {}
    for day in range(days):
        jd = start + day
        for tid, pid in TRANSIT_PLANETS:
            lon = swe.calc_ut(jd, pid, FLAGS)[0][0]
            sidx = int(lon // 30)
            seq = ingress.setdefault(tid, [])
            if not seq or seq[-1][1] != sidx:
                seq.append((day, sidx))
            for nid, nlon in targets:
                d = abs(lon - nlon) % 360
                d = min(d, 360 - d)
                for name, ang, _ in ASPECTS:
                    if abs(d - ang) <= orb:
                        track.setdefault((tid, nid, name), []).append((day, abs(d - ang)))

    def date_of(day):
        y, m, dd, _ = swe.revjul(start + day)
        return f"{y:04d}-{m:02d}-{dd:02d}"

    events = []
    for (tid, nid, name), hits in track.items():
        # split into contiguous periods (retrograde loops create several)
        period = [hits[0]]
        for h in hits[1:] + [None]:
            if h is not None and h[0] == period[-1][0] + 1:
                period.append(h)
                continue
            exact = min(period, key=lambda x: x[1])
            events.append({"transit": tid, "natal": nid, "type": name,
                           "from": date_of(period[0][0]), "to": date_of(period[-1][0]),
                           "exact": date_of(exact[0]), "minOrb": round(exact[1], 2)})
            if h is not None:
                period = [h]
    events.sort(key=lambda e: e["from"])

    signs_in_year = {tid: [{"sign": SIGNS[s], "from": date_of(d)} for d, s in seq] for tid, seq in ingress.items()}
    return {"year": year, "orb": orb, "events": events, "signs": signs_in_year}
