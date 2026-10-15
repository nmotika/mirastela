"""Offline city search (GeoNames via geonamescache) with IANA time zones."""
from __future__ import annotations

import unicodedata
from functools import lru_cache

import geonamescache

# GeoNames uses English names for a few capitals; show the local name instead.
LOCAL_NAMES = {"Warsaw": "Warszawa", "Prague": "Praha", "Bucharest": "București"}

MARKET_COUNTRY = {"pl": "PL", "hr": "HR", "sl": "SI", "ro": "RO",
                  "cs": "CZ", "hu": "HU", "en": None}


def norm(s: str) -> str:
    s = s.replace("ł", "l").replace("Ł", "L").replace("đ", "d").replace("Đ", "D")
    s = unicodedata.normalize("NFKD", s)
    return "".join(ch for ch in s if not unicodedata.combining(ch)).lower().strip()


@lru_cache(maxsize=1)
def _index():
    gc = geonamescache.GeonamesCache()
    countries = {c["iso"]: c["name"] for c in gc.get_countries().values()}
    rows = []
    for c in gc.get_cities().values():
        keys = {norm(c["name"])}
        keys.update(norm(a) for a in c.get("alternatenames", []) if a)
        rows.append((keys, {"id": c["geonameid"], "name": LOCAL_NAMES.get(c["name"], c["name"]),
                            "country": c["countrycode"],
                            "countryName": countries.get(c["countrycode"], ""),
                            "lat": c["latitude"], "lon": c["longitude"],
                            "tz": c["timezone"], "pop": c["population"]}))
    by_id = {r[1]["id"]: r[1] for r in rows}
    return rows, by_id


def search(q: str, lang: str = "en", limit: int = 8) -> list[dict]:
    nq = norm(q)
    if len(nq) < 2:
        return []
    home = MARKET_COUNTRY.get(lang)
    rows, _ = _index()
    hits = []
    for keys, city in rows:
        if any(k.startswith(nq) for k in keys):
            exact = norm(city["name"]).startswith(nq)
            score = (city["country"] == home, exact, city["pop"])
            hits.append((score, city))
    hits.sort(key=lambda h: h[0], reverse=True)
    return [h[1] for h in hits[:limit]]


def get(city_id: int) -> dict | None:
    return _index()[1].get(city_id)
