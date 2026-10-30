"""The sky of a whole year, for the yearly sign forecasts: where the slow planets stand and when they
change sign, Mercury (and Venus) retrograde periods, and the eclipses. Each fact is also translated
into the life area (solar house) it touches for every sign, so the model never counts houses itself."""
from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone

import swisseph as swe

from chart import FLAGS, SIGNS
from sky import AREAS

SLOW = [("jupiter", swe.JUPITER), ("saturn", swe.SATURN), ("uranus", swe.URANUS), ("neptune", swe.NEPTUNE),
        ("pluto", swe.PLUTO), ("mars", swe.MARS)]
FAST_RETRO = [("mercury", swe.MERCURY), ("venus", swe.VENUS)]


def _jd(d: date) -> float:
    return swe.julday(d.year, d.month, d.day, 12.0)


def _pos(d: date, num: int) -> tuple[float, float]:
    xx, _ = swe.calc_ut(_jd(d), num, FLAGS)
    return xx[0], xx[3]


def _days(year: int):
    d = date(year, 1, 1)
    while d.year == year:
        yield d
        d += timedelta(days=1)


def periods(year: int, num: int) -> list[dict]:
    """Stretches of the year a planet spends in one sign (a sign can come back after a retrograde)."""
    out, cur = [], None
    for d in _days(year):
        sign = int(_pos(d, num)[0] // 30)
        if cur is None or sign != cur["sign"]:
            if cur:
                cur["to"] = (d - timedelta(days=1)).isoformat()
            cur = {"sign": sign, "from": d.isoformat(), "to": None}
            out.append(cur)
    out[-1]["to"] = date(year, 12, 31).isoformat()
    return out


def retrogrades(year: int, num: int) -> list[dict]:
    out, cur = [], None
    for d in _days(year):
        lon, speed = _pos(d, num)
        if speed < 0 and cur is None:
            cur = {"from": d.isoformat(), "sign": int(lon // 30)}
        elif speed >= 0 and cur is not None:
            cur["to"] = (d - timedelta(days=1)).isoformat()
            cur["endSign"] = int(lon // 30)
            out.append(cur)
            cur = None
    if cur:
        cur["to"], cur["endSign"] = date(year, 12, 31).isoformat(), int(_pos(date(year, 12, 31), num)[0] // 30)
        out.append(cur)
    return out


def _jd_date(jd: float) -> date:
    y, m, d, _ = swe.revjul(jd)
    return date(y, m, d)


def eclipses(year: int) -> list[dict]:
    out = []
    start = swe.julday(year, 1, 1, 0)
    end = swe.julday(year + 1, 1, 1, 0)
    jd = start
    while True:
        res, tret = swe.sol_eclipse_when_glob(jd, FLAGS, 0)
        if tret[0] >= end:
            break
        lon = swe.calc_ut(tret[0], swe.SUN, FLAGS)[0][0]
        kind = "total" if res & swe.ECL_TOTAL else "annular" if res & swe.ECL_ANNULAR else "partial" if res & swe.ECL_PARTIAL else "hybrid"
        out.append({"type": f"{kind} solar eclipse", "date": _jd_date(tret[0]).isoformat(), "sign": int(lon // 30)})
        jd = tret[0] + 20
    jd = start
    while True:
        res, tret = swe.lun_eclipse_when(jd, FLAGS, 0)
        if tret[0] >= end:
            break
        lon = swe.calc_ut(tret[0], swe.MOON, FLAGS)[0][0]
        kind = "total" if res & swe.ECL_TOTAL else "partial" if res & swe.ECL_PARTIAL else "penumbral"
        out.append({"type": f"{kind} lunar eclipse", "date": _jd_date(tret[0]).isoformat(), "sign": int(lon // 30)})
        jd = tret[0] + 20
    return sorted(out, key=lambda e: e["date"])


def year_facts(year: int) -> dict:
    return {"year": year,
            "slow": {pid: periods(year, num) for pid, num in SLOW},
            "retro": {pid: retrogrades(year, num) for pid, num in FAST_RETRO},
            "eclipses": eclipses(year),
            "venus": periods(year, swe.VENUS)}


def year_text(facts: dict, sign: int) -> str:
    """Facts for one sign's yearly forecast, with the life area worked out."""
    area = lambda s: AREAS[(s - sign) % 12]
    rows = [f"Year {facts['year']}, for {SIGNS[sign]}. Each fact names the area of life it touches for this sign (solar houses, already worked out; use exactly these)."]
    rows.append("\nSlow planets (the main themes of the year):")
    for pid, per in facts["slow"].items():
        for p in per:
            rows.append(f"- {pid} in {SIGNS[p['sign']]} from {p['from']} to {p['to']} → {area(p['sign'])}")
    rows.append("\nRetrograde periods (time to review, not to start new things in that area):")
    for pid, rs in facts["retro"].items():
        for r in rs:
            where = SIGNS[r['sign']] if r['sign'] == r['endSign'] else f"{SIGNS[r['sign']]} and {SIGNS[r['endSign']]}"
            rows.append(f"- {pid} retrograde from {r['from']} to {r['to']} in {where} → {area(r['sign'])}")
    rows.append("\nEclipses (turning points):")
    for e in facts["eclipses"]:
        rows.append(f"- {e['type']} on {e['date']} in {SIGNS[e['sign']]} → {area(e['sign'])}")
    return "\n".join(rows)


def venus_text(facts: dict, sign: int) -> str:
    """Venus through the signs (love, pleasure, attraction), for the love page."""
    area = lambda s: AREAS[(s - sign) % 12]
    rows = ["\nVenus (love, attraction, pleasure) through the year:"]
    rows += [f"- venus in {SIGNS[p['sign']]} from {p['from']} to {p['to']} → {area(p['sign'])}" for p in facts.get("venus", [])]
    return "\n".join(rows)


if __name__ == "__main__":
    f = year_facts(2027)
    print(year_text(f, 0))
