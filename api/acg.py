"""Astrocartography prototype: where each planet was rising, setting, culminating (MC) or at the
nadir (IC) at the moment of birth, and which cities lie close to those lines.

    python acg.py 1985-06-11 16:15 Zagreb
"""
from __future__ import annotations

import math
import sys
from datetime import date, datetime, time
from zoneinfo import ZoneInfo

import swisseph as swe

import cities

PLANETS = [("sun", swe.SUN), ("moon", swe.MOON), ("mercury", swe.MERCURY), ("venus", swe.VENUS), ("mars", swe.MARS),
           ("jupiter", swe.JUPITER), ("saturn", swe.SATURN), ("uranus", swe.URANUS), ("neptune", swe.NEPTUNE), ("pluto", swe.PLUTO)]
# Theme weights per planet and angle kind; negative = harder places.
THEMES = {
    "love":   {"venus": 1.0, "moon": 0.6, "jupiter": 0.5, "sun": 0.3, "saturn": -0.6, "mars": -0.3, "pluto": -0.4},
    "career": {"sun": 1.0, "jupiter": 0.9, "mars": 0.5, "saturn": 0.3, "mercury": 0.4, "venus": 0.2, "neptune": -0.4},
    "home":   {"moon": 1.0, "venus": 0.6, "jupiter": 0.6, "saturn": -0.5, "uranus": -0.4, "pluto": -0.5},
}
ANGLE_W = {"MC": 1.0, "ASC": 1.0, "IC": 0.8, "DSC": 0.8}
THEME_ANGLE = {"career": {"MC": 1.3, "ASC": 1.0, "IC": 0.5, "DSC": 0.7}, "home": {"IC": 1.4, "ASC": 0.9, "MC": 0.6, "DSC": 0.8},
               "love": {"DSC": 1.4, "ASC": 1.0, "MC": 0.8, "IC": 0.9}}
ORB_KM = 900.0

# Places people actually move to (lat, lon).
CITIES = {
    "London": (51.51, -0.13), "Manchester": (53.48, -2.24), "Edinburgh": (55.95, -3.19), "Dublin": (53.35, -6.26),
    "Paris": (48.86, 2.35), "Lyon": (45.76, 4.84), "Nice": (43.70, 7.27), "Amsterdam": (52.37, 4.90), "Brussels": (50.85, 4.35),
    "Berlin": (52.52, 13.40), "Munich": (48.14, 11.58), "Hamburg": (53.55, 9.99), "Frankfurt": (50.11, 8.68), "Vienna": (48.21, 16.37),
    "Zürich": (47.38, 8.54), "Geneva": (46.20, 6.14), "Milan": (45.46, 9.19), "Rome": (41.90, 12.50), "Florence": (43.77, 11.26),
    "Madrid": (40.42, -3.70), "Barcelona": (41.39, 2.17), "Valencia": (39.47, -0.38), "Málaga": (36.72, -4.42), "Lisbon": (38.72, -9.14),
    "Porto": (41.15, -8.61), "Copenhagen": (55.68, 12.57), "Stockholm": (59.33, 18.07), "Oslo": (59.91, 10.75), "Helsinki": (60.17, 24.94),
    "Warsaw": (52.23, 21.01), "Kraków": (50.06, 19.94), "Prague": (50.08, 14.44), "Budapest": (47.50, 19.04), "Ljubljana": (46.06, 14.51),
    "Zagreb": (45.81, 15.98), "Split": (43.51, 16.44), "Belgrade": (44.79, 20.45), "Athens": (37.98, 23.73), "Istanbul": (41.01, 28.98),
    "Bucharest": (44.43, 26.10), "Sofia": (42.70, 23.32), "Tallinn": (59.44, 24.75), "Valletta": (35.90, 14.51), "Reykjavík": (64.15, -21.94),
    "New York": (40.71, -74.01), "Boston": (42.36, -71.06), "Miami": (25.76, -80.19), "Chicago": (41.88, -87.63), "Austin": (30.27, -97.74),
    "Denver": (39.74, -104.99), "Los Angeles": (34.05, -118.24), "San Francisco": (37.77, -122.42), "Seattle": (47.61, -122.33),
    "Toronto": (43.65, -79.38), "Montreal": (45.50, -73.57), "Vancouver": (49.28, -123.12), "Mexico City": (19.43, -99.13),
    "Buenos Aires": (-34.60, -58.38), "São Paulo": (-23.55, -46.63), "Rio de Janeiro": (-22.91, -43.17), "Lima": (-12.05, -77.04),
    "Dubai": (25.20, 55.27), "Tel Aviv": (32.09, 34.78), "Cairo": (30.04, 31.24), "Marrakesh": (31.63, -8.01), "Cape Town": (-33.92, 18.42),
    "Nairobi": (-1.29, 36.82), "Mumbai": (19.08, 72.88), "Bangkok": (13.76, 100.50), "Bali": (-8.65, 115.22), "Singapore": (1.35, 103.82),
    "Hong Kong": (22.32, 114.17), "Tokyo": (35.68, 139.69), "Seoul": (37.57, 126.98), "Sydney": (-33.87, 151.21), "Melbourne": (-37.81, 144.96),
    "Auckland": (-36.85, 174.76),
}


