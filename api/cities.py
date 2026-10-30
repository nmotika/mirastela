"""Offline city search (GeoNames via geonamescache) with IANA time zones."""
from __future__ import annotations

import unicodedata
from functools import lru_cache

import geonamescache

from exonyms import EXONYMS

# GeoNames uses English names for a few capitals; in English we show the local name instead.
LOCAL_NAMES = {"Warsaw": "Warszawa", "Prague": "Praha", "Bucharest": "București"}
# GeoNames writes Romanian with cedillas (ş ţ); the correct letters have commas (ș ț).
RO_FIX = str.maketrans({"ş": "ș", "Ş": "Ș", "ţ": "ț", "Ţ": "Ț"})

MARKET_COUNTRY = {"pl": "PL", "hr": "HR", "sl": "SI", "ro": "RO",
                  "cs": "CZ", "hu": "HU", "de": "DE", "fr": "FR", "it": "IT", "es": "ES", "en": None}


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
        key = (c["name"], c["countrycode"])
        keys.update(norm(ex[key]) for ex in EXONYMS.values() if key in ex)
        name = c["name"].translate(RO_FIX) if c["countrycode"] in ("RO", "MD") else c["name"]
        rows.append((keys, {"id": c["geonameid"], "name": LOCAL_NAMES.get(name, name), "key": key,
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
    ex = EXONYMS.get(lang, {})
    hits = []
    for keys, city in rows:
        if any(k.startswith(nq) for k in keys):
            shown = ex.get(city["key"], city["name"])
            # A whole-word match on any name ("beč" = Vienna) beats a prefix of a smaller town ("Béchar").
            full = nq in keys
            prefix_bonus = 3 if norm(shown).startswith(nq) else 1
            score = (city["country"] == home, full, city["pop"] * prefix_bonus)
            hits.append((score, city, shown))
    hits.sort(key=lambda h: h[0], reverse=True)
    return [{**{k: v for k, v in c.items() if k != "key"}, "name": shown} for _, c, shown in hits[:limit]]


def get(city_id: int, lang: str = "en") -> dict | None:
    c = _index()[1].get(city_id)
    if not c:
        return None
    return {**{k: v for k, v in c.items() if k != "key"}, "name": EXONYMS.get(lang, {}).get(c["key"], c["name"])}
