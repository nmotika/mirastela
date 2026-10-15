"""Mirastela API: city search, natal chart calculation, lead capture."""
from __future__ import annotations

import os
import json
import re
import secrets
import sqlite3
from datetime import date, datetime, time, timezone

from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

def _load_env():
    path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.strip().split("=", 1)
                if v:
                    os.environ.setdefault(k, v)


_load_env()

import chart
import cities
import report

DB_PATH = os.environ.get("MIRASTELA_DB", os.path.join(os.path.dirname(__file__), "mirastela.db"))
SOURCE_URL = os.environ.get("MIRASTELA_SOURCE_URL", "")  # AGPL: link to this source code

app = FastAPI(title="Mirastela API")
PROXY_SECRET = os.environ.get("MIRASTELA_PROXY_SECRET", "")


@app.middleware("http")
async def require_proxy_secret(request: Request, call_next):
    """In production only the Cloudflare Pages proxy may call the API."""
    if PROXY_SECRET and request.url.path != "/api/health" \
            and request.headers.get("x-proxy-secret") != PROXY_SECRET:
        return JSONResponse({"detail": "forbidden"}, status_code=403)
    return await call_next(request)


app.add_middleware(CORSMiddleware, allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
                   allow_methods=["GET", "POST"], allow_headers=["*"])


def db():
    con = sqlite3.connect(DB_PATH)
    con.execute("""create table if not exists leads(
        id integer primary key, created text, email text, lang text, name text,
        birth_date text, birth_time text, city_id integer, focus text, status text,
        marketing_consent integer)""")
    con.execute("""create table if not exists orders(
        token text primary key, created text, lang text, email text, name text,
        input text, chart text, coupon text)""")
    con.execute("""create table if not exists items(
        id integer primary key, token text, product text, input text, data text,
        status text, markdown text, model text, created text, unique(token, product))""")
    return con


COUPONS = {c.strip().upper() for c in os.environ.get("MIRASTELA_COUPONS", "MIRATEST").split(",") if c.strip()}
PRODUCTS = ("natal", "partner", "forecast")


def forecast_year() -> int:
    today = datetime.now(timezone.utc).date()
    return today.year + 1 if today.month >= 10 else today.year


def birth_chart(d: str, t: str | None, city_id: int) -> dict:
    city = cities.get(city_id)
    if not city:
        raise HTTPException(404, "city not found")
    clock = time.fromisoformat(t) if t else None
    res = chart.calculate(chart.BirthData(date.fromisoformat(d), clock, city["lat"], city["lon"], city["tz"]))
    res["city"] = {k: city[k] for k in ("id", "name", "country", "tz")}
    return res


@app.get("/api/health")
def health():
    return {"ok": True, "source": SOURCE_URL}


@app.get("/api/cities")
def city_search(q: str, lang: str = "en"):
    return cities.search(q, lang)


@app.get("/api/sun")
def sun_sign(d: date):
    """Sun sign for a date at 12:00 UTC (quick reward in the quiz; the full chart is exact)."""
    res = chart.calculate(chart.BirthData(d, time(12, 0), 0.0, 0.0, "UTC"))
    sun = res["planets"][0]
    return {"sign": sun["sign"], "signIndex": sun["signIndex"]}


class ChartIn(BaseModel):
    date: date
    time: str | None = Field(None, pattern=r"^\d{2}:\d{2}$")
    cityId: int


@app.post("/api/chart")
def make_chart(body: ChartIn):
    city = cities.get(body.cityId)
    if not city:
        raise HTTPException(404, "city not found")
    if not (date(1900, 1, 1) <= body.date <= datetime.now(timezone.utc).date()):
        raise HTTPException(422, "date out of range")
    clock = time.fromisoformat(body.time) if body.time else None
    res = chart.calculate(chart.BirthData(body.date, clock, city["lat"], city["lon"], city["tz"]))
    res["city"] = {k: city[k] for k in ("id", "name", "country", "tz")}
    return res


class LeadIn(BaseModel):
    email: str
    lang: str = "pl"
    name: str = ""
    date: str = ""
    time: str | None = None
    cityId: int | None = None
    focus: list[str] = []
    status: str = ""
    marketingConsent: bool = False


@app.post("/api/lead")
def lead(body: LeadIn):
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", body.email):
        raise HTTPException(422, "invalid email")
    with db() as con:
        con.execute("insert into leads(created,email,lang,name,birth_date,birth_time,city_id,focus,status,marketing_consent)"
                    " values(?,?,?,?,?,?,?,?,?,?)",
                    (datetime.now(timezone.utc).isoformat(), body.email.lower(), body.lang, body.name[:80],
                     body.date, body.time, body.cityId, ",".join(body.focus), body.status,
                     int(body.marketingConsent)))
    return {"ok": True}