def lines(jd: float) -> dict[str, dict]:
    gmst = swe.sidtime(jd) * 15.0
    eps = swe.calc_ut(jd, swe.ECL_NUT)[0][0]
    out = {}
    for pid, num in PLANETS:
        lon, lat = swe.calc_ut(jd, num, swe.FLG_SWIEPH)[0][:2]
        ra, dec = swe.cotrans((lon, lat, 1.0), -eps)[:2]
        out[pid] = {"ra": ra, "dec": dec, "mc": ((ra - gmst + 180) % 360) - 180}
    return out


def _lon_diff(a: float, b: float) -> float:
    return abs(((a - b + 180) % 360) - 180)


def distances(L: dict, phi: float, lam: float) -> list[tuple[str, str, float]]:
    """Distance in km from a place to each planet's four lines, measured along the parallel."""
    res = []
    k = 111.32 * math.cos(math.radians(phi))
    for pid, p in L.items():
        mc = p["mc"]
        res.append((pid, "MC", _lon_diff(lam, mc) * k))
        res.append((pid, "IC", _lon_diff(lam, mc + 180) * k))
        x = -math.tan(math.radians(phi)) * math.tan(math.radians(p["dec"]))
        if abs(x) <= 1:  # the planet rises and sets at this latitude
            h0 = math.degrees(math.acos(x))
            res.append((pid, "ASC", _lon_diff(lam, mc - h0) * k))
            res.append((pid, "DSC", _lon_diff(lam, mc + h0) * k))
    return res


def score(dist: list[tuple[str, str, float]], theme: str) -> tuple[float, list[tuple[str, str, int]]]:
    s, hits = 0.0, []
    for pid, ang, km in dist:
        if km > ORB_KM:
            continue
        w = THEMES[theme].get(pid, 0) * THEME_ANGLE[theme][ang] * (1 - km / ORB_KM)
        if w:
            s += w
            hits.append((pid, ang, round(km)))
    return s, sorted(hits, key=lambda h: h[2])


def main(d: str, t: str, place: str):
    c = cities.search(place, "hr")[0]
    local = datetime.combine(date.fromisoformat(d), time.fromisoformat(t), ZoneInfo(c["tz"]))
    u = local.astimezone(ZoneInfo("UTC"))
    jd = swe.julday(u.year, u.month, u.day, u.hour + u.minute / 60)
    L = lines(jd)
    print(f"{d} {t} {c['name']} ({c['tz']}), UTC {u:%H:%M}\n")
    print("MC lines (longitude):", ", ".join(f"{p} {v['mc']:.1f}" for p, v in L.items()))
    for theme in THEMES:
        ranked = sorted(((score(distances(L, *xy), theme), name) for name, xy in CITIES.items()), key=lambda r: -r[0][0])
        print(f"\n== {theme}: best")
        for (s, hits), name in ranked[:6]:
            print(f"  {name:15} {s:5.2f}  " + ", ".join(f"{p} {a} {km}km" for p, a, km in hits[:3]))
        print(f"-- {theme}: hardest")
        for (s, hits), name in ranked[-3:]:
            print(f"  {name:15} {s:5.2f}  " + ", ".join(f"{p} {a} {km}km" for p, a, km in hits[:3]))


if __name__ == "__main__":
    main(*sys.argv[1:4])