# ---------------------------------------------------------------- orders
class PartnerIn(BaseModel):
    name: str = Field("", max_length=40)
    date: date
    time: str | None = Field(None, pattern=r"^\d{2}:\d{2}$")
    cityId: int


class OrderIn(BaseModel):
    lang: str = "pl"
    email: str
    name: str = Field("", max_length=40)
    date: date
    time: str | None = Field(None, pattern=r"^\d{2}:\d{2}$")
    cityId: int
    focus: list[str] = []
    status: str = ""
    coupon: str = ""


class AddIn(BaseModel):
    product: str
    partner: PartnerIn | None = None


def _coupon_ok(code: str) -> bool:
    return code.strip().upper() in COUPONS


def _build(token: str, product: str):
    """Compute the product's data and write the report (runs in the background)."""
    with db() as con:
        lang, name, inp, natal = con.execute(
            "select lang, name, input, chart from orders where token=?", (token,)).fetchone()
        item_input = con.execute("select input from items where token=? and product=?", (token, product)).fetchone()[0]
    natal, inp = json.loads(natal), json.loads(inp)
    try:
        if product == "natal":
            bal = chart.balance(natal)
            data = {"balance": bal}
            prompt = report.prompt_natal(lang, name, natal, inp.get("focus", []), bal)
        elif product == "partner":
            p = json.loads(item_input)
            pc = birth_chart(p["date"], p.get("time"), p["cityId"])
            syn = chart.synastry(natal, pc)
            data = {"partner": p, "partnerChart": pc, "synastry": syn}
            prompt = report.prompt_partner(lang, name, p.get("name", ""), natal, pc, syn)
        else:
            tr = chart.transits(natal, forecast_year())
            data = {"transits": tr}
            prompt = report.prompt_forecast(lang, name, natal, tr)
        md, model = report.generate(prompt)
        status = "ready"
    except Exception as exc:  # keep the error visible for debugging
        data, md, model, status = {"error": str(exc)}, "", "", "error"
    with db() as con:
        con.execute("update items set data=?, markdown=?, model=?, status=? where token=? and product=?",
                    (json.dumps(data), md, model, status, token, product))


def _add_item(token: str, product: str, item_input: dict | None, bg: BackgroundTasks):
    with db() as con:
        con.execute("insert or ignore into items(token, product, input, status, created) values(?,?,?,?,?)",
                    (token, product, json.dumps(item_input or {}), "pending", datetime.now(timezone.utc).isoformat()))
    bg.add_task(_build, token, product)


@app.post("/api/order")
def create_order(body: OrderIn, bg: BackgroundTasks):
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", body.email):
        raise HTTPException(422, "invalid email")
    if not _coupon_ok(body.coupon):
        # Real payments (Stripe) come later; until then only a valid coupon completes an order.
        raise HTTPException(402, "payment required")
    natal = birth_chart(body.date.isoformat(), body.time, body.cityId)
    token = secrets.token_urlsafe(16)
    with db() as con:
        con.execute("insert into orders values(?,?,?,?,?,?,?,?)",
                    (token, datetime.now(timezone.utc).isoformat(), body.lang, body.email.lower(), body.name,
                     body.model_dump_json(exclude={"coupon"}), json.dumps(natal), body.coupon.strip().upper()))
    _add_item(token, "natal", None, bg)
    return {"token": token}


@app.post("/api/coupon")
def check_coupon(body: dict):
    return {"valid": _coupon_ok(str(body.get("code", "")))}


@app.post("/api/order/{token}/add")
def add_product(token: str, body: AddIn, bg: BackgroundTasks):
    if body.product not in ("partner", "forecast"):
        raise HTTPException(422, "unknown product")
    with db() as con:
        row = con.execute("select coupon from orders where token=?", (token,)).fetchone()
    if not row:
        raise HTTPException(404, "order not found")
    if not _coupon_ok(row[0] or ""):
        raise HTTPException(402, "payment required")
    if body.product == "partner":
        if not body.partner:
            raise HTTPException(422, "partner data required")
        _add_item(token, "partner", body.partner.model_dump(mode="json"), bg)
    else:
        _add_item(token, "forecast", None, bg)
    return {"ok": True}


@app.get("/api/order/{token}")
def get_order(token: str):
    with db() as con:
        row = con.execute("select lang, name, chart, input from orders where token=?", (token,)).fetchone()
        if not row:
            raise HTTPException(404, "order not found")
        items = con.execute("select product, status, markdown, data, model from items where token=? order by id",
                            (token,)).fetchall()
    lang, name, natal, inp = row
    return {
        "lang": lang, "name": name, "chart": json.loads(natal), "input": json.loads(inp),
        "forecastYear": forecast_year(),
        "items": [{"product": p, "status": s, "markdown": md or "", "data": json.loads(d) if d else None, "model": m}
                  for p, s, md, d, m in items],
    }
